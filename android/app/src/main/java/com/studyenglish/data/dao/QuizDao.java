package com.studyenglish.data.dao;

import androidx.lifecycle.LiveData;
import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;

import com.studyenglish.data.entity.Quiz;

import java.util.List;

@Dao
public interface QuizDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insert(Quiz quiz);

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insertAll(List<Quiz> quizzes);

    @Query("SELECT * FROM quiz WHERE id = :id")
    Quiz getById(String id);

    @Query("SELECT * FROM quiz ORDER BY RANDOM()")
    LiveData<List<Quiz>> getAll();

    @Query("SELECT * FROM quiz WHERE topic = :topic ORDER BY RANDOM()")
    LiveData<List<Quiz>> getByTopic(String topic);

    @Query("SELECT * FROM quiz WHERE level = :level ORDER BY RANDOM()")
    LiveData<List<Quiz>> getByLevel(String level);

    @Query("SELECT * FROM quiz WHERE topic = :topic AND level = :level ORDER BY RANDOM()")
    LiveData<List<Quiz>> getByTopicAndLevel(String topic, String level);

    @Query("SELECT * FROM quiz WHERE type = :type ORDER BY RANDOM()")
    LiveData<List<Quiz>> getByType(String type);

    @Query("SELECT * FROM quiz WHERE topic = :topic AND level = :level ORDER BY RANDOM() LIMIT :limit")
    List<Quiz> getRandomQuiz(String topic, String level, int limit);

    @Query("SELECT * FROM quiz ORDER BY RANDOM() LIMIT :limit")
    List<Quiz> getRandom(int limit);

    @Query("SELECT COUNT(*) FROM quiz")
    int getTotalCount();
}
