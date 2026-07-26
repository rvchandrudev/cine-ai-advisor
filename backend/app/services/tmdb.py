import httpx
from app.config import settings

TMDB_BASE_URL = "https://api.themoviedb.org/3"

async def search_movies(query:str) -> list:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/search/movie",
            params={
                "api_key": settings.tmdb_api_key,
                "query": query,
                "language": "en-US",
                "page": 1
            }
        )

        data = response.json()
        return data.get("results", [])

async def get_movie_details(tmdb_id:int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}",
            params={
                "api_key": settings.tmdb_api_key,
                "language": "en-US"
            }
        )
        return response.json()

async def get_trending_movies() -> list:
    """Get trending movies this week."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/trending/movie/week",
            params={
                "api_key": settings.tmdb_api_key,
                "language": "en-US",
            },
        )
        data = response.json()
        return data.get("results", [])


async def get_similar_movies(tmdb_id: int) -> list:
    """Get movies similar to a given movie."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}/similar",
            params={
                "api_key": settings.tmdb_api_key,
                "language": "en-US",
            },
        )
        data = response.json()
        return data.get("results", [])