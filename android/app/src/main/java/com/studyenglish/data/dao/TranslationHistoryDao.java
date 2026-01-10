package com.studyenglish.data.dao;

import androidx.lifecycle.LiveData;
import androidx.room.Dao;
import androidx.room.Delete;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;

import com.studyenglish.data.entity.TranslationHistory;

import java.util.List;

@Dao
public interface TranslationHistoryDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insert(TranslationHistory history);

    @Delete
    void delete(TranslationHistory history);

    @Query("DELETE FROM translation_history WHERE id = :id")
    void deleteById(String id);

    @Query("SELECT * FROM translation_history ORDER BY createdAt DESC")
    LiveData<List<TranslationHistory>> getAll();

    @Query("SELECT * FROM translation_history WHERE topic = :topic ORDER BY createdAt DESC")
    LiveData<List<TranslationHistory>> getByTopic(String topic);

    @Query("SELECT * FROM translation_history ORDER BY createdAt DESC LIMIT :limit")
    LiveData<List<TranslationHistory>> getRecent(int limit);

    @Query("SELECT COUNT(*) FROM translation_history")
    int getTotalCount();

    @Query("SELECT AVG(score) FROM translation_history WHERE score > 0")
    float getAverageScore();

    @Query("SELECT COUNT(*) FROM translation_history WHERE topic = :topic")
    int getCountByTopic(String topic);

    @Query("SELECT AVG(score) FROM translation_history WHERE topic = :topic AND score > 0")
    float getAverageScoreByTopic(String topic);
}
