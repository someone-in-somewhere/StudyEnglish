"""
SRS Service - Implements the SM-2 (SuperMemo 2) spaced repetition algorithm.
Manages vocabulary review scheduling and mastery progression.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.config import settings
from app.models.db_models import Vocabulary, UserVocabulary
from app.services.progress_service import ProgressService

logger = logging.getLogger(__name__)


class SRSService:
    """
    Service implementing the SM-2 spaced repetition algorithm.

    Performance ratings:
    - 1 (Again): Complete failure, reset interval
    - 2 (Hard): Correct with difficulty, minor interval increase
    - 3 (Good): Correct with some hesitation, normal progression
    - 4 (Easy): Perfect recall, accelerated progression
    """

    # SM-2 Constants
    MIN_EASE_FACTOR = 1.3
    DEFAULT_EASE_FACTOR = 2.5
    INITIAL_INTERVAL = 1  # days

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def get_due_reviews(
        self,
        limit: int = 50,
        topic: Optional[str] = None,
        level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get vocabulary words due for review.

        Args:
            limit: Maximum number of words to return
            topic: Optional topic filter
            level: Optional CEFR level filter

        Returns:
            List of vocabulary with SRS data
        """
        now = datetime.utcnow()

        query = (
            self.db.query(UserVocabulary)
            .join(Vocabulary)
            .filter(UserVocabulary.next_review <= now)
        )

        if topic:
            query = query.filter(Vocabulary.topic == topic)
        if level:
            query = query.filter(Vocabulary.level == level)

        # Order by: overdue first, then by mastery level (prioritize weak words)
        due_items = (
            query
            .order_by(UserVocabulary.next_review.asc(), UserVocabulary.mastery_level.asc())
            .limit(limit)
            .all()
        )

        results = []
        for user_vocab in due_items:
            vocab_dict = user_vocab.vocabulary.to_dict()
            vocab_dict["srs_data"] = {
                "user_vocab_id": user_vocab.id,
                "ease_factor": user_vocab.ease_factor,
                "interval": user_vocab.interval,
                "review_count": user_vocab.review_count,
                "mastery_level": user_vocab.mastery_level,
                "last_reviewed": user_vocab.last_reviewed.isoformat() if user_vocab.last_reviewed else None,
                "next_review": user_vocab.next_review.isoformat() if user_vocab.next_review else None,
                "times_correct": user_vocab.times_correct,
                "times_incorrect": user_vocab.times_incorrect,
                "overdue_days": (now - user_vocab.next_review).days if user_vocab.next_review else 0
            }
            results.append(vocab_dict)

        return results

    def review(
        self,
        vocabulary_id: int,
        performance: int
    ) -> Dict[str, Any]:
        """
        Process a vocabulary review with SM-2 algorithm.

        Args:
            vocabulary_id: ID of the vocabulary word
            performance: Rating 1-4 (Again, Hard, Good, Easy)

        Returns:
            Updated SRS data
        """
        if performance < 1 or performance > 4:
            return {
                "success": False,
                "message": "Performance must be between 1 and 4"
            }

        user_vocab = (
            self.db.query(UserVocabulary)
            .filter(UserVocabulary.vocabulary_id == vocabulary_id)
            .first()
        )

        if not user_vocab:
            return {
                "success": False,
                "message": "Vocabulary not found in learning list"
            }

        # Apply SM-2 algorithm
        new_ease, new_interval = self._calculate_sm2(
            performance=performance,
            current_ease=user_vocab.ease_factor,
            current_interval=user_vocab.interval
        )

        # Update mastery level
        new_mastery = self._calculate_mastery(
            current_mastery=user_vocab.mastery_level,
            performance=performance,
            review_count=user_vocab.review_count + 1
        )

        # Update statistics
        if performance >= 3:  # Good or Easy
            user_vocab.times_correct += 1
        else:
            user_vocab.times_incorrect += 1

        # Apply updates
        now = datetime.utcnow()
        user_vocab.ease_factor = new_ease
        user_vocab.interval = new_interval
        user_vocab.last_reviewed = now
        user_vocab.next_review = now + timedelta(days=new_interval)
        user_vocab.review_count += 1
        user_vocab.mastery_level = new_mastery

        self.db.commit()

        # Record activity
        progress_service = ProgressService(self.db)
        progress_service.record_activity("word_reviewed", {
            "vocabulary_id": vocabulary_id,
            "performance": performance,
            "new_interval": new_interval
        })

        return {
            "success": True,
            "vocabulary_id": vocabulary_id,
            "ease_factor": round(new_ease, 2),
            "interval": new_interval,
            "next_review": user_vocab.next_review.isoformat(),
            "mastery_level": new_mastery,
            "review_count": user_vocab.review_count
        }

    def _calculate_sm2(
        self,
        performance: int,
        current_ease: float,
        current_interval: int
    ) -> tuple:
        """
        Calculate new ease factor and interval using SM-2 algorithm.

        Args:
            performance: Rating 1-4
            current_ease: Current ease factor
            current_interval: Current interval in days

        Returns:
            Tuple of (new_ease_factor, new_interval)
        """
        # Calculate new ease factor
        # EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
        # Where q is quality (1-5), we map 1-4 to 1-5: q = performance + 1 for performance >= 2

        if performance == 1:  # Again
            # Complete failure - reset
            new_ease = max(self.MIN_EASE_FACTOR, current_ease - 0.2)
            new_interval = 1

        elif performance == 2:  # Hard
            # Difficult recall
            new_ease = max(self.MIN_EASE_FACTOR, current_ease - 0.15)
            new_interval = max(1, int(current_interval * 1.2))

        elif performance == 3:  # Good
            # Normal recall
            new_ease = current_ease  # No change
            if current_interval == 1:
                new_interval = 3
            else:
                new_interval = int(current_interval * current_ease)

        else:  # Easy (4)
            # Perfect recall
            new_ease = min(3.0, current_ease + 0.15)
            if current_interval == 1:
                new_interval = 4
            else:
                new_interval = int(current_interval * current_ease * 1.3)

        # Cap interval at 365 days
        new_interval = min(365, new_interval)

        return new_ease, new_interval

    def _calculate_mastery(
        self,
        current_mastery: int,
        performance: int,
        review_count: int
    ) -> int:
        """
        Calculate new mastery level (1-5).

        Args:
            current_mastery: Current mastery level
            performance: Review performance
            review_count: Total number of reviews

        Returns:
            New mastery level
        """
        if performance == 1:  # Again
            # Decrease mastery
            return max(1, current_mastery - 1)

        elif performance == 2:  # Hard
            # Stay same
            return current_mastery

        elif performance == 3:  # Good
            # Potentially increase
            if review_count >= 3 and current_mastery < 5:
                return current_mastery + 1
            return current_mastery

        else:  # Easy
            # Increase faster
            if current_mastery < 5:
                return min(5, current_mastery + 1)
            return 5

    def get_srs_stats(self) -> Dict[str, Any]:
        """Get SRS statistics."""
        now = datetime.utcnow()

        # Total in SRS system
        total = self.db.query(func.count(UserVocabulary.id)).scalar() or 0

        # Due now
        due_now = (
            self.db.query(func.count(UserVocabulary.id))
            .filter(UserVocabulary.next_review <= now)
            .scalar() or 0
        )

        # Due today
        end_of_day = now.replace(hour=23, minute=59, second=59)
        due_today = (
            self.db.query(func.count(UserVocabulary.id))
            .filter(UserVocabulary.next_review <= end_of_day)
            .scalar() or 0
        )

        # Due this week
        end_of_week = now + timedelta(days=7)
        due_week = (
            self.db.query(func.count(UserVocabulary.id))
            .filter(UserVocabulary.next_review <= end_of_week)
            .scalar() or 0
        )

        # By mastery level
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

        # Average ease factor
        avg_ease = (
            self.db.query(func.avg(UserVocabulary.ease_factor)).scalar() or 2.5
        )

        # Review success rate
        total_correct = (
            self.db.query(func.sum(UserVocabulary.times_correct)).scalar() or 0
        )
        total_incorrect = (
            self.db.query(func.sum(UserVocabulary.times_incorrect)).scalar() or 0
        )
        total_reviews = total_correct + total_incorrect
        success_rate = (total_correct / total_reviews * 100) if total_reviews > 0 else 0

        return {
            "total_in_srs": total,
            "due_now": due_now,
            "due_today": due_today,
            "due_this_week": due_week,
            "mastery_distribution": mastery_dist,
            "average_ease_factor": round(avg_ease, 2),
            "success_rate": round(success_rate, 1),
            "total_reviews": total_reviews
        }

    def get_review_forecast(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get forecast of upcoming reviews.

        Args:
            days: Number of days to forecast

        Returns:
            List of daily review counts
        """
        now = datetime.utcnow()
        forecast = []

        for i in range(days):
            day_start = now + timedelta(days=i)
            day_end = day_start + timedelta(days=1)

            count = (
                self.db.query(func.count(UserVocabulary.id))
                .filter(
                    and_(
                        UserVocabulary.next_review >= day_start,
                        UserVocabulary.next_review < day_end
                    )
                )
                .scalar() or 0
            )

            forecast.append({
                "date": day_start.date().isoformat(),
                "reviews_due": count
            })

        return forecast

    def bulk_review(
        self,
        reviews: List[Dict[str, int]]
    ) -> Dict[str, Any]:
        """
        Process multiple reviews at once.

        Args:
            reviews: List of {vocabulary_id, performance}

        Returns:
            Summary of results
        """
        results = []
        success_count = 0
        fail_count = 0

        for review in reviews:
            result = self.review(
                vocabulary_id=review["vocabulary_id"],
                performance=review["performance"]
            )

            if result["success"]:
                success_count += 1
            else:
                fail_count += 1

            results.append(result)

        return {
            "success": True,
            "processed": len(reviews),
            "successful": success_count,
            "failed": fail_count,
            "results": results
        }

    def reset_word(self, vocabulary_id: int) -> bool:
        """
        Reset a word's SRS data to initial state.

        Args:
            vocabulary_id: ID of the vocabulary word

        Returns:
            Success status
        """
        try:
            user_vocab = (
                self.db.query(UserVocabulary)
                .filter(UserVocabulary.vocabulary_id == vocabulary_id)
                .first()
            )

            if user_vocab:
                user_vocab.ease_factor = self.DEFAULT_EASE_FACTOR
                user_vocab.interval = self.INITIAL_INTERVAL
                user_vocab.next_review = datetime.utcnow() + timedelta(days=1)
                user_vocab.review_count = 0
                user_vocab.mastery_level = 1
                user_vocab.times_correct = 0
                user_vocab.times_incorrect = 0
                self.db.commit()
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to reset word: {e}")
            self.db.rollback()
            return False


def get_srs_service(db: Session) -> SRSService:
    """Factory function to create SRSService."""
    return SRSService(db)
