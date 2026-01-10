# StudyEnglish - Android App

Ứng dụng học tiếng Anh offline cho Android. Hoạt động hoàn toàn độc lập, không cần kết nối internet hoặc server backend.

## Tính Năng

- **Từ vựng**: 60+ từ vựng mẫu theo 6 cấp độ CEFR (A1-C2) và nhiều chủ đề
- **Quiz**: Kiểm tra kiến thức với câu hỏi trắc nghiệm
- **Flashcard**: Học từ vựng với thẻ ghi nhớ, vuốt trái/phải
- **SRS**: Hệ thống ôn tập theo thuật toán SM-2
- **Tiến độ**: Theo dõi thống kê học tập

## Yêu Cầu

- Android Studio Arctic Fox (2020.3.1) trở lên
- JDK 17
- Android SDK 34
- Gradle 8.2

## Cài Đặt

### 1. Mở Project

```bash
# Mở Android Studio
# File → Open → Chọn thư mục android/
```

### 2. Sync Gradle

Android Studio sẽ tự động sync. Nếu không:
- File → Sync Project with Gradle Files

### 3. Build APK

**Debug APK:**
```bash
./gradlew assembleDebug
# APK: app/build/outputs/apk/debug/app-debug.apk
```

**Release APK:**
```bash
./gradlew assembleRelease
# APK: app/build/outputs/apk/release/app-release.apk
```

### 4. Cài đặt lên thiết bị

```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

## Cấu Trúc Project

```
android/
├── app/
│   ├── src/main/
│   │   ├── java/com/studyenglish/
│   │   │   ├── data/
│   │   │   │   ├── dao/          # Data Access Objects
│   │   │   │   ├── entity/       # Database entities
│   │   │   │   ├── database/     # Room database
│   │   │   │   └── repository/   # Data repositories
│   │   │   ├── ui/
│   │   │   │   ├── vocabulary/   # Màn hình từ vựng
│   │   │   │   ├── quiz/         # Màn hình quiz
│   │   │   │   ├── flashcard/    # Màn hình flashcard
│   │   │   │   ├── srs/          # Màn hình ôn tập
│   │   │   │   └── progress/     # Màn hình tiến độ
│   │   │   ├── utils/            # Utilities
│   │   │   └── StudyEnglishApp.java
│   │   ├── res/
│   │   │   ├── layout/           # XML layouts
│   │   │   ├── values/           # Strings, colors, themes
│   │   │   ├── drawable/         # Icons, backgrounds
│   │   │   ├── menu/             # Menu items
│   │   │   ├── navigation/       # Navigation graph
│   │   │   └── anim/             # Animations
│   │   ├── assets/
│   │   │   └── database/         # Pre-populated SQLite DB
│   │   └── AndroidManifest.xml
│   └── build.gradle
├── scripts/
│   └── generate_database.py      # Script tạo database mẫu
├── build.gradle
├── settings.gradle
└── gradle.properties
```

## Thêm Từ Vựng

### Cách 1: Chỉnh sửa script Python

Mở `scripts/generate_database.py` và thêm từ vựng vào `VOCABULARY_DATA`:

```python
VOCABULARY_DATA = [
    # (word, definition, pronunciation, part_of_speech, topic, level, example, example_translation)
    ("hello", "Xin chào", "/həˈloʊ/", "interjection", "Personal", "A1", "Hello, how are you?", "Xin chào, bạn khỏe không?"),
    # Thêm từ mới ở đây...
]
```

Sau đó chạy:
```bash
python3 scripts/generate_database.py
```

### Cách 2: Thêm trực tiếp vào SQLite

```bash
sqlite3 app/src/main/assets/database/study_english.db
```

```sql
INSERT INTO vocabulary (id, word, definition, pronunciation, partOfSpeech, topic, level, example, exampleTranslation, createdAt, updatedAt)
VALUES ('uuid-here', 'word', 'nghĩa', '/pronunciation/', 'noun', 'Topic', 'A1', 'Example sentence', 'Câu ví dụ', 1234567890000, 1234567890000);
```

## Database Schema

### vocabulary
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key (UUID) |
| word | TEXT | Từ tiếng Anh |
| definition | TEXT | Nghĩa tiếng Việt |
| pronunciation | TEXT | Phiên âm IPA |
| partOfSpeech | TEXT | Loại từ (noun, verb, adj...) |
| topic | TEXT | Chủ đề |
| level | TEXT | Cấp độ CEFR (A1-C2) |
| example | TEXT | Câu ví dụ |
| exampleTranslation | TEXT | Dịch câu ví dụ |
| easeFactor | INTEGER | Hệ số dễ (SRS) |
| interval | INTEGER | Khoảng cách ôn tập (ngày) |
| repetitions | INTEGER | Số lần ôn tập thành công |
| nextReview | INTEGER | Timestamp ôn tập tiếp theo |
| isLearned | INTEGER | Đã học (0/1) |
| isFavorite | INTEGER | Yêu thích (0/1) |

### study_progress
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key |
| totalWordsLearned | INTEGER | Tổng từ đã học |
| totalQuizzesTaken | INTEGER | Tổng quiz đã làm |
| totalCorrectAnswers | INTEGER | Tổng câu đúng |
| totalWrongAnswers | INTEGER | Tổng câu sai |
| currentStreak | INTEGER | Streak hiện tại |
| longestStreak | INTEGER | Streak dài nhất |
| totalStudyTime | INTEGER | Tổng thời gian học (giây) |

## Công Nghệ

| Component | Technology |
|-----------|------------|
| Language | Java |
| Database | Room (SQLite) |
| Architecture | MVVM |
| Navigation | Jetpack Navigation |
| UI | Material Design 3 |

## So Sánh Với Phiên Bản Web

| Tính năng | Web | Android |
|-----------|-----|---------|
| AI Generation | ✅ | ❌ |
| Nội dung có sẵn | ❌ | ✅ |
| Offline | ✅ (với AI models) | ✅ |
| Dung lượng | ~8GB | ~50MB |
| Quiz | ✅ | ✅ |
| Flashcard | ✅ | ✅ |
| SRS | ✅ | ✅ |
| Translation | ✅ | ❌ |
| Chatbot | ✅ | ❌ |
| Reading | ✅ | ❌ |
| Writing | ✅ | ❌ |

## License

MIT License
