package com.studyenglish.ui.srs;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.cardview.widget.CardView;
import androidx.fragment.app.Fragment;

import com.studyenglish.R;
import com.studyenglish.StudyEnglishApp;
import com.studyenglish.data.database.AppDatabase;
import com.studyenglish.data.entity.Vocabulary;

import java.util.ArrayList;
import java.util.List;

public class SrsFragment extends Fragment {

    private CardView reviewCard;
    private TextView wordText;
    private TextView definitionText;
    private TextView dueCountText;
    private LinearLayout answerButtons;
    private LinearLayout emptyState;

    private List<Vocabulary> dueWords = new ArrayList<>();
    private int currentIndex = 0;
    private boolean showingAnswer = false;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                           @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_srs, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        reviewCard = view.findViewById(R.id.review_card);
        wordText = view.findViewById(R.id.text_word);
        definitionText = view.findViewById(R.id.text_definition);
        dueCountText = view.findViewById(R.id.text_due_count);
        answerButtons = view.findViewById(R.id.answer_buttons);
        emptyState = view.findViewById(R.id.empty_state);

        Button showAnswerBtn = view.findViewById(R.id.btn_show_answer);
        Button againBtn = view.findViewById(R.id.btn_again);
        Button hardBtn = view.findViewById(R.id.btn_hard);
        Button goodBtn = view.findViewById(R.id.btn_good);
        Button easyBtn = view.findViewById(R.id.btn_easy);

        showAnswerBtn.setOnClickListener(v -> showAnswer());
        againBtn.setOnClickListener(v -> submitReview(0));
        hardBtn.setOnClickListener(v -> submitReview(1));
        goodBtn.setOnClickListener(v -> submitReview(2));
        easyBtn.setOnClickListener(v -> submitReview(3));

        loadDueReviews();
    }

    private void loadDueReviews() {
        AppDatabase db = ((StudyEnglishApp) requireActivity().getApplication()).getDatabase();

        db.vocabularyDao().getDueForReview(System.currentTimeMillis())
            .observe(getViewLifecycleOwner(), words -> {
                dueWords = new ArrayList<>(words);
                if (dueWords.isEmpty()) {
                    showEmptyState();
                } else {
                    showReviewCard();
                }
            });
    }

    private void showEmptyState() {
        reviewCard.setVisibility(View.GONE);
        emptyState.setVisibility(View.VISIBLE);
        dueCountText.setText("0 từ cần ôn tập");
    }

    private void showReviewCard() {
        if (currentIndex >= dueWords.size()) {
            showEmptyState();
            return;
        }

        reviewCard.setVisibility(View.VISIBLE);
        emptyState.setVisibility(View.GONE);
        answerButtons.setVisibility(View.GONE);

        Vocabulary vocab = dueWords.get(currentIndex);
        wordText.setText(vocab.word);
        definitionText.setVisibility(View.GONE);
        dueCountText.setText(String.format("%d từ cần ôn tập", dueWords.size() - currentIndex));

        showingAnswer = false;
    }

    private void showAnswer() {
        if (currentIndex < dueWords.size()) {
            Vocabulary vocab = dueWords.get(currentIndex);
            definitionText.setText(vocab.definition);
            definitionText.setVisibility(View.VISIBLE);
            answerButtons.setVisibility(View.VISIBLE);
            showingAnswer = true;
        }
    }

    private void submitReview(int quality) {
        if (currentIndex >= dueWords.size()) return;

        Vocabulary vocab = dueWords.get(currentIndex);

        // SM-2 Algorithm
        int newEaseFactor = vocab.easeFactor;
        int newInterval;
        int newRepetitions;

        if (quality < 2) {
            // Failed review
            newRepetitions = 0;
            newInterval = 1;
        } else {
            // Successful review
            if (vocab.repetitions == 0) {
                newInterval = 1;
            } else if (vocab.repetitions == 1) {
                newInterval = 6;
            } else {
                newInterval = (int) Math.round(vocab.interval * (vocab.easeFactor / 100.0));
            }
            newRepetitions = vocab.repetitions + 1;
        }

        // Update ease factor
        newEaseFactor = vocab.easeFactor + (80 - 50 * (4 - quality) - 10 * (4 - quality) * (4 - quality));
        if (newEaseFactor < 130) newEaseFactor = 130;

        // Save to database
        vocab.easeFactor = newEaseFactor;
        vocab.interval = newInterval;
        vocab.repetitions = newRepetitions;
        vocab.nextReview = System.currentTimeMillis() + (newInterval * 24L * 60 * 60 * 1000);
        vocab.lastReviewed = System.currentTimeMillis();
        vocab.updatedAt = System.currentTimeMillis();

        AppDatabase db = ((StudyEnglishApp) requireActivity().getApplication()).getDatabase();
        AppDatabase.databaseWriteExecutor.execute(() -> db.vocabularyDao().update(vocab));

        currentIndex++;
        showReviewCard();
    }
}
