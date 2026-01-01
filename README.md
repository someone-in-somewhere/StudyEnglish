# StudyEnglish - Offline English Learning Application

A comprehensive, 100% offline English learning platform with local AI models. This desktop web application provides vocabulary learning, quizzes, translation, reading comprehension, writing practice, and more - all running locally without internet connection.

## Features

### Core Learning Features
- **Vocabulary Learning**: AI-generated vocabulary with Vietnamese translations, IPA pronunciation, examples, and synonyms across 23 topics and 6 CEFR levels (A1-C2)
- **Vocabulary Quiz**: Three quiz types - Multiple Choice, Fill in the Blank, and Matching
- **Translation**: Bidirectional English ↔ Vietnamese translation with level adjustment
- **Progress Dashboard**: Comprehensive statistics, charts, achievements, and study tracking

### Advanced Features
- **Spaced Repetition System (SRS)**: SM-2 algorithm for optimal long-term memory retention
- **Exercise Generator**: Five exercise types - Fill in the Blank, Sentence Rewriting, Translation, Word Order, Error Correction
- **AI Chatbot**: Conversational practice with real-time grammar correction
- **Reading Comprehension**: AI-generated passages with comprehension questions and WPM tracking
- **Writing Practice**: Essay writing with grammar, vocabulary, coherence scoring (IELTS-style 0-9 scale)
- **Flashcard System**: Auto-generated or custom flashcards with SRS integration
- **Error Analysis**: Track and analyze your mistakes for personalized recommendations
- **Learning Paths**: Structured 15-60 day curricula for Business English, IELTS Prep, Daily Conversation, and Travel English

## Technical Stack

### Backend
- **Python 3.10+** with **FastAPI**
- **SQLAlchemy** ORM with **SQLite** database
- **Uvicorn** ASGI server
- **Pydantic** for data validation

### Frontend
- **HTML5** with **Tailwind CSS**
- **Vanilla JavaScript** with **Alpine.js** for reactivity
- **Chart.js** for progress visualization
- **Font Awesome** for icons

### AI Models (Local)
| Model | Size | Purpose |
|-------|------|---------|
| Qwen2.5-7B-Instruct (Q4_K_M) | ~4.5 GB | Text generation, vocabulary, exercises, chat |
| T5-base-grammar-correction | ~800 MB | Grammar checking and correction |
| NLLB-200-distilled-1.3B | ~550 MB | EN ↔ VI translation |
| BGE-large-en-v1.5 | ~1.2 GB | Text embeddings and similarity |
| paraphrase-multilingual-mpnet-base-v2 | ~420 MB | Multilingual sentence embeddings |

## Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- 10+ GB disk space for AI models
- 8+ GB RAM recommended

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd StudyEnglish
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Download AI Models**

Create the `backend/ai_models` directory and download the required models:

```bash
mkdir -p backend/ai_models
```

**Qwen Model (GGUF format):**
Download from HuggingFace and place in `backend/ai_models/qwen2.5-7b-instruct-q4_k_m.gguf`

Other models (T5, NLLB, BGE, multilingual) will be automatically downloaded from HuggingFace on first use.

5. **Initialize the database**
```bash
cd backend
python -c "from app.database import init_db; init_db()"
```

6. **Run the application**
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

7. **Access the application**
Open your browser and navigate to: `http://127.0.0.1:8000`

## Project Structure

```
StudyEnglish/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # Database setup
│   │   ├── models/
│   │   │   ├── db_models.py     # SQLAlchemy models
│   │   │   └── schemas.py       # Pydantic schemas
│   │   ├── services/
│   │   │   ├── ai_model_manager.py    # AI model management
│   │   │   ├── vocabulary_service.py  # Vocabulary logic
│   │   │   ├── quiz_service.py        # Quiz generation
│   │   │   ├── translation_service.py # Translation
│   │   │   ├── progress_service.py    # Progress tracking
│   │   │   ├── srs_service.py         # Spaced repetition
│   │   │   ├── exercise_service.py    # Exercise generation
│   │   │   ├── chat_service.py        # AI chatbot
│   │   │   ├── reading_service.py     # Reading comprehension
│   │   │   ├── writing_service.py     # Writing practice
│   │   │   ├── flashcard_service.py   # Flashcards
│   │   │   ├── error_analysis_service.py  # Error tracking
│   │   │   └── learning_path_service.py   # Learning paths
│   │   └── routers/             # API endpoints
│   ├── ai_models/               # Local AI models directory
│   └── requirements.txt
├── frontend/
│   ├── index.html              # Main HTML file
│   ├── js/
│   │   └── app.js              # JavaScript application
│   ├── css/                    # Custom CSS (if needed)
│   └── pages/                  # Additional HTML pages
├── data/
│   └── study_english.db        # SQLite database
└── README.md
```

## API Endpoints

### Vocabulary
- `POST /api/vocabulary/generate` - Generate vocabulary with AI
- `POST /api/vocabulary/mark-learned` - Mark word as learned
- `GET /api/vocabulary/topic/{topic}` - Get vocabulary by topic

### Quiz
- `POST /api/quiz/generate` - Generate quiz
- `POST /api/quiz/submit` - Submit quiz answers
- `GET /api/quiz/stats` - Get quiz statistics

### Translation
- `POST /api/translation/translate` - Translate text
- `GET /api/translation/history` - Get translation history

### SRS
- `GET /api/srs/due-reviews` - Get words due for review
- `POST /api/srs/review` - Submit review
- `GET /api/srs/stats` - Get SRS statistics

### Chat
- `POST /api/chat/message` - Send message to chatbot
- `GET /api/chat/history/{session_id}` - Get chat history

### And more...
See the API documentation at `/api/docs` (when DEBUG=True)

## Topics (23 Categories)

**Tier 1 - Essential:**
1. Personal and Communication
2. Work and Business
3. Meetings and Presentations
4. Email and Written Communication
5. Small Talk and Social Skills

**Tier 2 - Professional:**
6. Science and Technology
7. Transportation and Travel
8. Shopping and Money

**Tier 3 - Daily Life:**
9. Everyday Life
10. Food and Drink
11. Entertainment and Leisure
12. Health and Medicine

**Tier 4 - General:**
13. School and Education
14. Public Services
15. Nature and Environment
16. Sports and Fitness

**Tier 5 - Culture:**
17. Culture and Society
18. Arts and Literature
19. History and Geography

**Tier 6 - Specialized:**
20. Government and Politics
21. Law and Justice
22. Religion and Spirituality
23. Philosophy and Ethics

## Development

### Debug Mode
Set `DEBUG=True` in environment or `.env` file to enable:
- API documentation at `/api/docs`
- Detailed logging
- Hot reload

### Testing
```bash
cd backend
pytest
```

## Offline Mode

The application is designed to run 100% offline:
- All AI inference runs locally
- Data stored in local SQLite database
- No external API calls required
- Models are cached locally after first download

## Performance

| Operation | Target Time |
|-----------|-------------|
| Vocabulary Generation | < 5 seconds |
| Translation | < 2 seconds |
| Quiz Generation | < 3 seconds |
| Page Load | < 1 second |
| Model Loading | < 30 seconds |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Qwen](https://huggingface.co/Qwen) - Large language model
- [HuggingFace](https://huggingface.co/) - AI model hub
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Alpine.js](https://alpinejs.dev/) - Lightweight JavaScript framework
