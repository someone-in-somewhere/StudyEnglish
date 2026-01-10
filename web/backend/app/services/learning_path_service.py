"""
Learning Path Service - Manages predefined learning paths and user progress.
Provides structured curriculum with daily lessons and mixed activities.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import LEARNING_PATHS, TOPICS
from app.models.db_models import LearningPath, PathEnrollment

logger = logging.getLogger(__name__)


class LearningPathService:
    """Service for learning path management."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
        self._ensure_paths_exist()

    def _ensure_paths_exist(self):
        """Ensure all predefined paths exist in database."""
        for path_data in LEARNING_PATHS:
            existing = (
                self.db.query(LearningPath)
                .filter(LearningPath.id == path_data["id"])
                .first()
            )

            if not existing:
                # Generate curriculum
                curriculum = self._generate_curriculum(path_data)

                path = LearningPath(
                    id=path_data["id"],
                    name=path_data["name"],
                    description=path_data["description"],
                    level=path_data["level"],
                    estimated_days=path_data["estimated_days"],
                    curriculum=curriculum,
                    icon=path_data.get("icon"),
                    color=path_data.get("color")
                )
                self.db.add(path)

        self.db.commit()

    def _generate_curriculum(self, path_data: Dict) -> Dict[str, Any]:
        """Generate curriculum structure for a learning path."""
        days = path_data["estimated_days"]
        topics = path_data.get("topics", [])

        curriculum = {"days": []}

        for day in range(1, days + 1):
            # Cycle through topics
            topic_idx = (day - 1) % len(topics) if topics else 0
            topic_id = topics[topic_idx] if topics else 1

            # Get topic info
            topic_info = None
            for t in TOPICS:
                if t["id"] == topic_id:
                    topic_info = t
                    break

            topic_name = topic_info["name"] if topic_info else "General"

            # Generate activities for the day
            activities = self._generate_day_activities(day, topic_name, path_data["level"])

            curriculum["days"].append({
                "day": day,
                "title": f"Day {day}: {topic_name}",
                "topic": topic_name,
                "topic_id": topic_id,
                "activities": activities
            })

        return curriculum

    def _generate_day_activities(
        self,
        day: int,
        topic: str,
        level: str
    ) -> List[Dict[str, Any]]:
        """Generate activities for a specific day."""
        activities = []

        # Vocabulary activity every day
        activities.append({
            "type": "vocabulary",
            "title": "Learn New Words",
            "description": f"Learn 5 new vocabulary words about {topic}",
            "params": {
                "topic": topic,
                "count": 5,
                "level": level.split("-")[0]  # Use lower bound of level range
            },
            "order": 1
        })

        # Alternate between different activity types
        day_mod = day % 5

        if day_mod == 1:
            activities.append({
                "type": "quiz",
                "title": "Vocabulary Quiz",
                "description": "Test your vocabulary knowledge",
                "params": {
                    "quiz_type": "multiple_choice",
                    "num_questions": 10
                },
                "order": 2
            })

        elif day_mod == 2:
            activities.append({
                "type": "reading",
                "title": "Reading Practice",
                "description": f"Read a passage about {topic}",
                "params": {
                    "topic": topic,
                    "length": 200
                },
                "order": 2
            })

        elif day_mod == 3:
            activities.append({
                "type": "exercise",
                "title": "Grammar Exercise",
                "description": "Practice with fill-in-the-blank exercises",
                "params": {
                    "exercise_type": "fill_blank",
                    "num_exercises": 5
                },
                "order": 2
            })

        elif day_mod == 4:
            activities.append({
                "type": "writing",
                "title": "Writing Practice",
                "description": f"Write about {topic}",
                "params": {
                    "topic": topic
                },
                "order": 2
            })

        else:
            activities.append({
                "type": "flashcard",
                "title": "Review Flashcards",
                "description": "Review your vocabulary with flashcards",
                "params": {
                    "mode": "due",
                    "limit": 20
                },
                "order": 2
            })

        # Add review activity every 5 days
        if day % 5 == 0:
            activities.append({
                "type": "srs_review",
                "title": "Spaced Repetition Review",
                "description": "Review words due for spaced repetition",
                "params": {},
                "order": 3
            })

        return activities

    def get_all_paths(self) -> List[Dict[str, Any]]:
        """Get all learning paths with enrollment status."""
        paths = self.db.query(LearningPath).all()

        result = []
        for path in paths:
            enrollment = (
                self.db.query(PathEnrollment)
                .filter(PathEnrollment.path_id == path.id)
                .first()
            )

            path_dict = path.to_dict()
            path_dict["is_enrolled"] = enrollment is not None
            path_dict["progress"] = None

            if enrollment:
                total_days = path.estimated_days
                current_day = enrollment.current_day
                path_dict["progress"] = (current_day / total_days) * 100 if total_days > 0 else 0
                path_dict["current_day"] = current_day
                path_dict["completed"] = enrollment.completed

            result.append(path_dict)

        return result

    def get_path(self, path_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific learning path with details."""
        path = self.db.query(LearningPath).filter(LearningPath.id == path_id).first()

        if not path:
            return None

        enrollment = (
            self.db.query(PathEnrollment)
            .filter(PathEnrollment.path_id == path_id)
            .first()
        )

        path_dict = path.to_dict()
        path_dict["is_enrolled"] = enrollment is not None

        if enrollment:
            path_dict["enrollment"] = enrollment.to_dict()
            path_dict["current_day"] = enrollment.current_day
            path_dict["progress"] = (enrollment.current_day / path.estimated_days) * 100

        return path_dict

    def enroll(self, path_id: int) -> Dict[str, Any]:
        """
        Enroll in a learning path.

        Args:
            path_id: ID of the learning path

        Returns:
            Enrollment data
        """
        path = self.db.query(LearningPath).filter(LearningPath.id == path_id).first()

        if not path:
            return {"success": False, "message": "Learning path not found"}

        # Check existing enrollment
        existing = (
            self.db.query(PathEnrollment)
            .filter(PathEnrollment.path_id == path_id)
            .first()
        )

        if existing:
            return {
                "success": True,
                "message": "Already enrolled",
                "enrollment_id": existing.id,
                "path_id": path_id,
                "current_day": existing.current_day
            }

        # Create enrollment
        enrollment = PathEnrollment(
            path_id=path_id,
            current_day=1,
            progress_data={"completed_activities": []}
        )

        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)

        return {
            "success": True,
            "enrollment_id": enrollment.id,
            "path_id": path_id,
            "started_at": enrollment.started_at.isoformat()
        }

    def get_current_lesson(self, path_id: int) -> Dict[str, Any]:
        """
        Get the current day's lesson for an enrolled path.

        Args:
            path_id: ID of the learning path

        Returns:
            Current lesson with activities
        """
        path = self.db.query(LearningPath).filter(LearningPath.id == path_id).first()

        if not path:
            return {"success": False, "message": "Path not found"}

        enrollment = (
            self.db.query(PathEnrollment)
            .filter(PathEnrollment.path_id == path_id)
            .first()
        )

        if not enrollment:
            return {"success": False, "message": "Not enrolled in this path"}

        curriculum = path.curriculum or {}
        days = curriculum.get("days", [])

        current_day = enrollment.current_day

        if current_day > len(days):
            return {
                "success": True,
                "completed": True,
                "message": "You have completed this learning path!"
            }

        day_data = days[current_day - 1]  # 0-indexed

        # Check which activities are completed
        progress_data = enrollment.progress_data or {}
        completed_activities = progress_data.get("completed_activities", [])

        for activity in day_data["activities"]:
            activity_key = f"day_{current_day}_activity_{activity['order']}"
            activity["completed"] = activity_key in completed_activities

        return {
            "success": True,
            "path_id": path_id,
            "path_name": path.name,
            "current_day": current_day,
            "total_days": path.estimated_days,
            "lesson": day_data
        }

    def complete_activity(
        self,
        path_id: int,
        day: int,
        activity_order: int
    ) -> Dict[str, Any]:
        """
        Mark an activity as completed.

        Args:
            path_id: ID of the learning path
            day: Day number
            activity_order: Order of the activity

        Returns:
            Updated progress
        """
        enrollment = (
            self.db.query(PathEnrollment)
            .filter(PathEnrollment.path_id == path_id)
            .first()
        )

        if not enrollment:
            return {"success": False, "message": "Not enrolled"}

        progress_data = enrollment.progress_data or {"completed_activities": []}
        activity_key = f"day_{day}_activity_{activity_order}"

        if activity_key not in progress_data["completed_activities"]:
            progress_data["completed_activities"].append(activity_key)
            enrollment.progress_data = progress_data

        self.db.commit()

        return {
            "success": True,
            "activity_key": activity_key,
            "message": "Activity completed"
        }

    def advance_day(self, path_id: int) -> Dict[str, Any]:
        """
        Advance to the next day in the learning path.

        Args:
            path_id: ID of the learning path

        Returns:
            Updated enrollment status
        """
        path = self.db.query(LearningPath).filter(LearningPath.id == path_id).first()
        enrollment = (
            self.db.query(PathEnrollment)
            .filter(PathEnrollment.path_id == path_id)
            .first()
        )

        if not enrollment:
            return {"success": False, "message": "Not enrolled"}

        if enrollment.current_day >= path.estimated_days:
            enrollment.completed = True
            enrollment.completed_at = datetime.utcnow()
            self.db.commit()

            return {
                "success": True,
                "completed": True,
                "message": "Congratulations! You have completed this learning path!"
            }

        enrollment.current_day += 1
        self.db.commit()

        return {
            "success": True,
            "current_day": enrollment.current_day,
            "total_days": path.estimated_days
        }

    def unenroll(self, path_id: int) -> bool:
        """Unenroll from a learning path."""
        try:
            deleted = (
                self.db.query(PathEnrollment)
                .filter(PathEnrollment.path_id == path_id)
                .delete()
            )
            self.db.commit()
            return deleted > 0
        except Exception as e:
            logger.error(f"Failed to unenroll: {e}")
            self.db.rollback()
            return False

    def get_progress_summary(self, path_id: int) -> Dict[str, Any]:
        """Get detailed progress summary for a learning path."""
        path = self.db.query(LearningPath).filter(LearningPath.id == path_id).first()
        enrollment = (
            self.db.query(PathEnrollment)
            .filter(PathEnrollment.path_id == path_id)
            .first()
        )

        if not path or not enrollment:
            return {"success": False, "message": "Path or enrollment not found"}

        progress_data = enrollment.progress_data or {}
        completed_activities = progress_data.get("completed_activities", [])

        # Count activities per day
        curriculum = path.curriculum or {}
        days = curriculum.get("days", [])

        total_activities = sum(len(d.get("activities", [])) for d in days)
        completed_count = len(completed_activities)

        return {
            "success": True,
            "path_id": path_id,
            "path_name": path.name,
            "current_day": enrollment.current_day,
            "total_days": path.estimated_days,
            "completed": enrollment.completed,
            "started_at": enrollment.started_at.isoformat() if enrollment.started_at else None,
            "completed_at": enrollment.completed_at.isoformat() if enrollment.completed_at else None,
            "total_activities": total_activities,
            "completed_activities": completed_count,
            "activity_progress": (completed_count / total_activities * 100) if total_activities > 0 else 0,
            "day_progress": (enrollment.current_day / path.estimated_days * 100) if path.estimated_days > 0 else 0
        }


def get_learning_path_service(db: Session) -> LearningPathService:
    """Factory function to create LearningPathService."""
    return LearningPathService(db)
