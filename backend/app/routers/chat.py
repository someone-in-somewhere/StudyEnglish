"""Chat API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_sync_session
from app.services.chat_service import ChatService
from app.models.schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
    BaseResponse
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=ChatMessageResponse)
def send_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_sync_session)
):
    """Send a message and get AI response with grammar feedback."""
    service = ChatService(db)

    result = service.send_message(
        message=request.message,
        session_id=request.session_id
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return ChatMessageResponse(
        success=True,
        session_id=result["session_id"],
        response=result["response"],
        has_errors=result.get("has_errors", False),
        corrections=result.get("corrections", [])
    )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
def get_chat_history(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_sync_session)
):
    """Get chat history for a session."""
    service = ChatService(db)

    messages = service.get_history(session_id=session_id, limit=limit)

    return ChatHistoryResponse(
        success=True,
        session_id=session_id,
        messages=messages
    )


@router.get("/sessions")
def get_chat_sessions(
    limit: int = 20,
    db: Session = Depends(get_sync_session)
):
    """Get list of chat sessions."""
    service = ChatService(db)

    sessions = service.get_sessions(limit=limit)

    return {"success": True, "sessions": sessions}


@router.post("/start-topic")
def start_topic_conversation(
    topic: str,
    session_id: Optional[str] = None,
    db: Session = Depends(get_sync_session)
):
    """Start a conversation about a specific topic."""
    service = ChatService(db)

    result = service.start_topic_conversation(
        topic=topic,
        session_id=session_id
    )

    return result


@router.get("/errors/{session_id}")
def get_session_errors(
    session_id: str,
    db: Session = Depends(get_sync_session)
):
    """Get summary of grammar errors in a session."""
    service = ChatService(db)

    summary = service.get_error_summary(session_id)

    return {"success": True, "summary": summary}


@router.delete("/session/{session_id}", response_model=BaseResponse)
def delete_session(
    session_id: str,
    db: Session = Depends(get_sync_session)
):
    """Delete a chat session."""
    service = ChatService(db)

    if service.delete_session(session_id):
        return BaseResponse(success=True, message="Session deleted")
    else:
        raise HTTPException(status_code=404, detail="Session not found")
