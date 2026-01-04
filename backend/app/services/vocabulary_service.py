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

        prompt = f'''You are an English vocabulary generator. Generate {num_words} vocabulary words for topic "{topic}" at {level} level.

For each word, output ONE JSON object per line with these fields:
- word: English word
- meaning_vi: Vietnamese meaning
- pronunciation: IPA (e.g. /wɜːd/)
- part_of_speech: noun/verb/adjective/adverb
- example_en: Example sentence in English
- example_vi: Vietnamese translation
- synonyms: 2 synonyms

Output format - one complete JSON object per line:
{{"word": "hello", "meaning_vi": "xin chào", "pronunciation": "/həˈləʊ/", "part_of_speech": "noun", "example_en": "Hello everyone.", "example_vi": "Xin chào mọi người.", "synonyms": "hi, greetings"}}

Generate {num_words} words for "{topic}" at {level} level:
'''

        return prompt

    def _parse_vocabulary_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse the AI response into vocabulary list."""
        try:
            full_response = response.strip()

            # Parse line by line - each line should be a JSON object
            vocabulary = []

            # Find all JSON objects in the response
            # Pattern to match complete JSON objects
            json_pattern = r'\{[^{}]*"word"[^{}]*\}'
            matches = re.findall(json_pattern, full_response)

            for match in matches:
                try:
                    # Clean up the match
                    cleaned = match.strip()
                    # Fix common issues
                    cleaned = re.sub(r',\s*}', '}', cleaned)
                    cleaned = re.sub(r'"\s*,\s*"', '", "', cleaned)

                    obj = json.loads(cleaned)
                    if "word" in obj:
                        vocabulary.append(obj)
                except json.JSONDecodeError:
                    continue

            # If regex didn't work, try line-by-line parsing
            if not vocabulary:
                lines = full_response.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('{') and 'word' in line:
                        # Ensure it ends with }
                        if not line.endswith('}'):
                            line = line.rstrip(',') + '}'
                        try:
                            obj = json.loads(line)
                            if "word" in obj:
                                vocabulary.append(obj)
                        except json.JSONDecodeError:
                            continue

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

    def import_vocabulary(
        self,
        topic: str,
        level: str,
        ai_response: str,
        topic_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Import vocabulary from external AI response.
        Parses JSON, filters duplicates, and saves to database.

        Args:
            topic: Topic name
            level: CEFR level
            ai_response: Raw AI response containing JSON vocabulary
            topic_id: Optional topic ID

        Returns:
            Dict with success status, added count, duplicates count, and vocabulary list
        """
        try:
            # Parse the AI response
            vocabulary_list = self._parse_ai_response(ai_response)

            if not vocabulary_list:
                return {
                    "success": False,
                    "message": "Could not parse vocabulary from AI response. Please check the JSON format.",
                    "added": 0,
                    "duplicates": 0,
                    "vocabulary": []
                }

            added = 0
            duplicates = 0
            saved_vocabulary = []

            for vocab_data in vocabulary_list:
                # Check if word already exists
                existing = (
                    self.db.query(Vocabulary)
                    .filter(
                        and_(
                            Vocabulary.word == vocab_data.get("word", ""),
                            Vocabulary.topic == topic,
                            Vocabulary.level == level
                        )
                    )
                    .first()
                )

                if existing:
                    duplicates += 1
                    saved_vocabulary.append(existing.to_dict())
                    continue

                # Save new vocabulary
                vocab = self._save_vocabulary(vocab_data, topic, level, topic_id)
                if vocab:
                    added += 1
                    saved_vocabulary.append(vocab.to_dict())

            logger.info(f"Imported vocabulary: {added} added, {duplicates} duplicates for {topic} at {level}")

            return {
                "success": True,
                "added": added,
                "duplicates": duplicates,
                "vocabulary": saved_vocabulary
            }

        except Exception as e:
            logger.error(f"Failed to import vocabulary: {e}")
            return {
                "success": False,
                "message": f"Error importing vocabulary: {str(e)}",
                "added": 0,
                "duplicates": 0,
                "vocabulary": []
            }

    def _parse_ai_response(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse AI response to extract vocabulary JSON."""
        try:
            text = ai_response.strip()

            # Try to find JSON array in the response
            # Look for [ ... ] pattern
            start_idx = text.find('[')
            end_idx = text.rfind(']')

            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx + 1]
                vocabulary = json.loads(json_str)

                if isinstance(vocabulary, list):
                    # Validate and clean each entry
                    cleaned = []
                    for vocab in vocabulary:
                        if isinstance(vocab, dict) and "word" in vocab:
                            cleaned_vocab = {
                                "word": str(vocab.get("word", "")).strip(),
                                "meaning_vi": str(vocab.get("meaning_vi", "")).strip(),
                                "pronunciation": str(vocab.get("pronunciation", "")).strip(),
                                "part_of_speech": str(vocab.get("part_of_speech", "noun")).strip().lower(),
                                "example_en": str(vocab.get("example_en", "")).strip(),
                                "example_vi": str(vocab.get("example_vi", "")).strip(),
                                "synonyms": vocab.get("synonyms", "")
                            }

                            # Validate part of speech
                            if cleaned_vocab["part_of_speech"] not in ["noun", "verb", "adjective", "adverb"]:
                                cleaned_vocab["part_of_speech"] = "noun"

                            cleaned.append(cleaned_vocab)

                    return cleaned

            # If no array found, try parsing individual JSON objects
            json_pattern = r'\{[^{}]*"word"[^{}]*\}'
            matches = re.findall(json_pattern, text)

            vocabulary = []
            for match in matches:
                try:
                    obj = json.loads(match)
                    if "word" in obj:
                        vocabulary.append(obj)
                except json.JSONDecodeError:
                    continue

            return vocabulary

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return []

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

    def unlearn_vocabulary(self, vocabulary_id: int) -> bool:
        """Remove a vocabulary word from learned list."""
        try:
            user_vocab = (
                self.db.query(UserVocabulary)
                .filter(UserVocabulary.vocabulary_id == vocabulary_id)
                .first()
            )

            if user_vocab:
                self.db.delete(user_vocab)
                self.db.commit()
                logger.info(f"Removed vocabulary {vocabulary_id} from learned list")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to unlearn vocabulary: {e}")
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

    def get_flashcard_words(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get flashcard words prioritizing weak words.

        Prioritizes words with:
        - Lower mastery level
        - Fewer review counts
        - Fewer quiz attempts (times_correct + times_incorrect)
        """
        query = (
            self.db.query(UserVocabulary)
            .join(Vocabulary)
            .order_by(
                UserVocabulary.mastery_level.asc(),
                UserVocabulary.review_count.asc(),
                (UserVocabulary.times_correct + UserVocabulary.times_incorrect).asc(),
                func.random()
            )
            .limit(limit)
        )

        results = query.all()

        flashcards = []
        for uv in results:
            flashcard = {
                "id": uv.vocabulary.id,
                "word": uv.vocabulary.word,
                "meaning_vi": uv.vocabulary.meaning_vi,
                "pronunciation": uv.vocabulary.pronunciation,
                "part_of_speech": uv.vocabulary.part_of_speech,
                "example_en": uv.vocabulary.example_en,
                "example_vi": uv.vocabulary.example_vi,
                "level": uv.vocabulary.level,
                "topic": uv.vocabulary.topic,
                "mastery_level": uv.mastery_level,
                "review_count": uv.review_count,
                "times_correct": uv.times_correct,
                "times_incorrect": uv.times_incorrect
            }
            flashcards.append(flashcard)

        return flashcards

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
