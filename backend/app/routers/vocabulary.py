"""Vocabulary API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_sync_session
from app.services.vocabulary_service import VocabularyService
from app.models.schemas import (
    VocabularyGenerateRequest,
    VocabularyGenerateResponse,
    MarkLearnedRequest,
    BaseResponse
)

router = APIRouter(prefix="/api/vocabulary", tags=["vocabulary"])


@router.post("/generate", response_model=VocabularyGenerateResponse)
def generate_vocabulary(
    request: VocabularyGenerateRequest,
    db: Session = Depends(get_sync_session)
):
    """Generate vocabulary words using AI for a topic and level."""
    service = VocabularyService(db)

    vocabulary = service.generate_vocabulary(
        topic=request.topic,
        level=request.level,
        num_words=request.num_words,
        topic_id=request.topic_id
    )

    return VocabularyGenerateResponse(
        success=True,
        vocabulary=vocabulary,
        count=len(vocabulary)
    )


@router.post("/mark-learned", response_model=BaseResponse)
def mark_as_learned(
    request: MarkLearnedRequest,
    db: Session = Depends(get_sync_session)
):
    """Mark a vocabulary word as learned."""
    service = VocabularyService(db)

    result = service.mark_as_learned(request.vocabulary_id)

    if result:
        return BaseResponse(success=True, message="Vocabulary marked as learned")
    else:
        raise HTTPException(status_code=404, detail="Vocabulary not found")


@router.post("/toggle-favorite/{vocabulary_id}", response_model=BaseResponse)
def toggle_favorite(
    vocabulary_id: int,
    db: Session = Depends(get_sync_session)
):
    """Toggle favorite status for a vocabulary word."""
    service = VocabularyService(db)

    is_favorite = service.toggle_favorite(vocabulary_id)

    return BaseResponse(
        success=True,
        message=f"Favorite {'added' if is_favorite else 'removed'}"
    )


@router.get("/topic/{topic}")
def get_vocabulary_by_topic(
    topic: str,
    level: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_sync_session)
):
    """Get vocabulary words for a specific topic."""
    service = VocabularyService(db)

    vocabulary = service.get_vocabulary_by_topic(
        topic=topic,
        level=level,
        limit=limit
    )

    return {"success": True, "vocabulary": vocabulary, "count": len(vocabulary)}


@router.get("/learned")
def get_learned_vocabulary(
    topic: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_sync_session)
):
    """Get user's learned vocabulary."""
    service = VocabularyService(db)

    vocabulary = service.get_learned_vocabulary(
        topic=topic,
        level=level,
        limit=limit
    )

    return {"success": True, "vocabulary": vocabulary, "count": len(vocabulary)}


@router.get("/stats")
def get_vocabulary_stats(db: Session = Depends(get_sync_session)):
    """Get vocabulary learning statistics."""
    service = VocabularyService(db)
    stats = service.get_vocabulary_stats()

    return {"success": True, "stats": stats}


@router.get("/search")
def search_vocabulary(
    q: str,
    limit: int = 20,
    db: Session = Depends(get_sync_session)
):
    """Search vocabulary by word or meaning."""
    service = VocabularyService(db)

    results = service.search_vocabulary(query=q, limit=limit)

    return {"success": True, "results": results, "count": len(results)}


@router.delete("/{vocabulary_id}", response_model=BaseResponse)
def delete_vocabulary(
    vocabulary_id: int,
    db: Session = Depends(get_sync_session)
):
    """Delete a vocabulary word."""
    service = VocabularyService(db)

    if service.delete_vocabulary(vocabulary_id):
        return BaseResponse(success=True, message="Vocabulary deleted")
    else:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
