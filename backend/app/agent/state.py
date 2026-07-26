from typing import TypedDict
class AdvisorState(TypedDict):
    """State that flows through the AI movie advisor agent."""
    user_message: str
    user_id: int
    preferences: str
    search_results: list
    recommendations: list
    response: str