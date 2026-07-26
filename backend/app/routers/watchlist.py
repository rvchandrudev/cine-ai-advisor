import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Movie, WatchlistItem
from app.db.session import get_db
from app.models.schemas import WatchlistItemCreate, WatchlistItemResponse
from app.services.tmdb import TMDBError, get_movie_details

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])
logger = logging.getLogger(__name__)


CURRENT_USER_ID = 1


async def _get_or_create_movie(tmdb_id: int, db: AsyncSession) -> Movie:
    result = await db.execute(select(Movie).where(Movie.tmdb_id == tmdb_id))
    movie = result.scalar_one_or_none()
    if movie:
        return movie

    try:
        details = await get_movie_details(tmdb_id)
    except TMDBError as exc:
        logger.exception("Failed to fetch TMDB movie %s", tmdb_id)
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    movie = Movie(
        tmdb_id=details["id"],
        title=details.get("title") or details.get("name") or "Untitled",
        overview=details.get("overview"),
        poster_path=details.get("poster_path"),
        release_date=details.get("release_date"),
        runtime=details.get("runtime"),
        genres=details.get("genres"),
        vote_average=details.get("vote_average"),
    )
    db.add(movie)
    await db.commit()
    await db.refresh(movie)
    return movie


@router.post("/", response_model=WatchlistItemResponse)
async def add_to_watchlist(
    request: WatchlistItemCreate,
    db: AsyncSession = Depends(get_db),
):
    movie = await _get_or_create_movie(request.tmdb_id, db)

    result = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.user_id == CURRENT_USER_ID,
            WatchlistItem.movie_id == movie.id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Movie already in watchlist")

    item = WatchlistItem(
        user_id=CURRENT_USER_ID,
        movie_id=movie.id,
        status=request.status,
        rating=request.rating,
    )
    db.add(item)
    await db.commit()

    result = await db.execute(
        select(WatchlistItem)
        .options(selectinload(WatchlistItem.movie))
        .where(WatchlistItem.id == item.id)
    )
    created = result.scalar_one()
    return created


@router.get("/", response_model=list[WatchlistItemResponse])
async def get_watchlist(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WatchlistItem)
        .options(selectinload(WatchlistItem.movie))
        .where(WatchlistItem.user_id == CURRENT_USER_ID)
        .order_by(WatchlistItem.added_at.desc())
    )
    return result.scalars().all()


@router.delete("/{item_id}")
async def remove_from_watchlist(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WatchlistItem).where(WatchlistItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    await db.delete(item)
    await db.commit()
    return {"message": "Removed from watchlist"}
