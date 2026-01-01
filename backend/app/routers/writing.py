"""Writing practice API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_sync_session
from app.services.writing_service import WritingService
from app.models.schemas import (
    WritingSubmitRequest,
    WritingSubmitResponse,
    WritingPromptsResponse
)

router = APIRouter(prefix="/api/writing", tags=["writing"])


@router.get("/prompts", response_model=WritingPromptsResponse)
def get_prompts(
    level: str = "B1",
    topic: Optional[str] = None,
    db: Session = Depends(get_sync_session)
):
    """Get writing prompts for a level."""
    service = WritingService(db)

    prompts = service.get_prompts(level=level, topic=topic)

    return WritingPromptsResponse(success=True, prompts=prompts)


@router.post("/submit", response_model=WritingSubmitResponse)
def submit_writing(
    request: WritingSubmitRequest,
    db: Session = Depends(get_sync_session)
):
    """Submit writing for analysis and scoring."""
    service = WritingService(db)

    result = service.submit_writing(
        prompt=request.prompt,
        user_text=request.user_text,
        topic=request.topic,
        level=request.level
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return WritingSubmitResponse(
        success=True,
        submission_id=result["submission_id"],
        corrected_text=result["corrected_text"],
        scores=result["scores"],
        errors=result["errors"],
        suggestions=result["suggestions"],
        word_count=result["word_count"]
    )


@router.get("/submission/{submission_id}")
def get_submission(
    submission_id: int,
    db: Session = Depends(get_sync_session)
):
    """Get a specific writing submission."""
    service = WritingService(db)

    submission = service.get_submission(submission_id)

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return {"success": True, "submission": submission}


@router.get("/history")
def get_writing_history(
    limit: int = 20,
    db: Session = Depends(get_sync_session)
):
    """Get writing submission history."""
    service = WritingService(db)

    history = service.get_history(limit=limit)

    return {"success": True, "history": history, "count": len(history)}


@router.get("/stats")
def get_writing_stats(db: Session = Depends(get_sync_session)):
    """Get writing statistics."""
    service = WritingService(db)

    stats = service.get_stats()

    return {"success": True, "stats": stats}
