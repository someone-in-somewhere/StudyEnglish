"""
SQLAlchemy database models for the StudyEnglish application.
Comprehensive models for vocabulary, quizzes, translations, and all learning features.
"""

from datetime import datetime, date
from typing import Optional
import json

from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, Date,
    ForeignKey, JSON, Index, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Vocabulary(Base):
    """Vocabulary words with translations and examples."""
    __tablename__ = "vocabulary"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), nullable=False, index=True)
    meaning_vi = Column(Text, nullable=False)
    pronunciation = Column(String(100))  # IPA format
    part_of_speech = Column(String(50))  # noun, verb, adjective, adverb
    level = Column(String(10), nullable=False, index=True)  # A1-C2
    topic = Column(String(100), nullable=False, index=True)
    topic_id = Column(Integer, index=True)
    example_en = Column(Text)
    example_vi = Column(Text)
    synonyms = Column(Text)  # JSON array of synonyms
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user_progress = relationship("UserVocabulary", back_populates="vocabulary", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="vocabulary", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_vocabulary_word_level", "word", "level"),
        Index("ix_vocabulary_topic_level", "topic", "level"),
    )

    def to_dict(self):
        """Convert to dictionary."""
        # Parse synonyms safely
        synonyms = []
        if self.synonyms:
            try:
                synonyms = json.loads(self.synonyms)
                if not isinstance(synonyms, list):
                    synonyms = []
            except (json.JSONDecodeError, TypeError):
                synonyms = []

        return {
            "id": self.id,
            "word": self.word or "",
            "meaning_vi": self.meaning_vi or "",
            "pronunciation": self.pronunciation or "",
            "part_of_speech": self.part_of_speech or "noun",
            "level": self.level or "B1",
            "topic": self.topic or "",
            "topic_id": self.topic_id,
            "example_en": self.example_en or "",
            "example_vi": self.example_vi or "",
            "synonyms": synonyms,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class UserVocabulary(Base):
    """User's vocabulary learning progress with SRS data."""
    __tablename__ = "user_vocabulary"

    id = Column(Integer, primary_key=True, index=True)
    vocabulary_id = Column(Integer, ForeignKey("vocabulary.id", ondelete="CASCADE"), nullable=False)
    learned_at = Column(DateTime, default=func.now())
    last_reviewed = Column(DateTime)
    next_review = Column(DateTime, index=True)
    review_count = Column(Integer, default=0)
    ease_factor = Column(Float, default=2.5)  # SM-2 algorithm
    interval = Column(Integer, default=1)  # Days until next review
    mastery_level = Column(Integer, default=1)  # 1-5 scale
    times_correct = Column(Integer, default=0)
    times_incorrect = Column(Integer, default=0)
    is_favorite = Column(Boolean, default=False)

    # Relationships
    vocabulary = relationship("Vocabulary", back_populates="user_progress")

    __table_args__ = (
        Index("ix_user_vocab_next_review", "next_review"),
    )

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "vocabulary_id": self.vocabulary_id,
            "learned_at": self.learned_at.isoformat() if self.learned_at else None,
            "last_reviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "next_review": self.next_review.isoformat() if self.next_review else None,
            "review_count": self.review_count,
            "ease_factor": self.ease_factor,
            "interval": self.interval,
            "mastery_level": self.mastery_level,
            "times_correct": self.times_correct,
            "times_incorrect": self.times_incorrect,
            "is_favorite": self.is_favorite
        }


class Quiz(Base):
    """Quiz sessions and results."""
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    quiz_type = Column(String(50), nullable=False)  # multiple_choice, fill_blank, matching
    topic = Column(String(100), index=True)
    topic_id = Column(Integer)
    level = Column(String(10), index=True)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, default=0)
    score = Column(Float, default=0.0)
    time_taken = Column(Integer)  # seconds
    questions_data = Column(JSON)  # Full quiz data
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)

    # Relationships
    errors = relationship("QuizError", back_populates="quiz", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "quiz_type": self.quiz_type,
            "topic": self.topic,
            "topic_id": self.topic_id,
            "level": self.level,
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "score": self.score,
            "time_taken": self.time_taken,
            "questions_data": self.questions_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class QuizError(Base):
    """Individual quiz errors for analysis."""
    __tablename__ = "quiz_errors"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    user_answer = Column(Text)
    correct_answer = Column(Text, nullable=False)
    error_type = Column(String(50))  # vocabulary, grammar, spelling
    error_category = Column(String(50))  # article, preposition, tense, word_choice
    vocabulary_id = Column(Integer, ForeignKey("vocabulary.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    quiz = relationship("Quiz", back_populates="errors")


class Translation(Base):
    """Translation history."""
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    source_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    source_lang = Column(String(10), nullable=False)  # en, vi
    target_lang = Column(String(10), nullable=False)
    level = Column(String(10))  # Optional level adjustment
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source_text": self.source_text,
            "translated_text": self.translated_text,
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "level": self.level,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class UserSettings(Base):
    """User preferences and statistics."""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    target_level = Column(String(10), default="B1")
    daily_goal = Column(Integer, default=10)  # Words per day
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_study_time = Column(Integer, default=0)  # Minutes
    last_study_date = Column(Date)
    theme = Column(String(20), default="light")
    notifications_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "target_level": self.target_level,
            "daily_goal": self.daily_goal,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "total_study_time": self.total_study_time,
            "last_study_date": self.last_study_date.isoformat() if self.last_study_date else None,
            "theme": self.theme,
            "notifications_enabled": self.notifications_enabled
        }


class ChatHistory(Base):
    """AI chatbot conversation history."""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant
    message = Column(Text, nullable=False)
    has_errors = Column(Boolean, default=False)
    corrections = Column(JSON)  # Grammar corrections if any
    timestamp = Column(DateTime, default=func.now())

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "message": self.message,
            "has_errors": self.has_errors,
            "corrections": self.corrections,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class ReadingPassage(Base):
    """AI-generated reading passages."""
    __tablename__ = "reading_passages"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    topic = Column(String(100), nullable=False, index=True)
    topic_id = Column(Integer)
    level = Column(String(10), nullable=False, index=True)
    content = Column(Text, nullable=False)
    word_count = Column(Integer)
    questions = Column(JSON)  # Comprehension questions
    created_at = Column(DateTime, default=func.now())

    # Relationships
    attempts = relationship("ReadingAttempt", back_populates="passage", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "topic": self.topic,
            "topic_id": self.topic_id,
            "level": self.level,
            "content": self.content,
            "word_count": self.word_count,
            "questions": self.questions,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ReadingAttempt(Base):
    """User's reading comprehension attempts."""
    __tablename__ = "reading_attempts"

    id = Column(Integer, primary_key=True, index=True)
    passage_id = Column(Integer, ForeignKey("reading_passages.id", ondelete="CASCADE"), nullable=False)
    time_taken = Column(Integer)  # seconds
    wpm = Column(Integer)  # Words per minute
    comprehension_score = Column(Float)
    answers = Column(JSON)
    completed_at = Column(DateTime, default=func.now())

    # Relationships
    passage = relationship("ReadingPassage", back_populates="attempts")


class WritingSubmission(Base):
    """User writing submissions with AI feedback."""
    __tablename__ = "writing_submissions"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    prompt_topic = Column(String(100))
    prompt_level = Column(String(10))
    user_text = Column(Text, nullable=False)
    corrected_text = Column(Text)
    grammar_score = Column(Float)
    vocabulary_score = Column(Float)
    coherence_score = Column(Float)
    overall_score = Column(Float)
    errors = Column(JSON)  # List of errors found
    suggestions = Column(JSON)  # Improvement suggestions
    word_count = Column(Integer)
    submitted_at = Column(DateTime, default=func.now())

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "prompt_topic": self.prompt_topic,
            "prompt_level": self.prompt_level,
            "user_text": self.user_text,
            "corrected_text": self.corrected_text,
            "grammar_score": self.grammar_score,
            "vocabulary_score": self.vocabulary_score,
            "coherence_score": self.coherence_score,
            "overall_score": self.overall_score,
            "errors": self.errors,
            "suggestions": self.suggestions,
            "word_count": self.word_count,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None
        }


class Flashcard(Base):
    """Flashcard system with SRS integration."""
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    vocabulary_id = Column(Integer, ForeignKey("vocabulary.id", ondelete="SET NULL"))
    front = Column(Text, nullable=False)  # Question/word
    back = Column(Text, nullable=False)  # Answer/meaning
    last_reviewed = Column(DateTime)
    next_review = Column(DateTime, index=True)
    ease_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=1)
    review_count = Column(Integer, default=0)
    is_favorite = Column(Boolean, default=False)
    is_custom = Column(Boolean, default=False)  # User-created vs auto-generated
    created_at = Column(DateTime, default=func.now())

    # Relationships
    vocabulary = relationship("Vocabulary", back_populates="flashcards")

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "vocabulary_id": self.vocabulary_id,
            "front": self.front,
            "back": self.back,
            "last_reviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "next_review": self.next_review.isoformat() if self.next_review else None,
            "ease_factor": self.ease_factor,
            "interval": self.interval,
            "review_count": self.review_count,
            "is_favorite": self.is_favorite,
            "is_custom": self.is_custom,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ErrorPattern(Base):
    """Tracked error patterns for personalized learning."""
    __tablename__ = "error_patterns"

    id = Column(Integer, primary_key=True, index=True)
    error_type = Column(String(50), nullable=False, index=True)  # grammar, vocabulary, spelling
    error_category = Column(String(50), nullable=False, index=True)  # article, preposition, etc.
    count = Column(Integer, default=1)
    last_occurrence = Column(DateTime, default=func.now())
    examples = Column(JSON)  # Sample errors
    improvement_rate = Column(Float, default=0.0)

    __table_args__ = (
        Index("ix_error_type_category", "error_type", "error_category"),
    )

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "error_type": self.error_type,
            "error_category": self.error_category,
            "count": self.count,
            "last_occurrence": self.last_occurrence.isoformat() if self.last_occurrence else None,
            "examples": self.examples,
            "improvement_rate": self.improvement_rate
        }


class LearningPath(Base):
    """Predefined learning paths."""
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    level = Column(String(20))  # e.g., "B1-B2"
    estimated_days = Column(Integer)
    curriculum = Column(JSON)  # Structured curriculum data
    icon = Column(String(50))
    color = Column(String(20))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    enrollments = relationship("PathEnrollment", back_populates="path", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "estimated_days": self.estimated_days,
            "curriculum": self.curriculum,
            "icon": self.icon,
            "color": self.color,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class PathEnrollment(Base):
    """User enrollment in learning paths."""
    __tablename__ = "path_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime, default=func.now())
    current_day = Column(Integer, default=1)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    progress_data = Column(JSON)  # Detailed progress tracking

    # Relationships
    path = relationship("LearningPath", back_populates="enrollments")

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "path_id": self.path_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "current_day": self.current_day,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "progress_data": self.progress_data
        }


class Exercise(Base):
    """Generated exercises."""
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    exercise_type = Column(String(50), nullable=False)  # fill_blank, rewrite, translation, word_order, error_correction
    topic = Column(String(100), index=True)
    topic_id = Column(Integer)
    level = Column(String(10), index=True)
    content = Column(JSON, nullable=False)  # Exercise content and answers
    created_at = Column(DateTime, default=func.now())

    # Relationships
    attempts = relationship("ExerciseAttempt", back_populates="exercise", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "exercise_type": self.exercise_type,
            "topic": self.topic,
            "topic_id": self.topic_id,
            "level": self.level,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ExerciseAttempt(Base):
    """User exercise attempts."""
    __tablename__ = "exercise_attempts"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    answers = Column(JSON)
    score = Column(Float)
    feedback = Column(JSON)
    completed_at = Column(DateTime, default=func.now())

    # Relationships
    exercise = relationship("Exercise", back_populates="attempts")


class TranslationPractice(Base):
    """Translation practice history."""
    __tablename__ = "translation_practices"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(100), nullable=False)
    level = Column(String(10), nullable=False)
    direction = Column(String(20), nullable=False)  # vi_to_en, en_to_vi
    length = Column(String(20))  # short, medium, long
    complexity = Column(String(50))
    score = Column(Float, nullable=False)
    practiced_at = Column(DateTime, default=func.now(), index=True)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "topic": self.topic,
            "level": self.level,
            "direction": self.direction,
            "length": self.length,
            "complexity": self.complexity,
            "score": self.score,
            "date": self.practiced_at.isoformat() if self.practiced_at else None
        }


class ConversationPractice(Base):
    """Conversation practice history."""
    __tablename__ = "conversation_practices"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(100), nullable=False)
    level = Column(String(10), nullable=False)
    style = Column(String(50), nullable=False)  # casual, formal, roleplay, debate, interview
    length = Column(String(20))  # short, medium, long
    score = Column(Float, nullable=False)
    practiced_at = Column(DateTime, default=func.now(), index=True)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "topic": self.topic,
            "level": self.level,
            "style": self.style,
            "length": self.length,
            "score": self.score,
            "date": self.practiced_at.isoformat() if self.practiced_at else None
        }


class StudySession(Base):
    """Daily study session tracking."""
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True, unique=True)
    words_learned = Column(Integer, default=0)
    words_reviewed = Column(Integer, default=0)
    quizzes_completed = Column(Integer, default=0)
    quiz_avg_score = Column(Float)
    exercises_completed = Column(Integer, default=0)
    reading_passages = Column(Integer, default=0)
    writing_submissions = Column(Integer, default=0)
    chat_messages = Column(Integer, default=0)
    study_time = Column(Integer, default=0)  # Minutes
    activities = Column(JSON)  # Detailed activity log

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "words_learned": self.words_learned,
            "words_reviewed": self.words_reviewed,
            "quizzes_completed": self.quizzes_completed,
            "quiz_avg_score": self.quiz_avg_score,
            "exercises_completed": self.exercises_completed,
            "reading_passages": self.reading_passages,
            "writing_submissions": self.writing_submissions,
            "chat_messages": self.chat_messages,
            "study_time": self.study_time,
            "activities": self.activities
        }
