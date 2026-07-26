import logging

from fastapi import APIRouter, HTTPException

from app.services.tmdb import (
    TMDBError,
    get_movie_details,
    get_similar_movies,
    get_trending_movies,
    search_movies,
)

router = APIRouter(
    prefix = "/movies",
    tags = ["Movies"]
)
logger = logging.getLogger(__name__)

@router.get("/search")
async def search(query: str):
    """Search movies by title."""
    try:
        results = await search_movies(query)
    except TMDBError as exc:
        logger.exception("Movie search failed")
        raise HTTPException(status_code=502, detail="Movie search service unavailable") from exc
    return {"results": results}

@router.get("/trending")
async def trending():
    """Get trending movies this week."""
    try:
        results = await get_trending_movies()
    except TMDBError as exc:
        logger.exception("Trending movies lookup failed")
        raise HTTPException(status_code=502, detail="Trending movies service unavailable") from exc
    return {"results": results}

@router.get("/{tmdb_id}")
async def movie_detail(tmdb_id:int):
    """Get full details for a movie."""
    try:
        movie = await get_movie_details(tmdb_id)
    except TMDBError as exc:
        logger.exception("Movie detail lookup failed for %s", tmdb_id)
        raise HTTPException(status_code=502, detail="Movie service unavailable") from exc
    if movie.get("success") is False:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.get("/{tmdb_id}/similar")
async def similar_movies(tmdb_id: int):
    """Get similar movies."""
    try:
        results = await get_similar_movies(tmdb_id)
    except TMDBError as exc:
        logger.exception("Similar movie lookup failed for %s", tmdb_id)
        raise HTTPException(status_code=502, detail="Movie service unavailable") from exc
    return {"results": results}
