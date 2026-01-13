# Study English - Web Version

Phiên bản web của ứng dụng học tiếng Anh với FastAPI backend và HTML/JS frontend.

## Yêu cầu

- Python 3.10+
- 8GB+ RAM (cho AI models)
- GPU (khuyến nghị, không bắt buộc)

## Cài đặt

### 1. Tạo virtual environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Tải AI Models

Tải và đặt các model vào thư mục `backend/ai_models/`:

| Model | Link | Mục đích |
|-------|------|----------|
| Qwen2.5-7B-Instruct-Q4_K_M.gguf | HuggingFace | Text generation |
| t5-base-grammar-correction | HuggingFace | Grammar check |
| nllb-200-distilled-1.3B | HuggingFace | Translation |

### 4. Chạy server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Truy cập: http://localhost:8000

## Cấu trúc thư mục

```
web/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── services/        # Business logic
│   │   ├── routers/         # API endpoints
│   │   ├── utils/           # Utilities
│   │   ├── main.py          # Entry point
│   │   ├── config.py        # Configuration
│   │   └── database.py      # Database setup
│   ├── ai_models/           # AI model files (not in git)
│   ├── data/                # SQLite database
│   └── requirements.txt
└── frontend/
    ├── index.html           # Main HTML
    └── js/
        └── app.js           # JavaScript application
```

## API Documentation

Khi chạy ở chế độ debug, truy cập:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Tính năng

- Học từ vựng (23 chủ đề, CEFR A1-C2)
- Quiz (Multiple Choice, Fill-in-Blank, Matching)
- Dịch thuật Anh ↔ Việt
- Spaced Repetition System (SM-2)
- AI Chatbot với sửa lỗi ngữ pháp
- Đọc hiểu với tracking WPM
- Viết luận chấm điểm IELTS
- Flashcards
- Learning Paths
