"""
Progress Service - Tracks user learning progress and statistics.
Provides comprehensive analytics and progress visualization data.
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.models.db_models import (
    Vocabulary, UserVocabulary, Quiz, StudySession, UserSettings,
    WritingSubmission, ReadingAttempt, ChatHistory, Exercise, ExerciseAttempt
)

logger = logging.getLogger(__name__)


class ProgressService:
    """Service for tracking and analyzing learning progress."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive progress statistics.

        Returns:
            Dictionary with all progress metrics
        """
        # Total words learned
        total_words = self.db.query(func.count(UserVocabulary.id)).scalar() or 0

        # Words by level
        words_by_level = {}
        level_counts = (
            self.db.query(
                Vocabulary.level,
                func.count(UserVocabulary.id)
            )
            .join(UserVocabulary, UserVocabulary.vocabulary_id == Vocabulary.id)
            .group_by(Vocabulary.level)
            .all()
        )
        for level, count in level_counts:
            words_by_level[level] = count

        # Words by topic
        words_by_topic = {}
        topic_counts = (
            self.db.query(
                Vocabulary.topic,
                func.count(UserVocabulary.id)
            )
            .join(UserVocabulary, UserVocabulary.vocabulary_id == Vocabulary.id)
            .group_by(Vocabulary.topic)
            .all()
        )
        for topic, count in topic_counts:
            words_by_topic[topic] = count

        # Quiz statistics
        quiz_count = (
            self.db.query(func.count(Quiz.id))
            .filter(Quiz.completed_at.isnot(None))
            .scalar() or 0
        )
        quiz_avg = (
            self.db.query(func.avg(Quiz.score))
            .filter(Quiz.completed_at.isnot(None))
            .scalar() or 0
        )

        # Streak information
        settings = self._get_or_create_settings()
        current_streak = settings.current_streak
        longest_streak = settings.longest_streak
        total_study_time = settings.total_study_time

        # Words due for review
        now = datetime.utcnow()
        words_due = (
            self.db.query(func.count(UserVocabulary.id))
            .filter(UserVocabulary.next_review <= now)
            .scalar() or 0
        )

        # Mastery distribution
        mastery_dist = {}
        mastery_counts = (
            self.db.query(
                UserVocabulary.mastery_level,
                func.count(UserVocabulary.id)
            )
            .group_by(UserVocabulary.mastery_level)
            .all()
        )
        for level, count in mastery_counts:
            mastery_dist[str(level)] = count

        return {
            "total_words": total_words,
            "words_by_level": words_by_level,
            "words_by_topic": words_by_topic,
            "quiz_count": quiz_count,
            "quiz_avg_score": round(quiz_avg, 1),
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_study_time": total_study_time,
            "words_due_review": words_due,
            "mastery_distribution": mastery_dist
        }

    def get_timeline(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily progress timeline for charts.

        Args:
            days: Number of days to include

        Returns:
            List of daily progress data
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)

        # Get study sessions
        sessions = (
            self.db.query(StudySession)
            .filter(StudySession.date >= start_date)
            .order_by(StudySession.date)
            .all()
        )

        session_map = {s.date: s for s in sessions}

        # Build timeline
        timeline = []
        current_date = start_date

        while current_date <= end_date:
            session = session_map.get(current_date)

            if session:
                timeline.append({
                    "date": current_date.isoformat(),
                    "words_learned": session.words_learned,
                    "words_reviewed": session.words_reviewed,
                    "quizzes_completed": session.quizzes_completed,
                    "study_time": session.study_time
                })
            else:
                timeline.append({
                    "date": current_date.isoformat(),
                    "words_learned": 0,
                    "words_reviewed": 0,
                    "quizzes_completed": 0,
                    "study_time": 0
                })

            current_date += timedelta(days=1)

        return timeline

    def record_activity(
        self,
        activity_type: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record a learning activity.

        Args:
            activity_type: Type of activity (word_learned, quiz_completed, etc.)
            details: Additional activity details

        Returns:
            Success status
        """
        try:
            today = date.today()

            # Get or create today's session
            session = (
                self.db.query(StudySession)
                .filter(StudySession.date == today)
                .first()
            )

            if not session:
                session = StudySession(date=today, activities=[])
                self.db.add(session)

            # Update session based on activity type
            if activity_type == "word_learned":
                session.words_learned += 1
            elif activity_type == "word_reviewed":
                session.words_reviewed += 1
            elif activity_type == "quiz_completed":
                session.quizzes_completed += 1
                if details and "score" in details:
                    # Update average score
                    if session.quiz_avg_score:
                        total_quizzes = session.quizzes_completed
                        session.quiz_avg_score = (
                            (session.quiz_avg_score * (total_quizzes - 1) + details["score"])
                            / total_quizzes
                        )
                    else:
                        session.quiz_avg_score = details["score"]
            elif activity_type == "exercise_completed":
                session.exercises_completed += 1
            elif activity_type == "reading_completed":
                session.reading_passages += 1
            elif activity_type == "writing_submitted":
                session.writing_submissions += 1
            elif activity_type == "chat_message":
                session.chat_messages += 1
            elif activity_type == "study_time":
                if details and "minutes" in details:
                    session.study_time += details["minutes"]

            # Add to activity log
            activities = session.activities or []
            activities.append({
                "type": activity_type,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details
            })
            session.activities = activities

            # Update streak
            self._update_streak()

            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Failed to record activity: {e}")
            self.db.rollback()
            return False

    def _update_streak(self):
        """Update study streak based on activity."""
        settings = self._get_or_create_settings()
        today = date.today()

        if settings.last_study_date:
            days_diff = (today - settings.last_study_date).days

            if days_diff == 0:
                # Same day, no change
                pass
            elif days_diff == 1:
                # Consecutive day
                settings.current_streak += 1
                if settings.current_streak > settings.longest_streak:
                    settings.longest_streak = settings.current_streak
            else:
                # Streak broken
                settings.current_streak = 1
        else:
            # First study day
            settings.current_streak = 1

        settings.last_study_date = today
        self.db.commit()

    def _get_or_create_settings(self) -> UserSettings:
        """Get or create user settings."""
        settings = self.db.query(UserSettings).first()

        if not settings:
            settings = UserSettings()
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)

        return settings

    def get_settings(self) -> Dict[str, Any]:
        """Get user settings."""
        settings = self._get_or_create_settings()
        return settings.to_dict()

    def update_settings(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user settings.

        Args:
            updates: Dictionary of settings to update

        Returns:
            Updated settings
        """
        settings = self._get_or_create_settings()

        allowed_fields = [
            "target_level", "daily_goal", "theme", "notifications_enabled"
        ]

        for field in allowed_fields:
            if field in updates:
                setattr(settings, field, updates[field])

        settings.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(settings)

        return settings.to_dict()

    def get_achievements(self) -> List[Dict[str, Any]]:
        """
        Get user achievements and badges.

        Returns:
            List of achievements with status
        """
        stats = self.get_stats()

        achievements = [
            {
                "id": "first_word",
                "name": "First Steps",
                "description": "Learn your first word",
                "icon": "fa-star",
                "earned": stats["total_words"] >= 1,
                "progress": min(1, stats["total_words"]) / 1
            },
            {
                "id": "ten_words",
                "name": "Word Collector",
                "description": "Learn 10 words",
                "icon": "fa-book",
                "earned": stats["total_words"] >= 10,
                "progress": min(10, stats["total_words"]) / 10
            },
            {
                "id": "fifty_words",
                "name": "Vocabulary Builder",
                "description": "Learn 50 words",
                "icon": "fa-graduation-cap",
                "earned": stats["total_words"] >= 50,
                "progress": min(50, stats["total_words"]) / 50
            },
            {
                "id": "hundred_words",
                "name": "Word Master",
                "description": "Learn 100 words",
                "icon": "fa-trophy",
                "earned": stats["total_words"] >= 100,
                "progress": min(100, stats["total_words"]) / 100
            },
            {
                "id": "first_quiz",
                "name": "Quiz Taker",
                "description": "Complete your first quiz",
                "icon": "fa-clipboard-check",
                "earned": stats["quiz_count"] >= 1,
                "progress": min(1, stats["quiz_count"]) / 1
            },
            {
                "id": "perfect_quiz",
                "name": "Perfectionist",
                "description": "Score 100% on a quiz",
                "icon": "fa-check-double",
                "earned": self._has_perfect_quiz(),
                "progress": 1 if self._has_perfect_quiz() else 0
            },
            {
                "id": "streak_3",
                "name": "Consistent Learner",
                "description": "Maintain a 3-day streak",
                "icon": "fa-fire",
                "earned": stats["longest_streak"] >= 3,
                "progress": min(3, stats["current_streak"]) / 3
            },
            {
                "id": "streak_7",
                "name": "Week Warrior",
                "description": "Maintain a 7-day streak",
                "icon": "fa-fire-alt",
                "earned": stats["longest_streak"] >= 7,
                "progress": min(7, stats["current_streak"]) / 7
            },
            {
                "id": "streak_30",
                "name": "Monthly Master",
                "description": "Maintain a 30-day streak",
                "icon": "fa-medal",
                "earned": stats["longest_streak"] >= 30,
                "progress": min(30, stats["current_streak"]) / 30
            },
        ]

        return achievements

    def _has_perfect_quiz(self) -> bool:
        """Check if user has achieved a perfect quiz score."""
        perfect = (
            self.db.query(Quiz)
            .filter(
                and_(
                    Quiz.completed_at.isnot(None),
                    Quiz.score == 100
                )
            )
            .first()
        )
        return perfect is not None

    def get_daily_summary(self) -> Dict[str, Any]:
        """Get today's learning summary."""
        today = date.today()

        session = (
            self.db.query(StudySession)
            .filter(StudySession.date == today)
            .first()
        )

        settings = self._get_or_create_settings()

        if session:
            return {
                "date": today.isoformat(),
                "words_learned": session.words_learned,
                "words_reviewed": session.words_reviewed,
                "quizzes_completed": session.quizzes_completed,
                "study_time": session.study_time,
                "daily_goal": settings.daily_goal,
                "goal_progress": min(1.0, session.words_learned / settings.daily_goal) if settings.daily_goal > 0 else 0,
                "streak": settings.current_streak
            }
        else:
            return {
                "date": today.isoformat(),
                "words_learned": 0,
                "words_reviewed": 0,
                "quizzes_completed": 0,
                "study_time": 0,
                "daily_goal": settings.daily_goal,
                "goal_progress": 0,
                "streak": settings.current_streak
            }

    def get_weekly_summary(self) -> Dict[str, Any]:
        """Get this week's learning summary."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        sessions = (
            self.db.query(StudySession)
            .filter(StudySession.date >= week_start)
            .all()
        )

        total_words = sum(s.words_learned for s in sessions)
        total_reviewed = sum(s.words_reviewed for s in sessions)
        total_quizzes = sum(s.quizzes_completed for s in sessions)
        total_time = sum(s.study_time for s in sessions)
        active_days = len(sessions)

        return {
            "week_start": week_start.isoformat(),
            "week_end": today.isoformat(),
            "total_words_learned": total_words,
            "total_words_reviewed": total_reviewed,
            "total_quizzes": total_quizzes,
            "total_study_time": total_time,
            "active_days": active_days,
            "avg_daily_words": round(total_words / max(1, active_days), 1)
        }


def get_progress_service(db: Session) -> ProgressService:
    """Factory function to create ProgressService."""
    return ProgressService(db)
