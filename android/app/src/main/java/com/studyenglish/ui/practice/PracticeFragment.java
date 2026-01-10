package com.studyenglish.ui.practice;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.navigation.Navigation;

import com.studyenglish.R;

public class PracticeFragment extends Fragment {

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                           @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_practice, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        View conversationCard = view.findViewById(R.id.card_conversation);
        View translationCard = view.findViewById(R.id.card_translation);

        conversationCard.setOnClickListener(v -> {
            Navigation.findNavController(v).navigate(R.id.action_practice_to_conversation);
        });

        translationCard.setOnClickListener(v -> {
            Navigation.findNavController(v).navigate(R.id.action_practice_to_translation);
        });
    }
}
