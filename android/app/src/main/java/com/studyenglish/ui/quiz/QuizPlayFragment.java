package com.studyenglish.ui.quiz;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.navigation.Navigation;

import com.studyenglish.R;
import com.studyenglish.StudyEnglishApp;
import com.studyenglish.data.database.AppDatabase;
import com.studyenglish.data.entity.Vocabulary;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class QuizPlayFragment extends Fragment {

    private TextView questionCountText;
    private TextView questionText;
    private RadioGroup answersGroup;
    private RadioButton[] answerButtons = new RadioButton[4];
    private Button nextButton;
    private ProgressBar progressBar;

    private List<Vocabulary> quizWords = new ArrayList<>();
    private int currentIndex = 0;
    private int correctAnswers = 0;
    private int totalQuestions = 10;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                           @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_quiz_play, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        questionCountText = view.findViewById(R.id.text_question_count);
        questionText = view.findViewById(R.id.text_question);
        answersGroup = view.findViewById(R.id.radio_group_answers);
        answerButtons[0] = view.findViewById(R.id.radio_answer_1);
        answerButtons[1] = view.findViewById(R.id.radio_answer_2);
        answerButtons[2] = view.findViewById(R.id.radio_answer_3);
        answerButtons[3] = view.findViewById(R.id.radio_answer_4);
        nextButton = view.findViewById(R.id.btn_next);
        progressBar = view.findViewById(R.id.progress_bar);

        Bundle args = getArguments();
        if (args != null) {
            totalQuestions = args.getInt("count", 10);
        }

        loadQuizData();

        nextButton.setOnClickListener(v -> checkAnswerAndNext());
    }

    private void loadQuizData() {
        AppDatabase db = ((StudyEnglishApp) requireActivity().getApplication()).getDatabase();

        AppDatabase.databaseWriteExecutor.execute(() -> {
            List<Vocabulary> words = db.vocabularyDao().getRandom(totalQuestions * 2);

            requireActivity().runOnUiThread(() -> {
                if (words.size() >= 4) {
                    quizWords = new ArrayList<>(words.subList(0, Math.min(totalQuestions, words.size())));
                    showQuestion();
                } else {
                    Toast.makeText(getContext(), "Không đủ từ vựng để tạo quiz", Toast.LENGTH_SHORT).show();
                    Navigation.findNavController(requireView()).popBackStack();
                }
            });
        });
    }

    private void showQuestion() {
        if (currentIndex >= quizWords.size()) {
            showResult();
            return;
        }

        Vocabulary currentWord = quizWords.get(currentIndex);
        questionCountText.setText(String.format("Câu %d/%d", currentIndex + 1, quizWords.size()));
        questionText.setText("\"" + currentWord.definition + "\" nghĩa là gì?");

        progressBar.setMax(quizWords.size());
        progressBar.setProgress(currentIndex + 1);

        // Create answers (1 correct + 3 wrong)
        List<String> answers = new ArrayList<>();
        answers.add(currentWord.word); // Correct answer

        // Get random wrong answers
        List<Vocabulary> wrongAnswers = new ArrayList<>(quizWords);
        wrongAnswers.remove(currentWord);
        Collections.shuffle(wrongAnswers);

        for (int i = 0; i < 3 && i < wrongAnswers.size(); i++) {
            answers.add(wrongAnswers.get(i).word);
        }

        // Pad with placeholders if needed
        while (answers.size() < 4) {
            answers.add("Option " + answers.size());
        }

        Collections.shuffle(answers);

        for (int i = 0; i < 4; i++) {
            answerButtons[i].setText(answers.get(i));
        }

        answersGroup.clearCheck();
        nextButton.setText(currentIndex == quizWords.size() - 1 ?
                getString(R.string.finish_quiz) : getString(R.string.next_question));
    }

    private void checkAnswerAndNext() {
        int selectedId = answersGroup.getCheckedRadioButtonId();
        if (selectedId == -1) {
            Toast.makeText(getContext(), "Vui lòng chọn câu trả lời", Toast.LENGTH_SHORT).show();
            return;
        }

        RadioButton selected = requireView().findViewById(selectedId);
        String selectedAnswer = selected.getText().toString();
        String correctAnswer = quizWords.get(currentIndex).word;

        if (selectedAnswer.equals(correctAnswer)) {
            correctAnswers++;
            Toast.makeText(getContext(), "Đúng!", Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(getContext(), "Sai! Đáp án: " + correctAnswer, Toast.LENGTH_SHORT).show();
        }

        currentIndex++;
        showQuestion();
    }

    private void showResult() {
        int score = (int) ((float) correctAnswers / quizWords.size() * 100);

        new androidx.appcompat.app.AlertDialog.Builder(requireContext())
            .setTitle(getString(R.string.quiz_result))
            .setMessage(String.format(getString(R.string.correct_answers), correctAnswers, quizWords.size()) +
                       "\n" + String.format(getString(R.string.quiz_score), score))
            .setPositiveButton(R.string.ok, (dialog, which) -> {
                Navigation.findNavController(requireView()).popBackStack();
            })
            .setCancelable(false)
            .show();
    }
}
