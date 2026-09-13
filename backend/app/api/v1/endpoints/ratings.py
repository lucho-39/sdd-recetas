"""
Rating endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import Rating, Recipe
from app.schemas.auth import UserResponse

router = APIRouter()


@router.post("/{recipe_id}", response_model=dict, status_code=201)
async def rate_recipe(
    recipe_id: str,
    score: int,
    review_text: str = None,
    db = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Rate a recipe (1-5 stars)."""
    if not 1 <= score <= 5:
        raise HTTPException(status_code=400, detail="Score must be between 1 and 5")

    # Check recipe exists
    from app.models import Recipe
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Check if user already rated
    existing = await db.execute(
        select(Rating).where(
            Rating.recipe_id == recipe_id,
            Rating.user_id == current_user.id
        )
    )
    existing_rating = existing.scalar_one_or_none()

    if existing_rating:
        # Update existing rating
        existing_rating.score = score
        existing_rating.review_text = review_text
    else:
        rating = Rating(
            recipe_id=recipe_id,
            user_id=current_user.id,
            score=score,
            review_text=review_text,
        )
        db.add(rating)

    await db.commit()

    # Recalculate average
    result = await db.execute(
        select(func.avg(Rating.score), func.count(Rating.id))
        .where(Rating.recipe_id == recipe_id)
    )
    avg, count = result.one()
    recipe.avg_rating = float(round(avg, 2)) if avg else 0
    recipe.rating_count = count
    await db.commit()

    return {
        "message": "Rating saved",
        "avg_rating": recipe.avg_rating,
        "rating_count": recipe.rating_count,
    }


@router.get("/{recipe_id}", summary="Get recipe ratings")
async def get_ratings(
    recipe_id: str,
    page: int = 1,
    limit: int = 10,
    db = Depends(get_db),
):
    """Get paginated ratings for a recipe."""
    from app.models import Rating, User

    offset = (page - 1) * 10
    result = await db.execute(
        select(Rating, User.display_name, User.avatar_url)
        .join(User, Rating.user_id == User.id)
        .where(Rating.recipe_id == recipe_id)
        .order_by(Rating.created_at.desc())
        .offset((page - 1) * 10)
        .limit(10)
    )
    ratings = []
    for rating, display_name, avatar_url in result.all():
        ratings.append({
            "id": rating.id,
            "score": rating.score,
            "review_text": rating.review_text,
            "created_at": rating.created_at,
            "user": {
                "display_name": display_name,
                "avatar_url": avatar_url,
            }
        })

    total = await db.scalar(
        select(func.count(Rating.id)).where(Rating.recipe_id == recipe_id)
    )

    distribution = {str(score): 0 for score in range(1, 6)}
    dist_result = await db.execute(
        select(Rating.score, func.count(Rating.id))
        .where(Rating.recipe_id == recipe_id)
        .group_by(Rating.score)
    )
    for score, count in dist_result.all():
        distribution[str(score)] = count

    return {
        "ratings": ratings,
        "total": total,
        "page": page,
        "limit": 10,
        "distribution": distribution,
    }


@router.get("/{recipe_id}/mine", summary="Get my rating")
async def get_my_rating(
    recipe_id: str,
    db = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Return the current user's rating for a recipe, if any."""
    rating = (
        await db.execute(
            select(Rating).where(
                Rating.recipe_id == recipe_id,
                Rating.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()

    if not rating:
        return {"score": None, "review_text": None}
    return {"score": rating.score, "review_text": rating.review_text}


@router.delete("/{recipe_id}", summary="Delete my rating")
async def delete_rating(
    recipe_id: str,
    db = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Remove the current user's rating and recalculate the aggregates."""
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    result = await db.execute(
        sql_delete(Rating).where(
            Rating.recipe_id == recipe_id,
            Rating.user_id == current_user.id,
        )
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="You have not rated this recipe")

    aggregate = await db.execute(
        select(func.avg(Rating.score), func.count(Rating.id)).where(
            Rating.recipe_id == recipe_id
        )
    )
    avg, count = aggregate.one()
    recipe.avg_rating = float(round(avg, 2)) if avg else 0
    recipe.rating_count = count
    await db.commit()

    return {
        "message": "Rating deleted",
        "avg_rating": recipe.avg_rating,
        "rating_count": recipe.rating_count,
    }