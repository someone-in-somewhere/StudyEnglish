"""Reading comprehension API endpoints."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_sync_session
from app.services.reading_service import ReadingService
from app.models.schemas import (
    ReadingGenerateRequest,
    ReadingGenerateResponse,
    ReadingSubmitRequest,
    ReadingSubmitResponse
)

router = APIRouter(prefix="/api/reading", tags=["reading"])


@router.post("/generate", response_model=ReadingGenerateResponse)
def generate_passage(
    request: ReadingGenerateRequest,
    db: Session = Depends(get_sync_session)
):
    """Generate a reading passage with comprehension questions."""
    service = ReadingService(db)

    result = service.generate_passage(
        topic=request.topic,
        level=request.level,
        length=request.length,
        topic_id=request.topic_id
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return ReadingGenerateResponse(
        success=True,
        passage_id=result["passage_id"],
        title=result["title"],
        content=result["content"],
        word_count=result["word_count"],
        questions=result["questions"]
    )


@router.post("/submit", response_model=ReadingSubmitResponse)
def submit_reading(
    request: ReadingSubmitRequest,
    db: Session = Depends(get_sync_session)
):
    """Submit reading comprehension answers."""
    service = ReadingService(db)

    result = service.submit_reading(
        passage_id=request.passage_id,
        answers=request.answers,
        time_taken=request.time_taken
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return ReadingSubmitResponse(
        success=True,
        passage_id=result["passage_id"],
        score=result["score"],
        wpm=result["wpm"],
        feedback=result["feedback"]
    )


@router.get("/passage/{passage_id}")
def get_passage(
    passage_id: int,
    db: Session = Depends(get_sync_session)
):
    """Get a specific reading passage."""
    service = ReadingService(db)

    passage = service.get_passage(passage_id)

    if not passage:
        raise HTTPException(status_code=404, detail="Passage not found")

    return {"success": True, "passage": passage}


@router.get("/passages")
def get_passages(
    topic: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_sync_session)
):
    """Get list of reading passages."""
    service = ReadingService(db)

    passages = service.get_passages(topic=topic, level=level, limit=limit)

    return {"success": True, "passages": passages, "count": len(passages)}


@router.get("/stats")
def get_reading_stats(db: Session = Depends(get_sync_session)):
    """Get reading statistics."""
    service = ReadingService(db)

    stats = service.get_reading_stats()

    return {"success": True, "stats": stats}
