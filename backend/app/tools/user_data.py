from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session
from app.db.models import WatchlistItem, Movie

async def get_user_watchlist(user_id:int) -> list:
    """Get the users watchlist with movie details."""
    async with async_session() as db:
        result = await db.execute(
            select(WatchlistItem, Movie)
            .join(Movie, WatchlistItem.movie_id == Movie.id)
            .where(WatchlistItem.user_id == user_id)
            .order_by(WatchlistItem.added_at.desc())
            .limit(20)
        )

        rows = result.all()
        return [
            {
                "movie_id": movie.id,
                "tmdb_id": movie.tmdb_id,
                "title": movie.title,
                "status": item.status,
                "rating": item.rating,
                "genres": movie.genres,
            }
            for item, movie in rows
        ]

async def get_user_ratings(user_id: int) -> list:
    """Get movies the user has rated."""
    async with async_session() as db:
        result = await db.execute(
            select(WatchlistItem, Movie)
            .join(Movie, WatchlistItem.movie_id == Movie.id)
            .where(
                WatchlistItem.user_id == user_id,
                WatchlistItem.rating.isnot(None),
            )
            .order_by(WatchlistItem.rating.desc())
        )
        rows = result.all()
        return [
            {
                "title": movie.title,
                "rating": item.rating,
                "genres": movie.genres,
            }
            for item, movie in rows
        ]