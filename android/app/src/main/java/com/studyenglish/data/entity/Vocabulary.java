package com.studyenglish.data.entity;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "vocabulary")
public class Vocabulary {
    @PrimaryKey
    @NonNull
    public String id;

    @NonNull
    public String word;

    @NonNull
    public String definition;        // Vietnamese translation

    public String pronunciation;      // IPA

    @NonNull
    public String partOfSpeech;      // noun, verb, adj, etc.

    public String example;           // Example sentence

    public String exampleTranslation; // Vietnamese translation of example

    @NonNull
    public String topic;             // Topic category

    @NonNull
    public String level;             // CEFR level: A1, A2, B1, B2, C1, C2

    public String synonyms;          // Comma-separated synonyms

    public String antonyms;          // Comma-separated antonyms

    // SRS fields
    public int easeFactor = 250;     // SM-2 ease factor (250 = 2.5)
    public int interval = 0;         // Days until next review
    public int repetitions = 0;      // Number of successful reviews
    public long nextReview = 0;      // Timestamp for next review
    public long lastReviewed = 0;    // Last review timestamp

    public boolean isLearned = false;
    public boolean isFavorite = false;

    public long createdAt;
    public long updatedAt;
}
