"""Progress tracking API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_sync_session
from app.services.progress_service import ProgressService
from app.models.schemas import (
    ProgressStatsResponse,
    ProgressTimelineResponse,
    UserSettingsUpdate,
    UserSettingsResponse,
    BaseResponse
)

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/stats", response_model=ProgressStatsResponse)
def get_progress_stats(db: Session = Depends(get_sync_session)):
    """Get comprehensive progress statistics."""
    service = ProgressService(db)

    stats = service.get_stats()

    return ProgressStatsResponse(success=True, stats=stats)


@router.get("/timeline", response_model=ProgressTimelineResponse)
def get_progress_timeline(
    days: int = 30,
    db: Session = Depends(get_sync_session)
):
    """Get daily progress timeline for charts."""
    service = ProgressService(db)

    timeline = service.get_timeline(days=days)

    return ProgressTimelineResponse(
        success=True,
        timeline=timeline,
        total_days=len(timeline)
    )


@router.get("/achievements")
def get_achievements(db: Session = Depends(get_sync_session)):
    """Get user achievements and badges."""
    service = ProgressService(db)

    achievements = service.get_achievements()

    return {"success": True, "achievements": achievements}


@router.get("/daily-summary")
def get_daily_summary(db: Session = Depends(get_sync_session)):
    """Get today's learning summary."""
    service = ProgressService(db)

    summary = service.get_daily_summary()

    return {"success": True, "summary": summary}


@router.get("/weekly-summary")
def get_weekly_summary(db: Session = Depends(get_sync_session)):
    """Get this week's learning summary."""
    service = ProgressService(db)

    summary = service.get_weekly_summary()

    return {"success": True, "summary": summary}


@router.get("/settings", response_model=UserSettingsResponse)
def get_settings(db: Session = Depends(get_sync_session)):
    """Get user settings."""
    service = ProgressService(db)

    settings = service.get_settings()

    return UserSettingsResponse(success=True, settings=settings)


@router.put("/settings", response_model=UserSettingsResponse)
def update_settings(
    request: UserSettingsUpdate,
    db: Session = Depends(get_sync_session)
):
    """Update user settings."""
    service = ProgressService(db)

    updates = request.model_dump(exclude_unset=True)
    settings = service.update_settings(updates)

    return UserSettingsResponse(success=True, settings=settings)


@router.post("/record-activity", response_model=BaseResponse)
def record_activity(
    activity_type: str,
    details: dict = None,
    db: Session = Depends(get_sync_session)
):
    """Record a learning activity."""
    service = ProgressService(db)

    if service.record_activity(activity_type, details):
        return BaseResponse(success=True, message="Activity recorded")
    else:
        return BaseResponse(success=False, message="Failed to record activity")
