/**
 * StudyEnglish - Main Application JavaScript
 * Handles all page interactions and API communication
 */

// API Base URL
const API_BASE = '/api';

// Utility Functions
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

function speakWord(word) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.lang = 'en-US';
        speechSynthesis.speak(utterance);
    }
}

// Main App Component
document.addEventListener('alpine:init', () => {
    // Global App State
    Alpine.data('app', () => ({
        sidebarOpen: window.innerWidth >= 1024,
        currentPage: 'dashboard',
        pageTitle: 'Dashboard',
        pageDescription: 'Overview of your learning progress',
        searchQuery: '',
        showNotifications: false,
        notifications: [],
        toasts: [],

        stats: {
            streak: 0,
            wordsLearned: 0
        },

        navSections: [
            {
                title: 'Learning',
                items: [
                    { id: 'dashboard', name: 'Dashboard', icon: 'fas fa-home' },
                    { id: 'vocabulary', name: 'Vocabulary', icon: 'fas fa-book' },
                    { id: 'quiz', name: 'Quiz', icon: 'fas fa-question-circle' },
                    { id: 'srs', name: 'Review', icon: 'fas fa-redo', badge: null },
                ]
            },
            {
                title: 'Practice',
                items: [
                    { id: 'chat', name: 'AI Chat', icon: 'fas fa-comments' },
                    { id: 'exercises', name: 'Exercises', icon: 'fas fa-dumbbell' },
                    { id: 'reading', name: 'Reading', icon: 'fas fa-book-reader' },
                    { id: 'writing', name: 'Writing', icon: 'fas fa-pen' },
                ]
            },
            {
                title: 'Tools',
                items: [
                    { id: 'translation', name: 'Translation', icon: 'fas fa-language' },
                    { id: 'flashcards', name: 'Flashcards', icon: 'fas fa-clone' },
                    { id: 'errors', name: 'Error Analysis', icon: 'fas fa-bug' },
                    { id: 'learning-paths', name: 'Learning Paths', icon: 'fas fa-route' },
                ]
            }
        ],

        init() {
            this.loadStats();
            this.loadDueReviews();

            // Listen for navigation events
            window.addEventListener('navigate', (e) => {
                this.navigateTo(e.detail);
            });

            // Handle resize
            window.addEventListener('resize', () => {
                this.sidebarOpen = window.innerWidth >= 1024;
            });
        },

        async loadStats() {
            try {
                const response = await fetchAPI('/progress/stats');
                if (response.success) {
                    this.stats.streak = response.stats.current_streak || 0;
                    this.stats.wordsLearned = response.stats.total_words || 0;
                }
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        },

        async loadDueReviews() {
            try {
                const response = await fetchAPI('/srs/due-reviews?limit=1');
                if (response.success && response.count > 0) {
                    const reviewNav = this.navSections[0].items.find(i => i.id === 'srs');
                    if (reviewNav) {
                        reviewNav.badge = response.count;
                    }
                }
            } catch (error) {
                console.error('Failed to load due reviews:', error);
            }
        },

        navigateTo(page) {
            this.currentPage = page;

            const pageTitles = {
                'dashboard': { title: 'Dashboard', desc: 'Overview of your learning progress' },
                'vocabulary': { title: 'Vocabulary', desc: 'Learn new words with AI' },
                'quiz': { title: 'Quiz', desc: 'Test your vocabulary knowledge' },
                'translation': { title: 'Translation', desc: 'English ↔ Vietnamese translation' },
                'srs': { title: 'Spaced Repetition', desc: 'Review words for long-term memory' },
                'chat': { title: 'AI Chat', desc: 'Practice conversation with AI tutor' },
                'exercises': { title: 'Exercises', desc: 'Grammar and vocabulary exercises' },
                'reading': { title: 'Reading', desc: 'Reading comprehension practice' },
                'writing': { title: 'Writing', desc: 'Writing practice with feedback' },
                'flashcards': { title: 'Flashcards', desc: 'Study with flashcards' },
                'errors': { title: 'Error Analysis', desc: 'Track and improve your weaknesses' },
                'learning-paths': { title: 'Learning Paths', desc: 'Structured learning curriculum' },
            };

            const pageInfo = pageTitles[page] || { title: 'StudyEnglish', desc: '' };
            this.pageTitle = pageInfo.title;
            this.pageDescription = pageInfo.desc;

            // Close sidebar on mobile
            if (window.innerWidth < 1024) {
                this.sidebarOpen = false;
            }
        },

        showToast(message, type = 'info') {
            const id = Date.now();
            this.toasts.push({ id, message, type });

            setTimeout(() => {
                this.toasts = this.toasts.filter(t => t.id !== id);
            }, 3000);
        },

        searchVocabulary() {
            if (this.searchQuery.trim()) {
                this.navigateTo('vocabulary');
                // Trigger search in vocabulary page
                window.dispatchEvent(new CustomEvent('search-vocabulary', {
                    detail: this.searchQuery
                }));
            }
        }
    }));

    // Dashboard Page Component
    Alpine.data('dashboardPage', () => ({
        dashStats: {
            totalWords: 0,
            quizAvg: 0,
            streak: 0,
            studyTime: 0,
            dueReviews: 0
        },
        progressChart: null,
        topicsChart: null,

        async init() {
            await this.loadDashboardData();
            this.initCharts();
        },

        async loadDashboardData() {
            try {
                const [statsRes, srsRes] = await Promise.all([
                    fetchAPI('/progress/stats'),
                    fetchAPI('/srs/stats')
                ]);

                if (statsRes.success) {
                    this.dashStats.totalWords = statsRes.stats.total_words || 0;
                    this.dashStats.quizAvg = statsRes.stats.quiz_avg_score || 0;
                    this.dashStats.streak = statsRes.stats.current_streak || 0;
                    this.dashStats.studyTime = statsRes.stats.total_study_time || 0;
                }

                if (srsRes.success) {
                    this.dashStats.dueReviews = srsRes.stats.due_now || 0;
                }
            } catch (error) {
                console.error('Failed to load dashboard data:', error);
            }
        },

        initCharts() {
            // Progress Chart
            const progressCtx = document.getElementById('progressChart');
            if (progressCtx) {
                this.progressChart = new Chart(progressCtx, {
                    type: 'line',
                    data: {
                        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                        datasets: [{
                            label: 'Words Learned',
                            data: [5, 8, 12, 7, 10, 15, 9],
                            borderColor: '#3B82F6',
                            tension: 0.4,
                            fill: true,
                            backgroundColor: 'rgba(59, 130, 246, 0.1)'
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
            }

            // Topics Chart
            const topicsCtx = document.getElementById('topicsChart');
            if (topicsCtx) {
                this.topicsChart = new Chart(topicsCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Work', 'Travel', 'Food', 'Technology', 'Other'],
                        datasets: [{
                            data: [30, 25, 20, 15, 10],
                            backgroundColor: [
                                '#3B82F6',
                                '#10B981',
                                '#F59E0B',
                                '#8B5CF6',
                                '#6B7280'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'bottom' }
                        }
                    }
                });
            }
        }
    }));

    // Vocabulary Page Component
    Alpine.data('vocabularyPage', () => ({
        topics: [],
        vocabulary: [],
        selectedTopic: '',
        selectedLevel: 'B1',
        numWords: 10,
        loading: false,
        generatedPrompt: '',
        aiResponse: '',
        saveResult: null,

        async init() {
            await this.loadTopics();

            // Listen for search events
            window.addEventListener('search-vocabulary', (e) => {
                this.searchVocabulary(e.detail);
            });
        },

        async loadTopics() {
            try {
                const response = await fetchAPI('/topics');
                if (response.success) {
                    this.topics = response.topics;
                }
            } catch (error) {
                console.error('Failed to load topics:', error);
            }
        },

        generatePrompt() {
            if (!this.selectedTopic) return;

            this.saveResult = null;
            this.aiResponse = '';

            const levelDescriptions = {
                'A1': 'very basic, everyday words for beginners',
                'A2': 'elementary level, simple and common words',
                'B1': 'intermediate level, practical vocabulary for daily use',
                'B2': 'upper-intermediate, more complex and nuanced vocabulary',
                'C1': 'advanced vocabulary including idiomatic expressions',
                'C2': 'proficiency level, sophisticated and specialized vocabulary'
            };

            const levelDesc = levelDescriptions[this.selectedLevel] || 'intermediate level vocabulary';

            this.generatedPrompt = `Generate ${this.numWords} English vocabulary words for the topic "${this.selectedTopic}" at ${this.selectedLevel} level (${levelDesc}).

For each word, provide a JSON object with these exact fields:
- word: the English word
- meaning_vi: Vietnamese translation/meaning
- pronunciation: IPA pronunciation (e.g., /wɜːrd/)
- part_of_speech: noun, verb, adjective, or adverb
- example_en: an example sentence in English
- example_vi: Vietnamese translation of the example
- synonyms: 2-3 synonyms separated by comma

Output as a JSON array. Example format:
[
  {
    "word": "collaborate",
    "meaning_vi": "hợp tác, cộng tác",
    "pronunciation": "/kəˈlæbəreɪt/",
    "part_of_speech": "verb",
    "example_en": "We need to collaborate with other teams to finish this project.",
    "example_vi": "Chúng ta cần hợp tác với các đội khác để hoàn thành dự án này.",
    "synonyms": "cooperate, work together, team up"
  }
]

Generate ${this.numWords} words for "${this.selectedTopic}" at ${this.selectedLevel} level. Output ONLY the JSON array, no explanation.`;
        },

        copyPrompt() {
            navigator.clipboard.writeText(this.generatedPrompt);
            Alpine.store('app')?.showToast?.('Prompt copied to clipboard!', 'success');
        },

        async saveVocabulary() {
            if (!this.aiResponse.trim()) return;

            this.loading = true;
            this.saveResult = null;

            try {
                const response = await fetchAPI('/vocabulary/import', {
                    method: 'POST',
                    body: JSON.stringify({
                        topic: this.selectedTopic,
                        level: this.selectedLevel,
                        ai_response: this.aiResponse
                    })
                });

                console.log('Save response:', response);

                if (response.success) {
                    this.saveResult = {
                        added: response.added,
                        duplicates: response.duplicates
                    };
                    this.vocabulary = response.vocabulary || [];
                    this.aiResponse = '';
                    Alpine.store('app')?.showToast?.(`Saved ${response.added} new words!`, 'success');
                } else {
                    Alpine.store('app')?.showToast?.(response.message || 'Failed to save vocabulary', 'error');
                }
            } catch (error) {
                console.error('Failed to save vocabulary:', error);
                Alpine.store('app')?.showToast?.('Failed to save vocabulary. Check JSON format.', 'error');
            } finally {
                this.loading = false;
            }
        },

        async markAsLearned(vocabId) {
            try {
                const response = await fetchAPI('/vocabulary/mark-learned', {
                    method: 'POST',
                    body: JSON.stringify({ vocabulary_id: vocabId })
                });

                if (response.success) {
                    Alpine.store('app')?.showToast?.('Word marked as learned!', 'success');
                }
            } catch (error) {
                console.error('Failed to mark as learned:', error);
            }
        },

        async toggleFavorite(vocabId) {
            try {
                await fetchAPI(`/vocabulary/toggle-favorite/${vocabId}`, {
                    method: 'POST'
                });
            } catch (error) {
                console.error('Failed to toggle favorite:', error);
            }
        },

        speakWord(word) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(word);
                utterance.lang = 'en-US';
                speechSynthesis.speak(utterance);
            }
        }
    }));

    // Quiz Page Component
    Alpine.data('quizPage', () => ({
        topics: [],
        quizType: 'multiple_choice',
        quizTopic: '',
        numQuestions: 10,
        loading: false,
        quizActive: false,
        quizComplete: false,
        quizId: null,
        questions: [],
        currentQuestion: 0,
        selectedAnswer: null,
        fillBlankAnswer: '',
        answers: [],
        timeElapsed: 0,
        timerInterval: null,
        score: 0,
        correctAnswers: 0,
        quizFeedback: [],

        async init() {
            await this.loadTopics();
        },

        async loadTopics() {
            try {
                const response = await fetchAPI('/topics/list');
                if (response.success) {
                    this.topics = response.topics;
                }
            } catch (error) {
                console.error('Failed to load topics:', error);
            }
        },

        async startQuiz() {
            this.loading = true;

            try {
                const response = await fetchAPI('/quiz/generate', {
                    method: 'POST',
                    body: JSON.stringify({
                        quiz_type: this.quizType,
                        topic: this.quizTopic || null,
                        num_questions: parseInt(this.numQuestions)
                    })
                });

                if (response.success) {
                    this.quizId = response.quiz_id;
                    this.questions = response.questions;
                    this.quizActive = true;
                    this.currentQuestion = 0;
                    this.answers = [];
                    this.startTimer();
                } else {
                    alert(response.message || 'Failed to generate quiz');
                }
            } catch (error) {
                console.error('Failed to start quiz:', error);
                alert('Failed to start quiz. Make sure you have learned some vocabulary first.');
            } finally {
                this.loading = false;
            }
        },

        startTimer() {
            this.timeElapsed = 0;
            this.timerInterval = setInterval(() => {
                this.timeElapsed++;
            }, 1000);
        },

        stopTimer() {
            if (this.timerInterval) {
                clearInterval(this.timerInterval);
                this.timerInterval = null;
            }
        },

        formatTime(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return `${mins}:${secs.toString().padStart(2, '0')}`;
        },

        selectAnswer(idx) {
            this.selectedAnswer = idx;
        },

        previousQuestion() {
            if (this.currentQuestion > 0) {
                this.saveCurrentAnswer();
                this.currentQuestion--;
                this.loadSavedAnswer();
            }
        },

        nextQuestion() {
            this.saveCurrentAnswer();

            if (this.currentQuestion < this.questions.length - 1) {
                this.currentQuestion++;
                this.loadSavedAnswer();
            } else {
                this.finishQuiz();
            }
        },

        saveCurrentAnswer() {
            const questionId = this.questions[this.currentQuestion]?.id;
            let answer;

            if (this.quizType === 'fill_blank') {
                answer = this.fillBlankAnswer;
            } else {
                answer = this.selectedAnswer;
            }

            const existingIdx = this.answers.findIndex(a => a.question_id === questionId);
            if (existingIdx >= 0) {
                this.answers[existingIdx].user_answer = answer;
            } else {
                this.answers.push({ question_id: questionId, user_answer: answer });
            }
        },

        loadSavedAnswer() {
            const questionId = this.questions[this.currentQuestion]?.id;
            const saved = this.answers.find(a => a.question_id === questionId);

            if (this.quizType === 'fill_blank') {
                this.fillBlankAnswer = saved?.user_answer || '';
            } else {
                this.selectedAnswer = saved?.user_answer ?? null;
            }
        },

        async finishQuiz() {
            this.stopTimer();
            this.loading = true;

            try {
                const response = await fetchAPI('/quiz/submit', {
                    method: 'POST',
                    body: JSON.stringify({
                        quiz_id: this.quizId,
                        answers: this.answers,
                        time_taken: this.timeElapsed
                    })
                });

                if (response.success) {
                    this.score = response.score;
                    this.correctAnswers = response.correct_answers;
                    this.quizFeedback = response.feedback;
                    this.quizComplete = true;
                }
            } catch (error) {
                console.error('Failed to submit quiz:', error);
            } finally {
                this.loading = false;
            }
        },

        resetQuiz() {
            this.quizActive = false;
            this.quizComplete = false;
            this.questions = [];
            this.answers = [];
            this.selectedAnswer = null;
            this.fillBlankAnswer = '';
            this.currentQuestion = 0;
            this.timeElapsed = 0;
        }
    }));

    // Translation Page Component
    Alpine.data('translationPage', () => ({
        sourceLang: 'en',
        targetLang: 'vi',
        sourceText: '',
        translatedText: '',
        adjustLevel: '',
        loading: false,
        history: [],

        async init() {
            await this.loadHistory();
        },

        async loadHistory() {
            try {
                const response = await fetchAPI('/translation/history?limit=10');
                if (response.success) {
                    this.history = response.translations;
                }
            } catch (error) {
                console.error('Failed to load history:', error);
            }
        },

        swapLanguages() {
            const temp = this.sourceLang;
            this.sourceLang = this.targetLang;
            this.targetLang = temp;

            const tempText = this.sourceText;
            this.sourceText = this.translatedText;
            this.translatedText = tempText;
        },

        async translate() {
            if (!this.sourceText.trim()) return;

            this.loading = true;

            try {
                const response = await fetchAPI('/translation/translate', {
                    method: 'POST',
                    body: JSON.stringify({
                        text: this.sourceText,
                        source_lang: this.sourceLang,
                        target_lang: this.targetLang,
                        level: this.adjustLevel || null
                    })
                });

                if (response.success) {
                    this.translatedText = response.translated_text;
                    await this.loadHistory();
                }
            } catch (error) {
                console.error('Translation failed:', error);
            } finally {
                this.loading = false;
            }
        },

        copyTranslation() {
            navigator.clipboard.writeText(this.translatedText);
            Alpine.store('app')?.showToast?.('Copied to clipboard!', 'success');
        },

        loadTranslation(item) {
            this.sourceText = item.source_text;
            this.translatedText = item.translated_text;
            this.sourceLang = item.source_lang;
            this.targetLang = item.target_lang;
        }
    }));

    // SRS Page Component
    Alpine.data('srsPage', () => ({
        srsStats: {
            dueNow: 0,
            dueToday: 0,
            totalInSRS: 0,
            successRate: 0
        },
        dueReviews: [],
        reviewActive: false,
        currentReviewIndex: 0,
        currentReview: null,
        showAnswer: false,

        async init() {
            await this.loadStats();
            await this.loadDueReviews();
        },

        async loadStats() {
            try {
                const response = await fetchAPI('/srs/stats');
                if (response.success) {
                    this.srsStats = {
                        dueNow: response.stats.due_now || 0,
                        dueToday: response.stats.due_today || 0,
                        totalInSRS: response.stats.total_in_srs || 0,
                        successRate: response.stats.success_rate || 0
                    };
                }
            } catch (error) {
                console.error('Failed to load SRS stats:', error);
            }
        },

        async loadDueReviews() {
            try {
                const response = await fetchAPI('/srs/due-reviews?limit=50');
                if (response.success) {
                    this.dueReviews = response.reviews;
                }
            } catch (error) {
                console.error('Failed to load due reviews:', error);
            }
        },

        startReview() {
            if (this.dueReviews.length === 0) return;

            this.reviewActive = true;
            this.currentReviewIndex = 0;
            this.loadCurrentReview();
        },

        loadCurrentReview() {
            if (this.currentReviewIndex < this.dueReviews.length) {
                this.currentReview = this.dueReviews[this.currentReviewIndex];
                this.showAnswer = false;
            } else {
                this.finishReview();
            }
        },

        async submitReview(performance) {
            try {
                await fetchAPI('/srs/review', {
                    method: 'POST',
                    body: JSON.stringify({
                        vocabulary_id: this.currentReview.id,
                        performance: performance
                    })
                });

                this.currentReviewIndex++;
                this.loadCurrentReview();
            } catch (error) {
                console.error('Failed to submit review:', error);
            }
        },

        finishReview() {
            this.reviewActive = false;
            this.loadStats();
            this.loadDueReviews();
            Alpine.store('app')?.showToast?.('Review session complete!', 'success');
        },

        speakWord(word) {
            if ('speechSynthesis' in window && word) {
                const utterance = new SpeechSynthesisUtterance(word);
                utterance.lang = 'en-US';
                speechSynthesis.speak(utterance);
            }
        }
    }));

    // Chat Page Component
    Alpine.data('chatPage', () => ({
        messages: [],
        inputMessage: '',
        loading: false,
        sessionId: null,

        init() {
            this.sessionId = 'session_' + Date.now();
            this.messages.push({
                id: 1,
                role: 'assistant',
                message: "Hello! I'm your English tutor. Feel free to chat with me to practice your English. I'll help correct any grammar mistakes you make. What would you like to talk about today?",
                corrections: []
            });
        },

        async sendMessage() {
            if (!this.inputMessage.trim() || this.loading) return;

            const userMessage = this.inputMessage.trim();
            this.inputMessage = '';

            // Add user message
            this.messages.push({
                id: Date.now(),
                role: 'user',
                message: userMessage,
                corrections: []
            });

            this.loading = true;
            this.scrollToBottom();

            try {
                const response = await fetchAPI('/chat/message', {
                    method: 'POST',
                    body: JSON.stringify({
                        message: userMessage,
                        session_id: this.sessionId
                    })
                });

                if (response.success) {
                    // Update user message with corrections
                    if (response.corrections && response.corrections.length > 0) {
                        const lastUserMsg = this.messages.find(m => m.message === userMessage);
                        if (lastUserMsg) {
                            lastUserMsg.corrections = response.corrections;
                        }
                    }

                    // Add assistant response
                    this.messages.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        message: response.response,
                        corrections: []
                    });
                }
            } catch (error) {
                console.error('Chat failed:', error);
                this.messages.push({
                    id: Date.now() + 1,
                    role: 'assistant',
                    message: "I'm sorry, I encountered an error. Please try again.",
                    corrections: []
                });
            } finally {
                this.loading = false;
                this.scrollToBottom();
            }
        },

        scrollToBottom() {
            this.$nextTick(() => {
                const container = document.getElementById('chatMessages');
                if (container) {
                    container.scrollTop = container.scrollHeight;
                }
            });
        },

        clearChat() {
            this.messages = [];
            this.sessionId = 'session_' + Date.now();
            this.init();
        }
    }));
});
