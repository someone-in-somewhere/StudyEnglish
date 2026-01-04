"""
Quiz Service - Generates and manages vocabulary quizzes.
Supports multiple choice, fill in the blank, and matching quiz types.
"""

import json
import logging
import random
from datetime import datetime
from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.db_models import Vocabulary, UserVocabulary, Quiz, QuizError
from app.services.ai_model_manager import ai_manager

logger = logging.getLogger(__name__)


class QuizService:
    """Service for quiz generation and management."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def generate_quiz(
        self,
        quiz_type: str,
        num_questions: int = 10,
        topic: Optional[str] = None,
        topic_id: Optional[int] = None,
        level: Optional[str] = None,
        use_learned_only: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a quiz from vocabulary.

        Args:
            quiz_type: Type of quiz (multiple_choice, fill_blank, matching)
            num_questions: Number of questions
            topic: Optional topic filter
            topic_id: Optional topic ID filter
            level: Optional CEFR level filter
            use_learned_only: Only use learned vocabulary

        Returns:
            Quiz data with questions
        """
        # Get vocabulary for quiz
        vocabulary = self._get_quiz_vocabulary(
            num_questions * 2,  # Get more than needed for options
            topic=topic,
            topic_id=topic_id,
            level=level,
            use_learned_only=use_learned_only
        )

        if len(vocabulary) < num_questions:
            # If not enough learned vocabulary, include unlearned
            vocabulary = self._get_quiz_vocabulary(
                num_questions * 2,
                topic=topic,
                topic_id=topic_id,
                level=level,
                use_learned_only=False
            )

        if len(vocabulary) < 4:
            return {
                "success": False,
                "message": "Not enough vocabulary for quiz. Learn more words first."
            }

        # Generate questions based on type
        if quiz_type == "multiple_choice":
            questions = self._generate_multiple_choice(vocabulary, num_questions)
        elif quiz_type == "fill_blank":
            questions = self._generate_fill_blank(vocabulary, num_questions)
        elif quiz_type == "matching":
            questions = self._generate_matching(vocabulary, num_questions)
        else:
            return {"success": False, "message": f"Unknown quiz type: {quiz_type}"}

        # Create quiz record
        quiz = Quiz(
            quiz_type=quiz_type,
            topic=topic,
            topic_id=topic_id,
            level=level,
            total_questions=len(questions),
            questions_data={"questions": questions}
        )

        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)

        return {
            "success": True,
            "quiz_id": quiz.id,
            "quiz_type": quiz_type,
            "questions": questions
        }

    def _get_quiz_vocabulary(
        self,
        limit: int,
        topic: Optional[str] = None,
        topic_id: Optional[int] = None,
        level: Optional[str] = None,
        use_learned_only: bool = True,
        prioritize_weak: bool = True
    ) -> List[Vocabulary]:
        """Get vocabulary for quiz generation.

        If prioritize_weak is True, prioritize words with:
        - Fewer review counts
        - Lower mastery level
        - Fewer times in quiz (times_correct + times_incorrect)
        """
        if use_learned_only:
            query = self.db.query(Vocabulary, UserVocabulary).join(
                UserVocabulary,
                UserVocabulary.vocabulary_id == Vocabulary.id
            )
        else:
            query = self.db.query(Vocabulary)

        if topic:
            query = query.filter(Vocabulary.topic == topic)
        if topic_id:
            query = query.filter(Vocabulary.topic_id == topic_id)
        if level:
            query = query.filter(Vocabulary.level == level)

        if use_learned_only and prioritize_weak:
            # Order by: mastery_level ASC, review_count ASC, (times_correct + times_incorrect) ASC
            # Then add some randomness
            query = query.order_by(
                UserVocabulary.mastery_level.asc(),
                UserVocabulary.review_count.asc(),
                (UserVocabulary.times_correct + UserVocabulary.times_incorrect).asc(),
                func.random()
            )
            results = query.limit(limit).all()
            # Extract just the Vocabulary objects
            vocabulary = [r[0] for r in results]
        else:
            # Randomize selection
            vocabulary = query.order_by(func.random()).limit(limit).all()

        return vocabulary

    def _generate_multiple_choice(
        self,
        vocabulary: List[Vocabulary],
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """Generate multiple choice questions."""
        questions = []
        selected = random.sample(vocabulary, min(num_questions, len(vocabulary)))

        for i, vocab in enumerate(selected):
            # Get wrong options
            other_vocab = [v for v in vocabulary if v.id != vocab.id]
            wrong_options = random.sample(
                other_vocab,
                min(3, len(other_vocab))
            )

            # Create options (word -> meaning)
            options = [vocab.meaning_vi] + [v.meaning_vi for v in wrong_options]
            random.shuffle(options)

            correct_index = options.index(vocab.meaning_vi)

            questions.append({
                "id": i + 1,
                "question": f"What is the meaning of '{vocab.word}'?",
                "word": vocab.word,
                "options": options,
                "correct_answer": correct_index,
                "vocabulary_id": vocab.id
            })

        return questions

    def _generate_fill_blank(
        self,
        vocabulary: List[Vocabulary],
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """Generate fill in the blank questions."""
        questions = []
        selected = random.sample(vocabulary, min(num_questions, len(vocabulary)))

        for i, vocab in enumerate(selected):
            if vocab.example_en:
                # Create blank in example sentence
                sentence = vocab.example_en
                # Replace the word with blank
                blank_sentence = sentence.replace(
                    vocab.word,
                    "_____",
                    1
                )

                # Also try with capitalized version
                if blank_sentence == sentence:
                    blank_sentence = sentence.replace(
                        vocab.word.capitalize(),
                        "_____",
                        1
                    )

                if blank_sentence != sentence:
                    questions.append({
                        "id": i + 1,
                        "question": f"Fill in the blank: {blank_sentence}",
                        "hint": vocab.meaning_vi,
                        "correct_answer": vocab.word.lower(),
                        "vocabulary_id": vocab.id,
                        "options": None  # User types the answer
                    })
                else:
                    # Fallback: use definition
                    questions.append({
                        "id": i + 1,
                        "question": f"What word means '{vocab.meaning_vi}'?",
                        "hint": f"Starts with '{vocab.word[0]}'",
                        "correct_answer": vocab.word.lower(),
                        "vocabulary_id": vocab.id,
                        "options": None
                    })
            else:
                # No example sentence
                questions.append({
                    "id": i + 1,
                    "question": f"What word means '{vocab.meaning_vi}'?",
                    "hint": f"Part of speech: {vocab.part_of_speech}",
                    "correct_answer": vocab.word.lower(),
                    "vocabulary_id": vocab.id,
                    "options": None
                })

        return questions

    def _generate_matching(
        self,
        vocabulary: List[Vocabulary],
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """Generate matching quiz (word to meaning pairs)."""
        selected = random.sample(vocabulary, min(num_questions, len(vocabulary)))

        # Create word-meaning pairs
        words = [{"id": i + 1, "word": v.word, "vocabulary_id": v.id} for i, v in enumerate(selected)]
        meanings = [{"id": i + 1, "meaning": v.meaning_vi, "vocabulary_id": v.id} for i, v in enumerate(selected)]

        # Shuffle meanings
        shuffled_meanings = meanings.copy()
        random.shuffle(shuffled_meanings)

        # Create correct answer mapping
        correct_mapping = {}
        for word in words:
            for j, meaning in enumerate(shuffled_meanings):
                if meaning["vocabulary_id"] == word["vocabulary_id"]:
                    correct_mapping[word["id"]] = j + 1
                    break

        return [{
            "id": 1,
            "type": "matching",
            "question": "Match each word with its correct meaning",
            "words": words,
            "meanings": [{"id": i + 1, "meaning": m["meaning"]} for i, m in enumerate(shuffled_meanings)],
            "correct_mapping": correct_mapping,
            "vocabulary_ids": [v.id for v in selected]
        }]

    def submit_quiz(
        self,
        quiz_id: int,
        answers: List[Dict[str, Any]],
        time_taken: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Submit quiz answers and calculate score.

        Args:
            quiz_id: ID of the quiz
            answers: List of {question_id, user_answer}
            time_taken: Time taken in seconds

        Returns:
            Quiz results with feedback
        """
        quiz = self.db.query(Quiz).filter(Quiz.id == quiz_id).first()

        if not quiz:
            return {"success": False, "message": "Quiz not found"}

        questions = quiz.questions_data.get("questions", [])
        feedback = []
        correct_count = 0

        for answer in answers:
            question_id = answer.get("question_id")
            user_answer = answer.get("user_answer")

            # Find the question
            question = None
            for q in questions:
                if q.get("id") == question_id:
                    question = q
                    break

            if not question:
                continue

            # Check answer based on quiz type
            if quiz.quiz_type == "multiple_choice":
                is_correct = user_answer == question.get("correct_answer")
                correct_answer_text = question["options"][question["correct_answer"]]
                user_answer_text = question["options"][user_answer] if isinstance(user_answer, int) and 0 <= user_answer < len(question["options"]) else str(user_answer)

            elif quiz.quiz_type == "fill_blank":
                correct_answer = question.get("correct_answer", "").lower().strip()
                user_answer_clean = str(user_answer).lower().strip()
                is_correct = user_answer_clean == correct_answer
                correct_answer_text = correct_answer
                user_answer_text = user_answer_clean

            elif quiz.quiz_type == "matching":
                # For matching, answer is a mapping {word_id: meaning_id}
                correct_mapping = question.get("correct_mapping", {})
                if isinstance(user_answer, dict):
                    # Check all mappings
                    all_correct = all(
                        user_answer.get(str(k)) == v
                        for k, v in correct_mapping.items()
                    )
                    is_correct = all_correct
                    correct_answer_text = json.dumps(correct_mapping)
                    user_answer_text = json.dumps(user_answer)
                else:
                    is_correct = False
                    correct_answer_text = json.dumps(correct_mapping)
                    user_answer_text = str(user_answer)

            else:
                is_correct = False
                correct_answer_text = "Unknown"
                user_answer_text = str(user_answer)

            if is_correct:
                correct_count += 1
                # Update user vocabulary - correct
                if question.get("vocabulary_id"):
                    self._update_vocabulary_stats(question["vocabulary_id"], True)
            else:
                # Record error
                if question.get("vocabulary_id"):
                    self._record_quiz_error(
                        quiz_id=quiz_id,
                        question=question.get("question", ""),
                        user_answer=user_answer_text,
                        correct_answer=correct_answer_text,
                        vocabulary_id=question.get("vocabulary_id")
                    )
                    self._update_vocabulary_stats(question["vocabulary_id"], False)

            feedback.append({
                "question_id": question_id,
                "is_correct": is_correct,
                "user_answer": user_answer_text,
                "correct_answer": correct_answer_text,
                "explanation": question.get("hint", "")
            })

        # Calculate score
        total = len(questions)
        if quiz.quiz_type == "matching" and questions:
            # For matching, count individual pairs
            total = len(questions[0].get("words", []))

        score = (correct_count / total * 100) if total > 0 else 0

        # Update quiz record
        quiz.correct_answers = correct_count
        quiz.score = score
        quiz.time_taken = time_taken
        quiz.completed_at = datetime.utcnow()

        self.db.commit()

        return {
            "success": True,
            "quiz_id": quiz_id,
            "score": round(score, 1),
            "correct_answers": correct_count,
            "total_questions": total,
            "feedback": feedback
        }

    def _update_vocabulary_stats(self, vocabulary_id: int, is_correct: bool):
        """Update user vocabulary statistics after quiz."""
        user_vocab = (
            self.db.query(UserVocabulary)
            .filter(UserVocabulary.vocabulary_id == vocabulary_id)
            .first()
        )

        if user_vocab:
            if is_correct:
                user_vocab.times_correct += 1
            else:
                user_vocab.times_incorrect += 1
            self.db.commit()

    def _record_quiz_error(
        self,
        quiz_id: int,
        question: str,
        user_answer: str,
        correct_answer: str,
        vocabulary_id: Optional[int] = None
    ):
        """Record a quiz error for analysis."""
        error = QuizError(
            quiz_id=quiz_id,
            question=question,
            user_answer=user_answer,
            correct_answer=correct_answer,
            error_type="vocabulary",
            error_category="word_choice",
            vocabulary_id=vocabulary_id
        )
        self.db.add(error)
        self.db.commit()

    def get_quiz_history(
        self,
        limit: int = 20,
        topic: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get quiz history."""
        query = self.db.query(Quiz).filter(Quiz.completed_at.isnot(None))

        if topic:
            query = query.filter(Quiz.topic == topic)

        quizzes = query.order_by(Quiz.completed_at.desc()).limit(limit).all()
        return [q.to_dict() for q in quizzes]

    def get_quiz_stats(self) -> Dict[str, Any]:
        """Get overall quiz statistics."""
        # Total quizzes
        total = self.db.query(func.count(Quiz.id)).filter(Quiz.completed_at.isnot(None)).scalar() or 0

        # Average score
        avg_score = self.db.query(func.avg(Quiz.score)).filter(Quiz.completed_at.isnot(None)).scalar() or 0

        # By quiz type
        type_stats = (
            self.db.query(
                Quiz.quiz_type,
                func.count(Quiz.id),
                func.avg(Quiz.score)
            )
            .filter(Quiz.completed_at.isnot(None))
            .group_by(Quiz.quiz_type)
            .all()
        )

        by_type = {
            t[0]: {"count": t[1], "avg_score": round(t[2] or 0, 1)}
            for t in type_stats
        }

        # Recent performance (last 10 quizzes)
        recent = (
            self.db.query(Quiz.score)
            .filter(Quiz.completed_at.isnot(None))
            .order_by(Quiz.completed_at.desc())
            .limit(10)
            .all()
        )
        recent_scores = [q.score for q in recent if q.score is not None]

        return {
            "total_quizzes": total,
            "average_score": round(avg_score, 1),
            "by_type": by_type,
            "recent_scores": recent_scores
        }

    def delete_quiz(self, quiz_id: int) -> bool:
        """Delete a quiz."""
        try:
            quiz = self.db.query(Quiz).filter(Quiz.id == quiz_id).first()
            if quiz:
                self.db.delete(quiz)
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete quiz: {e}")
            self.db.rollback()
            return False


def get_quiz_service(db: Session) -> QuizService:
    """Factory function to create QuizService."""
    return QuizService(db)
