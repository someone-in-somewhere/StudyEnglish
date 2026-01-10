package com.studyenglish.ui.vocabulary;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.SearchView;
import android.widget.Spinner;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;
import androidx.navigation.Navigation;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.studyenglish.R;
import com.studyenglish.data.entity.Vocabulary;

import java.util.ArrayList;
import java.util.List;

public class VocabularyFragment extends Fragment {

    private VocabularyViewModel viewModel;
    private VocabularyAdapter adapter;
    private RecyclerView recyclerView;
    private Spinner topicSpinner;
    private Spinner levelSpinner;
    private SearchView searchView;

    private String selectedTopic = "";
    private String selectedLevel = "";

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                           @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_vocabulary, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        viewModel = new ViewModelProvider(this).get(VocabularyViewModel.class);

        // Setup RecyclerView
        recyclerView = view.findViewById(R.id.recycler_vocabulary);
        recyclerView.setLayoutManager(new LinearLayoutManager(getContext()));
        adapter = new VocabularyAdapter(new ArrayList<>(), this::onVocabularyClick);
        recyclerView.setAdapter(adapter);

        // Setup Spinners
        topicSpinner = view.findViewById(R.id.spinner_topic);
        levelSpinner = view.findViewById(R.id.spinner_level);

        setupSpinners();

        // Setup SearchView
        searchView = view.findViewById(R.id.search_view);
        searchView.setOnQueryTextListener(new SearchView.OnQueryTextListener() {
            @Override
            public boolean onQueryTextSubmit(String query) {
                filterVocabulary();
                return true;
            }

            @Override
            public boolean onQueryTextChange(String newText) {
                filterVocabulary();
                return true;
            }
        });

        // Setup Add Vocabulary Button (AI Generator)
        Button addVocabBtn = view.findViewById(R.id.btn_add_vocab);
        addVocabBtn.setOnClickListener(v -> {
            Navigation.findNavController(v).navigate(R.id.action_vocabulary_to_generator);
        });

        // Observe vocabulary list
        viewModel.getAllVocabulary().observe(getViewLifecycleOwner(), vocabularies -> {
            adapter.updateList(vocabularies);
        });
    }

    private void setupSpinners() {
        // Topic spinner
        List<String> topics = new ArrayList<>();
        topics.add(getString(R.string.all_topics));
        topics.add("Personal");
        topics.add("Work");
        topics.add("Travel");
        topics.add("Food");
        topics.add("Health");
        topics.add("Education");
        topics.add("Technology");
        topics.add("Entertainment");
        topics.add("Nature");
        topics.add("Sports");

        ArrayAdapter<String> topicAdapter = new ArrayAdapter<>(
            requireContext(),
            android.R.layout.simple_spinner_item,
            topics
        );
        topicAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        topicSpinner.setAdapter(topicAdapter);
        topicSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                selectedTopic = position == 0 ? "" : topics.get(position);
                filterVocabulary();
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {}
        });

        // Level spinner
        List<String> levels = new ArrayList<>();
        levels.add(getString(R.string.all_levels));
        levels.add("A1");
        levels.add("A2");
        levels.add("B1");
        levels.add("B2");
        levels.add("C1");
        levels.add("C2");

        ArrayAdapter<String> levelAdapter = new ArrayAdapter<>(
            requireContext(),
            android.R.layout.simple_spinner_item,
            levels
        );
        levelAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        levelSpinner.setAdapter(levelAdapter);
        levelSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                selectedLevel = position == 0 ? "" : levels.get(position);
                filterVocabulary();
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {}
        });
    }

    private void filterVocabulary() {
        String query = searchView.getQuery().toString().trim();

        if (!query.isEmpty()) {
            viewModel.searchVocabulary(query).observe(getViewLifecycleOwner(), adapter::updateList);
        } else if (!selectedTopic.isEmpty() && !selectedLevel.isEmpty()) {
            viewModel.getByTopicAndLevel(selectedTopic, selectedLevel)
                .observe(getViewLifecycleOwner(), adapter::updateList);
        } else if (!selectedTopic.isEmpty()) {
            viewModel.getByTopic(selectedTopic).observe(getViewLifecycleOwner(), adapter::updateList);
        } else if (!selectedLevel.isEmpty()) {
            viewModel.getByLevel(selectedLevel).observe(getViewLifecycleOwner(), adapter::updateList);
        } else {
            viewModel.getAllVocabulary().observe(getViewLifecycleOwner(), adapter::updateList);
        }
    }

    private void onVocabularyClick(Vocabulary vocabulary) {
        // Navigate to detail or show dialog
        VocabularyDetailDialog dialog = VocabularyDetailDialog.newInstance(vocabulary);
        dialog.show(getParentFragmentManager(), "vocabulary_detail");
    }
}
