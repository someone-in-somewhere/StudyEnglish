package com.studyenglish.data.entity;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "conversation_history")
public class ConversationHistory {
    @PrimaryKey
    @NonNull
    public String id;

    @NonNull
    public String topic;

    @NonNull
    public String level;

    @NonNull
    public String style;          // casual, formal, business

    @NonNull
    public String length;         // short, medium, long

    public String context;        // suggested context

    public String prompt;         // generated prompt

    public float score;           // 0-10

    public String newVocabulary;  // JSON array of new words learned

    public long createdAt;
}
