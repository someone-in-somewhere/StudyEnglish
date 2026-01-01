"""Learning paths API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_sync_session
from app.services.learning_path_service import LearningPathService
from app.models.schemas import (
    LearningPathsResponse,
    PathEnrollRequest,
    PathEnrollResponse,
    CurrentLessonResponse,
    BaseResponse
)

router = APIRouter(prefix="/api/learning-paths", tags=["learning-paths"])


@router.get("", response_model=LearningPathsResponse)
def get_all_paths(db: Session = Depends(get_sync_session)):
    """Get all available learning paths."""
    service = LearningPathService(db)

    paths = service.get_all_paths()

    return LearningPathsResponse(success=True, paths=paths)


@router.get("/{path_id}")
def get_path(
    path_id: int,
    db: Session = Depends(get_sync_session)
):
    """Get a specific learning path with details."""
    service = LearningPathService(db)

    path = service.get_path(path_id)

    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    return {"success": True, "path": path}


@router.post("/enroll", response_model=PathEnrollResponse)
def enroll_in_path(
    request: PathEnrollRequest,
    db: Session = Depends(get_sync_session)
):
    """Enroll in a learning path."""
    service = LearningPathService(db)

    result = service.enroll(request.path_id)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return PathEnrollResponse(
        success=True,
        enrollment_id=result["enrollment_id"],
        path_id=result["path_id"],
        started_at=result.get("started_at")
    )


@router.get("/{path_id}/current-lesson", response_model=CurrentLessonResponse)
def get_current_lesson(
    path_id: int,
    db: Session = Depends(get_sync_session)
):
    """Get current day's lesson for an enrolled path."""
    service = LearningPathService(db)

    result = service.get_current_lesson(path_id)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    if result.get("completed"):
        return CurrentLessonResponse(
            success=True,
            path_id=path_id,
            path_name="Completed",
            current_day=0,
            lesson=None
        )

    return CurrentLessonResponse(
        success=True,
        path_id=path_id,
        path_name=result["path_name"],
        current_day=result["current_day"],
        lesson=result["lesson"]
    )


@router.post("/{path_id}/complete-activity")
def complete_activity(
    path_id: int,
    day: int,
    activity_order: int,
    db: Session = Depends(get_sync_session)
):
    """Mark an activity as completed."""
    service = LearningPathService(db)

    result = service.complete_activity(path_id, day, activity_order)

    return result


@router.post("/{path_id}/advance-day")
def advance_day(
    path_id: int,
    db: Session = Depends(get_sync_session)
):
    """Advance to the next day in the learning path."""
    service = LearningPathService(db)

    result = service.advance_day(path_id)

    return result


@router.get("/{path_id}/progress")
def get_progress_summary(
    path_id: int,
    db: Session = Depends(get_sync_session)
):
    """Get detailed progress summary for a learning path."""
    service = LearningPathService(db)

    result = service.get_progress_summary(path_id)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return result


@router.delete("/{path_id}/unenroll", response_model=BaseResponse)
def unenroll_from_path(
    path_id: int,
    db: Session = Depends(get_sync_session)
):
    """Unenroll from a learning path."""
    service = LearningPathService(db)

    if service.unenroll(path_id):
        return BaseResponse(success=True, message="Unenrolled successfully")
    else:
        raise HTTPException(status_code=404, detail="Enrollment not found")
