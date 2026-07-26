import httpx
from app.config import settings

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_TIMEOUT = httpx.Timeout(10.0, connect=5.0)

async def search_movies_tool(query: str) -> list:
    """Search movies by title on TMDB."""
    async with httpx.AsyncClient(timeout=TMDB_TIMEOUT) as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/search/movie",
            params={
                "api_key": settings.tmdb_api_key,
                "query": query,
                "language": "en-US",
            }
        )
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])[:5]
        return [
            {
                "id": m["id"],
                "title": m["title"],
                "overview": m.get("overview", ""),
                "rating": m.get("vote_average", 0),
                "release_date": m.get("release_date", ""),
            }
            for m in results
        ]

async def get_trending_tool() -> list:
    """Get trending movies this week."""
    async with httpx.AsyncClient(timeout=TMDB_TIMEOUT) as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/trending/movie/week",
            params={
                "api_key": settings.tmdb_api_key,
                "language": "en-US",
            },
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])[:5]
        return [
            {
                "id": m["id"],
                "title": m["title"],
                "overview": m.get("overview", ""),
                "rating": m.get("vote_average", 0),
            }
            for m in results
        ]


async def get_similar_tool(tmdb_id: int) -> list:
    """Get movies similar to a given movie."""
    async with httpx.AsyncClient(timeout=TMDB_TIMEOUT) as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}/similar",
            params={
                "api_key": settings.tmdb_api_key,
                "language": "en-US",
            },
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])[:5]
        return [
            {
                "id": m["id"],
                "title": m["title"],
                "overview": m.get("overview", ""),
                "rating": m.get("vote_average", 0),
            }
            for m in results
        ]
