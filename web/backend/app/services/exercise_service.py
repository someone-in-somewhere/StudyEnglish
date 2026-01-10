"""
Exercise Service - Generates various types of English exercises.
Supports fill in the blank, rewrite, translation, word order, and error correction.
"""

import json
import logging
import random
from datetime import datetime
from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.db_models import Vocabulary, UserVocabulary, Exercise, ExerciseAttempt
from app.services.ai_model_manager import ai_manager

logger = logging.getLogger(__name__)


class ExerciseService:
    """Service for generating and managing exercises."""

    EXERCISE_TYPES = [
        "fill_blank",
        "rewrite",
        "translation",
        "word_order",
        "error_correction"
    ]

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def generate_exercises(
        self,
        exercise_type: str,
        num_exercises: int = 10,
        topic: Optional[str] = None,
        level: str = "B1",
        words: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate exercises using AI.

        Args:
            exercise_type: Type of exercise
            num_exercises: Number of exercises to generate
            topic: Optional topic filter
            level: CEFR level
            words: Optional list of words to focus on

        Returns:
            Exercise data
        """
        if exercise_type not in self.EXERCISE_TYPES:
            return {
                "success": False,
                "message": f"Unknown exercise type: {exercise_type}"
            }

        # Get vocabulary words if not provided
        if not words:
            words = self._get_vocabulary_words(topic, level, num_exercises)

        if not words:
            return {
                "success": False,
                "message": "No vocabulary available for exercises"
            }

        # Build prompt and generate
        prompt = self._build_exercise_prompt(exercise_type, level, words, num_exercises)

        try:
            response = ai_manager.generate_text(
                prompt,
                max_tokens=2048,
                temperature=0.7
            )

            exercises = self._parse_exercise_response(response, exercise_type)

            if not exercises:
                exercises = self._get_fallback_exercises(exercise_type, words, level)

            # Save to database
            exercise_record = Exercise(
                exercise_type=exercise_type,
                topic=topic,
                level=level,
                content={"exercises": exercises, "words": words}
            )
            self.db.add(exercise_record)
            self.db.commit()
            self.db.refresh(exercise_record)

            return {
                "success": True,
                "exercise_id": exercise_record.id,
                "exercise_type": exercise_type,
                "level": level,
                "exercises": exercises
            }

        except Exception as e:
            logger.error(f"Exercise generation failed: {e}")
            # Return fallback
            exercises = self._get_fallback_exercises(exercise_type, words, level)

            exercise_record = Exercise(
                exercise_type=exercise_type,
                topic=topic,
                level=level,
                content={"exercises": exercises, "words": words}
            )
            self.db.add(exercise_record)
            self.db.commit()
            self.db.refresh(exercise_record)

            return {
                "success": True,
                "exercise_id": exercise_record.id,
                "exercise_type": exercise_type,
                "level": level,
                "exercises": exercises
            }

    def _get_vocabulary_words(
        self,
        topic: Optional[str],
        level: str,
        limit: int
    ) -> List[str]:
        """Get vocabulary words for exercises."""
        query = (
            self.db.query(Vocabulary.word)
            .join(UserVocabulary, UserVocabulary.vocabulary_id == Vocabulary.id)
        )

        if topic:
            query = query.filter(Vocabulary.topic == topic)
        if level:
            query = query.filter(Vocabulary.level == level)

        words = query.order_by(func.random()).limit(limit).all()
        return [w.word for w in words]

    def _build_exercise_prompt(
        self,
        exercise_type: str,
        level: str,
        words: List[str],
        num_exercises: int
    ) -> str:
        """Build AI prompt for exercise generation."""
        words_str = ", ".join(words)

        if exercise_type == "fill_blank":
            return f"""Create {num_exercises} fill-in-the-blank sentences using these words: {words_str}.
Level: {level}

Return a JSON array with this structure:
[{{"id": 1, "sentence": "She ___ to work every day.", "answer": "goes", "hint": "verb form"}}]

Important:
- Replace the target word with ___
- Provide natural, useful sentences
- Match the {level} CEFR level

JSON array:
["""

        elif exercise_type == "rewrite":
            return f"""Create {num_exercises} sentence rewriting exercises at {level} level.

Each exercise should have an original sentence and a prompt for rewriting.
Use words: {words_str}

Return a JSON array:
[{{"id": 1, "original": "He goes to school.", "instruction": "Rewrite in past tense", "answer": "He went to school."}}]

JSON array:
["""

        elif exercise_type == "translation":
            return f"""Create {num_exercises} translation exercises from Vietnamese to English.
Level: {level}
Use vocabulary: {words_str}

Return a JSON array:
[{{"id": 1, "vietnamese": "Tôi đi làm mỗi ngày.", "english": "I go to work every day.", "key_words": ["work", "every day"]}}]

JSON array:
["""

        elif exercise_type == "word_order":
            return f"""Create {num_exercises} word order exercises at {level} level.
Include words: {words_str}

Provide jumbled words that students must arrange correctly.

Return a JSON array:
[{{"id": 1, "jumbled": ["work", "I", "every", "to", "go", "day"], "answer": "I go to work every day"}}]

JSON array:
["""

        elif exercise_type == "error_correction":
            return f"""Create {num_exercises} error correction exercises at {level} level.

Each sentence should have ONE grammatical error for students to find and correct.

Return a JSON array:
[{{"id": 1, "sentence": "She go to work every day.", "error": "go", "correction": "goes", "explanation": "Third person singular requires 's'"}}]

JSON array:
["""

        return ""

    def _parse_exercise_response(
        self,
        response: str,
        exercise_type: str
    ) -> List[Dict[str, Any]]:
        """Parse AI response into exercises."""
        try:
            # Clean and parse JSON
            if not response.strip().startswith("["):
                response = "[" + response

            # Find complete JSON
            bracket_count = 0
            end_pos = 0
            for i, char in enumerate(response):
                if char == "[":
                    bracket_count += 1
                elif char == "]":
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_pos = i + 1
                        break

            if end_pos > 0:
                json_str = response[:end_pos]
            else:
                json_str = response + "]"

            # Clean up
            json_str = json_str.replace(",]", "]").replace(",}", "}")

            exercises = json.loads(json_str)

            # Validate and clean
            cleaned = []
            for i, ex in enumerate(exercises):
                if isinstance(ex, dict):
                    ex["id"] = i + 1
                    cleaned.append(ex)

            return cleaned

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse exercises: {e}")
            return []

    def _get_fallback_exercises(
        self,
        exercise_type: str,
        words: List[str],
        level: str
    ) -> List[Dict[str, Any]]:
        """Generate fallback exercises."""
        exercises = []

        if exercise_type == "fill_blank":
            templates = [
                ("I ___ to work every day.", "go"),
                ("She ___ English very well.", "speaks"),
                ("They ___ in the park yesterday.", "played"),
            ]
            for i, (sentence, answer) in enumerate(templates):
                exercises.append({
                    "id": i + 1,
                    "sentence": sentence,
                    "answer": answer,
                    "hint": "Complete the sentence"
                })

        elif exercise_type == "rewrite":
            exercises = [
                {
                    "id": 1,
                    "original": "He goes to school.",
                    "instruction": "Rewrite in past tense",
                    "answer": "He went to school."
                },
                {
                    "id": 2,
                    "original": "She is reading a book.",
                    "instruction": "Rewrite in simple present",
                    "answer": "She reads a book."
                }
            ]

        elif exercise_type == "word_order":
            exercises = [
                {
                    "id": 1,
                    "jumbled": ["work", "I", "every", "to", "go", "day"],
                    "answer": "I go to work every day"
                },
                {
                    "id": 2,
                    "jumbled": ["is", "She", "English", "studying"],
                    "answer": "She is studying English"
                }
            ]

        elif exercise_type == "error_correction":
            exercises = [
                {
                    "id": 1,
                    "sentence": "She go to work every day.",
                    "error": "go",
                    "correction": "goes",
                    "explanation": "Third person singular requires 's'"
                }
            ]

        elif exercise_type == "translation":
            exercises = [
                {
                    "id": 1,
                    "vietnamese": "Tôi đi làm mỗi ngày.",
                    "english": "I go to work every day.",
                    "key_words": ["work", "every day"]
                }
            ]

        return exercises

    def submit_exercises(
        self,
        exercise_id: int,
        answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Submit exercise answers and get feedback.

        Args:
            exercise_id: ID of the exercise set
            answers: List of {exercise_id, answer}

        Returns:
            Results with feedback
        """
        exercise = self.db.query(Exercise).filter(Exercise.id == exercise_id).first()

        if not exercise:
            return {"success": False, "message": "Exercise not found"}

        exercises = exercise.content.get("exercises", [])
        exercise_type = exercise.exercise_type

        feedback = []
        correct_count = 0

        for answer in answers:
            ex_id = answer.get("exercise_id")
            user_answer = answer.get("answer", "").strip().lower()

            # Find matching exercise
            ex = None
            for e in exercises:
                if e.get("id") == ex_id:
                    ex = e
                    break

            if not ex:
                continue

            # Check answer based on type
            if exercise_type == "fill_blank":
                correct = ex.get("answer", "").lower()
                is_correct = user_answer == correct

            elif exercise_type == "rewrite":
                correct = ex.get("answer", "").lower()
                # More lenient matching for rewrite
                is_correct = self._check_rewrite_answer(user_answer, correct)

            elif exercise_type == "word_order":
                correct = ex.get("answer", "").lower()
                is_correct = user_answer == correct

            elif exercise_type == "error_correction":
                correct = ex.get("correction", "").lower()
                is_correct = correct in user_answer

            elif exercise_type == "translation":
                correct = ex.get("english", "").lower()
                # Check key words
                key_words = [w.lower() for w in ex.get("key_words", [])]
                is_correct = all(kw in user_answer for kw in key_words)

            else:
                is_correct = False
                correct = "Unknown"

            if is_correct:
                correct_count += 1

            feedback.append({
                "exercise_id": ex_id,
                "is_correct": is_correct,
                "user_answer": answer.get("answer"),
                "correct_answer": ex.get("answer") or ex.get("english") or ex.get("correction"),
                "explanation": ex.get("explanation") or ex.get("hint", "")
            })

        # Calculate score
        total = len(exercises)
        score = (correct_count / total * 100) if total > 0 else 0

        # Save attempt
        attempt = ExerciseAttempt(
            exercise_id=exercise_id,
            answers=answers,
            score=score,
            feedback=feedback
        )
        self.db.add(attempt)
        self.db.commit()

        return {
            "success": True,
            "exercise_id": exercise_id,
            "score": round(score, 1),
            "correct_count": correct_count,
            "total": total,
            "feedback": feedback
        }

    def _check_rewrite_answer(self, user_answer: str, correct: str) -> bool:
        """Check rewrite answer with some flexibility."""
        # Exact match
        if user_answer == correct:
            return True

        # Remove punctuation and compare
        import re
        clean_user = re.sub(r'[^\w\s]', '', user_answer)
        clean_correct = re.sub(r'[^\w\s]', '', correct)

        return clean_user == clean_correct

    def get_exercise_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get exercise history with scores."""
        attempts = (
            self.db.query(ExerciseAttempt)
            .join(Exercise)
            .order_by(ExerciseAttempt.completed_at.desc())
            .limit(limit)
            .all()
        )

        results = []
        for attempt in attempts:
            results.append({
                "id": attempt.id,
                "exercise_id": attempt.exercise_id,
                "exercise_type": attempt.exercise.exercise_type,
                "topic": attempt.exercise.topic,
                "level": attempt.exercise.level,
                "score": attempt.score,
                "completed_at": attempt.completed_at.isoformat()
            })

        return results


def get_exercise_service(db: Session) -> ExerciseService:
    """Factory function to create ExerciseService."""
    return ExerciseService(db)
