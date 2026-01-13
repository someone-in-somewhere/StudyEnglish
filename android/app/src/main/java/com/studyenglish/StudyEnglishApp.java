package com.studyenglish;

import android.app.Application;

import com.studyenglish.data.database.AppDatabase;

public class StudyEnglishApp extends Application {

    private AppDatabase database;

    @Override
    public void onCreate() {
        super.onCreate();
        // Initialize database
        database = AppDatabase.getDatabase(this);
    }

    public AppDatabase getDatabase() {
        return database;
    }
}
