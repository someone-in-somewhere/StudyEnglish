"""
Topic Service - Manages the 23 predefined learning topics.
"""

import logging
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import TOPICS
from app.models.db_models import Vocabulary, UserVocabulary

logger = logging.getLogger(__name__)


class TopicService:
    """Service for managing learning topics."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    @staticmethod
    def get_all_topics() -> List[Dict[str, Any]]:
        """
        Get all 23 predefined topics.

        Returns:
            List of topic dictionaries with metadata
        """
        return TOPICS.copy()

    @staticmethod
    def get_topic_by_id(topic_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a topic by its ID.

        Args:
            topic_id: The topic ID

        Returns:
            Topic dictionary or None if not found
        """
        for topic in TOPICS:
            if topic["id"] == topic_id:
                return topic.copy()
        return None

    @staticmethod
    def get_topic_by_name(name: str) -> Optional[Dict[str, Any]]:
        """
        Get a topic by its name (case-insensitive).

        Args:
            name: The topic name

        Returns:
            Topic dictionary or None if not found
        """
        name_lower = name.lower()
        for topic in TOPICS:
            if topic["name"].lower() == name_lower:
                return topic.copy()
        return None

    @staticmethod
    def get_topics_by_tier(tier: int) -> List[Dict[str, Any]]:
        """
        Get all topics in a specific tier.

        Args:
            tier: Tier number (1-6)

        Returns:
            List of topics in the tier
        """
        return [t.copy() for t in TOPICS if t["tier"] == tier]

    def get_topics_with_stats(self) -> List[Dict[str, Any]]:
        """
        Get all topics with vocabulary statistics.

        Returns:
            List of topics with word_count and learned_count
        """
        topics = self.get_all_topics()

        # Get word counts per topic
        word_counts = (
            self.db.query(
                Vocabulary.topic_id,
                func.count(Vocabulary.id).label("count")
            )
            .group_by(Vocabulary.topic_id)
            .all()
        )

        word_count_map = {tc.topic_id: tc.count for tc in word_counts}

        # Get learned counts per topic
        learned_counts = (
            self.db.query(
                Vocabulary.topic_id,
                func.count(UserVocabulary.id).label("count")
            )
            .join(UserVocabulary, UserVocabulary.vocabulary_id == Vocabulary.id)
            .group_by(Vocabulary.topic_id)
            .all()
        )

        learned_count_map = {lc.topic_id: lc.count for lc in learned_counts}

        # Add stats to topics
        for topic in topics:
            topic["word_count"] = word_count_map.get(topic["id"], 0)
            topic["learned_count"] = learned_count_map.get(topic["id"], 0)

        return topics

    @staticmethod
    def get_tier_names() -> Dict[int, str]:
        """
        Get tier names mapping.

        Returns:
            Dictionary mapping tier number to name
        """
        return {
            1: "Essential",
            2: "Professional",
            3: "Daily Life",
            4: "General",
            5: "Culture",
            6: "Specialized"
        }

    @staticmethod
    def get_topic_icon(topic_id: int) -> str:
        """Get Font Awesome icon class for a topic."""
        topic = TopicService.get_topic_by_id(topic_id)
        return topic["icon"] if topic else "fa-book"

    @staticmethod
    def get_topic_color(topic_id: int) -> str:
        """Get color for a topic."""
        topic = TopicService.get_topic_by_id(topic_id)
        return topic["color"] if topic else "#6B7280"

    def search_topics(self, query: str) -> List[Dict[str, Any]]:
        """
        Search topics by name.

        Args:
            query: Search query

        Returns:
            List of matching topics
        """
        query_lower = query.lower()
        matching = []

        for topic in TOPICS:
            if query_lower in topic["name"].lower():
                topic_copy = topic.copy()
                matching.append(topic_copy)

        return matching


# Singleton instance for static access
topic_service_static = TopicService(None)


def get_topic_service(db: Session) -> TopicService:
    """Factory function to create TopicService with db session."""
    return TopicService(db)
