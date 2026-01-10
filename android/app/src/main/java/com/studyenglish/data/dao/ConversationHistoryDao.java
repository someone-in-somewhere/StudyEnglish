package com.studyenglish.data.dao;

import androidx.lifecycle.LiveData;
import androidx.room.Dao;
import androidx.room.Delete;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;

import com.studyenglish.data.entity.ConversationHistory;

import java.util.List;

@Dao
public interface ConversationHistoryDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insert(ConversationHistory history);

    @Delete
    void delete(ConversationHistory history);

    @Query("DELETE FROM conversation_history WHERE id = :id")
    void deleteById(String id);

    @Query("SELECT * FROM conversation_history ORDER BY createdAt DESC")
    LiveData<List<ConversationHistory>> getAll();

    @Query("SELECT * FROM conversation_history WHERE topic = :topic ORDER BY createdAt DESC")
    LiveData<List<ConversationHistory>> getByTopic(String topic);

    @Query("SELECT * FROM conversation_history ORDER BY createdAt DESC LIMIT :limit")
    LiveData<List<ConversationHistory>> getRecent(int limit);

    @Query("SELECT COUNT(*) FROM conversation_history")
    int getTotalCount();

    @Query("SELECT AVG(score) FROM conversation_history WHERE score > 0")
    float getAverageScore();

    @Query("SELECT COUNT(*) FROM conversation_history WHERE topic = :topic")
    int getCountByTopic(String topic);

    @Query("SELECT AVG(score) FROM conversation_history WHERE topic = :topic AND score > 0")
    float getAverageScoreByTopic(String topic);
}
