"""Flashcard API endpoints."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_sync_session
from app.services.flashcard_service import FlashcardService
from app.models.schemas import (
    FlashcardCreate,
    FlashcardResponse,
    FlashcardStudyRequest,
    FlashcardStudyResponse,
    FlashcardReviewRequest,
    BaseResponse
)

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


@router.post("/create", response_model=dict)
def create_flashcard(
    request: FlashcardCreate,
    db: Session = Depends(get_sync_session)
):
    """Create a new flashcard."""
    service = FlashcardService(db)

    result = service.create_flashcard(
        vocabulary_id=request.vocabulary_id,
        front=request.front,
        back=request.back
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return result


@router.post("/create-batch")
def create_flashcard_batch(
    vocabulary_ids: List[int],
    db: Session = Depends(get_sync_session)
):
    """Create flashcards from multiple vocabulary words."""
    service = FlashcardService(db)

    result = service.create_from_vocabulary_batch(vocabulary_ids)

    return result


@router.post("/study", response_model=FlashcardStudyResponse)
def get_study_session(
    request: FlashcardStudyRequest,
    db: Session = Depends(get_sync_session)
):
    """Get flashcards for a study session."""
    service = FlashcardService(db)

    flashcards = service.get_study_session(
        mode=request.mode,
        topic=request.topic,
        level=request.level,
        limit=request.limit
    )

    return FlashcardStudyResponse(
        success=True,
        flashcards=flashcards,
        count=len(flashcards)
    )


@router.post("/review")
def review_flashcard(
    request: FlashcardReviewRequest,
    db: Session = Depends(get_sync_session)
):
    """Submit flashcard review with performance rating."""
    service = FlashcardService(db)

    result = service.review_flashcard(
        flashcard_id=request.flashcard_id,
        performance=request.performance
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return result


@router.post("/toggle-favorite/{flashcard_id}")
def toggle_favorite(
    flashcard_id: int,
    db: Session = Depends(get_sync_session)
):
    """Toggle favorite status for a flashcard."""
    service = FlashcardService(db)

    result = service.toggle_favorite(flashcard_id)

    return result


@router.get("/favorites")
def get_favorites(
    limit: int = 50,
    db: Session = Depends(get_sync_session)
):
    """Get favorite flashcards."""
    service = FlashcardService(db)

    flashcards = service.get_favorites(limit=limit)

    return {"success": True, "flashcards": flashcards, "count": len(flashcards)}


@router.put("/{flashcard_id}")
def update_flashcard(
    flashcard_id: int,
    front: Optional[str] = None,
    back: Optional[str] = None,
    db: Session = Depends(get_sync_session)
):
    """Update flashcard content."""
    service = FlashcardService(db)

    result = service.update_flashcard(
        flashcard_id=flashcard_id,
        front=front,
        back=back
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return result


@router.delete("/{flashcard_id}", response_model=BaseResponse)
def delete_flashcard(
    flashcard_id: int,
    db: Session = Depends(get_sync_session)
):
    """Delete a flashcard."""
    service = FlashcardService(db)

    if service.delete_flashcard(flashcard_id):
        return BaseResponse(success=True, message="Flashcard deleted")
    else:
        raise HTTPException(status_code=404, detail="Flashcard not found")


@router.get("/stats")
def get_flashcard_stats(db: Session = Depends(get_sync_session)):
    """Get flashcard statistics."""
    service = FlashcardService(db)

    stats = service.get_stats()

    return {"success": True, "stats": stats}


@router.post("/sync", response_model=BaseResponse)
def sync_with_vocabulary(db: Session = Depends(get_sync_session)):
    """Sync flashcards with learned vocabulary."""
    service = FlashcardService(db)

    result = service.sync_with_vocabulary()

    return BaseResponse(success=True, message=result.get("message", "Sync complete"))
