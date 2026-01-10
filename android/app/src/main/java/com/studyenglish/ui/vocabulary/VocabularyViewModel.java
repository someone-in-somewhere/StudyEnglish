package com.studyenglish.ui.vocabulary;

import android.app.Application;

import androidx.annotation.NonNull;
import androidx.lifecycle.AndroidViewModel;
import androidx.lifecycle.LiveData;

import com.studyenglish.StudyEnglishApp;
import com.studyenglish.data.dao.VocabularyDao;
import com.studyenglish.data.database.AppDatabase;
import com.studyenglish.data.entity.Vocabulary;

import java.util.List;

public class VocabularyViewModel extends AndroidViewModel {

    private final VocabularyDao vocabularyDao;

    public VocabularyViewModel(@NonNull Application application) {
        super(application);
        AppDatabase db = ((StudyEnglishApp) application).getDatabase();
        vocabularyDao = db.vocabularyDao();
    }

    public LiveData<List<Vocabulary>> getAllVocabulary() {
        return vocabularyDao.getAll();
    }

    public LiveData<List<Vocabulary>> getByTopic(String topic) {
        return vocabularyDao.getByTopic(topic);
    }

    public LiveData<List<Vocabulary>> getByLevel(String level) {
        return vocabularyDao.getByLevel(level);
    }

    public LiveData<List<Vocabulary>> getByTopicAndLevel(String topic, String level) {
        return vocabularyDao.getByTopicAndLevel(topic, level);
    }

    public LiveData<List<Vocabulary>> searchVocabulary(String query) {
        return vocabularyDao.search(query);
    }

    public LiveData<List<Vocabulary>> getFavorites() {
        return vocabularyDao.getFavorites();
    }

    public LiveData<List<Vocabulary>> getLearned() {
        return vocabularyDao.getLearned();
    }

    public void updateVocabulary(Vocabulary vocabulary) {
        AppDatabase.databaseWriteExecutor.execute(() -> {
            vocabulary.updatedAt = System.currentTimeMillis();
            vocabularyDao.update(vocabulary);
        });
    }

    public void markAsLearned(Vocabulary vocabulary) {
        AppDatabase.databaseWriteExecutor.execute(() -> {
            vocabulary.isLearned = true;
            vocabulary.updatedAt = System.currentTimeMillis();
            vocabularyDao.update(vocabulary);
        });
    }

    public void toggleFavorite(Vocabulary vocabulary) {
        AppDatabase.databaseWriteExecutor.execute(() -> {
            vocabulary.isFavorite = !vocabulary.isFavorite;
            vocabulary.updatedAt = System.currentTimeMillis();
            vocabularyDao.update(vocabulary);
        });
    }
}
