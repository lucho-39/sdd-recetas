"""
User endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import User
from app.schemas.auth import UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user = Depends(get_current_active_user),
):
    """Get current user profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    user_data: dict,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """Update user profile."""
    if "display_name" in user_data:
        current_user.display_name = user_data["display_name"]
    if "avatar_url" in user_data:
        current_user.avatar_url = user_data["avatar_url"]

    await db.commit()
    await db.refresh(current_user)
    return current_user