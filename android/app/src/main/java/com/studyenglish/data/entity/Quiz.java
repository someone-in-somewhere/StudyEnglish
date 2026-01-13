package com.studyenglish.data.entity;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "quiz")
public class Quiz {
    @PrimaryKey
    @NonNull
    public String id;

    @NonNull
    public String question;

    @NonNull
    public String correctAnswer;

    public String wrongAnswer1;
    public String wrongAnswer2;
    public String wrongAnswer3;

    @NonNull
    public String type;              // multiple_choice, fill_blank, matching

    @NonNull
    public String topic;

    @NonNull
    public String level;

    public String vocabularyId;      // Related vocabulary word

    public String hint;

    public long createdAt;
}
