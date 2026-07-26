import logging

import httpx
from app.config import settings

TMDB_BASE_URL = "https://api.themoviedb.org/3"
logger = logging.getLogger(__name__)


class TMDBError(RuntimeError):
    """Raised when TMDB requests fail."""


async def _tmdb_get(path: str, params: dict) -> dict:
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(f"{TMDB_BASE_URL}{path}", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.exception("TMDB returned an error for %s", path)
            raise TMDBError(f"TMDB responded with HTTP {exc.response.status_code}") from exc
        except httpx.RequestError as exc:
            logger.exception("TMDB request failed for %s", path)
            raise TMDBError("TMDB request failed") from exc

async def search_movies(query:str) -> list:
    data = await _tmdb_get(
        "/search/movie",
        {
            "api_key": settings.tmdb_api_key,
            "query": query,
            "language": "en-US",
            "page": 1,
        },
    )
    return data.get("results", [])

async def get_movie_details(tmdb_id:int) -> dict:
    return await _tmdb_get(
        f"/movie/{tmdb_id}",
        {
            "api_key": settings.tmdb_api_key,
            "language": "en-US",
        },
    )

async def get_trending_movies() -> list:
    """Get trending movies this week."""
    data = await _tmdb_get(
        "/trending/movie/week",
        {
            "api_key": settings.tmdb_api_key,
            "language": "en-US",
        },
    )
    return data.get("results", [])


async def get_similar_movies(tmdb_id: int) -> list:
    """Get movies similar to a given movie."""
    data = await _tmdb_get(
        f"/movie/{tmdb_id}/similar",
        {
            "api_key": settings.tmdb_api_key,
            "language": "en-US",
        },
    )
    return data.get("results", [])
