"""
Flashcard Service - Manages flashcard creation and SRS-based study sessions.
Supports auto-generation from vocabulary and custom flashcard creation.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.config import settings
from app.models.db_models import Flashcard, Vocabulary, UserVocabulary

logger = logging.getLogger(__name__)


class FlashcardService:
    """Service for flashcard management and study sessions."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def create_flashcard(
        self,
        vocabulary_id: Optional[int] = None,
        front: Optional[str] = None,
        back: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new flashcard.

        Args:
            vocabulary_id: Optional vocabulary word ID (auto-creates card)
            front: Optional custom front text
            back: Optional custom back text

        Returns:
            Created flashcard data
        """
        if vocabulary_id:
            # Create from vocabulary
            vocab = self.db.query(Vocabulary).filter(Vocabulary.id == vocabulary_id).first()

            if not vocab:
                return {"success": False, "message": "Vocabulary not found"}

            # Check if flashcard already exists
            existing = (
                self.db.query(Flashcard)
                .filter(Flashcard.vocabulary_id == vocabulary_id)
                .first()
            )

            if existing:
                return {
                    "success": True,
                    "message": "Flashcard already exists",
                    "flashcard": existing.to_dict()
                }

            flashcard = Flashcard(
                vocabulary_id=vocabulary_id,
                front=vocab.word,
                back=f"{vocab.meaning_vi}\n({vocab.pronunciation})",
                is_custom=False,
                next_review=datetime.utcnow() + timedelta(days=1)
            )

        elif front and back:
            # Create custom flashcard
            flashcard = Flashcard(
                front=front,
                back=back,
                is_custom=True,
                next_review=datetime.utcnow() + timedelta(days=1)
            )
        else:
            return {
                "success": False,
                "message": "Provide vocabulary_id or both front and back text"
            }

        self.db.add(flashcard)
        self.db.commit()
        self.db.refresh(flashcard)

        return {
            "success": True,
            "flashcard": flashcard.to_dict()
        }

    def create_from_vocabulary_batch(
        self,
        vocabulary_ids: List[int]
    ) -> Dict[str, Any]:
        """Create flashcards from multiple vocabulary words."""
        created = 0
        skipped = 0

        for vocab_id in vocabulary_ids:
            result = self.create_flashcard(vocabulary_id=vocab_id)
            if result.get("success"):
                if "already exists" in result.get("message", ""):
                    skipped += 1
                else:
                    created += 1

        return {
            "success": True,
            "created": created,
            "skipped": skipped,
            "total": len(vocabulary_ids)
        }

    def get_study_session(
        self,
        mode: str = "random",
        topic: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get flashcards for a study session.

        Args:
            mode: Study mode (random, topic, level, due)
            topic: Filter by topic (for topic mode)
            level: Filter by level (for level mode)
            limit: Maximum number of cards

        Returns:
            List of flashcards for study
        """
        query = self.db.query(Flashcard)

        if mode == "due":
            # Get cards due for review
            now = datetime.utcnow()
            query = query.filter(Flashcard.next_review <= now)
            query = query.order_by(Flashcard.next_review.asc())

        elif mode == "topic" and topic:
            # Filter by topic through vocabulary
            query = (
                query
                .join(Vocabulary, Flashcard.vocabulary_id == Vocabulary.id)
                .filter(Vocabulary.topic == topic)
            )
            query = query.order_by(func.random())

        elif mode == "level" and level:
            # Filter by level through vocabulary
            query = (
                query
                .join(Vocabulary, Flashcard.vocabulary_id == Vocabulary.id)
                .filter(Vocabulary.level == level)
            )
            query = query.order_by(func.random())

        else:
            # Random mode
            query = query.order_by(func.random())

        flashcards = query.limit(limit).all()

        return [f.to_dict() for f in flashcards]

    def review_flashcard(
        self,
        flashcard_id: int,
        performance: int
    ) -> Dict[str, Any]:
        """
        Process flashcard review with SRS algorithm.

        Args:
            flashcard_id: ID of the flashcard
            performance: Rating 1-4 (Again, Hard, Good, Easy)

        Returns:
            Updated flashcard data
        """
        if performance < 1 or performance > 4:
            return {"success": False, "message": "Performance must be 1-4"}

        flashcard = self.db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()

        if not flashcard:
            return {"success": False, "message": "Flashcard not found"}

        # Apply SM-2 algorithm
        new_ease, new_interval = self._calculate_sm2(
            performance=performance,
            current_ease=flashcard.ease_factor,
            current_interval=flashcard.interval
        )

        # Update flashcard
        now = datetime.utcnow()
        flashcard.ease_factor = new_ease
        flashcard.interval = new_interval
        flashcard.last_reviewed = now
        flashcard.next_review = now + timedelta(days=new_interval)
        flashcard.review_count += 1

        self.db.commit()

        return {
            "success": True,
            "flashcard_id": flashcard_id,
            "ease_factor": round(new_ease, 2),
            "interval": new_interval,
            "next_review": flashcard.next_review.isoformat()
        }

    def _calculate_sm2(
        self,
        performance: int,
        current_ease: float,
        current_interval: int
    ) -> tuple:
        """SM-2 algorithm for flashcard scheduling."""
        MIN_EASE = 1.3

        if performance == 1:  # Again
            new_ease = max(MIN_EASE, current_ease - 0.2)
            new_interval = 1
        elif performance == 2:  # Hard
            new_ease = max(MIN_EASE, current_ease - 0.15)
            new_interval = max(1, int(current_interval * 1.2))
        elif performance == 3:  # Good
            new_ease = current_ease
            if current_interval == 1:
                new_interval = 3
            else:
                new_interval = int(current_interval * current_ease)
        else:  # Easy
            new_ease = min(3.0, current_ease + 0.15)
            if current_interval == 1:
                new_interval = 4
            else:
                new_interval = int(current_interval * current_ease * 1.3)

        new_interval = min(365, new_interval)

        return new_ease, new_interval

    def toggle_favorite(self, flashcard_id: int) -> Dict[str, Any]:
        """Toggle favorite status for a flashcard."""
        flashcard = self.db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()

        if not flashcard:
            return {"success": False, "message": "Flashcard not found"}

        flashcard.is_favorite = not flashcard.is_favorite
        self.db.commit()

        return {
            "success": True,
            "flashcard_id": flashcard_id,
            "is_favorite": flashcard.is_favorite
        }

    def get_favorites(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get favorite flashcards."""
        flashcards = (
            self.db.query(Flashcard)
            .filter(Flashcard.is_favorite == True)
            .order_by(desc(Flashcard.created_at))
            .limit(limit)
            .all()
        )

        return [f.to_dict() for f in flashcards]

    def delete_flashcard(self, flashcard_id: int) -> bool:
        """Delete a flashcard."""
        try:
            flashcard = self.db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
            if flashcard:
                self.db.delete(flashcard)
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete flashcard: {e}")
            self.db.rollback()
            return False

    def update_flashcard(
        self,
        flashcard_id: int,
        front: Optional[str] = None,
        back: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update flashcard content."""
        flashcard = self.db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()

        if not flashcard:
            return {"success": False, "message": "Flashcard not found"}

        if front:
            flashcard.front = front
        if back:
            flashcard.back = back

        self.db.commit()
        self.db.refresh(flashcard)

        return {
            "success": True,
            "flashcard": flashcard.to_dict()
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get flashcard statistics."""
        now = datetime.utcnow()

        total = self.db.query(func.count(Flashcard.id)).scalar() or 0
        custom = self.db.query(func.count(Flashcard.id)).filter(Flashcard.is_custom == True).scalar() or 0
        favorites = self.db.query(func.count(Flashcard.id)).filter(Flashcard.is_favorite == True).scalar() or 0

        due_now = (
            self.db.query(func.count(Flashcard.id))
            .filter(Flashcard.next_review <= now)
            .scalar() or 0
        )

        avg_ease = self.db.query(func.avg(Flashcard.ease_factor)).scalar() or 2.5
        total_reviews = self.db.query(func.sum(Flashcard.review_count)).scalar() or 0

        return {
            "total_flashcards": total,
            "custom_flashcards": custom,
            "favorites": favorites,
            "due_now": due_now,
            "average_ease_factor": round(avg_ease, 2),
            "total_reviews": total_reviews
        }

    def sync_with_vocabulary(self) -> Dict[str, Any]:
        """
        Sync flashcards with learned vocabulary.
        Creates flashcards for vocabulary that doesn't have them.
        """
        # Get vocabulary IDs that have flashcards
        existing_vocab_ids = (
            self.db.query(Flashcard.vocabulary_id)
            .filter(Flashcard.vocabulary_id.isnot(None))
            .all()
        )
        existing_ids = {r.vocabulary_id for r in existing_vocab_ids}

        # Get learned vocabulary without flashcards
        missing_vocab = (
            self.db.query(Vocabulary)
            .join(UserVocabulary, UserVocabulary.vocabulary_id == Vocabulary.id)
            .filter(~Vocabulary.id.in_(existing_ids) if existing_ids else True)
            .all()
        )

        created = 0
        for vocab in missing_vocab:
            flashcard = Flashcard(
                vocabulary_id=vocab.id,
                front=vocab.word,
                back=f"{vocab.meaning_vi}\n({vocab.pronunciation})",
                is_custom=False,
                next_review=datetime.utcnow() + timedelta(days=1)
            )
            self.db.add(flashcard)
            created += 1

        self.db.commit()

        return {
            "success": True,
            "created": created,
            "message": f"Created {created} new flashcards from vocabulary"
        }


def get_flashcard_service(db: Session) -> FlashcardService:
    """Factory function to create FlashcardService."""
    return FlashcardService(db)
