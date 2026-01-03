"""
Vocabulary Service - Handles vocabulary generation, storage, and learning progress.
Uses Qwen AI model for generating vocabulary with translations and examples.
"""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.config import settings, TOPICS
from app.models.db_models import Vocabulary, UserVocabulary
from app.services.ai_model_manager import ai_manager

logger = logging.getLogger(__name__)


class VocabularyService:
    """Service for vocabulary management and AI-powered generation."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def generate_vocabulary(
        self,
        topic: str,
        level: str,
        num_words: int = 10,
        topic_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate vocabulary words using AI for a specific topic and level.

        Args:
            topic: Topic name (e.g., "Work and Business")
            level: CEFR level (A1-C2)
            num_words: Number of words to generate
            topic_id: Optional topic ID

        Returns:
            List of vocabulary dictionaries
        """
        prompt = self._build_vocabulary_prompt(topic, level, num_words)
        tokens_needed = min(num_words * 150, 1500)

        try:
            response = ai_manager.generate_text(
                prompt,
                max_tokens=tokens_needed,
                temperature=0.7
            )

            vocabulary_list = self._parse_vocabulary_response(response)

            saved_vocabulary = []
            for vocab_data in vocabulary_list[:num_words]:
                vocab = self._save_vocabulary(vocab_data, topic, level, topic_id)
                if vocab:
                    saved_vocabulary.append(vocab.to_dict())

            logger.info(f"Generated {len(saved_vocabulary)} vocabulary words for {topic} at {level}")
            return saved_vocabulary

        except Exception as e:
            logger.error(f"Vocabulary generation failed: {e}")
            return self._get_fallback_vocabulary(topic, level, num_words)

    def _build_vocabulary_prompt(self, topic: str, level: str, num_words: int) -> str:
        """Build the prompt for vocabulary generation."""
        level_descriptions = {
            "A1": "very basic, everyday words for beginners",
            "A2": "elementary level, simple and common words",
            "B1": "intermediate level, practical vocabulary for daily use",
            "B2": "upper-intermediate, more complex and nuanced vocabulary",
            "C1": "advanced vocabulary including idiomatic expressions",
            "C2": "proficiency level, sophisticated and specialized vocabulary"
        }

        level_desc = level_descriptions.get(level, "intermediate level vocabulary")

        prompt = f"""Generate {num_words} English vocabulary words for topic "{topic}" at {level} level ({level_desc}).

Return a JSON array of objects. Each object must use curly braces {{}}.

Example format:
[
  {{"word": "example", "meaning_vi": "ví dụ", "pronunciation": "/ɪɡˈzæmpəl/", "part_of_speech": "noun", "example_en": "This is an example.", "example_vi": "Đây là một ví dụ.", "synonyms": "instance, sample"}}
]

Now generate {num_words} words for "{topic}" at {level} level. Output ONLY valid JSON array:
[
  {{"""

        return prompt

    def _parse_vocabulary_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse the AI response into vocabulary list."""
        try:
            # The prompt ends with "[\n  {" so response continues from there
            # Prepend the opening to make valid JSON
            json_str = '[{' + response.strip()

            # Fix common AI output issues
            # Convert ["key": value] to {"key": value}
            json_str = re.sub(r'\[("word")', r'{\1', json_str)
            json_str = re.sub(r'("synonyms":\s*"[^"]*")\s*\]', r'\1}', json_str)

            # Find the end of valid JSON array
            bracket_count = 0
            brace_count = 0
            end_pos = len(json_str)

            for i, char in enumerate(json_str):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_pos = i + 1
                        break
                elif char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1

            json_str = json_str[:end_pos]

            # Ensure proper closing
            if not json_str.rstrip().endswith(']'):
                # Close any open braces first
                while brace_count > 0:
                    json_str += '}'
                    brace_count -= 1
                json_str += ']'

            # Clean up common issues
            json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r'}\s*{', '},{', json_str)  # Add missing commas between objects

            vocabulary = json.loads(json_str)

            # Validate and clean each entry
            cleaned = []
            for vocab in vocabulary:
                if isinstance(vocab, dict) and "word" in vocab:
                    cleaned_vocab = {
                        "word": str(vocab.get("word", "")).strip(),
                        "meaning_vi": str(vocab.get("meaning_vi", "")).strip(),
                        "pronunciation": str(vocab.get("pronunciation", "")).strip(),
                        "part_of_speech": str(vocab.get("part_of_speech", "")).strip().lower(),
                        "example_en": str(vocab.get("example_en", "")).strip(),
                        "example_vi": str(vocab.get("example_vi", "")).strip(),
                        "synonyms": vocab.get("synonyms", "")
                    }

                    # Validate part of speech
                    if cleaned_vocab["part_of_speech"] not in ["noun", "verb", "adjective", "adverb"]:
                        cleaned_vocab["part_of_speech"] = "noun"

                    cleaned.append(cleaned_vocab)

            return cleaned

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse vocabulary JSON: {e}")
            logger.debug(f"Response was: {response[:500]}")
            return []

    def _save_vocabulary(
        self,
        vocab_data: Dict[str, Any],
        topic: str,
        level: str,
        topic_id: Optional[int] = None
    ) -> Optional[Vocabulary]:
        """Save vocabulary to database."""
        try:
            # Check if word already exists for this topic/level
            existing = (
                self.db.query(Vocabulary)
                .filter(
                    and_(
                        Vocabulary.word == vocab_data["word"],
                        Vocabulary.topic == topic,
                        Vocabulary.level == level
                    )
                )
                .first()
            )

            if existing:
                return existing

            # Create new vocabulary entry
            synonyms = vocab_data.get("synonyms", "")
            if isinstance(synonyms, list):
                synonyms_json = json.dumps(synonyms)
            elif isinstance(synonyms, str):
                synonyms_json = json.dumps([s.strip() for s in synonyms.split(",") if s.strip()])
            else:
                synonyms_json = "[]"

            vocabulary = Vocabulary(
                word=vocab_data["word"],
                meaning_vi=vocab_data["meaning_vi"],
                pronunciation=vocab_data.get("pronunciation", ""),
                part_of_speech=vocab_data.get("part_of_speech", "noun"),
                level=level,
                topic=topic,
                topic_id=topic_id,
                example_en=vocab_data.get("example_en", ""),
                example_vi=vocab_data.get("example_vi", ""),
                synonyms=synonyms_json
            )

            self.db.add(vocabulary)
            self.db.commit()
            self.db.refresh(vocabulary)

            return vocabulary

        except Exception as e:
            logger.error(f"Failed to save vocabulary: {e}")
            self.db.rollback()
            return None

    def _get_fallback_vocabulary(
        self,
        topic: str,
        level: str,
        num_words: int
    ) -> List[Dict[str, Any]]:
        """Get fallback vocabulary when AI generation fails."""
        # Basic fallback vocabulary by level
        fallback_words = {
            "A1": [
                {"word": "hello", "meaning_vi": "xin chào", "pronunciation": "/həˈloʊ/", "part_of_speech": "interjection", "example_en": "Hello, how are you?", "example_vi": "Xin chào, bạn khỏe không?", "synonyms": "hi, hey"},
                {"word": "work", "meaning_vi": "làm việc", "pronunciation": "/wɜːrk/", "part_of_speech": "verb", "example_en": "I work in an office.", "example_vi": "Tôi làm việc trong văn phòng.", "synonyms": "labor, toil"},
                {"word": "good", "meaning_vi": "tốt", "pronunciation": "/ɡʊd/", "part_of_speech": "adjective", "example_en": "This is a good book.", "example_vi": "Đây là một cuốn sách hay.", "synonyms": "great, fine"},
            ],
            "B1": [
                {"word": "collaborate", "meaning_vi": "hợp tác", "pronunciation": "/kəˈlæbəreɪt/", "part_of_speech": "verb", "example_en": "We need to collaborate on this project.", "example_vi": "Chúng ta cần hợp tác trong dự án này.", "synonyms": "cooperate, work together"},
                {"word": "efficient", "meaning_vi": "hiệu quả", "pronunciation": "/ɪˈfɪʃənt/", "part_of_speech": "adjective", "example_en": "This is an efficient method.", "example_vi": "Đây là một phương pháp hiệu quả.", "synonyms": "effective, productive"},
            ],
        }

        words = fallback_words.get(level, fallback_words["B1"])
        return words[:num_words]

    def mark_as_learned(self, vocabulary_id: int) -> Optional[UserVocabulary]:
        """
        Mark a vocabulary word as learned.

        Args:
            vocabulary_id: ID of the vocabulary word

        Returns:
            UserVocabulary record or None
        """
        try:
            # Check if already learned
            existing = (
                self.db.query(UserVocabulary)
                .filter(UserVocabulary.vocabulary_id == vocabulary_id)
                .first()
            )

            if existing:
                return existing

            # Create new user vocabulary record
            now = datetime.utcnow()
            user_vocab = UserVocabulary(
                vocabulary_id=vocabulary_id,
                learned_at=now,
                next_review=now + timedelta(days=1),
                ease_factor=settings.SRS_INITIAL_EASE_FACTOR,
                interval=settings.SRS_INITIAL_INTERVAL
            )

            self.db.add(user_vocab)
            self.db.commit()
            self.db.refresh(user_vocab)

            return user_vocab

        except Exception as e:
            logger.error(f"Failed to mark vocabulary as learned: {e}")
            self.db.rollback()
            return None

    def toggle_favorite(self, vocabulary_id: int) -> bool:
        """Toggle favorite status for a vocabulary word."""
        try:
            user_vocab = (
                self.db.query(UserVocabulary)
                .filter(UserVocabulary.vocabulary_id == vocabulary_id)
                .first()
            )

            if user_vocab:
                user_vocab.is_favorite = not user_vocab.is_favorite
                self.db.commit()
                return user_vocab.is_favorite

            return False

        except Exception as e:
            logger.error(f"Failed to toggle favorite: {e}")
            self.db.rollback()
            return False

    def get_vocabulary_by_topic(
        self,
        topic: str,
        level: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get vocabulary words for a specific topic."""
        query = self.db.query(Vocabulary).filter(Vocabulary.topic == topic)

        if level:
            query = query.filter(Vocabulary.level == level)

        vocabulary = query.order_by(Vocabulary.created_at.desc()).limit(limit).all()
        return [v.to_dict() for v in vocabulary]

    def get_learned_vocabulary(
        self,
        topic: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get user's learned vocabulary."""
        query = (
            self.db.query(UserVocabulary)
            .join(Vocabulary)
        )

        if topic:
            query = query.filter(Vocabulary.topic == topic)
        if level:
            query = query.filter(Vocabulary.level == level)

        results = query.order_by(UserVocabulary.learned_at.desc()).limit(limit).all()

        vocabulary_list = []
        for uv in results:
            vocab_dict = uv.vocabulary.to_dict()
            vocab_dict["user_progress"] = uv.to_dict()
            vocabulary_list.append(vocab_dict)

        return vocabulary_list

    def get_vocabulary_stats(self) -> Dict[str, Any]:
        """Get vocabulary learning statistics."""
        # Total vocabulary
        total_vocab = self.db.query(func.count(Vocabulary.id)).scalar() or 0

        # Learned vocabulary
        learned_count = self.db.query(func.count(UserVocabulary.id)).scalar() or 0

        # By level
        by_level = {}
        level_counts = (
            self.db.query(
                Vocabulary.level,
                func.count(Vocabulary.id)
            )
            .join(UserVocabulary, UserVocabulary.vocabulary_id == Vocabulary.id)
            .group_by(Vocabulary.level)
            .all()
        )
        for level, count in level_counts:
            by_level[level] = count

        # By topic
        by_topic = {}
        topic_counts = (
            self.db.query(
                Vocabulary.topic,
                func.count(Vocabulary.id)
            )
            .join(UserVocabulary, UserVocabulary.vocabulary_id == Vocabulary.id)
            .group_by(Vocabulary.topic)
            .all()
        )
        for topic, count in topic_counts:
            by_topic[topic] = count

        # Mastery levels
        mastery_counts = (
            self.db.query(
                UserVocabulary.mastery_level,
                func.count(UserVocabulary.id)
            )
            .group_by(UserVocabulary.mastery_level)
            .all()
        )
        by_mastery = {str(level): count for level, count in mastery_counts}

        return {
            "total_vocabulary": total_vocab,
            "learned_count": learned_count,
            "by_level": by_level,
            "by_topic": by_topic,
            "by_mastery": by_mastery
        }

    def search_vocabulary(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search vocabulary by word or meaning."""
        search_term = f"%{query}%"

        results = (
            self.db.query(Vocabulary)
            .filter(
                or_(
                    Vocabulary.word.ilike(search_term),
                    Vocabulary.meaning_vi.ilike(search_term)
                )
            )
            .limit(limit)
            .all()
        )

        return [v.to_dict() for v in results]

    def delete_vocabulary(self, vocabulary_id: int) -> bool:
        """Delete a vocabulary word."""
        try:
            vocab = self.db.query(Vocabulary).filter(Vocabulary.id == vocabulary_id).first()
            if vocab:
                self.db.delete(vocab)
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete vocabulary: {e}")
            self.db.rollback()
            return False


def get_vocabulary_service(db: Session) -> VocabularyService:
    """Factory function to create VocabularyService."""
    return VocabularyService(db)
