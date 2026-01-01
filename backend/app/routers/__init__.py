"""API Routers package."""

from app.routers.vocabulary import router as vocabulary_router
from app.routers.quiz import router as quiz_router
from app.routers.translation import router as translation_router
from app.routers.progress import router as progress_router
from app.routers.srs import router as srs_router
from app.routers.exercises import router as exercises_router
from app.routers.chat import router as chat_router
from app.routers.reading import router as reading_router
from app.routers.writing import router as writing_router
from app.routers.flashcards import router as flashcards_router
from app.routers.errors import router as errors_router
from app.routers.learning_paths import router as learning_paths_router
from app.routers.topics import router as topics_router

__all__ = [
    "vocabulary_router",
    "quiz_router",
    "translation_router",
    "progress_router",
    "srs_router",
    "exercises_router",
    "chat_router",
    "reading_router",
    "writing_router",
    "flashcards_router",
    "errors_router",
    "learning_paths_router",
    "topics_router",
]
