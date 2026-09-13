"""
Admin: tag management (/api/admin/tags).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models import Tag
from app.schemas.admin import TagAdminCreate, TagAdminUpdate

router = APIRouter()


@router.get("", summary="List tags (admin)")
async def list_tags(
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if search:
        term = f"%{search}%"
        filters.append(or_(Tag.name.ilike(term), Tag.slug.ilike(term)))

    total = await db.scalar(select(func.count()).select_from(Tag).where(*filters))
    result = await db.execute(
        select(Tag)
        .where(*filters)
        .order_by(Tag.usage_count.desc(), Tag.name)
        .offset((page - 1) * limit)
        .limit(limit)
    )
    items = result.scalars().all()
    return {
        "items": [
            {"id": str(t.id), "slug": t.slug, "name": t.name, "usage_count": t.usage_count}
            for t in items
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.post("", status_code=201, summary="Create tag (admin)")
async def create_tag(
    data: TagAdminCreate,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    exists = await db.scalar(select(Tag.id).where(Tag.slug == data.slug))
    if exists:
        raise HTTPException(status_code=400, detail="Tag slug already exists")
    tag = Tag(**data.model_dump())
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return {"id": str(tag.id), "slug": tag.slug, "name": tag.name}


@router.patch("/{tag_id}", summary="Update tag (admin)")
async def update_tag(
    tag_id: UUID,
    data: TagAdminUpdate,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tag, field, value)
    await db.commit()
    await db.refresh(tag)
    return {"id": str(tag.id), "slug": tag.slug, "name": tag.name}


@router.delete("/{tag_id}", summary="Delete tag (admin)")
async def delete_tag(
    tag_id: UUID,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    await db.delete(tag)
    await db.commit()
    return {"deleted": True}
