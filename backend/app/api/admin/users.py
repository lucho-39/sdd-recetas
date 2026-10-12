"""
Admin: user management (/api/admin/users).
"""
import secrets
from datetime import UTC, date, datetime, time, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import record_audit
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import (
    create_password_reset_token,
    get_password_hash,
    require_admin,
    revoke_all_refresh_tokens,
)
from app.models import Favorite, OAuthAccount, Rating, Recipe, User, UserRole
from app.schemas.admin import GdprEraseRequest, UserAdminUpdate
from app.services.email import send_email

router = APIRouter()


def _to_item(user: User, **extra: object) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "role": user.role.value if hasattr(user.role, "value") else user.role,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at,
        "last_login_at": user.last_login_at,
        # Without these the row cannot tell "inactive" from "GDPR erased":
        # both have is_active=False.
        "deactivated_at": user.deactivated_at,
        "deleted_at": user.deleted_at,
        **extra,
    }


def _provider_filter(provider: str):
    """UC-ADMIN-005 AC2: ``email`` means "no linked OAuth account at all"."""
    linked = select(OAuthAccount.id).where(OAuthAccount.user_id == User.id).correlate(User)
    if provider == "email":
        return ~linked.exists()
    return linked.where(OAuthAccount.provider == provider).exists()


def _status_filter(state: str) -> list:
    # ``deleted`` is orthogonal to activity: a GDPR-erased account is both
    # inactive and deleted, and belongs in the "deleted" bucket.
    if state == "deleted":
        return [User.deleted_at.is_not(None)]
    active = state == "active"
    return [User.is_active.is_(active), User.deleted_at.is_(None)]


@router.get("", summary="List users (admin)")
async def list_users(
    search: str | None = Query(None),
    account_status: str | None = Query(
        None, alias="status", pattern="^(active|inactive|deleted)$"
    ),
    role: str | None = Query(None, pattern="^(user|admin)$"),
    provider: str | None = Query(None, pattern="^(email|google|github)$"),
    created_from: date | None = Query(None),
    created_to: date | None = Query(None),
    sort: str = Query("created_at", pattern="^(created_at|last_login_at|email|recipes_count)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if search:
        term = f"%{search}%"
        filters.append(or_(User.email.ilike(term), User.display_name.ilike(term)))
    if account_status:
        filters.extend(_status_filter(account_status))
    if role:
        filters.append(User.role == UserRole(role))
    if provider:
        filters.append(_provider_filter(provider))

    # UC-ADMIN-005 AC2: an inclusive day range, so picking the same date twice
    # matches that day rather than only its first instant.
    if created_from is not None:
        filters.append(User.created_at >= _at_start_of_day(created_from))
    if created_to is not None:
        filters.append(User.created_at < _at_start_of_day(created_to + timedelta(days=1)))

    recipes_count = (
        select(func.count(Recipe.id))
        .where(Recipe.author_id == User.id, Recipe.deleted_at.is_(None))
        .correlate(User)
        .scalar_subquery()
    )
    favorites_count = (
        # Composite PK, so there is no ``id`` column to count.
        select(func.count(Favorite.recipe_id))
        .where(Favorite.user_id == User.id)
        .correlate(User)
        .scalar_subquery()
    )
    ratings_count = (
        select(func.count(Rating.id))
        .where(Rating.user_id == User.id)
        .correlate(User)
        .scalar_subquery()
    )
    # A user may link more than one provider; show one, filter with EXISTS so
    # every linked provider still matches.
    provider_value = func.coalesce(
        select(func.min(OAuthAccount.provider))
        .where(OAuthAccount.user_id == User.id)
        .correlate(User)
        .scalar_subquery(),
        "email",
    )

    total = await db.scalar(select(func.count()).select_from(User).where(*filters))
    stmt = (
        select(
            User,
            provider_value.label("provider"),
            recipes_count.label("recipes_count"),
            favorites_count.label("favorites_count"),
            ratings_count.label("ratings_count"),
        )
        .where(*filters)
        .order_by(*_order_by(sort, recipes_count))
        .offset((page - 1) * limit)
        .limit(limit)
    )
    rows = (await db.execute(stmt)).all()
    return {
        "items": [
            _to_item(
                user,
                provider=provider,
                recipes_count=recipes,
                favorites_count=favorites,
                ratings_count=ratings,
            )
            for user, provider, recipes, favorites, ratings in rows
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


def _at_start_of_day(day: date) -> datetime:
    """Store datetimes are tz-aware; asyncpg rejects a naive bound on them."""
    return datetime.combine(day, time.min, tzinfo=UTC)


def _order_by(sort: str, recipes_count):
    if sort == "last_login_at":
        return (User.last_login_at.desc().nullslast(),)
    if sort == "email":
        return (User.email.asc(),)
    if sort == "recipes_count":
        return (recipes_count.desc(),)
    return (User.created_at.desc(),)


def _tally(predicate):
    """COUNT matching a predicate — an aggregate over an empty set is NULL."""
    return func.coalesce(func.sum(case((predicate, 1), else_=0)), 0)


async def _metrics(db: AsyncSession, user_id: UUID) -> dict:
    """UC-ADMIN-006 AC3 / UC-ADMIN-008 AC2: the numbers both panels show.

    The recipe breakdown is one aggregate rather than four COUNTs, because
    splitting visibility and deletion means four passes over the same rows.
    """
    recipes_public, recipes_private, recipes_deleted = (
        await db.execute(
            select(
                _tally(and_(Recipe.deleted_at.is_(None), Recipe.is_public.is_(True))),
                _tally(and_(Recipe.deleted_at.is_(None), Recipe.is_public.is_(False))),
                _tally(Recipe.deleted_at.is_not(None)),
            )
            .select_from(Recipe)
            .where(Recipe.author_id == user_id)
        )
    ).one()

    favorites = await db.scalar(
        select(func.count(Favorite.recipe_id)).where(Favorite.user_id == user_id)
    )
    ratings_count = await db.scalar(
        select(func.count(Rating.id)).where(Rating.user_id == user_id)
    )
    ratings_average = await db.scalar(
        select(func.avg(Rating.score)).where(Rating.user_id == user_id)
    )
    provider = await db.scalar(
        select(func.coalesce(func.min(OAuthAccount.provider), "email")).where(
            OAuthAccount.user_id == user_id
        )
    )

    return {
        "provider": provider,
        # public + private, so this still matches the list's recipes_count,
        # which already excludes soft-deleted rows.
        "recipes_count": int(recipes_public) + int(recipes_private),
        "recipes_public": int(recipes_public),
        "recipes_private": int(recipes_private),
        "recipes_deleted": int(recipes_deleted),
        "favorites_count": int(favorites or 0),
        "ratings_count": int(ratings_count or 0),
        "ratings_average": round(float(ratings_average), 2)
        if ratings_average is not None
        else None,
    }


@router.get("/{user_id}", summary="User detail (admin)")
async def get_user(
    user_id: UUID,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # _to_item, not UserResponse: the shared auth schema backs the public
    # /auth and /users/me endpoints, and UC-ADMIN-006 needs avatar_url plus
    # the two tombstone dates that schema does not carry.
    return {**_to_item(user), **await _metrics(db, user_id)}


@router.post("/{user_id}/activate", summary="Activate user (admin)")
async def activate_user(
    user_id: UUID,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    user.is_verified = True
    # UC-ADMIN-007 AC3: restoring access also clears the deactivation stamp,
    # otherwise the row still reads as "deactivated" and UC-009 AC1 no longer
    # distinguishes this account from one that is still suspended.
    user.deactivated_at = None
    await record_audit(db, admin.id, "user.activate", target_type="user", target_id=str(user.id))
    await db.commit()
    return _to_item(user)


@router.post("/{user_id}/deactivate", summary="Deactivate user (admin)")
async def deactivate_user(
    user_id: UUID,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    # UC-ADMIN-007 AC2: stamp the suspension (UC-009 AC1 keys off it) and cut
    # short any session already held by the account — flipping is_active only
    # stops new logins, while a live refresh token keeps minting access tokens.
    user.deactivated_at = datetime.utcnow()
    await record_audit(db, admin.id, "user.deactivate", target_type="user", target_id=str(user.id))
    await revoke_all_refresh_tokens(db, user.id)
    await db.commit()
    return _to_item(user)


@router.post("/{user_id}/reactivate", summary="Reactivate user (admin)")
async def reactivate_user(
    user_id: UUID,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """UC-ADMIN-009: restore an account the admin had suspended."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_active or user.deactivated_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only a deactivated account can be reactivated",
        )

    user.is_active = True
    user.deactivated_at = None
    # UC-ADMIN-009 AC3
    user.must_change_password = False

    await record_audit(
        db, admin.id, "user.force_reactivate", target_type="user", target_id=str(user.id)
    )

    # AC3: the account is reachable again, but only the holder of this link
    # may walk back in — deactivation is what an admin does after a
    # compromise, and the old password may still belong to the attacker.
    reset_url = (
        f"{get_settings().FRONTEND_URL}/reset-password"
        f"?token={create_password_reset_token(str(user.id))}"
    )
    await send_email(
        db,
        to_email=user.email,
        subject="Tu cuenta fue reactivada — Recetario IA",
        body=(
            "Hola,\n\n"
            "Alguien con permisos administrativos reactivó tu cuenta.\n"
            "Para elegir una contraseña nueva abrí este enlace:\n"
            f"{reset_url}\n\n"
            "Si no esperabas este mensaje, avisá al equipo de Recetario IA.\n\n— Recetario IA"
        ),
    )
    await db.commit()

    payload = _to_item(user)
    # Same concession as forgot_password: SMTP is external, so dev exposes the
    # link to make the flow exercisable without a mail server.
    if get_settings().ENVIRONMENT != "production":
        payload["reset_url"] = reset_url
    return payload


@router.post("/{user_id}/gdpr-erase", summary="Erase user data (GDPR, admin)")
async def gdpr_erase_user(
    user_id: UUID,
    data: GdprEraseRequest,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Anonymize the user's PII and deactivate the account.

    Optionally soft-deletes the user's recipes as well.
    """
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recipes_deleted = 0
    if data.delete_recipes:
        recipes = (
            await db.execute(
                select(Recipe).where(Recipe.author_id == user.id, Recipe.deleted_at.is_(None))
            )
        ).scalars().all()
        for recipe in recipes:
            recipe.deleted_at = datetime.utcnow()
            recipe.is_public = False
            recipes_deleted += 1

    user.email = f"deleted+{user.id}@recetario.local"
    user.display_name = "Usuario eliminado"
    user.avatar_url = None
    user.password_hash = get_password_hash(secrets.token_urlsafe(24))
    user.is_active = False
    user.is_verified = False
    user.deleted_at = datetime.utcnow()

    await record_audit(
        db,
        admin.id,
        "user.gdpr_erase",
        target_type="user",
        target_id=str(user.id),
        detail={"delete_recipes": data.delete_recipes, "recipes_deleted": recipes_deleted},
    )
    await db.commit()
    return {"erased": True, "id": str(user.id), "recipes_deleted": recipes_deleted}


@router.patch("/{user_id}/role", summary="Change user role (admin)")
async def change_role(
    user_id: UUID,
    data: UserAdminUpdate,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.role is not None:
        # UC-ADMIN-011 AC2: demoting yourself drops you out of require_admin on
        # the next request, and there is no recovery path in the MVP.
        if data.role != UserRole.ADMIN and user.id == admin.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot change your own role",
            )
        # UC-ADMIN-011 AC1: role changes apply to live accounts only — a
        # dormant account must be reactivated first so the audit trail names
        # an actor who still exists.
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reactivate the account before changing its role",
            )
        user.role = UserRole(data.role)

    if data.is_verified is not None:
        user.is_verified = data.is_verified
    await record_audit(
        db,
        admin.id,
        "user.update",
        target_type="user",
        target_id=str(user.id),
        detail=data.model_dump(exclude_unset=True),
    )
    await db.commit()
    return _to_item(user)
