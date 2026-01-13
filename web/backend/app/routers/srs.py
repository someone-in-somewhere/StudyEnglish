"""SRS (Spaced Repetition System) API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_sync_session
from app.services.srs_service import SRSService
from app.models.schemas import (
    SRSReviewRequest,
    SRSReviewResponse,
    DueReviewsResponse,
    BaseResponse
)

router = APIRouter(prefix="/api/srs", tags=["srs"])


@router.get("/due-reviews", response_model=DueReviewsResponse)
def get_due_reviews(
    limit: int = 50,
    topic: Optional[str] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_sync_session)
):
    """Get vocabulary words due for review."""
    service = SRSService(db)

    reviews = service.get_due_reviews(
        limit=limit,
        topic=topic,
        level=level
    )

    return DueReviewsResponse(
        success=True,
        reviews=reviews,
        count=len(reviews)
    )


@router.post("/review", response_model=SRSReviewResponse)
def submit_review(
    request: SRSReviewRequest,
    db: Session = Depends(get_sync_session)
):
    """Submit a vocabulary review with performance rating."""
    service = SRSService(db)

    result = service.review(
        vocabulary_id=request.vocabulary_id,
        performance=request.performance
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return SRSReviewResponse(
        success=True,
        vocabulary_id=result["vocabulary_id"],
        next_review=result["next_review"],
        interval=result["interval"],
        ease_factor=result["ease_factor"],
        mastery_level=result.get("mastery_level", 1)
    )


@router.post("/bulk-review")
def submit_bulk_review(
    reviews: list,
    db: Session = Depends(get_sync_session)
):
    """Submit multiple reviews at once."""
    service = SRSService(db)

    result = service.bulk_review(reviews)

    return result


@router.get("/stats")
def get_srs_stats(db: Session = Depends(get_sync_session)):
    """Get SRS statistics."""
    service = SRSService(db)

    stats = service.get_srs_stats()

    return {"success": True, "stats": stats}


@router.get("/forecast")
def get_review_forecast(
    days: int = 30,
    db: Session = Depends(get_sync_session)
):
    """Get forecast of upcoming reviews."""
    service = SRSService(db)

    forecast = service.get_review_forecast(days=days)

    return {"success": True, "forecast": forecast}


@router.post("/reset/{vocabulary_id}", response_model=BaseResponse)
def reset_word(
    vocabulary_id: int,
    db: Session = Depends(get_sync_session)
):
    """Reset a word's SRS data to initial state."""
    service = SRSService(db)

    if service.reset_word(vocabulary_id):
        return BaseResponse(success=True, message="Word reset successfully")
    else:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
