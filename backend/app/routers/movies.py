from fastapi import APIRouter, HTTPException
from app.services.tmdb import search_movies, get_movie_details, get_similar_movies, get_trending_movies

router = APIRouter(
    prefix = "/movies",
    tags = ["Movies"]
)

@router.get("/search")
async def search(query: str):
    "search movies by title"
    results = await search_movies(query)
    return {
        "results" : results
    }

@router.get("/trending")
async def trending():
    """Get trending movies this week."""
    results = await get_trending_movies()
    return {
        "results": results
    }

@router.get("/{tmdb_id}")
async def movie_detail(tmdb_id:int):
    """Get full details for a movie."""
    movie = await get_movie_details(tmdb_id)
    if "success" in movie and not movie["success"]:
        raise HTTPException(
            status_code= 404,
            detail="Movie Not found"
        )
    return movie

@router.get("/{tmdb_id}/similar")
async def similar_movies(tmdb_id: int):
    """Get similar movies."""
    results = await get_similar_movies(tmdb_id)
    return {
        "result": results
    }