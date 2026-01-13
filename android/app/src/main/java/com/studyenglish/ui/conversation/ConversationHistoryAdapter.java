package com.studyenglish.ui.conversation;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.studyenglish.R;
import com.studyenglish.data.entity.ConversationHistory;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class ConversationHistoryAdapter extends RecyclerView.Adapter<ConversationHistoryAdapter.ViewHolder> {

    private List<ConversationHistory> historyList;
    private final OnDeleteClickListener deleteListener;
    private final SimpleDateFormat dateFormat = new SimpleDateFormat("dd/MM/yyyy HH:mm", Locale.getDefault());

    public interface OnDeleteClickListener {
        void onDelete(ConversationHistory history);
    }

    public ConversationHistoryAdapter(List<ConversationHistory> historyList, OnDeleteClickListener deleteListener) {
        this.historyList = historyList;
        this.deleteListener = deleteListener;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_practice_history, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        ConversationHistory history = historyList.get(position);
        holder.bind(history);
    }

    @Override
    public int getItemCount() {
        return historyList.size();
    }

    public void updateList(List<ConversationHistory> newList) {
        this.historyList = newList;
        notifyDataSetChanged();
    }

    class ViewHolder extends RecyclerView.ViewHolder {
        private final TextView dateText;
        private final TextView topicText;
        private final TextView levelText;
        private final TextView styleText;
        private final TextView lengthText;
        private final TextView scoreText;
        private final ImageButton deleteBtn;

        ViewHolder(View itemView) {
            super(itemView);
            dateText = itemView.findViewById(R.id.text_date);
            topicText = itemView.findViewById(R.id.text_topic);
            levelText = itemView.findViewById(R.id.text_level);
            styleText = itemView.findViewById(R.id.text_style);
            lengthText = itemView.findViewById(R.id.text_length);
            scoreText = itemView.findViewById(R.id.text_score);
            deleteBtn = itemView.findViewById(R.id.btn_delete);
        }

        void bind(ConversationHistory history) {
            dateText.setText(dateFormat.format(new Date(history.createdAt)));
            topicText.setText(history.topic);
            levelText.setText(history.level);
            styleText.setText(getStyleVi(history.style));
            lengthText.setText(getLengthVi(history.length));
            scoreText.setText(String.format(Locale.getDefault(), "%.1f", history.score));

            deleteBtn.setOnClickListener(v -> deleteListener.onDelete(history));
        }

        private String getStyleVi(String style) {
            switch (style) {
                case "casual": return "Thân mật";
                case "formal": return "Trang trọng";
                case "business": return "Công việc";
                default: return style;
            }
        }

        private String getLengthVi(String length) {
            switch (length) {
                case "short": return "Ngắn";
                case "medium": return "Trung bình";
                case "long": return "Dài";
                default: return length;
            }
        }
    }
}
