"""Quiz API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_sync_session
from app.services.quiz_service import QuizService
from app.models.schemas import (
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
    BaseResponse
)

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


@router.post("/generate", response_model=QuizGenerateResponse)
def generate_quiz(
    request: QuizGenerateRequest,
    db: Session = Depends(get_sync_session)
):
    """Generate a quiz from learned vocabulary."""
    service = QuizService(db)

    result = service.generate_quiz(
        quiz_type=request.quiz_type,
        num_questions=request.num_questions,
        topic=request.topic,
        topic_id=request.topic_id,
        level=request.level
    )

    if not result.get("success", True):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return QuizGenerateResponse(
        success=True,
        quiz_id=result["quiz_id"],
        quiz_type=result["quiz_type"],
        questions=result["questions"]
    )


@router.post("/submit", response_model=QuizSubmitResponse)
def submit_quiz(
    request: QuizSubmitRequest,
    db: Session = Depends(get_sync_session)
):
    """Submit quiz answers and get results."""
    service = QuizService(db)

    answers = [
        {"question_id": a.question_id, "user_answer": a.user_answer}
        for a in request.answers
    ]

    result = service.submit_quiz(
        quiz_id=request.quiz_id,
        answers=answers,
        time_taken=request.time_taken
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return QuizSubmitResponse(
        success=True,
        quiz_id=result["quiz_id"],
        score=result["score"],
        correct_answers=result["correct_answers"],
        total_questions=result["total_questions"],
        feedback=result["feedback"]
    )


@router.get("/history")
def get_quiz_history(
    topic: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_sync_session)
):
    """Get quiz history."""
    service = QuizService(db)

    history = service.get_quiz_history(limit=limit, topic=topic)

    return {"success": True, "history": history, "count": len(history)}


@router.get("/stats")
def get_quiz_stats(db: Session = Depends(get_sync_session)):
    """Get quiz statistics."""
    service = QuizService(db)

    stats = service.get_quiz_stats()

    return {"success": True, "stats": stats}


@router.delete("/{quiz_id}", response_model=BaseResponse)
def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_sync_session)
):
    """Delete a quiz."""
    service = QuizService(db)

    if service.delete_quiz(quiz_id):
        return BaseResponse(success=True, message="Quiz deleted")
    else:
        raise HTTPException(status_code=404, detail="Quiz not found")
