package com.studyenglish.ui.translation;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.studyenglish.R;
import com.studyenglish.StudyEnglishApp;
import com.studyenglish.data.database.AppDatabase;
import com.studyenglish.data.entity.TranslationHistory;
import com.studyenglish.utils.PromptGenerator;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class TranslationPracticeFragment extends Fragment {

    private Spinner topicSpinner;
    private Spinner levelSpinner;
    private Spinner directionSpinner;
    private Spinner complexitySpinner;
    private Spinner lengthSpinner;
    private TextView promptText;
    private View promptCard;
    private RecyclerView historyRecycler;
    private TranslationHistoryAdapter historyAdapter;

    private String currentPrompt = "";
    private String currentTopic = "";
    private String currentLevel = "";
    private String currentDirection = "";
    private String currentComplexity = "";
    private String currentLength = "";

    private final String[] topics = {"Personal", "Work", "Travel", "Food", "Health", "Education", "Technology", "Entertainment"};
    private final String[] topicsVi = {"Giao tiếp cá nhân", "Công việc & Kinh doanh", "Du lịch", "Ẩm thực", "Sức khỏe", "Giáo dục", "Công nghệ", "Giải trí"};
    private final String[] levels = {"A1", "A2", "B1", "B2", "C1", "C2"};
    private final String[] levelsVi = {"A1 - Beginner (Cơ bản)", "A2 - Elementary (Sơ cấp)", "B1 - Intermediate (Trung cấp)", "B2 - Upper Intermediate (Trung cao)", "C1 - Advanced (Cao cấp)", "C2 - Proficiency (Thành thạo)"};
    private final String[] directions = {"en_to_vi", "vi_to_en"};
    private final String[] directionsVi = {"English → Vietnamese", "Vietnamese → English"};
    private final String[] complexities = {"simple", "medium", "complex"};
    private final String[] complexitiesVi = {"Simple & Short (Câu đơn ngắn)", "Medium (Trung bình)", "Complex (Phức tạp)"};
    private final String[] lengths = {"short", "medium", "long"};
    private final String[] lengthsVi = {"Short - 5-8 sentences (Ngắn)", "Medium - 10-15 sentences (Trung bình)", "Long - 20+ sentences (Dài)"};

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                           @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_translation_practice, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        // Find views
        topicSpinner = view.findViewById(R.id.spinner_topic);
        levelSpinner = view.findViewById(R.id.spinner_level);
        directionSpinner = view.findViewById(R.id.spinner_direction);
        complexitySpinner = view.findViewById(R.id.spinner_complexity);
        lengthSpinner = view.findViewById(R.id.spinner_length);
        promptText = view.findViewById(R.id.text_prompt);
        promptCard = view.findViewById(R.id.card_prompt);
        historyRecycler = view.findViewById(R.id.recycler_history);

        Button generateBtn = view.findViewById(R.id.btn_generate);
        Button copyBtn = view.findViewById(R.id.btn_copy);
        Button saveBtn = view.findViewById(R.id.btn_save);

        setupSpinners();
        setupHistoryRecycler();

        generateBtn.setOnClickListener(v -> generatePrompt());
        copyBtn.setOnClickListener(v -> copyPrompt());
        saveBtn.setOnClickListener(v -> showSaveDialog());

        loadHistory();
    }

    private void setupSpinners() {
        // Topic spinner
        ArrayAdapter<String> topicAdapter = new ArrayAdapter<>(requireContext(),
                android.R.layout.simple_spinner_item, topicsVi);
        topicAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        topicSpinner.setAdapter(topicAdapter);

        // Level spinner
        ArrayAdapter<String> levelAdapter = new ArrayAdapter<>(requireContext(),
                android.R.layout.simple_spinner_item, levelsVi);
        levelAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        levelSpinner.setAdapter(levelAdapter);

        // Direction spinner
        ArrayAdapter<String> directionAdapter = new ArrayAdapter<>(requireContext(),
                android.R.layout.simple_spinner_item, directionsVi);
        directionAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        directionSpinner.setAdapter(directionAdapter);

        // Complexity spinner
        ArrayAdapter<String> complexityAdapter = new ArrayAdapter<>(requireContext(),
                android.R.layout.simple_spinner_item, complexitiesVi);
        complexityAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        complexitySpinner.setAdapter(complexityAdapter);

        // Length spinner
        ArrayAdapter<String> lengthAdapter = new ArrayAdapter<>(requireContext(),
                android.R.layout.simple_spinner_item, lengthsVi);
        lengthAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        lengthSpinner.setAdapter(lengthAdapter);
    }

    private void setupHistoryRecycler() {
        historyRecycler.setLayoutManager(new LinearLayoutManager(getContext()));
        historyAdapter = new TranslationHistoryAdapter(new ArrayList<>(), this::deleteHistory);
        historyRecycler.setAdapter(historyAdapter);
    }

    private void generatePrompt() {
        int topicIndex = topicSpinner.getSelectedItemPosition();
        int levelIndex = levelSpinner.getSelectedItemPosition();
        int directionIndex = directionSpinner.getSelectedItemPosition();
        int complexityIndex = complexitySpinner.getSelectedItemPosition();
        int lengthIndex = lengthSpinner.getSelectedItemPosition();

        currentTopic = topics[topicIndex];
        currentLevel = levels[levelIndex];
        currentDirection = directions[directionIndex];
        currentComplexity = complexities[complexityIndex];
        currentLength = lengths[lengthIndex];

        currentPrompt = PromptGenerator.generateTranslationPrompt(
                currentTopic, currentLevel, currentDirection, currentComplexity, currentLength);

        promptText.setText(currentPrompt);
        promptCard.setVisibility(View.VISIBLE);

        Toast.makeText(getContext(), "Đã tạo prompt! Nhấn Copy để sao chép.", Toast.LENGTH_SHORT).show();
    }

    private void copyPrompt() {
        if (currentPrompt.isEmpty()) {
            Toast.makeText(getContext(), "Vui lòng tạo prompt trước", Toast.LENGTH_SHORT).show();
            return;
        }

        ClipboardManager clipboard = (ClipboardManager) requireContext().getSystemService(Context.CLIPBOARD_SERVICE);
        ClipData clip = ClipData.newPlainText("Translation Prompt", currentPrompt);
        clipboard.setPrimaryClip(clip);

        Toast.makeText(getContext(), "Đã copy! Paste vào ChatGPT hoặc Claude để luyện dịch.", Toast.LENGTH_LONG).show();
    }

    private void showSaveDialog() {
        if (currentPrompt.isEmpty()) {
            Toast.makeText(getContext(), "Vui lòng tạo prompt trước", Toast.LENGTH_SHORT).show();
            return;
        }

        View dialogView = LayoutInflater.from(getContext()).inflate(R.layout.dialog_save_practice, null);
        EditText scoreEdit = dialogView.findViewById(R.id.edit_score);
        EditText vocabEdit = dialogView.findViewById(R.id.edit_vocabulary);

        new AlertDialog.Builder(requireContext())
                .setTitle("Lưu kết quả luyện dịch")
                .setView(dialogView)
                .setPositiveButton("Lưu", (dialog, which) -> {
                    String scoreStr = scoreEdit.getText().toString().trim();
                    String vocabStr = vocabEdit.getText().toString().trim();

                    float score = 0;
                    try {
                        score = Float.parseFloat(scoreStr);
                        if (score < 0) score = 0;
                        if (score > 10) score = 10;
                    } catch (NumberFormatException e) {
                        // Keep default 0
                    }

                    saveHistory(score, vocabStr);
                })
                .setNegativeButton("Hủy", null)
                .show();
    }

    private void saveHistory(float score, String vocabulary) {
        TranslationHistory history = new TranslationHistory();
        history.id = UUID.randomUUID().toString();
        history.topic = currentTopic;
        history.level = currentLevel;
        history.direction = currentDirection;
        history.complexity = currentComplexity;
        history.passageLength = currentLength;
        history.prompt = currentPrompt;
        history.score = score;
        history.newVocabulary = vocabulary;
        history.createdAt = System.currentTimeMillis();

        AppDatabase db = ((StudyEnglishApp) requireActivity().getApplication()).getDatabase();
        AppDatabase.databaseWriteExecutor.execute(() -> {
            db.translationHistoryDao().insert(history);
            requireActivity().runOnUiThread(() -> {
                Toast.makeText(getContext(), "Đã lưu kết quả!", Toast.LENGTH_SHORT).show();
            });
        });
    }

    private void loadHistory() {
        AppDatabase db = ((StudyEnglishApp) requireActivity().getApplication()).getDatabase();
        db.translationHistoryDao().getRecent(20).observe(getViewLifecycleOwner(), history -> {
            historyAdapter.updateList(history);
        });
    }

    private void deleteHistory(TranslationHistory history) {
        new AlertDialog.Builder(requireContext())
                .setTitle("Xóa lịch sử")
                .setMessage("Bạn có chắc muốn xóa mục này?")
                .setPositiveButton("Xóa", (dialog, which) -> {
                    AppDatabase db = ((StudyEnglishApp) requireActivity().getApplication()).getDatabase();
                    AppDatabase.databaseWriteExecutor.execute(() -> db.translationHistoryDao().delete(history));
                })
                .setNegativeButton("Hủy", null)
                .show();
    }
}
