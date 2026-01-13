"""Exercise API endpoints."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_sync_session
from app.services.exercise_service import ExerciseService
from app.models.schemas import (
    ExerciseGenerateRequest,
    ExerciseGenerateResponse,
    ExerciseSubmitRequest,
    ExerciseSubmitResponse
)

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


@router.post("/generate", response_model=ExerciseGenerateResponse)
def generate_exercises(
    request: ExerciseGenerateRequest,
    db: Session = Depends(get_sync_session)
):
    """Generate exercises using AI."""
    service = ExerciseService(db)

    result = service.generate_exercises(
        exercise_type=request.exercise_type,
        num_exercises=request.num_exercises,
        topic=request.topic,
        level=request.level,
        words=request.words
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return ExerciseGenerateResponse(
        success=True,
        exercise_id=result["exercise_id"],
        exercise_type=result["exercise_type"],
        exercises=result["exercises"]
    )


@router.post("/submit", response_model=ExerciseSubmitResponse)
def submit_exercises(
    request: ExerciseSubmitRequest,
    db: Session = Depends(get_sync_session)
):
    """Submit exercise answers."""
    service = ExerciseService(db)

    result = service.submit_exercises(
        exercise_id=request.exercise_id,
        answers=request.answers
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return ExerciseSubmitResponse(
        success=True,
        exercise_id=result["exercise_id"],
        score=result["score"],
        feedback=result["feedback"]
    )


@router.get("/types")
def get_exercise_types():
    """Get available exercise types."""
    return {
        "success": True,
        "types": [
            {"id": "fill_blank", "name": "Fill in the Blank", "description": "Complete sentences with missing words"},
            {"id": "rewrite", "name": "Sentence Rewriting", "description": "Rewrite sentences as instructed"},
            {"id": "translation", "name": "Translation", "description": "Translate Vietnamese to English"},
            {"id": "word_order", "name": "Word Order", "description": "Arrange words to form correct sentences"},
            {"id": "error_correction", "name": "Error Correction", "description": "Find and correct grammar errors"}
        ]
    }


@router.get("/history")
def get_exercise_history(
    limit: int = 20,
    db: Session = Depends(get_sync_session)
):
    """Get exercise history."""
    service = ExerciseService(db)

    history = service.get_exercise_history(limit=limit)

    return {"success": True, "history": history}
