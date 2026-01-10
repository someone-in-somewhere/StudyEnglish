package com.studyenglish.ui.vocabulary;

import android.app.Dialog;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.fragment.app.DialogFragment;
import androidx.lifecycle.ViewModelProvider;

import com.studyenglish.R;
import com.studyenglish.data.entity.Vocabulary;

import java.util.Locale;

public class VocabularyDetailDialog extends DialogFragment {

    private static final String ARG_VOCAB_ID = "vocab_id";
    private static final String ARG_VOCAB_WORD = "vocab_word";
    private static final String ARG_VOCAB_PRONUNCIATION = "vocab_pronunciation";
    private static final String ARG_VOCAB_DEFINITION = "vocab_definition";
    private static final String ARG_VOCAB_EXAMPLE = "vocab_example";
    private static final String ARG_VOCAB_LEVEL = "vocab_level";
    private static final String ARG_VOCAB_TOPIC = "vocab_topic";

    private TextToSpeech tts;
    private VocabularyViewModel viewModel;

    public static VocabularyDetailDialog newInstance(Vocabulary vocab) {
        VocabularyDetailDialog dialog = new VocabularyDetailDialog();
        Bundle args = new Bundle();
        args.putString(ARG_VOCAB_ID, vocab.id);
        args.putString(ARG_VOCAB_WORD, vocab.word);
        args.putString(ARG_VOCAB_PRONUNCIATION, vocab.pronunciation);
        args.putString(ARG_VOCAB_DEFINITION, vocab.definition);
        args.putString(ARG_VOCAB_EXAMPLE, vocab.example);
        args.putString(ARG_VOCAB_LEVEL, vocab.level);
        args.putString(ARG_VOCAB_TOPIC, vocab.topic);
        dialog.setArguments(args);
        return dialog;
    }

    @NonNull
    @Override
    public Dialog onCreateDialog(@Nullable Bundle savedInstanceState) {
        viewModel = new ViewModelProvider(this).get(VocabularyViewModel.class);

        View view = LayoutInflater.from(getContext())
                .inflate(R.layout.dialog_vocabulary_detail, null);

        Bundle args = getArguments();
        if (args != null) {
            TextView wordText = view.findViewById(R.id.text_word);
            TextView pronunciationText = view.findViewById(R.id.text_pronunciation);
            TextView definitionText = view.findViewById(R.id.text_definition);
            TextView exampleText = view.findViewById(R.id.text_example);
            TextView levelText = view.findViewById(R.id.text_level);
            TextView topicText = view.findViewById(R.id.text_topic);
            ImageButton speakButton = view.findViewById(R.id.btn_speak);

            wordText.setText(args.getString(ARG_VOCAB_WORD, ""));
            pronunciationText.setText(args.getString(ARG_VOCAB_PRONUNCIATION, ""));
            definitionText.setText(args.getString(ARG_VOCAB_DEFINITION, ""));
            exampleText.setText(args.getString(ARG_VOCAB_EXAMPLE, ""));
            levelText.setText(args.getString(ARG_VOCAB_LEVEL, ""));
            topicText.setText(args.getString(ARG_VOCAB_TOPIC, ""));

            // Text-to-Speech
            tts = new TextToSpeech(getContext(), status -> {
                if (status == TextToSpeech.SUCCESS) {
                    tts.setLanguage(Locale.US);
                }
            });

            speakButton.setOnClickListener(v -> {
                String word = args.getString(ARG_VOCAB_WORD, "");
                if (tts != null && !word.isEmpty()) {
                    tts.speak(word, TextToSpeech.QUEUE_FLUSH, null, null);
                }
            });
        }

        return new AlertDialog.Builder(requireContext())
                .setView(view)
                .setPositiveButton(R.string.ok, null)
                .create();
    }

    @Override
    public void onDestroy() {
        if (tts != null) {
            tts.stop();
            tts.shutdown();
        }
        super.onDestroy();
    }
}
