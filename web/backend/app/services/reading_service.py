"""
Reading Service - AI-generated reading comprehension passages.
Generates passages with comprehension questions and tracks performance.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.db_models import ReadingPassage, ReadingAttempt
from app.services.ai_model_manager import ai_manager

logger = logging.getLogger(__name__)


class ReadingService:
    """Service for reading comprehension exercises."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def generate_passage(
        self,
        topic: str,
        level: str = "B1",
        length: int = 300,
        topic_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a reading passage with comprehension questions.

        Args:
            topic: Topic for the passage
            level: CEFR level
            length: Approximate word count
            topic_id: Optional topic ID

        Returns:
            Passage with questions
        """
        prompt = self._build_reading_prompt(topic, level, length)

        try:
            response = ai_manager.generate_text(
                prompt,
                max_tokens=2048,
                temperature=0.7
            )

            passage_data = self._parse_reading_response(response)

            if not passage_data:
                passage_data = self._get_fallback_passage(topic, level)

            # Count actual words
            word_count = len(passage_data.get("passage", "").split())

            # Save to database
            passage = ReadingPassage(
                title=passage_data.get("title", f"Reading: {topic}"),
                topic=topic,
                topic_id=topic_id,
                level=level,
                content=passage_data.get("passage", ""),
                word_count=word_count,
                questions=passage_data.get("questions", [])
            )

            self.db.add(passage)
            self.db.commit()
            self.db.refresh(passage)

            return {
                "success": True,
                "passage_id": passage.id,
                "title": passage.title,
                "content": passage.content,
                "word_count": word_count,
                "level": level,
                "questions": [
                    {
                        "id": i + 1,
                        "question": q["question"],
                        "options": q["options"]
                    }
                    for i, q in enumerate(passage_data.get("questions", []))
                ]
            }

        except Exception as e:
            logger.error(f"Passage generation failed: {e}")
            # Use fallback
            passage_data = self._get_fallback_passage(topic, level)

            passage = ReadingPassage(
                title=passage_data["title"],
                topic=topic,
                topic_id=topic_id,
                level=level,
                content=passage_data["passage"],
                word_count=len(passage_data["passage"].split()),
                questions=passage_data["questions"]
            )

            self.db.add(passage)
            self.db.commit()
            self.db.refresh(passage)

            return {
                "success": True,
                "passage_id": passage.id,
                "title": passage.title,
                "content": passage.content,
                "word_count": passage.word_count,
                "level": level,
                "questions": [
                    {"id": i + 1, "question": q["question"], "options": q["options"]}
                    for i, q in enumerate(passage_data["questions"])
                ]
            }

    def _build_reading_prompt(self, topic: str, level: str, length: int) -> str:
        """Build prompt for reading passage generation."""
        level_guidance = {
            "A1": "Use very simple vocabulary and short sentences. Focus on concrete, everyday topics.",
            "A2": "Use simple vocabulary and basic sentence structures. Include some common expressions.",
            "B1": "Use clear, standard language. Include some compound sentences and common idioms.",
            "B2": "Use more sophisticated vocabulary and complex sentence structures.",
            "C1": "Use advanced vocabulary and varied sentence structures. Include nuanced ideas.",
            "C2": "Use sophisticated, native-like language with idiomatic expressions."
        }

        guidance = level_guidance.get(level, level_guidance["B1"])

        return f"""Generate a reading passage about "{topic}" for English learners at {level} level.

Requirements:
- Length: approximately {length} words
- {guidance}
- Include an engaging title
- Create 5 comprehension questions with 4 multiple choice options each

Return as JSON:
{{
    "title": "Passage Title",
    "passage": "The full passage text...",
    "questions": [
        {{
            "question": "Question text?",
            "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
            "answer": 0
        }}
    ]
}}

JSON output:
{{"""

    def _parse_reading_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse AI response into passage data."""
        try:
            # Add opening brace if needed
            if not response.strip().startswith("{"):
                response = "{" + response

            # Find complete JSON
            brace_count = 0
            end_pos = 0
            for i, char in enumerate(response):
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break

            if end_pos > 0:
                json_str = response[:end_pos]
            else:
                json_str = response + "}"

            # Clean up
            json_str = json_str.replace(",}", "}").replace(",]", "]")

            data = json.loads(json_str)

            # Validate required fields
            if "passage" in data and "questions" in data:
                return data

            return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse reading response: {e}")
            return None

    def _get_fallback_passage(self, topic: str, level: str) -> Dict[str, Any]:
        """Get fallback reading passage."""
        return {
            "title": f"Learning About {topic}",
            "passage": f"""Learning English is an important skill in today's world. Many people around the world speak English as a second language. It is used in business, education, and travel.

There are many ways to learn English. You can take classes, use apps, or practice with native speakers. Reading books and watching movies in English can also help.

The most important thing is to practice regularly. Even 15 minutes a day can make a big difference. Don't be afraid to make mistakes - they are part of learning.

With patience and practice, anyone can improve their English skills. The key is to stay motivated and enjoy the learning process.""",
            "questions": [
                {
                    "question": "According to the passage, why is learning English important?",
                    "options": [
                        "A. It is used in business, education, and travel",
                        "B. It is the only language in the world",
                        "C. It is easy to learn",
                        "D. It is required by law"
                    ],
                    "answer": 0
                },
                {
                    "question": "What is one way to learn English mentioned in the passage?",
                    "options": [
                        "A. Only reading textbooks",
                        "B. Taking classes or using apps",
                        "C. Only speaking with teachers",
                        "D. Memorizing the dictionary"
                    ],
                    "answer": 1
                },
                {
                    "question": "How much daily practice is suggested as helpful?",
                    "options": [
                        "A. 5 minutes",
                        "B. 15 minutes",
                        "C. 2 hours",
                        "D. 30 minutes"
                    ],
                    "answer": 1
                },
                {
                    "question": "What does the passage say about making mistakes?",
                    "options": [
                        "A. They should be avoided at all costs",
                        "B. They are part of learning",
                        "C. They mean you should stop",
                        "D. They are not mentioned"
                    ],
                    "answer": 1
                },
                {
                    "question": "What is the key to improving English skills?",
                    "options": [
                        "A. Being perfect from the start",
                        "B. Only studying grammar",
                        "C. Staying motivated and enjoying learning",
                        "D. Avoiding practice"
                    ],
                    "answer": 2
                }
            ]
        }

    def submit_reading(
        self,
        passage_id: int,
        answers: List[int],
        time_taken: int
    ) -> Dict[str, Any]:
        """
        Submit reading comprehension answers.

        Args:
            passage_id: ID of the reading passage
            answers: List of answer indices (0-3)
            time_taken: Time taken in seconds

        Returns:
            Results with score and WPM
        """
        passage = self.db.query(ReadingPassage).filter(ReadingPassage.id == passage_id).first()

        if not passage:
            return {"success": False, "message": "Passage not found"}

        questions = passage.questions or []

        # Calculate score
        correct_count = 0
        feedback = []

        for i, user_answer in enumerate(answers):
            if i >= len(questions):
                break

            question = questions[i]
            correct_answer = question.get("answer", 0)
            is_correct = user_answer == correct_answer

            if is_correct:
                correct_count += 1

            feedback.append({
                "question_id": i + 1,
                "is_correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "options": question.get("options", [])
            })

        total_questions = len(questions)
        score = (correct_count / total_questions * 100) if total_questions > 0 else 0

        # Calculate WPM
        word_count = passage.word_count or len(passage.content.split())
        minutes = time_taken / 60 if time_taken > 0 else 1
        wpm = int(word_count / minutes)

        # Save attempt
        attempt = ReadingAttempt(
            passage_id=passage_id,
            time_taken=time_taken,
            wpm=wpm,
            comprehension_score=score,
            answers=answers
        )
        self.db.add(attempt)
        self.db.commit()

        return {
            "success": True,
            "passage_id": passage_id,
            "score": round(score, 1),
            "correct_count": correct_count,
            "total_questions": total_questions,
            "wpm": wpm,
            "time_taken": time_taken,
            "feedback": feedback
        }

    def get_passage(self, passage_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific reading passage."""
        passage = self.db.query(ReadingPassage).filter(ReadingPassage.id == passage_id).first()

        if not passage:
            return None

        return {
            "id": passage.id,
            "title": passage.title,
            "topic": passage.topic,
            "level": passage.level,
            "content": passage.content,
            "word_count": passage.word_count,
            "questions": [
                {"id": i + 1, "question": q["question"], "options": q["options"]}
                for i, q in enumerate(passage.questions or [])
            ],
            "created_at": passage.created_at.isoformat() if passage.created_at else None
        }

    def get_passages(
        self,
        topic: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get list of reading passages."""
        query = self.db.query(ReadingPassage)

        if topic:
            query = query.filter(ReadingPassage.topic == topic)
        if level:
            query = query.filter(ReadingPassage.level == level)

        passages = query.order_by(desc(ReadingPassage.created_at)).limit(limit).all()

        return [p.to_dict() for p in passages]

    def get_reading_stats(self) -> Dict[str, Any]:
        """Get reading statistics."""
        from sqlalchemy import func

        total_passages = self.db.query(func.count(ReadingPassage.id)).scalar() or 0
        total_attempts = self.db.query(func.count(ReadingAttempt.id)).scalar() or 0

        avg_score = self.db.query(func.avg(ReadingAttempt.comprehension_score)).scalar() or 0
        avg_wpm = self.db.query(func.avg(ReadingAttempt.wpm)).scalar() or 0

        return {
            "total_passages": total_passages,
            "total_attempts": total_attempts,
            "average_score": round(avg_score, 1),
            "average_wpm": int(avg_wpm)
        }


def get_reading_service(db: Session) -> ReadingService:
    """Factory function to create ReadingService."""
    return ReadingService(db)
