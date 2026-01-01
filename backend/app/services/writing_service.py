"""
Writing Service - Essay writing practice with AI-powered feedback.
Provides grammar correction, vocabulary analysis, coherence scoring, and suggestions.
"""

import logging
import re
from datetime import datetime
from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.db_models import WritingSubmission
from app.services.ai_model_manager import ai_manager

logger = logging.getLogger(__name__)


class WritingService:
    """Service for writing practice and AI-powered correction."""

    # Writing prompts by topic and level
    PROMPTS = {
        "A1": [
            {"prompt": "Write about your family.", "word_limit": 50},
            {"prompt": "Describe your daily routine.", "word_limit": 50},
            {"prompt": "Write about your favorite food.", "word_limit": 50},
        ],
        "A2": [
            {"prompt": "Describe your hometown.", "word_limit": 100},
            {"prompt": "Write about a typical weekend.", "word_limit": 100},
            {"prompt": "Describe your best friend.", "word_limit": 100},
        ],
        "B1": [
            {"prompt": "Write about the advantages and disadvantages of social media.", "word_limit": 150},
            {"prompt": "Describe an important experience in your life.", "word_limit": 150},
            {"prompt": "Write about your career goals.", "word_limit": 150},
        ],
        "B2": [
            {"prompt": "Discuss the impact of technology on education.", "word_limit": 250},
            {"prompt": "Write about environmental protection in your country.", "word_limit": 250},
            {"prompt": "Analyze the pros and cons of working from home.", "word_limit": 250},
        ],
        "C1": [
            {"prompt": "Evaluate the role of artificial intelligence in modern society.", "word_limit": 350},
            {"prompt": "Discuss the challenges facing global healthcare systems.", "word_limit": 350},
            {"prompt": "Analyze the relationship between economic growth and environmental sustainability.", "word_limit": 350},
        ],
        "C2": [
            {"prompt": "Critically examine the concept of cultural identity in a globalized world.", "word_limit": 400},
            {"prompt": "Discuss the philosophical implications of technological advancement.", "word_limit": 400},
            {"prompt": "Analyze the interplay between individual freedom and social responsibility.", "word_limit": 400},
        ],
    }

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def get_prompts(
        self,
        level: str = "B1",
        topic: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get writing prompts for a level.

        Args:
            level: CEFR level
            topic: Optional topic filter

        Returns:
            List of prompts
        """
        prompts = self.PROMPTS.get(level, self.PROMPTS["B1"])

        result = []
        for i, p in enumerate(prompts):
            result.append({
                "id": i + 1,
                "prompt": p["prompt"],
                "level": level,
                "topic": topic or "General",
                "word_limit": p.get("word_limit")
            })

        return result

    def submit_writing(
        self,
        prompt: str,
        user_text: str,
        topic: Optional[str] = None,
        level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit writing for analysis and scoring.

        Args:
            prompt: The writing prompt
            user_text: User's written text
            topic: Optional topic
            level: Optional CEFR level

        Returns:
            Detailed feedback and scores
        """
        word_count = len(user_text.split())

        if word_count < 20:
            return {
                "success": False,
                "message": "Please write at least 20 words for meaningful feedback."
            }

        # 1. Grammar correction
        grammar_result = ai_manager.correct_grammar(user_text)
        corrected_text = grammar_result["corrected"]
        grammar_errors = grammar_result["corrections"]

        # 2. Calculate scores
        grammar_score = self._calculate_grammar_score(grammar_errors, word_count)
        vocabulary_score = self._calculate_vocabulary_score(user_text, level)
        coherence_score = self._calculate_coherence_score(user_text)

        # 3. Calculate overall score (IELTS-style 0-9)
        overall_score = self._calculate_overall_score(
            grammar_score,
            vocabulary_score,
            coherence_score
        )

        # 4. Generate suggestions
        suggestions = self._generate_suggestions(
            user_text,
            grammar_errors,
            grammar_score,
            vocabulary_score,
            coherence_score
        )

        # 5. Format errors for response
        formatted_errors = []
        for error in grammar_errors:
            formatted_errors.append({
                "original": error.get("original", ""),
                "corrected": error.get("corrected", ""),
                "error_type": error.get("error_type", "grammar"),
                "explanation": error.get("explanation", "")
            })

        # Save submission
        submission = WritingSubmission(
            prompt=prompt,
            prompt_topic=topic,
            prompt_level=level,
            user_text=user_text,
            corrected_text=corrected_text,
            grammar_score=grammar_score,
            vocabulary_score=vocabulary_score,
            coherence_score=coherence_score,
            overall_score=overall_score,
            errors=formatted_errors,
            suggestions=suggestions,
            word_count=word_count
        )

        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)

        return {
            "success": True,
            "submission_id": submission.id,
            "corrected_text": corrected_text,
            "scores": {
                "grammar": round(grammar_score, 1),
                "vocabulary": round(vocabulary_score, 1),
                "coherence": round(coherence_score, 1),
                "overall": round(overall_score, 1)
            },
            "errors": formatted_errors,
            "suggestions": suggestions,
            "word_count": word_count
        }

    def _calculate_grammar_score(
        self,
        errors: List[Dict],
        word_count: int
    ) -> float:
        """Calculate grammar score (0-9)."""
        if word_count == 0:
            return 5.0

        error_count = len(errors)
        error_rate = error_count / word_count

        # Score mapping based on error rate
        if error_rate == 0:
            return 9.0
        elif error_rate < 0.02:
            return 8.0
        elif error_rate < 0.05:
            return 7.0
        elif error_rate < 0.08:
            return 6.0
        elif error_rate < 0.12:
            return 5.0
        elif error_rate < 0.16:
            return 4.0
        elif error_rate < 0.20:
            return 3.0
        else:
            return 2.0

    def _calculate_vocabulary_score(
        self,
        text: str,
        level: Optional[str] = None
    ) -> float:
        """Calculate vocabulary score based on diversity and appropriateness."""
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = len(words)

        if word_count == 0:
            return 5.0

        # Unique words ratio (Type-Token Ratio)
        unique_words = set(words)
        ttr = len(unique_words) / word_count

        # Average word length (indicator of complexity)
        avg_word_length = sum(len(w) for w in words) / word_count

        # Calculate base score
        if ttr > 0.7 and avg_word_length > 5.5:
            base_score = 8.0
        elif ttr > 0.6 and avg_word_length > 5.0:
            base_score = 7.0
        elif ttr > 0.5 and avg_word_length > 4.5:
            base_score = 6.0
        elif ttr > 0.4:
            base_score = 5.0
        else:
            base_score = 4.0

        return base_score

    def _calculate_coherence_score(self, text: str) -> float:
        """Calculate coherence score using sentence analysis."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 5.0

        # Check for coherence markers
        coherence_markers = [
            "however", "therefore", "furthermore", "moreover",
            "in addition", "on the other hand", "for example",
            "firstly", "secondly", "finally", "in conclusion",
            "as a result", "consequently", "although", "because",
            "since", "while", "whereas"
        ]

        text_lower = text.lower()
        marker_count = sum(1 for marker in coherence_markers if marker in text_lower)

        # Calculate sentence similarity for flow (simplified)
        try:
            similarities = []
            for i in range(len(sentences) - 1):
                sim = ai_manager.compute_similarity(sentences[i], sentences[i + 1])
                similarities.append(sim)

            avg_similarity = sum(similarities) / len(similarities) if similarities else 0.5
        except:
            avg_similarity = 0.5

        # Score based on markers and flow
        marker_score = min(2.0, marker_count * 0.3)
        flow_score = avg_similarity * 3

        base_score = 4.0 + marker_score + flow_score

        return min(9.0, base_score)

    def _calculate_overall_score(
        self,
        grammar: float,
        vocabulary: float,
        coherence: float
    ) -> float:
        """Calculate weighted overall score."""
        # IELTS-style weighting
        overall = (grammar * 0.35 + vocabulary * 0.30 + coherence * 0.35)
        return round(overall, 1)

    def _generate_suggestions(
        self,
        text: str,
        errors: List[Dict],
        grammar_score: float,
        vocabulary_score: float,
        coherence_score: float
    ) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []

        # Grammar suggestions
        if grammar_score < 6:
            suggestions.append("Focus on basic grammar rules, especially verb tenses and subject-verb agreement.")
            if any("article" in str(e).lower() for e in errors):
                suggestions.append("Pay attention to article usage (a, an, the).")
            if any("preposition" in str(e).lower() for e in errors):
                suggestions.append("Review common preposition patterns.")

        # Vocabulary suggestions
        if vocabulary_score < 6:
            suggestions.append("Try to use more varied vocabulary. Avoid repeating the same words.")
            suggestions.append("Learn synonyms for common words you use frequently.")
        elif vocabulary_score < 7:
            suggestions.append("Consider using more advanced vocabulary appropriate to your level.")

        # Coherence suggestions
        if coherence_score < 6:
            suggestions.append("Use more linking words (however, therefore, furthermore) to connect your ideas.")
            suggestions.append("Make sure each paragraph has a clear main idea.")
        elif coherence_score < 7:
            suggestions.append("Try to improve the flow between sentences and paragraphs.")

        # General positive feedback
        if grammar_score >= 7 and vocabulary_score >= 7 and coherence_score >= 7:
            suggestions.append("Good work! Keep practicing to maintain and improve your skills.")

        return suggestions

    def get_submission(self, submission_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific writing submission."""
        submission = (
            self.db.query(WritingSubmission)
            .filter(WritingSubmission.id == submission_id)
            .first()
        )

        return submission.to_dict() if submission else None

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get writing submission history."""
        submissions = (
            self.db.query(WritingSubmission)
            .order_by(desc(WritingSubmission.submitted_at))
            .limit(limit)
            .all()
        )

        return [s.to_dict() for s in submissions]

    def get_stats(self) -> Dict[str, Any]:
        """Get writing statistics."""
        total = self.db.query(func.count(WritingSubmission.id)).scalar() or 0

        avg_grammar = self.db.query(func.avg(WritingSubmission.grammar_score)).scalar() or 0
        avg_vocabulary = self.db.query(func.avg(WritingSubmission.vocabulary_score)).scalar() or 0
        avg_coherence = self.db.query(func.avg(WritingSubmission.coherence_score)).scalar() or 0
        avg_overall = self.db.query(func.avg(WritingSubmission.overall_score)).scalar() or 0

        avg_word_count = self.db.query(func.avg(WritingSubmission.word_count)).scalar() or 0

        return {
            "total_submissions": total,
            "average_scores": {
                "grammar": round(avg_grammar, 1),
                "vocabulary": round(avg_vocabulary, 1),
                "coherence": round(avg_coherence, 1),
                "overall": round(avg_overall, 1)
            },
            "average_word_count": int(avg_word_count)
        }


def get_writing_service(db: Session) -> WritingService:
    """Factory function to create WritingService."""
    return WritingService(db)
