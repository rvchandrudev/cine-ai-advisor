import logging
import asyncio
import json

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from app.agent.state import AdvisorState
from app.config import settings
from app.tools.movie_search import search_movies_tool, get_trending_tool
from app.tools.user_data import get_user_watchlist, get_user_ratings

llm = ChatGroq(
    model=settings.llm_model,
    api_key=settings.groq_api_key,
    temperature=0.3,
)
logger = logging.getLogger(__name__)


async def understand_preferences(state: AdvisorState) -> AdvisorState:
    user_message = state["user_message"]
    user_id = state["user_id"]

    watchlist_result, ratings_result = await asyncio.gather(
        get_user_watchlist(user_id),
        get_user_ratings(user_id),
        return_exceptions=True,
    )

    watchlist = [] if isinstance(watchlist_result, Exception) else watchlist_result
    ratings = [] if isinstance(ratings_result, Exception) else ratings_result
    if isinstance(watchlist_result, Exception) or isinstance(ratings_result, Exception):
        logger.warning("Falling back to empty user context for user_id=%s", user_id)

    prompt = f"""Analyze movie preferences.

User message: {user_message}
Watchlist: {json.dumps(watchlist)}
Ratings: {json.dumps(ratings)}

Summarize: genres liked, current mood, what fits best. 2-3 sentences."""

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    state["preferences"] = response.content
    return state


async def search_movies_node(state: AdvisorState) -> AdvisorState:
    user_message = state["user_message"]
    preferences = state["preferences"]

    prompt = f"""Extract 2-3 movie search queries.
Message: {user_message}
Preferences: {preferences}
Return ONLY JSON list. Example: ["sci-fi thriller", "mind bending"]"""

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    try:
        queries = json.loads(response.content.strip())
    except json.JSONDecodeError:
        queries = [user_message]

    search_tasks = [search_movies_tool(q) for q in queries[:2]]
    searched_results = (
        await asyncio.gather(*search_tasks, return_exceptions=True) if search_tasks else []
    )

    all_results = []
    for results in searched_results:
        if isinstance(results, Exception):
            logger.warning("Skipping failed movie search result")
            continue
        all_results.extend(results)

    try:
        trending = await get_trending_tool()
        all_results.extend(trending[:2])
    except Exception:
        logger.exception("Unable to load trending movies")

    seen = set()
    unique = []
    for m in all_results:
        if m["id"] not in seen:
            seen.add(m["id"])
            unique.append(m)

    state["search_results"] = unique[:10]
    return state


async def generate_recommendations(state: AdvisorState) -> AdvisorState:
    preferences = state["preferences"]
    results = state["search_results"]

    if not results:
        state["response"] = "No movies found. Try a different request!"
        state["recommendations"] = []
        return state

    prompt = f"""You are a friendly movie advisor. Recommend 3 movies.

Preferences: {preferences}
Results: {json.dumps(results)}

For each: title, rating, why it fits, fun recommendation. Keep conversational."""

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    state["response"] = response.content
    state["recommendations"] = results[:3]
    return state
