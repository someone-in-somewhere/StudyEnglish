"""
Error Analysis Service - Tracks and analyzes user errors across all activities.
Provides personalized recommendations based on error patterns.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.db_models import (
    QuizError, ErrorPattern, WritingSubmission, ChatHistory
)

logger = logging.getLogger(__name__)


class ErrorAnalysisService:
    """Service for error tracking and analysis."""

    # Error categories and their descriptions
    ERROR_CATEGORIES = {
        "grammar": {
            "article": "Article usage (a, an, the)",
            "preposition": "Preposition usage",
            "tense": "Verb tense errors",
            "subject_verb": "Subject-verb agreement",
            "word_form": "Word form (noun/verb/adjective)",
            "sentence_structure": "Sentence structure",
        },
        "vocabulary": {
            "word_choice": "Incorrect word choice",
            "spelling": "Spelling errors",
            "collocation": "Word collocation errors",
            "meaning": "Meaning confusion",
        },
        "other": {
            "punctuation": "Punctuation errors",
            "capitalization": "Capitalization errors",
        }
    }

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def record_error(
        self,
        error_type: str,
        error_category: str,
        example: Optional[str] = None
    ) -> bool:
        """
        Record an error occurrence.

        Args:
            error_type: Type of error (grammar, vocabulary, other)
            error_category: Specific category
            example: Example of the error

        Returns:
            Success status
        """
        try:
            # Find existing pattern
            pattern = (
                self.db.query(ErrorPattern)
                .filter(
                    ErrorPattern.error_type == error_type,
                    ErrorPattern.error_category == error_category
                )
                .first()
            )

            if pattern:
                pattern.count += 1
                pattern.last_occurrence = datetime.utcnow()

                # Update examples (keep last 5)
                examples = pattern.examples or []
                if example and example not in examples:
                    examples.append(example)
                    pattern.examples = examples[-5:]
            else:
                pattern = ErrorPattern(
                    error_type=error_type,
                    error_category=error_category,
                    count=1,
                    examples=[example] if example else []
                )
                self.db.add(pattern)

            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Failed to record error: {e}")
            self.db.rollback()
            return False

    def get_analysis(self) -> Dict[str, Any]:
        """
        Get comprehensive error analysis.

        Returns:
            Analysis with top errors, categories, and trends
        """
        # Get all error patterns
        patterns = (
            self.db.query(ErrorPattern)
            .order_by(desc(ErrorPattern.count))
            .all()
        )

        # Top errors
        top_errors = []
        for p in patterns[:10]:
            top_errors.append({
                "error_type": p.error_type,
                "error_category": p.error_category,
                "count": p.count,
                "examples": p.examples or [],
                "description": self._get_category_description(p.error_type, p.error_category)
            })

        # By category
        by_category = defaultdict(int)
        for p in patterns:
            by_category[p.error_type] += p.count

        # Get quiz errors for recent trends
        recent_errors = self._get_recent_quiz_errors(days=30)

        # Calculate improvement rate
        improvement_data = self._calculate_improvement()

        return {
            "top_errors": top_errors,
            "by_category": dict(by_category),
            "total_errors": sum(p.count for p in patterns),
            "trends": recent_errors,
            "improvement": improvement_data
        }

    def _get_category_description(
        self,
        error_type: str,
        error_category: str
    ) -> str:
        """Get description for an error category."""
        type_cats = self.ERROR_CATEGORIES.get(error_type, {})
        return type_cats.get(error_category, f"{error_type}: {error_category}")

    def _get_recent_quiz_errors(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent quiz error trends."""
        since = datetime.utcnow() - timedelta(days=days)

        errors = (
            self.db.query(
                QuizError.error_category,
                func.count(QuizError.id).label("count"),
                func.date(QuizError.created_at).label("date")
            )
            .filter(QuizError.created_at >= since)
            .group_by(QuizError.error_category, func.date(QuizError.created_at))
            .order_by(func.date(QuizError.created_at))
            .all()
        )

        trends = []
        for e in errors:
            trends.append({
                "category": e.error_category,
                "count": e.count,
                "date": e.date.isoformat() if e.date else None
            })

        return trends

    def _calculate_improvement(self) -> Dict[str, Any]:
        """Calculate improvement rate over time."""
        now = datetime.utcnow()
        last_week = now - timedelta(days=7)
        prev_week = now - timedelta(days=14)

        # Count errors from last week
        recent_count = (
            self.db.query(func.count(QuizError.id))
            .filter(QuizError.created_at >= last_week)
            .scalar() or 0
        )

        # Count errors from previous week
        prev_count = (
            self.db.query(func.count(QuizError.id))
            .filter(
                QuizError.created_at >= prev_week,
                QuizError.created_at < last_week
            )
            .scalar() or 0
        )

        if prev_count > 0:
            improvement_rate = ((prev_count - recent_count) / prev_count) * 100
        else:
            improvement_rate = 0

        return {
            "recent_errors": recent_count,
            "previous_errors": prev_count,
            "improvement_rate": round(improvement_rate, 1),
            "is_improving": recent_count < prev_count
        }

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get personalized learning recommendations based on errors.

        Returns:
            List of recommendations with practice suggestions
        """
        analysis = self.get_analysis()
        recommendations = []

        for error in analysis["top_errors"][:5]:
            rec = self._generate_recommendation(
                error["error_type"],
                error["error_category"],
                error["count"]
            )
            if rec:
                recommendations.append(rec)

        # Add general recommendations if few errors
        if len(recommendations) < 3:
            recommendations.append({
                "type": "general",
                "title": "Keep practicing!",
                "description": "Continue with your vocabulary learning and quiz practice.",
                "action": "vocabulary",
                "priority": "low"
            })

        return recommendations

    def _generate_recommendation(
        self,
        error_type: str,
        error_category: str,
        count: int
    ) -> Optional[Dict[str, Any]]:
        """Generate a specific recommendation for an error pattern."""
        priority = "high" if count > 10 else ("medium" if count > 5 else "low")

        if error_type == "grammar":
            if error_category == "article":
                return {
                    "type": "grammar",
                    "title": "Article Usage Practice",
                    "description": "You frequently make errors with articles (a, an, the). Practice using articles with nouns.",
                    "action": "exercise",
                    "exercise_type": "fill_blank",
                    "focus": "articles",
                    "priority": priority
                }
            elif error_category == "tense":
                return {
                    "type": "grammar",
                    "title": "Verb Tense Review",
                    "description": "Review verb tenses and when to use each one. Practice with sentence rewriting exercises.",
                    "action": "exercise",
                    "exercise_type": "rewrite",
                    "focus": "tenses",
                    "priority": priority
                }
            elif error_category == "preposition":
                return {
                    "type": "grammar",
                    "title": "Preposition Practice",
                    "description": "Prepositions can be tricky. Focus on common preposition patterns with verbs and nouns.",
                    "action": "exercise",
                    "exercise_type": "fill_blank",
                    "focus": "prepositions",
                    "priority": priority
                }
            elif error_category == "subject_verb":
                return {
                    "type": "grammar",
                    "title": "Subject-Verb Agreement",
                    "description": "Practice matching subjects with their correct verb forms.",
                    "action": "exercise",
                    "exercise_type": "error_correction",
                    "focus": "subject_verb",
                    "priority": priority
                }

        elif error_type == "vocabulary":
            if error_category == "word_choice":
                return {
                    "type": "vocabulary",
                    "title": "Vocabulary Review",
                    "description": "Review words you've confused. Use flashcards for spaced repetition.",
                    "action": "flashcard",
                    "priority": priority
                }
            elif error_category == "spelling":
                return {
                    "type": "vocabulary",
                    "title": "Spelling Practice",
                    "description": "Practice spelling commonly misspelled words.",
                    "action": "quiz",
                    "quiz_type": "fill_blank",
                    "priority": priority
                }

        # Default recommendation
        return {
            "type": error_type,
            "title": f"Practice {error_category.replace('_', ' ').title()}",
            "description": f"You have made {count} errors in this category. More practice will help.",
            "action": "exercise",
            "priority": priority
        }

    def get_error_details(
        self,
        error_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get detailed error examples."""
        query = self.db.query(QuizError)

        if error_type:
            query = query.filter(QuizError.error_type == error_type)

        errors = query.order_by(desc(QuizError.created_at)).limit(limit).all()

        return [
            {
                "question": e.question,
                "user_answer": e.user_answer,
                "correct_answer": e.correct_answer,
                "error_type": e.error_type,
                "error_category": e.error_category,
                "created_at": e.created_at.isoformat() if e.created_at else None
            }
            for e in errors
        ]

    def process_writing_errors(self, submission_id: int) -> int:
        """
        Process and record errors from a writing submission.

        Args:
            submission_id: ID of the writing submission

        Returns:
            Number of errors recorded
        """
        submission = (
            self.db.query(WritingSubmission)
            .filter(WritingSubmission.id == submission_id)
            .first()
        )

        if not submission or not submission.errors:
            return 0

        count = 0
        for error in submission.errors:
            error_type = error.get("error_type", "grammar")
            # Categorize error
            category = self._categorize_error(error)

            self.record_error(
                error_type=error_type,
                error_category=category,
                example=error.get("original", "")
            )
            count += 1

        return count

    def _categorize_error(self, error: Dict) -> str:
        """Categorize an error based on its content."""
        original = error.get("original", "").lower()
        corrected = error.get("corrected", "").lower()
        explanation = error.get("explanation", "").lower()

        # Check for specific patterns
        if any(w in explanation for w in ["article", "a ", "an ", "the "]):
            return "article"
        if any(w in explanation for w in ["preposition", "in", "on", "at", "to", "for"]):
            return "preposition"
        if any(w in explanation for w in ["tense", "past", "present", "future"]):
            return "tense"
        if "subject" in explanation and "verb" in explanation:
            return "subject_verb"
        if any(w in explanation for w in ["spelling", "spell"]):
            return "spelling"

        return "word_form"

    def clear_old_data(self, days: int = 90) -> int:
        """Clear error data older than specified days."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        deleted = (
            self.db.query(QuizError)
            .filter(QuizError.created_at < cutoff)
            .delete()
        )

        self.db.commit()
        return deleted


def get_error_analysis_service(db: Session) -> ErrorAnalysisService:
    """Factory function to create ErrorAnalysisService."""
    return ErrorAnalysisService(db)
