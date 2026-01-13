package com.studyenglish.data.entity;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "study_progress")
public class StudyProgress {
    @PrimaryKey
    @NonNull
    public String id;

    public int totalWordsLearned = 0;
    public int totalQuizzesTaken = 0;
    public int totalCorrectAnswers = 0;
    public int totalWrongAnswers = 0;

    public int currentStreak = 0;       // Days in a row
    public int longestStreak = 0;

    public long totalStudyTime = 0;     // In seconds

    public long lastStudyDate = 0;

    // Per level stats (JSON stored as string)
    public String levelStats;           // {"A1": 10, "A2": 5, ...}

    // Per topic stats
    public String topicStats;           // {"personal": 15, ...}

    public long createdAt;
    public long updatedAt;
}
