"""
Application configuration settings.
All settings are designed for offline operation with local AI models.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    APP_NAME: str = "StudyEnglish"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True  # Enable debug mode

    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Paths - calculated at runtime
    @property
    def BASE_DIR(self) -> Path:
        return Path(__file__).parent.parent.resolve()

    @property
    def PROJECT_DIR(self) -> Path:
        return self.BASE_DIR.parent

    @property
    def DATA_DIR(self) -> Path:
        return self.PROJECT_DIR / "data"

    @property
    def AI_MODELS_DIR(self) -> Path:
        return self.BASE_DIR / "ai_models"

    @property
    def FRONTEND_DIR(self) -> Path:
        return self.PROJECT_DIR / "frontend"

    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite:///{self.DATA_DIR / 'study_english.db'}"

    @property
    def DATABASE_ASYNC_URL(self) -> str:
        return f"sqlite+aiosqlite:///{self.DATA_DIR / 'study_english.db'}"

    # AI Model Paths (relative to AI_MODELS_DIR)
    QWEN_MODEL_PATH: str = "qwen2.5-7b-instruct-q4_k_m.gguf"
    T5_GRAMMAR_MODEL: str = "vennify/t5-base-grammar-correction"
    NLLB_MODEL: str = "facebook/nllb-200-distilled-1.3B"
    BGE_MODEL: str = "BAAI/bge-large-en-v1.5"
    MULTILINGUAL_MODEL: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

    # AI Model Settings
    QWEN_N_CTX: int = 4096
    QWEN_N_THREADS: int = 4
    QWEN_N_GPU_LAYERS: int = 0  # Set > 0 for GPU acceleration
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.7

    # Performance
    MODEL_TIMEOUT: int = 60  # seconds
    QUERY_TIMEOUT: int = 30  # seconds
    MAX_VOCABULARY_BATCH: int = 20

    # SRS Algorithm Settings
    SRS_INITIAL_EASE_FACTOR: float = 2.5
    SRS_MIN_EASE_FACTOR: float = 1.3
    SRS_INITIAL_INTERVAL: int = 1  # days

    # CEFR Levels
    CEFR_LEVELS: list = ["A1", "A2", "B1", "B2", "C1", "C2"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist."""
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.AI_MODELS_DIR.mkdir(parents=True, exist_ok=True)


# Topic definitions with metadata
TOPICS = [
    # Tier 1: Essential
    {"id": 1, "name": "Personal and Communication", "icon": "fa-user-friends", "color": "#3B82F6", "tier": 1},
    {"id": 2, "name": "Work and Business", "icon": "fa-briefcase", "color": "#10B981", "tier": 1},
    {"id": 3, "name": "Meetings and Presentations", "icon": "fa-presentation", "color": "#8B5CF6", "tier": 1},
    {"id": 4, "name": "Email and Written Communication", "icon": "fa-envelope", "color": "#F59E0B", "tier": 1},
    {"id": 5, "name": "Small Talk and Social Skills", "icon": "fa-comments", "color": "#EF4444", "tier": 1},

    # Tier 2: Professional
    {"id": 6, "name": "Science and Technology", "icon": "fa-laptop-code", "color": "#06B6D4", "tier": 2},
    {"id": 7, "name": "Transportation and Travel", "icon": "fa-plane", "color": "#84CC16", "tier": 2},
    {"id": 8, "name": "Shopping and Money", "icon": "fa-shopping-cart", "color": "#14B8A6", "tier": 2},

    # Tier 3: Daily Life
    {"id": 9, "name": "Everyday Life", "icon": "fa-home", "color": "#6366F1", "tier": 3},
    {"id": 10, "name": "Food and Drink", "icon": "fa-utensils", "color": "#F97316", "tier": 3},
    {"id": 11, "name": "Entertainment and Leisure", "icon": "fa-film", "color": "#EC4899", "tier": 3},
    {"id": 12, "name": "Health and Medicine", "icon": "fa-heartbeat", "color": "#DC2626", "tier": 3},

    # Tier 4: General
    {"id": 13, "name": "School and Education", "icon": "fa-graduation-cap", "color": "#7C3AED", "tier": 4},
    {"id": 14, "name": "Public Services", "icon": "fa-building", "color": "#0EA5E9", "tier": 4},
    {"id": 15, "name": "Nature and Environment", "icon": "fa-tree", "color": "#059669", "tier": 4},
    {"id": 16, "name": "Sports and Fitness", "icon": "fa-running", "color": "#D97706", "tier": 4},

    # Tier 5: Culture
    {"id": 17, "name": "Culture and Society", "icon": "fa-users", "color": "#DB2777", "tier": 5},
    {"id": 18, "name": "Arts and Literature", "icon": "fa-palette", "color": "#9333EA", "tier": 5},
    {"id": 19, "name": "History and Geography", "icon": "fa-globe", "color": "#0891B2", "tier": 5},

    # Tier 6: Specialized
    {"id": 20, "name": "Government and Politics", "icon": "fa-landmark", "color": "#1E40AF", "tier": 6},
    {"id": 21, "name": "Law and Justice", "icon": "fa-gavel", "color": "#92400E", "tier": 6},
    {"id": 22, "name": "Religion and Spirituality", "icon": "fa-church", "color": "#7E22CE", "tier": 6},
    {"id": 23, "name": "Philosophy and Ethics", "icon": "fa-brain", "color": "#4338CA", "tier": 6},
]


# Learning path definitions
LEARNING_PATHS = [
    {
        "id": 1,
        "name": "Business English",
        "description": "Master professional English for workplace success",
        "level": "B1-B2",
        "estimated_days": 30,
        "topics": [2, 3, 4, 5],
        "icon": "fa-briefcase",
        "color": "#10B981"
    },
    {
        "id": 2,
        "name": "IELTS Preparation",
        "description": "Comprehensive preparation for IELTS exam",
        "level": "B2-C1",
        "estimated_days": 60,
        "topics": [1, 6, 13, 15, 17],
        "icon": "fa-graduation-cap",
        "color": "#7C3AED"
    },
    {
        "id": 3,
        "name": "Daily Conversation",
        "description": "Essential English for everyday communication",
        "level": "A2-B1",
        "estimated_days": 20,
        "topics": [1, 5, 9, 10, 11],
        "icon": "fa-comments",
        "color": "#3B82F6"
    },
    {
        "id": 4,
        "name": "Travel English",
        "description": "English skills for travelers and tourists",
        "level": "A2-B1",
        "estimated_days": 15,
        "topics": [7, 8, 10, 14],
        "icon": "fa-plane",
        "color": "#84CC16"
    },
]
