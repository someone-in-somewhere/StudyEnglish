package com.studyenglish.ui.vocabulary;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.studyenglish.R;
import com.studyenglish.data.entity.Vocabulary;

import java.util.List;

public class VocabularyAdapter extends RecyclerView.Adapter<VocabularyAdapter.ViewHolder> {

    private List<Vocabulary> vocabularyList;
    private final OnVocabularyClickListener listener;

    public interface OnVocabularyClickListener {
        void onClick(Vocabulary vocabulary);
    }

    public VocabularyAdapter(List<Vocabulary> vocabularyList, OnVocabularyClickListener listener) {
        this.vocabularyList = vocabularyList;
        this.listener = listener;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_vocabulary, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        Vocabulary vocab = vocabularyList.get(position);
        holder.bind(vocab);
    }

    @Override
    public int getItemCount() {
        return vocabularyList.size();
    }

    public void updateList(List<Vocabulary> newList) {
        this.vocabularyList = newList;
        notifyDataSetChanged();
    }

    class ViewHolder extends RecyclerView.ViewHolder {
        private final TextView wordText;
        private final TextView pronunciationText;
        private final TextView definitionText;
        private final TextView levelBadge;
        private final ImageView favoriteIcon;
        private final ImageView learnedIcon;

        ViewHolder(View itemView) {
            super(itemView);
            wordText = itemView.findViewById(R.id.text_word);
            pronunciationText = itemView.findViewById(R.id.text_pronunciation);
            definitionText = itemView.findViewById(R.id.text_definition);
            levelBadge = itemView.findViewById(R.id.badge_level);
            favoriteIcon = itemView.findViewById(R.id.icon_favorite);
            learnedIcon = itemView.findViewById(R.id.icon_learned);
        }

        void bind(Vocabulary vocab) {
            wordText.setText(vocab.word);
            pronunciationText.setText(vocab.pronunciation != null ? vocab.pronunciation : "");
            definitionText.setText(vocab.definition);
            levelBadge.setText(vocab.level);

            // Set level color
            int colorRes = getLevelColor(vocab.level);
            levelBadge.setBackgroundTintList(
                itemView.getContext().getColorStateList(colorRes)
            );

            // Icons
            favoriteIcon.setVisibility(vocab.isFavorite ? View.VISIBLE : View.GONE);
            learnedIcon.setVisibility(vocab.isLearned ? View.VISIBLE : View.GONE);

            // Click listener
            itemView.setOnClickListener(v -> listener.onClick(vocab));
        }

        private int getLevelColor(String level) {
            switch (level) {
                case "A1": return R.color.level_a1;
                case "A2": return R.color.level_a2;
                case "B1": return R.color.level_b1;
                case "B2": return R.color.level_b2;
                case "C1": return R.color.level_c1;
                case "C2": return R.color.level_c2;
                default: return R.color.primary;
            }
        }
    }
}
