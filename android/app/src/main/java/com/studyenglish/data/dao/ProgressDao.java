package com.studyenglish.data.dao;

import androidx.lifecycle.LiveData;
import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;
import androidx.room.Update;

import com.studyenglish.data.entity.StudyProgress;

@Dao
public interface ProgressDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insert(StudyProgress progress);

    @Update
    void update(StudyProgress progress);

    @Query("SELECT * FROM study_progress WHERE id = 'main' LIMIT 1")
    LiveData<StudyProgress> getProgress();

    @Query("SELECT * FROM study_progress WHERE id = 'main' LIMIT 1")
    StudyProgress getProgressSync();

    @Query("UPDATE study_progress SET totalWordsLearned = totalWordsLearned + 1, updatedAt = :now WHERE id = 'main'")
    void incrementWordsLearned(long now);

    @Query("UPDATE study_progress SET totalQuizzesTaken = totalQuizzesTaken + 1, updatedAt = :now WHERE id = 'main'")
    void incrementQuizzesTaken(long now);

    @Query("UPDATE study_progress SET totalCorrectAnswers = totalCorrectAnswers + 1, updatedAt = :now WHERE id = 'main'")
    void incrementCorrectAnswers(long now);

    @Query("UPDATE study_progress SET totalWrongAnswers = totalWrongAnswers + 1, updatedAt = :now WHERE id = 'main'")
    void incrementWrongAnswers(long now);

    @Query("UPDATE study_progress SET currentStreak = :streak, longestStreak = CASE WHEN :streak > longestStreak THEN :streak ELSE longestStreak END, lastStudyDate = :date, updatedAt = :now WHERE id = 'main'")
    void updateStreak(int streak, long date, long now);

    @Query("UPDATE study_progress SET totalStudyTime = totalStudyTime + :seconds, updatedAt = :now WHERE id = 'main'")
    void addStudyTime(long seconds, long now);
}
