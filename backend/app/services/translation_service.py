"""
Translation Service - Handles English-Vietnamese bidirectional translation.
Uses NLLB-200 model for offline translation.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.db_models import Translation
from app.services.ai_model_manager import ai_manager

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for translation between English and Vietnamese."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        level: Optional[str] = None,
        save_history: bool = True
    ) -> Dict[str, Any]:
        """
        Translate text between English and Vietnamese.

        Args:
            text: Text to translate
            source_lang: Source language (en/vi)
            target_lang: Target language (en/vi)
            level: Optional CEFR level for simplification
            save_history: Whether to save to history

        Returns:
            Translation result
        """
        if source_lang == target_lang:
            return {
                "success": False,
                "message": "Source and target language must be different"
            }

        if source_lang not in ["en", "vi"] or target_lang not in ["en", "vi"]:
            return {
                "success": False,
                "message": "Only English (en) and Vietnamese (vi) are supported"
            }

        try:
            # Perform translation
            translated_text = ai_manager.translate(text, source_lang, target_lang)

            # Apply level adjustment if specified
            if level and target_lang == "en":
                translated_text = self._adjust_level(translated_text, level)

            # Save to history
            translation_record = None
            if save_history:
                translation_record = Translation(
                    source_text=text,
                    translated_text=translated_text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    level=level
                )
                self.db.add(translation_record)
                self.db.commit()
                self.db.refresh(translation_record)

            return {
                "success": True,
                "id": translation_record.id if translation_record else None,
                "source_text": text,
                "translated_text": translated_text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "level": level,
                "created_at": translation_record.created_at.isoformat() if translation_record else None
            }

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "success": False,
                "message": f"Translation failed: {str(e)}"
            }

    def _adjust_level(self, text: str, level: str) -> str:
        """
        Adjust text complexity based on CEFR level.
        Uses AI to simplify or complexify the translation.

        Args:
            text: Text to adjust
            level: Target CEFR level

        Returns:
            Adjusted text
        """
        level_instructions = {
            "A1": "very simple words and short sentences for beginners",
            "A2": "simple vocabulary and basic sentence structures",
            "B1": "clear and standard language for intermediate learners",
            "B2": "more complex vocabulary and varied sentence structures",
            "C1": "sophisticated vocabulary and complex grammar",
            "C2": "native-like fluency with idiomatic expressions"
        }

        instruction = level_instructions.get(level, "intermediate level")

        prompt = f"""Rewrite the following English text for a {level} level English learner.
Use {instruction}.

Original text: {text}

Rewritten text at {level} level:"""

        try:
            adjusted = ai_manager.generate_text(
                prompt,
                max_tokens=500,
                temperature=0.3
            )
            return adjusted.strip() if adjusted else text
        except Exception as e:
            logger.error(f"Level adjustment failed: {e}")
            return text

    def get_history(
        self,
        limit: int = 50,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get translation history.

        Args:
            limit: Maximum number of records
            source_lang: Filter by source language
            target_lang: Filter by target language

        Returns:
            List of translation records
        """
        query = self.db.query(Translation)

        if source_lang:
            query = query.filter(Translation.source_lang == source_lang)
        if target_lang:
            query = query.filter(Translation.target_lang == target_lang)

        translations = query.order_by(desc(Translation.created_at)).limit(limit).all()
        return [t.to_dict() for t in translations]

    def get_translation_by_id(self, translation_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific translation by ID."""
        translation = self.db.query(Translation).filter(Translation.id == translation_id).first()
        return translation.to_dict() if translation else None

    def delete_translation(self, translation_id: int) -> bool:
        """Delete a translation from history."""
        try:
            translation = self.db.query(Translation).filter(Translation.id == translation_id).first()
            if translation:
                self.db.delete(translation)
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete translation: {e}")
            self.db.rollback()
            return False

    def clear_history(self) -> int:
        """
        Clear all translation history.

        Returns:
            Number of records deleted
        """
        try:
            count = self.db.query(Translation).delete()
            self.db.commit()
            return count
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            self.db.rollback()
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get translation statistics."""
        from sqlalchemy import func

        total = self.db.query(func.count(Translation.id)).scalar() or 0

        # By direction
        en_to_vi = (
            self.db.query(func.count(Translation.id))
            .filter(Translation.source_lang == "en", Translation.target_lang == "vi")
            .scalar() or 0
        )

        vi_to_en = (
            self.db.query(func.count(Translation.id))
            .filter(Translation.source_lang == "vi", Translation.target_lang == "en")
            .scalar() or 0
        )

        # Average text length
        avg_source_length = (
            self.db.query(func.avg(func.length(Translation.source_text))).scalar() or 0
        )

        return {
            "total_translations": total,
            "en_to_vi": en_to_vi,
            "vi_to_en": vi_to_en,
            "avg_source_length": round(avg_source_length)
        }

    def batch_translate(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str
    ) -> List[Dict[str, Any]]:
        """
        Translate multiple texts.

        Args:
            texts: List of texts to translate
            source_lang: Source language
            target_lang: Target language

        Returns:
            List of translation results
        """
        results = []

        for text in texts:
            result = self.translate(
                text=text,
                source_lang=source_lang,
                target_lang=target_lang,
                save_history=False  # Don't clutter history with batch
            )
            results.append(result)

        return results


def get_translation_service(db: Session) -> TranslationService:
    """Factory function to create TranslationService."""
    return TranslationService(db)
