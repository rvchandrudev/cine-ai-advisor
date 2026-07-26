from langgraph.graph import StateGraph, END
from app.agent.state import AdvisorState
from app.agent.nodes import understand_preferences, search_movies_node, generate_recommendations


def build_graph():
    workflow = StateGraph(AdvisorState)

    workflow.add_node("understand", understand_preferences)
    workflow.add_node("search", search_movies_node)
    workflow.add_node("recommend", generate_recommendations)

    workflow.set_entry_point("understand")
    workflow.add_edge("understand", "search")
    workflow.add_edge("search", "recommend")
    workflow.add_edge("recommend", END)

    return workflow.compile()


agent_graph = build_graph()