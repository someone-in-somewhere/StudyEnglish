package com.studyenglish.data.entity;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "translation_history")
public class TranslationHistory {
    @PrimaryKey
    @NonNull
    public String id;

    @NonNull
    public String topic;

    @NonNull
    public String level;

    @NonNull
    public String direction;       // en_to_vi, vi_to_en

    @NonNull
    public String complexity;      // simple, medium, complex

    @NonNull
    public String passageLength;   // short, medium, long

    public String prompt;          // generated prompt

    public float score;            // 0-10

    public String newVocabulary;   // JSON array of new words learned

    public long createdAt;
}
