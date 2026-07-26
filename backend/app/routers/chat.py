import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import ChatSession, ChatMessage
from app.models.schemas import ChatRequest, ChatResponse
from app.agent.graph import agent_graph
from app.agent.state import AdvisorState

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    if request.session_id:
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == request.session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ChatSession(user_id=1)
        db.add(session)
        await db.commit()
        await db.refresh(session)

    user_msg = ChatMessage(session_id=session.id, role="user", content=request.message)
    db.add(user_msg)
    await db.commit()

    initial_state: AdvisorState = {
        "user_message": request.message,
        "user_id": 1,
        "preferences": "",
        "search_results": [],
        "recommendations": [],
        "response": "",
    }

    config = {"configurable": {"thread_id": str(session.id)}}

    try:
        final_state = await agent_graph.ainvoke(initial_state, config)
    except Exception as exc:
        logger.exception("Agent execution failed for session_id=%s", session.id)
        error_detail = str(exc).strip()
        if error_detail and error_detail != exc.__class__.__name__:
            detail = f"Agent error: {exc.__class__.__name__}: {error_detail}"
        else:
            detail = f"Agent error: {exc.__class__.__name__}"
        raise HTTPException(
            status_code=500,
            detail=detail,
        ) from exc

    agent_response = final_state.get("response", "")
    recommendations = final_state.get("recommendations", [])

    if not agent_response:
        agent_response = "I couldn't generate recommendations. Try a different request!"

    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=agent_response,
    )
    db.add(assistant_msg)
    await db.commit()

    return ChatResponse(
        session_id=session.id,
        message=agent_response,
        recommendations=recommendations,
    )
