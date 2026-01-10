package com.studyenglish.data.database;

import android.content.Context;

import androidx.annotation.NonNull;
import androidx.room.Database;
import androidx.room.Room;
import androidx.room.RoomDatabase;
import androidx.sqlite.db.SupportSQLiteDatabase;

import com.studyenglish.data.dao.ProgressDao;
import com.studyenglish.data.dao.QuizDao;
import com.studyenglish.data.dao.VocabularyDao;
import com.studyenglish.data.entity.Quiz;
import com.studyenglish.data.entity.StudyProgress;
import com.studyenglish.data.entity.Vocabulary;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@Database(
    entities = {
        Vocabulary.class,
        Quiz.class,
        StudyProgress.class
    },
    version = 1,
    exportSchema = true
)
public abstract class AppDatabase extends RoomDatabase {

    public abstract VocabularyDao vocabularyDao();
    public abstract QuizDao quizDao();
    public abstract ProgressDao progressDao();

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
                    .createFromAsset("database/study_english.db")
                    .addCallback(new Callback() {
                        @Override
                        public void onCreate(@NonNull SupportSQLiteDatabase db) {
                            super.onCreate(db);
                            // Initialize default progress
                            databaseWriteExecutor.execute(() -> {
                                ProgressDao progressDao = INSTANCE.progressDao();
                                StudyProgress progress = new StudyProgress();
                                progress.id = "main";
                                progress.createdAt = System.currentTimeMillis();
                                progress.updatedAt = System.currentTimeMillis();
                                progressDao.insert(progress);
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
}
