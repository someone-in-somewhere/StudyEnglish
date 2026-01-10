# StudyEnglish - Offline English Learning Application

A comprehensive, 100% offline English learning platform with local AI models. Available for both **Web** and **Android** platforms.

## Project Structure

```
StudyEnglish/
├── web/                    # 🌐 Phiên bản Web
│   ├── backend/            # FastAPI backend (Python)
│   │   ├── app/            # Main application
│   │   │   ├── models/     # Database models
│   │   │   ├── services/   # Business logic (14 services)
│   │   │   ├── routers/    # API endpoints (18 routers)
│   │   │   └── utils/      # Utilities
│   │   ├── ai_models/      # Local AI models
│   │   └── requirements.txt
│   └── frontend/           # HTML/JS frontend
│       ├── index.html
│       └── js/app.js
│
├── android/                # 📱 Phiên bản Android
│   ├── app/                # Android app module
│   │   ├── src/main/
│   │   │   ├── java/       # Java source code
│   │   │   ├── res/        # Resources (layouts, values)
│   │   │   └── AndroidManifest.xml
│   │   └── build.gradle
│   ├── build.gradle
│   └── settings.gradle
│
├── shared/                 # 🔗 Code dùng chung
│   ├── config.json         # App configuration
│   └── constants.js        # Shared constants
│
└── README.md
```

## Platforms

### 🌐 Web Version
Desktop web application chạy trên trình duyệt.

**Xem chi tiết:** [web/README.md](./web/README.md)

```bash
# Quick Start
cd web/backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
# Truy cập: http://localhost:8000
```

### 📱 Android Version
Ứng dụng Android APK sử dụng WebView.

**Xem chi tiết:** [android/README.md](./android/README.md)

```bash
# Build APK
cd android
./gradlew assembleDebug
# APK: app/build/outputs/apk/debug/app-debug.apk
```

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

### Backend (Python)
| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Database | SQLite + SQLAlchemy |
| Server | Uvicorn |
| Validation | Pydantic |

### Frontend (Web)
| Component | Technology |
|-----------|------------|
| Styling | Tailwind CSS |
| Reactivity | Alpine.js |
| Charts | Chart.js |
| Icons | Font Awesome |

### Android
| Component | Technology |
|-----------|------------|
| Language | Java |
| Min SDK | 24 (Android 7.0) |
| Target SDK | 34 (Android 14) |
| Build | Gradle 8.2 |

### AI Models (Local)
| Model | Size | Purpose |
|-------|------|---------|
| Qwen2.5-7B-Instruct (Q4_K_M) | ~4.5 GB | Text generation, vocabulary, exercises, chat |
| T5-base-grammar-correction | ~800 MB | Grammar checking and correction |
| NLLB-200-distilled-1.3B | ~550 MB | EN ↔ VI translation |
| BGE-large-en-v1.5 | ~1.2 GB | Text embeddings and similarity |
| paraphrase-multilingual-mpnet-base-v2 | ~420 MB | Multilingual sentence embeddings |

## Requirements

### Web Version
- Python 3.10+
- 10+ GB disk space (for AI models)
- 8+ GB RAM recommended
- Modern web browser

### Android Version
- Android Studio Arctic Fox+
- JDK 17
- Android device/emulator (API 24+)
- Backend server running

## Topics (23 Categories)

**Tier 1 - Essential:** Personal & Communication, Work & Business, Meetings, Email, Small Talk

**Tier 2 - Professional:** Science & Tech, Transportation, Shopping

**Tier 3 - Daily Life:** Everyday Life, Food, Entertainment, Health

**Tier 4 - General:** Education, Public Services, Nature, Sports

**Tier 5 - Culture:** Culture & Society, Arts, History

**Tier 6 - Specialized:** Government, Law, Religion, Philosophy

## API Endpoints

| Category | Endpoints |
|----------|-----------|
| Vocabulary | `/api/vocabulary/generate`, `/api/vocabulary/mark-learned` |
| Quiz | `/api/quiz/generate`, `/api/quiz/submit` |
| Translation | `/api/translation/translate` |
| SRS | `/api/srs/due-reviews`, `/api/srs/review` |
| Chat | `/api/chat/message` |
| Reading | `/api/reading/generate`, `/api/reading/submit` |
| Writing | `/api/writing/submit` |
| Flashcards | `/api/flashcards/*` |
| Progress | `/api/progress/*` |

Full API docs: `http://localhost:8000/docs` (when DEBUG=True)

## Offline Mode

The application is designed to run 100% offline:
- All AI inference runs locally
- Data stored in local SQLite database
- No external API calls required
- Models are cached locally after first download

## Development

### Debug Mode
Set `DEBUG=True` in environment to enable:
- API documentation at `/docs`
- Detailed logging
- Hot reload

### Testing
```bash
cd web/backend
pytest
```

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Qwen](https://huggingface.co/Qwen) - Large language model
- [HuggingFace](https://huggingface.co/) - AI model hub
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Alpine.js](https://alpinejs.dev/) - Lightweight JavaScript framework
