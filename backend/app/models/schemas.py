"""
Pydantic schemas for request/response validation.
All API inputs and outputs are validated through these schemas.
"""

from datetime import datetime, date
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, validator


# ============== Base Schemas ==============

class BaseResponse(BaseModel):
    """Base response with success status."""
    success: bool = True
    message: Optional[str] = None


# ============== Vocabulary Schemas ==============

class VocabularyBase(BaseModel):
    """Base vocabulary schema."""
    word: str
    meaning_vi: str
    pronunciation: Optional[str] = None
    part_of_speech: Optional[str] = None
    level: str
    topic: str
    example_en: Optional[str] = None
    example_vi: Optional[str] = None
    synonyms: Optional[List[str]] = None


class VocabularyCreate(VocabularyBase):
    """Schema for creating vocabulary."""
    topic_id: Optional[int] = None


class VocabularyResponse(VocabularyBase):
    """Schema for vocabulary response."""
    id: int
    topic_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VocabularyGenerateRequest(BaseModel):
    """Request to generate vocabulary."""
    topic: str
    topic_id: Optional[int] = None
    level: str = Field(..., pattern="^(A1|A2|B1|B2|C1|C2)$")
    num_words: int = Field(default=10, ge=5, le=20)


class VocabularyGenerateResponse(BaseResponse):
    """Response with generated vocabulary."""
    vocabulary: List[VocabularyResponse] = []
    count: int = 0


class MarkLearnedRequest(BaseModel):
    """Request to mark vocabulary as learned."""
    vocabulary_id: int


class UserVocabularyResponse(BaseModel):
    """User vocabulary progress response."""
    id: int
    vocabulary_id: int
    vocabulary: Optional[VocabularyResponse] = None
    learned_at: Optional[datetime] = None
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    review_count: int = 0
    ease_factor: float = 2.5
    interval: int = 1
    mastery_level: int = 1
    times_correct: int = 0
    times_incorrect: int = 0
    is_favorite: bool = False

    class Config:
        from_attributes = True


# ============== Quiz Schemas ==============

class QuizQuestion(BaseModel):
    """Individual quiz question."""
    id: int
    question: str
    options: Optional[List[str]] = None  # For multiple choice
    correct_answer: str
    word: Optional[str] = None
    vocabulary_id: Optional[int] = None


class QuizGenerateRequest(BaseModel):
    """Request to generate quiz."""
    quiz_type: str = Field(..., pattern="^(multiple_choice|fill_blank|matching)$")
    topic: Optional[str] = None
    topic_id: Optional[int] = None
    level: Optional[str] = Field(None, pattern="^(A1|A2|B1|B2|C1|C2)$")
    num_questions: int = Field(default=10, ge=5, le=30)


class QuizGenerateResponse(BaseResponse):
    """Response with generated quiz."""
    quiz_id: int
    quiz_type: str
    questions: List[QuizQuestion] = []


class QuizAnswer(BaseModel):
    """Individual quiz answer."""
    question_id: int
    user_answer: str


class QuizSubmitRequest(BaseModel):
    """Request to submit quiz answers."""
    quiz_id: int
    answers: List[QuizAnswer]
    time_taken: Optional[int] = None  # seconds


class QuizFeedback(BaseModel):
    """Feedback for individual question."""
    question_id: int
    is_correct: bool
    user_answer: str
    correct_answer: str
    explanation: Optional[str] = None


class QuizSubmitResponse(BaseResponse):
    """Response after quiz submission."""
    quiz_id: int
    score: float
    correct_answers: int
    total_questions: int
    feedback: List[QuizFeedback] = []


# ============== Translation Schemas ==============

class TranslationRequest(BaseModel):
    """Request to translate text."""
    text: str = Field(..., min_length=1, max_length=5000)
    source_lang: str = Field(..., pattern="^(en|vi)$")
    target_lang: str = Field(..., pattern="^(en|vi)$")
    level: Optional[str] = Field(None, pattern="^(A1|A2|B1|B2|C1|C2)$")


class TranslationResponse(BaseResponse):
    """Translation response."""
    id: int
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    level: Optional[str] = None
    created_at: Optional[datetime] = None


class TranslationHistoryResponse(BaseResponse):
    """Translation history response."""
    translations: List[TranslationResponse] = []
    total: int = 0


# ============== Progress Schemas ==============

class ProgressStats(BaseModel):
    """User progress statistics."""
    total_words: int = 0
    words_by_level: Dict[str, int] = {}
    words_by_topic: Dict[str, int] = {}
    quiz_avg_score: float = 0.0
    quiz_count: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    total_study_time: int = 0  # minutes
    words_due_review: int = 0


class ProgressStatsResponse(BaseResponse):
    """Progress stats response."""
    stats: ProgressStats


class DailyProgress(BaseModel):
    """Daily progress data."""
    date: str
    words_learned: int = 0
    words_reviewed: int = 0
    quizzes_completed: int = 0
    study_time: int = 0


class ProgressTimelineResponse(BaseResponse):
    """Timeline response for charts."""
    timeline: List[DailyProgress] = []
    total_days: int = 0


# ============== SRS Schemas ==============

class SRSReviewRequest(BaseModel):
    """Request to submit SRS review."""
    vocabulary_id: int
    performance: int = Field(..., ge=1, le=4)  # 1=Again, 2=Hard, 3=Good, 4=Easy


class SRSReviewResponse(BaseResponse):
    """Response after SRS review."""
    vocabulary_id: int
    next_review: datetime
    interval: int
    ease_factor: float
    mastery_level: int


class DueReviewsResponse(BaseResponse):
    """Response with due reviews."""
    reviews: List[UserVocabularyResponse] = []
    count: int = 0


# ============== Exercise Schemas ==============

class ExerciseItem(BaseModel):
    """Individual exercise item."""
    id: int
    question: str
    answer: str
    options: Optional[List[str]] = None
    hint: Optional[str] = None


class ExerciseGenerateRequest(BaseModel):
    """Request to generate exercises."""
    exercise_type: str = Field(..., pattern="^(fill_blank|rewrite|translation|word_order|error_correction)$")
    topic: Optional[str] = None
    topic_id: Optional[int] = None
    level: str = Field(default="B1", pattern="^(A1|A2|B1|B2|C1|C2)$")
    words: Optional[List[str]] = None
    num_exercises: int = Field(default=10, ge=5, le=20)


class ExerciseGenerateResponse(BaseResponse):
    """Response with generated exercises."""
    exercise_id: int
    exercise_type: str
    exercises: List[ExerciseItem] = []


class ExerciseSubmitRequest(BaseModel):
    """Request to submit exercise answers."""
    exercise_id: int
    answers: List[Dict[str, Any]]


class ExerciseSubmitResponse(BaseResponse):
    """Response after exercise submission."""
    exercise_id: int
    score: float
    feedback: List[Dict[str, Any]] = []


# ============== Chat Schemas ==============

class ChatMessageRequest(BaseModel):
    """Request to send chat message."""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None


class GrammarCorrection(BaseModel):
    """Grammar correction detail."""
    original: str
    corrected: str
    explanation: str
    error_type: Optional[str] = None


class ChatMessageResponse(BaseResponse):
    """Response from chatbot."""
    session_id: str
    response: str
    corrections: List[GrammarCorrection] = []
    has_errors: bool = False


class ChatHistoryResponse(BaseResponse):
    """Chat history response."""
    session_id: str
    messages: List[Dict[str, Any]] = []


# ============== Reading Schemas ==============

class ReadingGenerateRequest(BaseModel):
    """Request to generate reading passage."""
    topic: str
    topic_id: Optional[int] = None
    level: str = Field(default="B1", pattern="^(A1|A2|B1|B2|C1|C2)$")
    length: int = Field(default=300, ge=100, le=1000)  # word count


class ReadingQuestion(BaseModel):
    """Reading comprehension question."""
    id: int
    question: str
    options: List[str]
    correct_answer: int  # Index of correct option


class ReadingGenerateResponse(BaseResponse):
    """Response with reading passage."""
    passage_id: int
    title: str
    content: str
    word_count: int
    questions: List[ReadingQuestion] = []


class ReadingSubmitRequest(BaseModel):
    """Request to submit reading answers."""
    passage_id: int
    answers: List[int]  # Indices of selected options
    time_taken: int  # seconds


class ReadingSubmitResponse(BaseResponse):
    """Response after reading submission."""
    passage_id: int
    score: float
    wpm: int
    feedback: List[Dict[str, Any]] = []


# ============== Writing Schemas ==============

class WritingPromptResponse(BaseModel):
    """Writing prompt."""
    id: int
    prompt: str
    topic: str
    level: str
    word_limit: Optional[int] = None


class WritingPromptsResponse(BaseResponse):
    """List of writing prompts."""
    prompts: List[WritingPromptResponse] = []


class WritingSubmitRequest(BaseModel):
    """Request to submit writing."""
    prompt: str
    user_text: str = Field(..., min_length=50, max_length=10000)
    topic: Optional[str] = None
    level: Optional[str] = None


class WritingError(BaseModel):
    """Writing error detail."""
    original: str
    corrected: str
    error_type: str
    position: Optional[int] = None
    explanation: Optional[str] = None


class WritingSubmitResponse(BaseResponse):
    """Response after writing submission."""
    submission_id: int
    corrected_text: str
    scores: Dict[str, float]  # grammar, vocabulary, coherence, overall
    errors: List[WritingError] = []
    suggestions: List[str] = []
    word_count: int


# ============== Flashcard Schemas ==============

class FlashcardCreate(BaseModel):
    """Create flashcard request."""
    vocabulary_id: Optional[int] = None
    front: Optional[str] = None
    back: Optional[str] = None


class FlashcardResponse(BaseModel):
    """Flashcard response."""
    id: int
    vocabulary_id: Optional[int] = None
    front: str
    back: str
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    ease_factor: float = 2.5
    interval: int = 1
    review_count: int = 0
    is_favorite: bool = False
    is_custom: bool = False

    class Config:
        from_attributes = True


class FlashcardStudyRequest(BaseModel):
    """Request for flashcard study session."""
    mode: str = Field(default="random", pattern="^(random|topic|level|due)$")
    topic: Optional[str] = None
    level: Optional[str] = None
    limit: int = Field(default=20, ge=5, le=50)


class FlashcardStudyResponse(BaseResponse):
    """Response with flashcards for study."""
    flashcards: List[FlashcardResponse] = []
    count: int = 0


class FlashcardReviewRequest(BaseModel):
    """Request to review flashcard."""
    flashcard_id: int
    performance: int = Field(..., ge=1, le=4)


# ============== Error Analysis Schemas ==============

class ErrorAnalysis(BaseModel):
    """Error analysis data."""
    error_type: str
    error_category: str
    count: int
    examples: List[str] = []
    improvement_rate: float = 0.0


class ErrorAnalysisResponse(BaseResponse):
    """Error analysis response."""
    top_errors: List[ErrorAnalysis] = []
    by_category: Dict[str, int] = {}
    trends: List[Dict[str, Any]] = []


class RecommendationsResponse(BaseResponse):
    """Learning recommendations response."""
    recommendations: List[Dict[str, Any]] = []


# ============== Learning Path Schemas ==============

class LearningPathResponse(BaseModel):
    """Learning path response."""
    id: int
    name: str
    description: str
    level: str
    estimated_days: int
    icon: Optional[str] = None
    color: Optional[str] = None
    is_enrolled: bool = False
    progress: Optional[float] = None

    class Config:
        from_attributes = True


class LearningPathsResponse(BaseResponse):
    """List of learning paths."""
    paths: List[LearningPathResponse] = []


class PathEnrollRequest(BaseModel):
    """Request to enroll in path."""
    path_id: int


class PathEnrollResponse(BaseResponse):
    """Response after path enrollment."""
    enrollment_id: int
    path_id: int
    started_at: datetime


class DayLesson(BaseModel):
    """Daily lesson content."""
    day: int
    title: str
    activities: List[Dict[str, Any]] = []
    completed: bool = False


class CurrentLessonResponse(BaseResponse):
    """Current lesson response."""
    path_id: int
    path_name: str
    current_day: int
    lesson: DayLesson


# ============== User Settings Schemas ==============

class UserSettingsUpdate(BaseModel):
    """Update user settings."""
    target_level: Optional[str] = Field(None, pattern="^(A1|A2|B1|B2|C1|C2)$")
    daily_goal: Optional[int] = Field(None, ge=1, le=100)
    theme: Optional[str] = Field(None, pattern="^(light|dark)$")
    notifications_enabled: Optional[bool] = None


class UserSettingsResponse(BaseResponse):
    """User settings response."""
    settings: Dict[str, Any]


# ============== Topic Schemas ==============

class TopicResponse(BaseModel):
    """Topic information."""
    id: int
    name: str
    icon: str
    color: str
    tier: int
    word_count: int = 0
    learned_count: int = 0


class TopicsResponse(BaseResponse):
    """List of topics."""
    topics: List[TopicResponse] = []
    total: int = 0
