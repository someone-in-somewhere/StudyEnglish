package com.studyenglish.data.dao;

import androidx.lifecycle.LiveData;
import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;
import androidx.room.Update;

import com.studyenglish.data.entity.Vocabulary;

import java.util.List;

@Dao
public interface VocabularyDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insert(Vocabulary vocabulary);

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insertAll(List<Vocabulary> vocabularies);

    @Update
    void update(Vocabulary vocabulary);

    @Query("SELECT * FROM vocabulary WHERE id = :id")
    Vocabulary getById(String id);

    @Query("SELECT * FROM vocabulary ORDER BY word ASC")
    LiveData<List<Vocabulary>> getAll();

    @Query("SELECT * FROM vocabulary WHERE topic = :topic ORDER BY word ASC")
    LiveData<List<Vocabulary>> getByTopic(String topic);

    @Query("SELECT * FROM vocabulary WHERE level = :level ORDER BY word ASC")
    LiveData<List<Vocabulary>> getByLevel(String level);

    @Query("SELECT * FROM vocabulary WHERE topic = :topic AND level = :level ORDER BY word ASC")
    LiveData<List<Vocabulary>> getByTopicAndLevel(String topic, String level);

    @Query("SELECT * FROM vocabulary WHERE isLearned = 1 ORDER BY updatedAt DESC")
    LiveData<List<Vocabulary>> getLearned();

    @Query("SELECT * FROM vocabulary WHERE isFavorite = 1 ORDER BY word ASC")
    LiveData<List<Vocabulary>> getFavorites();

    // SRS queries
    @Query("SELECT * FROM vocabulary WHERE nextReview <= :now AND isLearned = 1 ORDER BY nextReview ASC")
    LiveData<List<Vocabulary>> getDueForReview(long now);

    @Query("SELECT COUNT(*) FROM vocabulary WHERE nextReview <= :now AND isLearned = 1")
    LiveData<Integer> getDueCount(long now);

    @Query("SELECT * FROM vocabulary WHERE word LIKE '%' || :query || '%' OR definition LIKE '%' || :query || '%' ORDER BY word ASC")
    LiveData<List<Vocabulary>> search(String query);

    @Query("SELECT COUNT(*) FROM vocabulary")
    int getTotalCount();

    @Query("SELECT COUNT(*) FROM vocabulary WHERE isLearned = 1")
    int getLearnedCount();

    @Query("SELECT DISTINCT topic FROM vocabulary ORDER BY topic ASC")
    LiveData<List<String>> getAllTopics();

    @Query("SELECT DISTINCT level FROM vocabulary ORDER BY level ASC")
    LiveData<List<String>> getAllLevels();

    // Random vocabulary for quiz
    @Query("SELECT * FROM vocabulary WHERE topic = :topic AND level = :level ORDER BY RANDOM() LIMIT :limit")
    List<Vocabulary> getRandomForQuiz(String topic, String level, int limit);

    @Query("SELECT * FROM vocabulary ORDER BY RANDOM() LIMIT :limit")
    List<Vocabulary> getRandom(int limit);
}
