#!/usr/bin/env python3
"""
Script to generate pre-populated SQLite database for Android app.
Run this script to create the database file at:
  android/app/src/main/assets/database/study_english.db
"""

import sqlite3
import os
import uuid
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__),
    '..', 'app', 'src', 'main', 'assets', 'database', 'study_english.db')

# Sample vocabulary data
VOCABULARY_DATA = [
    # A1 - Personal
    ("hello", "Xin chào", "/həˈloʊ/", "interjection", "Personal", "A1", "Hello, how are you?", "Xin chào, bạn khỏe không?"),
    ("goodbye", "Tạm biệt", "/ˌɡʊdˈbaɪ/", "interjection", "Personal", "A1", "Goodbye, see you tomorrow!", "Tạm biệt, hẹn gặp lại ngày mai!"),
    ("name", "Tên", "/neɪm/", "noun", "Personal", "A1", "My name is John.", "Tên tôi là John."),
    ("friend", "Bạn", "/frend/", "noun", "Personal", "A1", "She is my friend.", "Cô ấy là bạn tôi."),
    ("family", "Gia đình", "/ˈfæməli/", "noun", "Personal", "A1", "I love my family.", "Tôi yêu gia đình tôi."),
    ("mother", "Mẹ", "/ˈmʌðər/", "noun", "Personal", "A1", "My mother is a teacher.", "Mẹ tôi là giáo viên."),
    ("father", "Bố", "/ˈfɑːðər/", "noun", "Personal", "A1", "My father works in a bank.", "Bố tôi làm việc ở ngân hàng."),
    ("brother", "Anh/Em trai", "/ˈbrʌðər/", "noun", "Personal", "A1", "I have one brother.", "Tôi có một anh trai."),
    ("sister", "Chị/Em gái", "/ˈsɪstər/", "noun", "Personal", "A1", "My sister is older than me.", "Chị tôi lớn hơn tôi."),
    ("house", "Nhà", "/haʊs/", "noun", "Personal", "A1", "We live in a big house.", "Chúng tôi sống trong một ngôi nhà lớn."),

    # A1 - Work
    ("work", "Làm việc", "/wɜːrk/", "verb", "Work", "A1", "I work every day.", "Tôi làm việc mỗi ngày."),
    ("job", "Công việc", "/dʒɑːb/", "noun", "Work", "A1", "I have a new job.", "Tôi có một công việc mới."),
    ("office", "Văn phòng", "/ˈɔːfɪs/", "noun", "Work", "A1", "The office is downtown.", "Văn phòng ở trung tâm."),
    ("meeting", "Cuộc họp", "/ˈmiːtɪŋ/", "noun", "Work", "A1", "We have a meeting at 3 PM.", "Chúng tôi có cuộc họp lúc 3 giờ."),
    ("boss", "Sếp", "/bɔːs/", "noun", "Work", "A1", "My boss is very nice.", "Sếp tôi rất tốt."),

    # A1 - Food
    ("food", "Thức ăn", "/fuːd/", "noun", "Food", "A1", "I love Vietnamese food.", "Tôi thích đồ ăn Việt Nam."),
    ("water", "Nước", "/ˈwɔːtər/", "noun", "Food", "A1", "Please give me some water.", "Làm ơn cho tôi ít nước."),
    ("rice", "Cơm", "/raɪs/", "noun", "Food", "A1", "We eat rice every day.", "Chúng tôi ăn cơm mỗi ngày."),
    ("meat", "Thịt", "/miːt/", "noun", "Food", "A1", "I don't eat meat.", "Tôi không ăn thịt."),
    ("fruit", "Trái cây", "/fruːt/", "noun", "Food", "A1", "Fruit is good for health.", "Trái cây tốt cho sức khỏe."),

    # A2 - Travel
    ("travel", "Du lịch", "/ˈtrævəl/", "verb", "Travel", "A2", "I love to travel abroad.", "Tôi thích du lịch nước ngoài."),
    ("airport", "Sân bay", "/ˈerpɔːrt/", "noun", "Travel", "A2", "The airport is far from here.", "Sân bay xa đây."),
    ("hotel", "Khách sạn", "/hoʊˈtel/", "noun", "Travel", "A2", "We stayed at a nice hotel.", "Chúng tôi ở một khách sạn đẹp."),
    ("ticket", "Vé", "/ˈtɪkɪt/", "noun", "Travel", "A2", "I bought a plane ticket.", "Tôi đã mua vé máy bay."),
    ("passport", "Hộ chiếu", "/ˈpæspɔːrt/", "noun", "Travel", "A2", "Don't forget your passport.", "Đừng quên hộ chiếu."),

    # A2 - Health
    ("doctor", "Bác sĩ", "/ˈdɑːktər/", "noun", "Health", "A2", "I need to see a doctor.", "Tôi cần gặp bác sĩ."),
    ("hospital", "Bệnh viện", "/ˈhɑːspɪtl/", "noun", "Health", "A2", "The hospital is nearby.", "Bệnh viện ở gần đây."),
    ("medicine", "Thuốc", "/ˈmedɪsn/", "noun", "Health", "A2", "Take this medicine twice a day.", "Uống thuốc này hai lần một ngày."),
    ("headache", "Đau đầu", "/ˈhedeɪk/", "noun", "Health", "A2", "I have a headache.", "Tôi bị đau đầu."),
    ("fever", "Sốt", "/ˈfiːvər/", "noun", "Health", "A2", "She has a high fever.", "Cô ấy bị sốt cao."),

    # B1 - Technology
    ("computer", "Máy tính", "/kəmˈpjuːtər/", "noun", "Technology", "B1", "I use a computer for work.", "Tôi dùng máy tính để làm việc."),
    ("internet", "Internet", "/ˈɪntərnet/", "noun", "Technology", "B1", "The internet is slow today.", "Internet hôm nay chậm."),
    ("software", "Phần mềm", "/ˈsɔːftwer/", "noun", "Technology", "B1", "We need to update the software.", "Chúng ta cần cập nhật phần mềm."),
    ("application", "Ứng dụng", "/ˌæplɪˈkeɪʃn/", "noun", "Technology", "B1", "Download this application.", "Tải ứng dụng này."),
    ("website", "Trang web", "/ˈwebsaɪt/", "noun", "Technology", "B1", "Visit our website for more info.", "Truy cập trang web để biết thêm."),

    # B1 - Education
    ("university", "Đại học", "/ˌjuːnɪˈvɜːrsəti/", "noun", "Education", "B1", "I study at the university.", "Tôi học ở đại học."),
    ("student", "Sinh viên", "/ˈstuːdnt/", "noun", "Education", "B1", "She is a good student.", "Cô ấy là sinh viên giỏi."),
    ("teacher", "Giáo viên", "/ˈtiːtʃər/", "noun", "Education", "B1", "The teacher explains well.", "Giáo viên giảng giải rõ ràng."),
    ("exam", "Kỳ thi", "/ɪɡˈzæm/", "noun", "Education", "B1", "I have an exam tomorrow.", "Tôi có kỳ thi ngày mai."),
    ("homework", "Bài tập về nhà", "/ˈhoʊmwɜːrk/", "noun", "Education", "B1", "Did you finish your homework?", "Bạn làm xong bài tập chưa?"),

    # B2 - Business
    ("negotiate", "Đàm phán", "/nɪˈɡoʊʃieɪt/", "verb", "Work", "B2", "We need to negotiate the contract.", "Chúng ta cần đàm phán hợp đồng."),
    ("deadline", "Hạn chót", "/ˈdedlaɪn/", "noun", "Work", "B2", "The deadline is next week.", "Hạn chót là tuần sau."),
    ("budget", "Ngân sách", "/ˈbʌdʒɪt/", "noun", "Work", "B2", "We exceeded the budget.", "Chúng tôi đã vượt ngân sách."),
    ("investment", "Đầu tư", "/ɪnˈvestmənt/", "noun", "Work", "B2", "This is a good investment.", "Đây là một khoản đầu tư tốt."),
    ("strategy", "Chiến lược", "/ˈstrætədʒi/", "noun", "Work", "B2", "We need a new strategy.", "Chúng ta cần chiến lược mới."),

    # B2 - Environment
    ("pollution", "Ô nhiễm", "/pəˈluːʃn/", "noun", "Nature", "B2", "Air pollution is a serious problem.", "Ô nhiễm không khí là vấn đề nghiêm trọng."),
    ("climate", "Khí hậu", "/ˈklaɪmət/", "noun", "Nature", "B2", "Climate change affects everyone.", "Biến đổi khí hậu ảnh hưởng đến mọi người."),
    ("environment", "Môi trường", "/ɪnˈvaɪrənmənt/", "noun", "Nature", "B2", "Protect the environment.", "Bảo vệ môi trường."),
    ("renewable", "Tái tạo", "/rɪˈnuːəbl/", "adjective", "Nature", "B2", "We should use renewable energy.", "Chúng ta nên dùng năng lượng tái tạo."),
    ("sustainable", "Bền vững", "/səˈsteɪnəbl/", "adjective", "Nature", "B2", "Sustainable development is important.", "Phát triển bền vững rất quan trọng."),

    # C1 - Advanced
    ("ambiguous", "Mơ hồ", "/æmˈbɪɡjuəs/", "adjective", "Education", "C1", "The statement is ambiguous.", "Phát biểu này mơ hồ."),
    ("comprehensive", "Toàn diện", "/ˌkɑːmprɪˈhensɪv/", "adjective", "Education", "C1", "We need a comprehensive analysis.", "Chúng ta cần phân tích toàn diện."),
    ("pragmatic", "Thực dụng", "/præɡˈmætɪk/", "adjective", "Work", "C1", "Take a pragmatic approach.", "Hãy tiếp cận thực dụng."),
    ("eloquent", "Hùng biện", "/ˈeləkwənt/", "adjective", "Personal", "C1", "She is an eloquent speaker.", "Cô ấy là diễn giả hùng biện."),
    ("meticulous", "Tỉ mỉ", "/məˈtɪkjələs/", "adjective", "Work", "C1", "He is meticulous in his work.", "Anh ấy tỉ mỉ trong công việc."),

    # C2 - Proficiency
    ("quintessential", "Tinh túy", "/ˌkwɪntɪˈsenʃl/", "adjective", "Education", "C2", "This is the quintessential example.", "Đây là ví dụ tinh túy."),
    ("ubiquitous", "Có mặt khắp nơi", "/juːˈbɪkwɪtəs/", "adjective", "Technology", "C2", "Smartphones are ubiquitous.", "Điện thoại thông minh có mặt khắp nơi."),
    ("ephemeral", "Phù du", "/ɪˈfemərəl/", "adjective", "Nature", "C2", "Fame is often ephemeral.", "Danh tiếng thường phù du."),
    ("sycophant", "Kẻ xu nịnh", "/ˈsɪkəfænt/", "noun", "Work", "C2", "He is just a sycophant.", "Anh ta chỉ là kẻ xu nịnh."),
    ("vicissitude", "Thăng trầm", "/vɪˈsɪsɪtuːd/", "noun", "Personal", "C2", "Life is full of vicissitudes.", "Cuộc sống đầy thăng trầm."),
]

def create_database():
    """Create and populate the SQLite database."""

    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Remove existing database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    # Create database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vocabulary (
            id TEXT PRIMARY KEY NOT NULL,
            word TEXT NOT NULL,
            definition TEXT NOT NULL,
            pronunciation TEXT,
            partOfSpeech TEXT NOT NULL,
            example TEXT,
            exampleTranslation TEXT,
            topic TEXT NOT NULL,
            level TEXT NOT NULL,
            synonyms TEXT,
            antonyms TEXT,
            easeFactor INTEGER DEFAULT 250,
            interval INTEGER DEFAULT 0,
            repetitions INTEGER DEFAULT 0,
            nextReview INTEGER DEFAULT 0,
            lastReviewed INTEGER DEFAULT 0,
            isLearned INTEGER DEFAULT 0,
            isFavorite INTEGER DEFAULT 0,
            createdAt INTEGER,
            updatedAt INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz (
            id TEXT PRIMARY KEY NOT NULL,
            question TEXT NOT NULL,
            correctAnswer TEXT NOT NULL,
            wrongAnswer1 TEXT,
            wrongAnswer2 TEXT,
            wrongAnswer3 TEXT,
            type TEXT NOT NULL,
            topic TEXT NOT NULL,
            level TEXT NOT NULL,
            vocabularyId TEXT,
            hint TEXT,
            createdAt INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_progress (
            id TEXT PRIMARY KEY NOT NULL,
            totalWordsLearned INTEGER DEFAULT 0,
            totalQuizzesTaken INTEGER DEFAULT 0,
            totalCorrectAnswers INTEGER DEFAULT 0,
            totalWrongAnswers INTEGER DEFAULT 0,
            currentStreak INTEGER DEFAULT 0,
            longestStreak INTEGER DEFAULT 0,
            totalStudyTime INTEGER DEFAULT 0,
            lastStudyDate INTEGER DEFAULT 0,
            levelStats TEXT,
            topicStats TEXT,
            createdAt INTEGER,
            updatedAt INTEGER
        )
    ''')

    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_vocabulary_topic ON vocabulary(topic)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_vocabulary_level ON vocabulary(level)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_vocabulary_word ON vocabulary(word)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_quiz_topic ON quiz(topic)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_quiz_level ON quiz(level)')

    # Insert vocabulary data
    now = int(datetime.now().timestamp() * 1000)

    for vocab in VOCABULARY_DATA:
        word, definition, pronunciation, pos, topic, level, example, example_trans = vocab
        vocab_id = str(uuid.uuid4())

        cursor.execute('''
            INSERT INTO vocabulary (id, word, definition, pronunciation, partOfSpeech,
                topic, level, example, exampleTranslation, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (vocab_id, word, definition, pronunciation, pos, topic, level,
              example, example_trans, now, now))

    # Create initial progress record
    cursor.execute('''
        INSERT INTO study_progress (id, createdAt, updatedAt)
        VALUES ('main', ?, ?)
    ''', (now, now))

    conn.commit()
    conn.close()

    print(f"Database created successfully at: {DB_PATH}")
    print(f"Total vocabulary items: {len(VOCABULARY_DATA)}")

if __name__ == '__main__':
    create_database()
