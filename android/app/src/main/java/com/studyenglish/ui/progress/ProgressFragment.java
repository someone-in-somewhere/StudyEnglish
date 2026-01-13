package com.studyenglish.ui.progress;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.studyenglish.R;
import com.studyenglish.StudyEnglishApp;
import com.studyenglish.data.database.AppDatabase;
import com.studyenglish.data.entity.StudyProgress;

public class ProgressFragment extends Fragment {

    private TextView wordsLearnedText;
    private TextView quizzesTakenText;
    private TextView accuracyText;
    private TextView streakText;
    private TextView studyTimeText;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                           @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_progress, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        wordsLearnedText = view.findViewById(R.id.text_words_learned);
        quizzesTakenText = view.findViewById(R.id.text_quizzes_taken);
        accuracyText = view.findViewById(R.id.text_accuracy);
        streakText = view.findViewById(R.id.text_streak);
        studyTimeText = view.findViewById(R.id.text_study_time);

        loadProgress();
    }

    private void loadProgress() {
        AppDatabase db = ((StudyEnglishApp) requireActivity().getApplication()).getDatabase();

        db.progressDao().getProgress().observe(getViewLifecycleOwner(), progress -> {
            if (progress != null) {
                updateUI(progress);
            }
        });

        // Also get vocabulary stats
        db.vocabularyDao().getDueCount(System.currentTimeMillis())
            .observe(getViewLifecycleOwner(), count -> {
                // Update due count if needed
            });
    }

    private void updateUI(StudyProgress progress) {
        wordsLearnedText.setText(String.valueOf(progress.totalWordsLearned));
        quizzesTakenText.setText(String.valueOf(progress.totalQuizzesTaken));

        // Calculate accuracy
        int total = progress.totalCorrectAnswers + progress.totalWrongAnswers;
        int accuracy = total > 0 ?
            (int) ((float) progress.totalCorrectAnswers / total * 100) : 0;
        accuracyText.setText(accuracy + "%");

        streakText.setText(progress.currentStreak + " ngày");

        // Format study time
        long hours = progress.totalStudyTime / 3600;
        long minutes = (progress.totalStudyTime % 3600) / 60;
        studyTimeText.setText(String.format("%dh %dm", hours, minutes));
    }
}
