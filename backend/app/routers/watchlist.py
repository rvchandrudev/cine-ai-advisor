from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db 
from app.db.models import WatchlistItem, Movie
from app.models.schemas import WatchlistItemCreate, WatchlistItemResponse
from app.services.tmdb import get_movie_details

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


# Hardcoded user ID for now (auth will replace this later)
CURRENT_USER_ID = 1

@router.get("/", response_model=WatchlistItemResponse)
async def add_to_watchlist(
    request: WatchlistItemCreate,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Movie).where(Movie.id == request.movie_id)
    )

    movie = result.scalar_one_or_none()

    if not movie:
        raise HTTPException(status_code=404,  detail="Movie not found")

    result = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.user_id == CURRENT_USER_ID,
            WatchlistItem.movie_id == request.movie_id
        )
    )

    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code = 400,
            detail="Movie already in watchlist"
        )
    item = WatchlistItem(
        user_id = CURRENT_USER_ID,
        movie_id= request.movie_id,
        status = request.status
    )

    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.get("/", response_model=List[WatchlistItemResponse])
async def get_watchlist(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WatchlistItem).
        where(WatchlistItem.user_id == CURRENT_USER_ID)
        .order_by(WatchlistItem.added_at.desc())
    )
    items = result.scalar().all()
    return items

@router.delete("/{item_id}")
async def remove_from_watchlist(item_id: int, db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(WatchlistItem).where(WatchlistItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    await db.delete(item)
    await db.commit()
    return {
        "message": "Removed from watchlist"
    }