package com.studyenglish.ui.vocabulary;

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
import android.widget.SeekBar;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.studyenglish.R;
import com.studyenglish.StudyEnglishApp;
import com.studyenglish.data.database.AppDatabase;
import com.studyenglish.data.entity.Vocabulary;

import java.util.UUID;

public class VocabularyGeneratorFragment extends Fragment {

    private Spinner topicSpinner;
    private Spinner levelSpinner;
    private SeekBar wordCountSeekBar;
    private TextView wordCountText;
    private TextView promptText;
    private EditText aiResponseEdit;
    private View promptCard;

    private String currentPrompt = "";
    private int wordCount = 10;

    private final String[] topics = {"Personal", "Work", "Travel", "Food", "Health", "Education", "Technology", "Entertainment", "Nature", "Sports"};
    private final String[] topicsVi = {
        "Personal (Giao tiếp cá nhân)",
        "Work and Business (Công việc và Kinh doanh)",
        "Travel (Du lịch)",
        "Food (Ẩm thực)",
        "Health (Sức khỏe)",
        "Education (Giáo dục)",
        "Technology (Công nghệ)",
        "Entertainment (Giải trí)",
        "Nature (Thiên nhiên)",
        "Sports (Thể thao)"
    };

    private final String[] levels = {"A1", "A2", "B1", "B2", "C1", "C2"};
    private final String[] levelsVi = {
        "A1 - Beginner (Cơ bản)",
        "A2 - Elementary (Sơ cấp)",
        "B1 - Intermediate (Trung cấp)",
        "B2 - Upper Intermediate (Trung cao)",
        "C1 - Advanced (Cao cấp)",
        "C2 - Proficiency (Thành thạo)"
    };

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                           @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_vocabulary_generator, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        // Find views
        topicSpinner = view.findViewById(R.id.spinner_topic);
        levelSpinner = view.findViewById(R.id.spinner_level);
        wordCountSeekBar = view.findViewById(R.id.seekbar_word_count);
        wordCountText = view.findViewById(R.id.text_word_count);
        promptText = view.findViewById(R.id.text_prompt);
        promptCard = view.findViewById(R.id.card_prompt);
        aiResponseEdit = view.findViewById(R.id.edit_ai_response);

        Button getPromptBtn = view.findViewById(R.id.btn_get_prompt);
        Button copyBtn = view.findViewById(R.id.btn_copy);
        Button saveBtn = view.findViewById(R.id.btn_save_vocabulary);

        setupSpinners();
        setupSeekBar();

        getPromptBtn.setOnClickListener(v -> generatePrompt());
        copyBtn.setOnClickListener(v -> copyPrompt());
        saveBtn.setOnClickListener(v -> saveVocabulary());
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
    }

    private void setupSeekBar() {
        wordCountSeekBar.setMax(20);
        wordCountSeekBar.setProgress(10);
        wordCountText.setText("10 words");

        wordCountSeekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                wordCount = Math.max(5, progress); // Minimum 5 words
                wordCountText.setText(wordCount + " words");
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });
    }

    private void generatePrompt() {
        int topicIndex = topicSpinner.getSelectedItemPosition();
        int levelIndex = levelSpinner.getSelectedItemPosition();

        String topic = topics[topicIndex];
        String level = levels[levelIndex];
        String levelDescription = getLevelDescription(level);

        StringBuilder prompt = new StringBuilder();
        prompt.append("Generate ").append(wordCount).append(" English vocabulary words for the topic \"")
              .append(topic).append("\" at ").append(level).append(" level (")
              .append(levelDescription).append(", practical vocabulary for daily use).\n\n");

        prompt.append("For each word, provide a JSON object with these exact fields:\n");
        prompt.append("- word: the English word\n");
        prompt.append("- meaning_vi: Vietnamese translation/meaning\n");
        prompt.append("- pronunciation: IPA pronunciation (e.g., /wɜːrd/)\n");
        prompt.append("- part_of_speech: noun, verb, adjective, or adverb\n");
        prompt.append("- example_en: an example sentence in English\n");
        prompt.append("- example_vi: Vietnamese translation of the example\n\n");

        prompt.append("Return ONLY a valid JSON array with no additional text. Example format:\n");
        prompt.append("[\n");
        prompt.append("  {\n");
        prompt.append("    \"word\": \"example\",\n");
        prompt.append("    \"meaning_vi\": \"ví dụ\",\n");
        prompt.append("    \"pronunciation\": \"/ɪɡˈzæmpl/\",\n");
        prompt.append("    \"part_of_speech\": \"noun\",\n");
        prompt.append("    \"example_en\": \"This is an example.\",\n");
        prompt.append("    \"example_vi\": \"Đây là một ví dụ.\"\n");
        prompt.append("  }\n");
        prompt.append("]\n\n");

        prompt.append("Generate ").append(wordCount).append(" unique, commonly used words for ").append(topic).append(" at ").append(level).append(" level.");

        currentPrompt = prompt.toString();
        promptText.setText(currentPrompt);
        promptCard.setVisibility(View.VISIBLE);

        Toast.makeText(getContext(), "Prompt đã được tạo! Nhấn Copy để sao chép.", Toast.LENGTH_SHORT).show();
    }

    private String getLevelDescription(String level) {
        switch (level) {
            case "A1": return "very basic, everyday words";
            case "A2": return "elementary, simple phrases";
            case "B1": return "intermediate level";
            case "B2": return "upper-intermediate";
            case "C1": return "advanced vocabulary";
            case "C2": return "proficiency level";
            default: return "intermediate level";
        }
    }

    private void copyPrompt() {
        if (currentPrompt.isEmpty()) {
            Toast.makeText(getContext(), "Vui lòng tạo prompt trước", Toast.LENGTH_SHORT).show();
            return;
        }

        ClipboardManager clipboard = (ClipboardManager) requireContext().getSystemService(Context.CLIPBOARD_SERVICE);
        ClipData clip = ClipData.newPlainText("Vocabulary Prompt", currentPrompt);
        clipboard.setPrimaryClip(clip);

        Toast.makeText(getContext(), "Đã copy! Paste vào ChatGPT hoặc Claude.", Toast.LENGTH_LONG).show();
    }

    private void saveVocabulary() {
        String jsonResponse = aiResponseEdit.getText().toString().trim();

        if (jsonResponse.isEmpty()) {
            Toast.makeText(getContext(), "Vui lòng paste JSON response từ AI", Toast.LENGTH_SHORT).show();
            return;
        }

        try {
            // Parse JSON array
            JsonArray jsonArray = JsonParser.parseString(jsonResponse).getAsJsonArray();

            int topicIndex = topicSpinner.getSelectedItemPosition();
            int levelIndex = levelSpinner.getSelectedItemPosition();
            String topic = topics[topicIndex];
            String level = levels[levelIndex];

            AppDatabase db = ((StudyEnglishApp) requireActivity().getApplication()).getDatabase();
            long now = System.currentTimeMillis();
            int savedCount = 0;

            for (JsonElement element : jsonArray) {
                JsonObject obj = element.getAsJsonObject();

                Vocabulary vocab = new Vocabulary();
                vocab.id = UUID.randomUUID().toString();
                vocab.word = getJsonString(obj, "word");
                vocab.definition = getJsonString(obj, "meaning_vi");
                vocab.pronunciation = getJsonString(obj, "pronunciation");
                vocab.partOfSpeech = getJsonString(obj, "part_of_speech");
                vocab.example = getJsonString(obj, "example_en");
                vocab.exampleTranslation = getJsonString(obj, "example_vi");
                vocab.topic = topic;
                vocab.level = level;
                vocab.createdAt = now;
                vocab.updatedAt = now;

                if (!vocab.word.isEmpty() && !vocab.definition.isEmpty()) {
                    AppDatabase.databaseWriteExecutor.execute(() -> db.vocabularyDao().insert(vocab));
                    savedCount++;
                }
            }

            final int finalCount = savedCount;
            requireActivity().runOnUiThread(() -> {
                Toast.makeText(getContext(), "Đã lưu " + finalCount + " từ vựng mới!", Toast.LENGTH_LONG).show();
                aiResponseEdit.setText("");
            });

        } catch (Exception e) {
            Toast.makeText(getContext(), "Lỗi parse JSON: " + e.getMessage() + "\n\nHãy đảm bảo AI trả về đúng format JSON.", Toast.LENGTH_LONG).show();
        }
    }

    private String getJsonString(JsonObject obj, String key) {
        if (obj.has(key) && !obj.get(key).isJsonNull()) {
            return obj.get(key).getAsString();
        }
        return "";
    }
}
