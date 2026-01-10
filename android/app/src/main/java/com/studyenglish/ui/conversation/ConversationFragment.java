package com.studyenglish.ui.conversation;

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
import com.studyenglish.data.entity.ConversationHistory;
import com.studyenglish.utils.PromptGenerator;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class ConversationFragment extends Fragment {

    private Spinner topicSpinner;
    private Spinner levelSpinner;
    private Spinner styleSpinner;
    private Spinner lengthSpinner;
    private TextView promptText;
    private View promptCard;
    private RecyclerView historyRecycler;
    private ConversationHistoryAdapter historyAdapter;

    private String currentPrompt = "";
    private String currentTopic = "";
    private String currentLevel = "";
    private String currentStyle = "";
    private String currentLength = "";

    private final String[] topics = {"Personal", "Work", "Travel", "Food", "Health", "Education", "Technology", "Entertainment"};
    private final String[] topicsVi = {"Giao tiếp cá nhân", "Công việc & Kinh doanh", "Du lịch", "Ẩm thực", "Sức khỏe", "Giáo dục", "Công nghệ", "Giải trí"};
    private final String[] levels = {"A1", "A2", "B1", "B2", "C1", "C2"};
    private final String[] levelsVi = {"A1 - Beginner (Cơ bản)", "A2 - Elementary (Sơ cấp)", "B1 - Intermediate (Trung cấp)", "B2 - Upper Intermediate (Trung cao)", "C1 - Advanced (Cao cấp)", "C2 - Proficiency (Thành thạo)"};
    private final String[] styles = {"casual", "formal", "business"};
    private final String[] stylesVi = {"Casual (Thân mật, bạn bè)", "Formal (Trang trọng)", "Business (Công việc)"};
    private final String[] lengths = {"short", "medium", "long"};
    private final String[] lengthsVi = {"Short - 5-8 exchanges (Ngắn)", "Medium - 10-15 exchanges (Trung bình)", "Long - 20+ exchanges (Dài)"};

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                           @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_conversation, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        // Find views
        topicSpinner = view.findViewById(R.id.spinner_topic);
        levelSpinner = view.findViewById(R.id.spinner_level);
        styleSpinner = view.findViewById(R.id.spinner_style);
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

        // Style spinner
        ArrayAdapter<String> styleAdapter = new ArrayAdapter<>(requireContext(),
                android.R.layout.simple_spinner_item, stylesVi);
        styleAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        styleSpinner.setAdapter(styleAdapter);

        // Length spinner
        ArrayAdapter<String> lengthAdapter = new ArrayAdapter<>(requireContext(),
                android.R.layout.simple_spinner_item, lengthsVi);
        lengthAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        lengthSpinner.setAdapter(lengthAdapter);
    }

    private void setupHistoryRecycler() {
        historyRecycler.setLayoutManager(new LinearLayoutManager(getContext()));
        historyAdapter = new ConversationHistoryAdapter(new ArrayList<>(), this::deleteHistory);
        historyRecycler.setAdapter(historyAdapter);
    }

    private void generatePrompt() {
        int topicIndex = topicSpinner.getSelectedItemPosition();
        int levelIndex = levelSpinner.getSelectedItemPosition();
        int styleIndex = styleSpinner.getSelectedItemPosition();
        int lengthIndex = lengthSpinner.getSelectedItemPosition();

        currentTopic = topics[topicIndex];
        currentLevel = levels[levelIndex];
        currentStyle = styles[styleIndex];
        currentLength = lengths[lengthIndex];

        // Get a random context suggestion
        String[] contexts = PromptGenerator.getSuggestedContexts(currentTopic);
        String context = contexts[(int) (Math.random() * contexts.length)];

        currentPrompt = PromptGenerator.generateConversationPrompt(
                currentTopic, currentLevel, currentStyle, currentLength, context);

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
        ClipData clip = ClipData.newPlainText("Conversation Prompt", currentPrompt);
        clipboard.setPrimaryClip(clip);

        Toast.makeText(getContext(), "Đã copy! Paste vào ChatGPT hoặc Claude để luyện tập.", Toast.LENGTH_LONG).show();
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
                .setTitle("Lưu kết quả luyện tập")
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
        ConversationHistory history = new ConversationHistory();
        history.id = UUID.randomUUID().toString();
        history.topic = currentTopic;
        history.level = currentLevel;
        history.style = currentStyle;
        history.length = currentLength;
        history.prompt = currentPrompt;
        history.score = score;
        history.newVocabulary = vocabulary;
        history.createdAt = System.currentTimeMillis();

        AppDatabase db = ((StudyEnglishApp) requireActivity().getApplication()).getDatabase();
        AppDatabase.databaseWriteExecutor.execute(() -> {
            db.conversationHistoryDao().insert(history);
            requireActivity().runOnUiThread(() -> {
                Toast.makeText(getContext(), "Đã lưu kết quả!", Toast.LENGTH_SHORT).show();
            });
        });
    }

    private void loadHistory() {
        AppDatabase db = ((StudyEnglishApp) requireActivity().getApplication()).getDatabase();
        db.conversationHistoryDao().getRecent(20).observe(getViewLifecycleOwner(), history -> {
            historyAdapter.updateList(history);
        });
    }

    private void deleteHistory(ConversationHistory history) {
        new AlertDialog.Builder(requireContext())
                .setTitle("Xóa lịch sử")
                .setMessage("Bạn có chắc muốn xóa mục này?")
                .setPositiveButton("Xóa", (dialog, which) -> {
                    AppDatabase db = ((StudyEnglishApp) requireActivity().getApplication()).getDatabase();
                    AppDatabase.databaseWriteExecutor.execute(() -> db.conversationHistoryDao().delete(history));
                })
                .setNegativeButton("Hủy", null)
                .show();
    }
}
