package com.studyenglish.ui.quiz;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.navigation.Navigation;

import com.studyenglish.R;

import java.util.ArrayList;
import java.util.List;

public class QuizFragment extends Fragment {

    private Spinner topicSpinner;
    private Spinner levelSpinner;
    private Spinner countSpinner;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                           @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_quiz, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        topicSpinner = view.findViewById(R.id.spinner_topic);
        levelSpinner = view.findViewById(R.id.spinner_level);
        countSpinner = view.findViewById(R.id.spinner_count);
        Button startButton = view.findViewById(R.id.btn_start_quiz);

        setupSpinners();

        startButton.setOnClickListener(v -> startQuiz());
    }

    private void setupSpinners() {
        // Topics
        List<String> topics = new ArrayList<>();
        topics.add("Tất cả chủ đề");
        topics.add("Personal");
        topics.add("Work");
        topics.add("Travel");
        topics.add("Food");
        topics.add("Health");

        ArrayAdapter<String> topicAdapter = new ArrayAdapter<>(
            requireContext(), android.R.layout.simple_spinner_item, topics);
        topicAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        topicSpinner.setAdapter(topicAdapter);

        // Levels
        List<String> levels = new ArrayList<>();
        levels.add("Tất cả cấp độ");
        levels.add("A1");
        levels.add("A2");
        levels.add("B1");
        levels.add("B2");
        levels.add("C1");
        levels.add("C2");

        ArrayAdapter<String> levelAdapter = new ArrayAdapter<>(
            requireContext(), android.R.layout.simple_spinner_item, levels);
        levelAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        levelSpinner.setAdapter(levelAdapter);

        // Question count
        List<String> counts = new ArrayList<>();
        counts.add("5 câu");
        counts.add("10 câu");
        counts.add("15 câu");
        counts.add("20 câu");

        ArrayAdapter<String> countAdapter = new ArrayAdapter<>(
            requireContext(), android.R.layout.simple_spinner_item, counts);
        countAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        countSpinner.setAdapter(countAdapter);
        countSpinner.setSelection(1); // Default 10 questions
    }

    private void startQuiz() {
        String topic = topicSpinner.getSelectedItemPosition() == 0 ? "" :
                      topicSpinner.getSelectedItem().toString();
        String level = levelSpinner.getSelectedItemPosition() == 0 ? "" :
                      levelSpinner.getSelectedItem().toString();

        int[] countValues = {5, 10, 15, 20};
        int count = countValues[countSpinner.getSelectedItemPosition()];

        Bundle args = new Bundle();
        args.putString("topic", topic);
        args.putString("level", level);
        args.putInt("count", count);

        Navigation.findNavController(requireView())
                .navigate(R.id.action_quiz_to_play, args);
    }
}
