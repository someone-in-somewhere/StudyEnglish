package com.studyenglish.ui.flashcard;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
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

public class FlashcardFragment extends Fragment {

    private CardView flashcard;
    private TextView frontText;
    private TextView backText;
    private TextView remainingText;
    private View frontView;
    private View backView;

    private List<Vocabulary> cards = new ArrayList<>();
    private int currentIndex = 0;
    private boolean showingFront = true;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                           @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_flashcard, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        flashcard = view.findViewById(R.id.flashcard);
        frontView = view.findViewById(R.id.card_front);
        backView = view.findViewById(R.id.card_back);
        frontText = view.findViewById(R.id.text_front);
        backText = view.findViewById(R.id.text_back);
        remainingText = view.findViewById(R.id.text_remaining);

        View btnKnow = view.findViewById(R.id.btn_know);
        View btnDontKnow = view.findViewById(R.id.btn_dont_know);

        flashcard.setOnClickListener(v -> flipCard());
        btnKnow.setOnClickListener(v -> nextCard(true));
        btnDontKnow.setOnClickListener(v -> nextCard(false));

        loadCards();
    }

    private void loadCards() {
        AppDatabase db = ((StudyEnglishApp) requireActivity().getApplication()).getDatabase();

        AppDatabase.databaseWriteExecutor.execute(() -> {
            List<Vocabulary> words = db.vocabularyDao().getRandom(20);

            requireActivity().runOnUiThread(() -> {
                cards = new ArrayList<>(words);
                if (!cards.isEmpty()) {
                    showCard();
                }
            });
        });
    }

    private void showCard() {
        if (currentIndex >= cards.size()) {
            frontText.setText("Hoàn thành!");
            backText.setText("Bạn đã xem hết tất cả thẻ");
            remainingText.setText("0 thẻ còn lại");
            return;
        }

        Vocabulary vocab = cards.get(currentIndex);
        frontText.setText(vocab.word);
        backText.setText(vocab.definition +
                (vocab.pronunciation != null ? "\n" + vocab.pronunciation : ""));
        remainingText.setText(String.format(getString(R.string.cards_remaining),
                cards.size() - currentIndex));

        showingFront = true;
        frontView.setVisibility(View.VISIBLE);
        backView.setVisibility(View.GONE);
    }

    private void flipCard() {
        Animation flipOut = AnimationUtils.loadAnimation(getContext(), R.anim.flip_out);
        Animation flipIn = AnimationUtils.loadAnimation(getContext(), R.anim.flip_in);

        flipOut.setAnimationListener(new Animation.AnimationListener() {
            @Override
            public void onAnimationStart(Animation animation) {}

            @Override
            public void onAnimationEnd(Animation animation) {
                if (showingFront) {
                    frontView.setVisibility(View.GONE);
                    backView.setVisibility(View.VISIBLE);
                } else {
                    frontView.setVisibility(View.VISIBLE);
                    backView.setVisibility(View.GONE);
                }
                showingFront = !showingFront;
                flashcard.startAnimation(flipIn);
            }

            @Override
            public void onAnimationRepeat(Animation animation) {}
        });

        flashcard.startAnimation(flipOut);
    }

    private void nextCard(boolean known) {
        if (known) {
            // Mark as learned
            Vocabulary vocab = cards.get(currentIndex);
            AppDatabase db = ((StudyEnglishApp) requireActivity().getApplication()).getDatabase();
            AppDatabase.databaseWriteExecutor.execute(() -> {
                vocab.isLearned = true;
                vocab.updatedAt = System.currentTimeMillis();
                db.vocabularyDao().update(vocab);
            });
        }

        currentIndex++;
        showCard();
    }
}
