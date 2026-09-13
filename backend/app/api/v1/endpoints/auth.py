"""
Authentication endpoints
"""
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode
from uuid import UUID, uuid4

import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.app_settings import get_setting
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    create_email_verification_token,
    create_password_reset_token,
    create_oauth_state,
    decode_token,
    blacklist_token,
)
from app.models import OAuthAccount, RefreshToken, User, UserRole
from app.schemas.auth import (
    Token,
    TokenRefresh,
    UserCreate,
    UserResponse,
    PasswordChange,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChange as PasswordChangeSchema,
)
from app.services.email import send_email

settings = get_settings()

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if not payload:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception

    try:
        user_uuid = UUID(str(user_id))
    except (ValueError, TypeError):
        raise credentials_exception

    result = await db.execute(
        select(User).where(User.id == user_uuid)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def create_admin_user(db: AsyncSession) -> None:
    """Create initial admin user if not exists (bootstrap)."""
    settings = get_settings()

    # Check if admin already exists
    result = await db.execute(
        select(User).where(User.email == settings.ADMIN_INITIAL_USER)
    )
    existing_admin = result.scalar_one_or_none()

    if existing_admin:
        return  # Admin already exists

    # Create admin user
    admin_user = User(
        email=settings.ADMIN_INITIAL_USER,
        password_hash=get_password_hash(settings.ADMIN_INITIAL_PASSWORD),
        display_name="Administrador",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
        must_change_password=True,
    )

    db.add(admin_user)
    await db.commit()
    await db.refresh(admin_user)
    print(f"Admin user created: {admin_user.email}")


async def _issue_tokens(
    db: AsyncSession, user: User, family_id: Optional[str] = None
) -> tuple[str, str]:
    """Create an access + refresh pair and persist the refresh token row."""
    jti = str(uuid4())
    family = family_id or jti
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id), jti=jti)
    db.add(
        RefreshToken(
            user_id=user.id,
            jti=jti,
            family_id=family,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )
    await db.commit()
    return access_token, refresh_token


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=60 * 60 * 24 * 30,  # 30 days
        path="/api/v1/auth/refresh",
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    if not await get_setting(db, "registration_open"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is currently closed",
        )

    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    require_verification = bool(await get_setting(db, "require_email_verification"))
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        display_name=user_data.display_name,
        is_verified=not require_verification,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Login with email and password."""
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()

    access_token, refresh_token = await _issue_tokens(db, user)
    _set_refresh_cookie(response, refresh_token)

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using the refresh token cookie.

    Rotates the refresh token and detects reuse: presenting a revoked token
    revokes the whole rotation family.
    """
    refresh = request.cookies.get("refresh_token")
    if not refresh:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )

    payload = decode_token(refresh)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    jti = payload.get("jti")
    user_id = payload.get("sub")
    if not jti or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    stored = (
        await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    ).scalar_one_or_none()
    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    if stored.revoked:
        # Reuse detected: revoke the entire family.
        family = (
            await db.execute(
                select(RefreshToken).where(RefreshToken.family_id == stored.family_id)
            )
        ).scalars().all()
        for token in family:
            token.revoked = True
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token reuse detected",
        )

    try:
        user_uuid = UUID(str(user_id))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    user = await db.get(User, user_uuid)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    stored.revoked = True
    new_access_token, new_refresh_token = await _issue_tokens(
        db, user, family_id=stored.family_id
    )
    _set_refresh_cookie(response, new_refresh_token)

    return Token(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Logout - revoke the presented refresh token."""
    refresh = request.cookies.get("refresh_token")
    if refresh:
        payload = decode_token(refresh)
        jti = payload.get("jti") if payload else None
        if jti:
            stored = (
                await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
            ).scalar_one_or_none()
            if stored is not None:
                stored.revoked = True
                await db.commit()
        blacklist_token(refresh)

    response.delete_cookie(key="refresh_token", path="/api/v1/auth/refresh")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    user_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile."""
    if "display_name" in user_data:
        current_user.display_name = user_data["display_name"]
    if "avatar_url" in user_data:
        current_user.avatar_url = user_data["avatar_url"]

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Change password for authenticated user."""
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.must_change_password = False
    await db.commit()

    return {"message": "Password changed successfully"}


class VerifyEmailRequest(BaseModel):
    token: str


@router.post("/request-verification")
async def request_verification(
    payload: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate an email verification link for an account.

    Unauthenticated on purpose: an unverified user cannot log in yet. Email
    delivery is v2, so outside production the link is returned in the response
    (the response never reveals whether the email exists or is already verified).
    """
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if user and not user.is_verified:
        token = create_email_verification_token(str(user.id))
        url = f"/verify-email?token={token}" if settings.ENVIRONMENT != "production" else None
        return {"message": "Verification link generated", "verification_url": url}

    return {
        "message": "If the account needs verification, a link has been sent",
        "verification_url": None,
    }


@router.post("/verify-email")
async def verify_email(
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    """Mark the user's email as verified using a verification token."""
    data = decode_token(payload.token)
    if not data or data.get("type") != "email_verify":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    try:
        user_uuid = UUID(str(data.get("sub")))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    user = await db.get(User, user_uuid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_verified = True
    await db.commit()
    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request a password reset link (never reveals whether the email exists)."""
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    reset_url: Optional[str] = None
    if user and user.is_active:
        token = create_password_reset_token(str(user.id))
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        await send_email(
            db,
            to_email=user.email,
            subject="Restablecer tu contraseña — Recetario IA",
            body=(
                "Hola,\n\n"
                "Para restablecer tu contraseña abrí este enlace:\n"
                f"{reset_url}\n\n"
                "Si no lo pediste, ignorá este mensaje.\n\n— Recetario IA"
            ),
        )

    response: dict = {"message": "If the email exists, a reset link has been sent"}
    # Email delivery is external; in dev expose the link to exercise the flow.
    if settings.ENVIRONMENT != "production":
        response["reset_url"] = reset_url
    return response


@router.post("/reset-password")
async def reset_password(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    """Reset the password using a valid reset token."""
    payload = decode_token(request.token)
    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    try:
        user_uuid = UUID(str(payload.get("sub")))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    user = await db.get(User, user_uuid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password_hash = get_password_hash(request.new_password)
    user.must_change_password = False
    await db.commit()
    return {"message": "Password has been reset"}


OAUTH_PROVIDERS = {
    "google": {
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
        "scope": "openid email profile",
    },
    "github": {
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "emails_url": "https://api.github.com/user/emails",
        "scope": "read:user user:email",
    },
}


def _oauth_client(provider: str) -> tuple[str, str]:
    """Return (client_id, client_secret) or raise 404/503."""
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown provider")
    client_id = getattr(settings, f"{provider.upper()}_CLIENT_ID", "")
    client_secret = getattr(settings, f"{provider.upper()}_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{provider} OAuth is not configured",
        )
    return client_id, client_secret


@router.get("/oauth/{provider}", summary="Start OAuth login")
async def oauth_login(provider: str):
    client_id, _ = _oauth_client(provider)
    config = OAUTH_PROVIDERS[provider]
    params = {
        "client_id": client_id,
        "redirect_uri": f"{settings.OAUTH_REDIRECT_BASE}/api/v1/auth/oauth/{provider}/callback",
        "response_type": "code",
        "scope": config["scope"],
        "state": create_oauth_state(provider),
    }
    return RedirectResponse(f"{config['authorize_url']}?{urlencode(params)}")


@router.get("/oauth/{provider}/callback", summary="OAuth callback")
async def oauth_callback(
    provider: str,
    code: str | None = None,
    state: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    client_id, client_secret = _oauth_client(provider)
    config = OAUTH_PROVIDERS[provider]

    if not code or not state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing code or state")

    state_payload = decode_token(state)
    if (
        not state_payload
        or state_payload.get("type") != "oauth_state"
        or state_payload.get("provider") != provider
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state")

    redirect_uri = f"{settings.OAUTH_REDIRECT_BASE}/api/v1/auth/oauth/{provider}/callback"
    async with httpx.AsyncClient(timeout=15) as client:
        token_response = await client.post(
            config["token_url"],
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Accept": "application/json"},
        )
        token_data = token_response.json()
        provider_token = token_data.get("access_token")
        if not provider_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth token exchange failed"
            )

        headers = {"Authorization": f"Bearer {provider_token}", "Accept": "application/json"}
        user_response = await client.get(config["userinfo_url"], headers=headers)
        info = user_response.json()

        email = info.get("email")
        if not email and config.get("emails_url"):
            emails_response = await client.get(config["emails_url"], headers=headers)
            for entry in emails_response.json():
                if entry.get("primary") and entry.get("verified"):
                    email = entry.get("email")
                    break

    provider_id = info.get("sub") or info.get("id")
    if not provider_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not read the account email",
        )

    account = (
        await db.execute(
            select(OAuthAccount).where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_id == str(provider_id),
            )
        )
    ).scalar_one_or_none()

    if account is not None:
        user = await db.get(User, account.user_id)
    else:
        user = (
            await db.execute(select(User).where(User.email == email))
        ).scalar_one_or_none()
        if user is None:
            user = User(
                email=email,
                password_hash=get_password_hash(str(uuid4())),
                display_name=info.get("name") or email.split("@")[0],
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            await db.flush()
        db.add(OAuthAccount(user_id=user.id, provider=provider, provider_id=str(provider_id)))
        await db.commit()

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active")

    access_token, refresh_token = await _issue_tokens(db, user)
    redirect = RedirectResponse(
        f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}"
    )
    _set_refresh_cookie(redirect, refresh_token)
    return redirect


@router.post("/bootstrap-admin", status_code=status.HTTP_201_CREATED)
async def bootstrap_admin(db: AsyncSession = Depends(get_db)):
    """Bootstrap initial admin user (idempotent)."""
    await create_admin_user(db)
    return {"message": "Admin user created or already exists"}