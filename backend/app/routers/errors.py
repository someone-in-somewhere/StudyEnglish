"""Error analysis API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_sync_session
from app.services.error_analysis_service import ErrorAnalysisService
from app.models.schemas import (
    ErrorAnalysisResponse,
    RecommendationsResponse,
    BaseResponse
)

router = APIRouter(prefix="/api/errors", tags=["errors"])


@router.get("/analysis", response_model=ErrorAnalysisResponse)
def get_error_analysis(db: Session = Depends(get_sync_session)):
    """Get comprehensive error analysis."""
    service = ErrorAnalysisService(db)

    analysis = service.get_analysis()

    return ErrorAnalysisResponse(
        success=True,
        top_errors=analysis["top_errors"],
        by_category=analysis["by_category"],
        trends=analysis["trends"]
    )


@router.get("/recommendations", response_model=RecommendationsResponse)
def get_recommendations(db: Session = Depends(get_sync_session)):
    """Get personalized learning recommendations based on errors."""
    service = ErrorAnalysisService(db)

    recommendations = service.get_recommendations()

    return RecommendationsResponse(success=True, recommendations=recommendations)


@router.get("/details")
def get_error_details(
    error_type: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_sync_session)
):
    """Get detailed error examples."""
    service = ErrorAnalysisService(db)

    details = service.get_error_details(error_type=error_type, limit=limit)

    return {"success": True, "errors": details, "count": len(details)}


@router.get("/categories")
def get_error_categories():
    """Get all error categories with descriptions."""
    return {
        "success": True,
        "categories": ErrorAnalysisService.ERROR_CATEGORIES
    }


@router.delete("/clear-old", response_model=BaseResponse)
def clear_old_errors(
    days: int = 90,
    db: Session = Depends(get_sync_session)
):
    """Clear error data older than specified days."""
    service = ErrorAnalysisService(db)

    deleted = service.clear_old_data(days=days)

    return BaseResponse(success=True, message=f"Cleared {deleted} old error records")
