package com.studyenglish.data.database;

import android.content.Context;

import androidx.annotation.NonNull;
import androidx.room.Database;
import androidx.room.Room;
import androidx.room.RoomDatabase;
import androidx.sqlite.db.SupportSQLiteDatabase;

import com.studyenglish.data.dao.ConversationHistoryDao;
import com.studyenglish.data.dao.ProgressDao;
import com.studyenglish.data.dao.QuizDao;
import com.studyenglish.data.dao.TranslationHistoryDao;
import com.studyenglish.data.dao.VocabularyDao;
import com.studyenglish.data.entity.ConversationHistory;
import com.studyenglish.data.entity.Quiz;
import com.studyenglish.data.entity.StudyProgress;
import com.studyenglish.data.entity.TranslationHistory;
import com.studyenglish.data.entity.Vocabulary;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@Database(
    entities = {
        Vocabulary.class,
        Quiz.class,
        StudyProgress.class,
        ConversationHistory.class,
        TranslationHistory.class
    },
    version = 2,
    exportSchema = false
)
public abstract class AppDatabase extends RoomDatabase {

    public abstract VocabularyDao vocabularyDao();
    public abstract QuizDao quizDao();
    public abstract ProgressDao progressDao();
    public abstract ConversationHistoryDao conversationHistoryDao();
    public abstract TranslationHistoryDao translationHistoryDao();

    private static volatile AppDatabase INSTANCE;
    private static final int NUMBER_OF_THREADS = 4;
    public static final ExecutorService databaseWriteExecutor =
            Executors.newFixedThreadPool(NUMBER_OF_THREADS);

    public static AppDatabase getDatabase(final Context context) {
        if (INSTANCE == null) {
            synchronized (AppDatabase.class) {
                if (INSTANCE == null) {
                    INSTANCE = Room.databaseBuilder(
                            context.getApplicationContext(),
                            AppDatabase.class,
                            "study_english_db"
                    )
                    .addCallback(new Callback() {
                        @Override
                        public void onCreate(@NonNull SupportSQLiteDatabase db) {
                            super.onCreate(db);
                            // Populate initial data on first run
                            databaseWriteExecutor.execute(() -> {
                                // Initialize default progress
                                ProgressDao progressDao = INSTANCE.progressDao();
                                StudyProgress progress = new StudyProgress();
                                progress.id = "main";
                                progress.createdAt = System.currentTimeMillis();
                                progress.updatedAt = System.currentTimeMillis();
                                progressDao.insert(progress);

                                // Populate initial vocabulary
                                VocabularyDao vocabDao = INSTANCE.vocabularyDao();
                                populateInitialVocabulary(vocabDao);
                            });
                        }
                    })
                    .fallbackToDestructiveMigration()
                    .build();
                }
            }
        }
        return INSTANCE;
    }

    private static void populateInitialVocabulary(VocabularyDao dao) {
        long now = System.currentTimeMillis();
        String[][] vocabData = {
            // A1 - Personal
            {"hello", "Xin chào", "/həˈloʊ/", "interjection", "Personal", "A1", "Hello, how are you?", "Xin chào, bạn khỏe không?"},
            {"goodbye", "Tạm biệt", "/ˌɡʊdˈbaɪ/", "interjection", "Personal", "A1", "Goodbye, see you tomorrow!", "Tạm biệt, hẹn gặp lại ngày mai!"},
            {"name", "Tên", "/neɪm/", "noun", "Personal", "A1", "My name is John.", "Tên tôi là John."},
            {"friend", "Bạn", "/frend/", "noun", "Personal", "A1", "She is my friend.", "Cô ấy là bạn tôi."},
            {"family", "Gia đình", "/ˈfæməli/", "noun", "Personal", "A1", "I love my family.", "Tôi yêu gia đình tôi."},
            {"mother", "Mẹ", "/ˈmʌðər/", "noun", "Personal", "A1", "My mother is a teacher.", "Mẹ tôi là giáo viên."},
            {"father", "Bố", "/ˈfɑːðər/", "noun", "Personal", "A1", "My father works in a bank.", "Bố tôi làm việc ở ngân hàng."},
            {"brother", "Anh/Em trai", "/ˈbrʌðər/", "noun", "Personal", "A1", "I have one brother.", "Tôi có một anh trai."},
            {"sister", "Chị/Em gái", "/ˈsɪstər/", "noun", "Personal", "A1", "My sister is older than me.", "Chị tôi lớn hơn tôi."},
            {"house", "Nhà", "/haʊs/", "noun", "Personal", "A1", "We live in a big house.", "Chúng tôi sống trong một ngôi nhà lớn."},
            // A1 - Work
            {"work", "Làm việc", "/wɜːrk/", "verb", "Work", "A1", "I work every day.", "Tôi làm việc mỗi ngày."},
            {"job", "Công việc", "/dʒɑːb/", "noun", "Work", "A1", "I have a new job.", "Tôi có một công việc mới."},
            {"office", "Văn phòng", "/ˈɔːfɪs/", "noun", "Work", "A1", "The office is downtown.", "Văn phòng ở trung tâm."},
            {"meeting", "Cuộc họp", "/ˈmiːtɪŋ/", "noun", "Work", "A1", "We have a meeting at 3 PM.", "Chúng tôi có cuộc họp lúc 3 giờ."},
            {"boss", "Sếp", "/bɔːs/", "noun", "Work", "A1", "My boss is very nice.", "Sếp tôi rất tốt."},
            // A1 - Food
            {"food", "Thức ăn", "/fuːd/", "noun", "Food", "A1", "I love Vietnamese food.", "Tôi thích đồ ăn Việt Nam."},
            {"water", "Nước", "/ˈwɔːtər/", "noun", "Food", "A1", "Please give me some water.", "Làm ơn cho tôi ít nước."},
            {"rice", "Cơm", "/raɪs/", "noun", "Food", "A1", "We eat rice every day.", "Chúng tôi ăn cơm mỗi ngày."},
            {"meat", "Thịt", "/miːt/", "noun", "Food", "A1", "I don't eat meat.", "Tôi không ăn thịt."},
            {"fruit", "Trái cây", "/fruːt/", "noun", "Food", "A1", "Fruit is good for health.", "Trái cây tốt cho sức khỏe."},
            // A2 - Travel
            {"travel", "Du lịch", "/ˈtrævəl/", "verb", "Travel", "A2", "I love to travel abroad.", "Tôi thích du lịch nước ngoài."},
            {"airport", "Sân bay", "/ˈerpɔːrt/", "noun", "Travel", "A2", "The airport is far from here.", "Sân bay xa đây."},
            {"hotel", "Khách sạn", "/hoʊˈtel/", "noun", "Travel", "A2", "We stayed at a nice hotel.", "Chúng tôi ở một khách sạn đẹp."},
            {"ticket", "Vé", "/ˈtɪkɪt/", "noun", "Travel", "A2", "I bought a plane ticket.", "Tôi đã mua vé máy bay."},
            {"passport", "Hộ chiếu", "/ˈpæspɔːrt/", "noun", "Travel", "A2", "Don't forget your passport.", "Đừng quên hộ chiếu."},
            // A2 - Health
            {"doctor", "Bác sĩ", "/ˈdɑːktər/", "noun", "Health", "A2", "I need to see a doctor.", "Tôi cần gặp bác sĩ."},
            {"hospital", "Bệnh viện", "/ˈhɑːspɪtl/", "noun", "Health", "A2", "The hospital is nearby.", "Bệnh viện ở gần đây."},
            {"medicine", "Thuốc", "/ˈmedɪsn/", "noun", "Health", "A2", "Take this medicine twice a day.", "Uống thuốc này hai lần một ngày."},
            {"headache", "Đau đầu", "/ˈhedeɪk/", "noun", "Health", "A2", "I have a headache.", "Tôi bị đau đầu."},
            {"fever", "Sốt", "/ˈfiːvər/", "noun", "Health", "A2", "She has a high fever.", "Cô ấy bị sốt cao."},
            // B1 - Technology
            {"computer", "Máy tính", "/kəmˈpjuːtər/", "noun", "Technology", "B1", "I use a computer for work.", "Tôi dùng máy tính để làm việc."},
            {"internet", "Internet", "/ˈɪntərnet/", "noun", "Technology", "B1", "The internet is slow today.", "Internet hôm nay chậm."},
            {"software", "Phần mềm", "/ˈsɔːftwer/", "noun", "Technology", "B1", "We need to update the software.", "Chúng ta cần cập nhật phần mềm."},
            {"application", "Ứng dụng", "/ˌæplɪˈkeɪʃn/", "noun", "Technology", "B1", "Download this application.", "Tải ứng dụng này."},
            {"website", "Trang web", "/ˈwebsaɪt/", "noun", "Technology", "B1", "Visit our website for more info.", "Truy cập trang web để biết thêm."},
            // B1 - Education
            {"university", "Đại học", "/ˌjuːnɪˈvɜːrsəti/", "noun", "Education", "B1", "I study at the university.", "Tôi học ở đại học."},
            {"student", "Sinh viên", "/ˈstuːdnt/", "noun", "Education", "B1", "She is a good student.", "Cô ấy là sinh viên giỏi."},
            {"teacher", "Giáo viên", "/ˈtiːtʃər/", "noun", "Education", "B1", "The teacher explains well.", "Giáo viên giảng giải rõ ràng."},
            {"exam", "Kỳ thi", "/ɪɡˈzæm/", "noun", "Education", "B1", "I have an exam tomorrow.", "Tôi có kỳ thi ngày mai."},
            {"homework", "Bài tập về nhà", "/ˈhoʊmwɜːrk/", "noun", "Education", "B1", "Did you finish your homework?", "Bạn làm xong bài tập chưa?"},
            // B2 - Business
            {"negotiate", "Đàm phán", "/nɪˈɡoʊʃieɪt/", "verb", "Work", "B2", "We need to negotiate the contract.", "Chúng ta cần đàm phán hợp đồng."},
            {"deadline", "Hạn chót", "/ˈdedlaɪn/", "noun", "Work", "B2", "The deadline is next week.", "Hạn chót là tuần sau."},
            {"budget", "Ngân sách", "/ˈbʌdʒɪt/", "noun", "Work", "B2", "We exceeded the budget.", "Chúng tôi đã vượt ngân sách."},
            {"investment", "Đầu tư", "/ɪnˈvestmənt/", "noun", "Work", "B2", "This is a good investment.", "Đây là một khoản đầu tư tốt."},
            {"strategy", "Chiến lược", "/ˈstrætədʒi/", "noun", "Work", "B2", "We need a new strategy.", "Chúng ta cần chiến lược mới."},
            // B2 - Nature
            {"pollution", "Ô nhiễm", "/pəˈluːʃn/", "noun", "Nature", "B2", "Air pollution is a serious problem.", "Ô nhiễm không khí là vấn đề nghiêm trọng."},
            {"climate", "Khí hậu", "/ˈklaɪmət/", "noun", "Nature", "B2", "Climate change affects everyone.", "Biến đổi khí hậu ảnh hưởng đến mọi người."},
            {"environment", "Môi trường", "/ɪnˈvaɪrənmənt/", "noun", "Nature", "B2", "Protect the environment.", "Bảo vệ môi trường."},
            // C1 - Advanced
            {"ambiguous", "Mơ hồ", "/æmˈbɪɡjuəs/", "adjective", "Education", "C1", "The statement is ambiguous.", "Phát biểu này mơ hồ."},
            {"comprehensive", "Toàn diện", "/ˌkɑːmprɪˈhensɪv/", "adjective", "Education", "C1", "We need a comprehensive analysis.", "Chúng ta cần phân tích toàn diện."},
            {"pragmatic", "Thực dụng", "/præɡˈmætɪk/", "adjective", "Work", "C1", "Take a pragmatic approach.", "Hãy tiếp cận thực dụng."},
            // C2 - Proficiency
            {"quintessential", "Tinh túy", "/ˌkwɪntɪˈsenʃl/", "adjective", "Education", "C2", "This is the quintessential example.", "Đây là ví dụ tinh túy."},
            {"ubiquitous", "Có mặt khắp nơi", "/juːˈbɪkwɪtəs/", "adjective", "Technology", "C2", "Smartphones are ubiquitous.", "Điện thoại thông minh có mặt khắp nơi."},
        };

        for (String[] v : vocabData) {
            Vocabulary vocab = new Vocabulary();
            vocab.id = java.util.UUID.randomUUID().toString();
            vocab.word = v[0];
            vocab.definition = v[1];
            vocab.pronunciation = v[2];
            vocab.partOfSpeech = v[3];
            vocab.topic = v[4];
            vocab.level = v[5];
            vocab.example = v[6];
            vocab.exampleTranslation = v[7];
            vocab.createdAt = now;
            vocab.updatedAt = now;
            dao.insert(vocab);
        }
    }
}
