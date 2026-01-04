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
                    { id: 'quiz', name: 'Quiz Vocabulary', icon: 'fas fa-question-circle' },
                    { id: 'srs', name: 'Review', icon: 'fas fa-redo', badge: null },
                ]
            },
            {
                title: 'Tools',
                items: [
                    { id: 'translation', name: 'Translation', icon: 'fas fa-language' },
                    { id: 'flashcards', name: 'Flashcards', icon: 'fas fa-clone' },
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
                'quiz': { title: 'Quiz Vocabulary', desc: 'Test your vocabulary knowledge' },
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
        viewMode: 'saved', // 'saved' or 'learned'

        // Vietnamese translations for topics
        topicTranslations: {
            'Personal and Communication': 'Giao tiếp cá nhân',
            'Work and Business': 'Công việc và Kinh doanh',
            'Meetings and Presentations': 'Họp và Thuyết trình',
            'Email and Written Communication': 'Email và Giao tiếp văn bản',
            'Small Talk and Social Skills': 'Trò chuyện xã giao',
            'Science and Technology': 'Khoa học và Công nghệ',
            'Transportation and Travel': 'Giao thông và Du lịch',
            'Shopping and Money': 'Mua sắm và Tiền bạc',
            'Everyday Life': 'Cuộc sống hàng ngày',
            'Food and Drink': 'Đồ ăn và Thức uống',
            'Entertainment and Leisure': 'Giải trí và Nghỉ ngơi',
            'Health and Medicine': 'Sức khỏe và Y tế',
            'School and Education': 'Trường học và Giáo dục',
            'Public Services': 'Dịch vụ công cộng',
            'Nature and Environment': 'Thiên nhiên và Môi trường',
            'Sports and Fitness': 'Thể thao và Rèn luyện',
            'Culture and Society': 'Văn hóa và Xã hội',
            'Arts and Literature': 'Nghệ thuật và Văn học',
            'History and Geography': 'Lịch sử và Địa lý',
            'Government and Politics': 'Chính phủ và Chính trị',
            'Law and Justice': 'Pháp luật và Công lý',
            'Religion and Spirituality': 'Tôn giáo và Tâm linh',
            'Philosophy and Ethics': 'Triết học và Đạo đức'
        },

        getTopicLabel(topicName) {
            const viTrans = this.topicTranslations[topicName];
            return viTrans ? `${topicName} (${viTrans})` : topicName;
        },

        formatDate(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            return date.toLocaleDateString('vi-VN', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        async removeFromLearned(vocabId) {
            if (!confirm('Bạn có chắc muốn xóa từ này khỏi danh sách đã học?')) return;

            try {
                const response = await fetchAPI(`/vocabulary/unlearn/${vocabId}`, {
                    method: 'DELETE'
                });

                if (response.success) {
                    // Remove from current list
                    this.vocabulary = this.vocabulary.filter(v => v.id !== vocabId);
                    Alpine.store('app')?.showToast?.('Đã xóa khỏi danh sách học', 'success');
                } else {
                    Alpine.store('app')?.showToast?.(response.message || 'Không thể xóa', 'error');
                }
            } catch (error) {
                console.error('Failed to remove from learned:', error);
                Alpine.store('app')?.showToast?.('Không thể xóa từ vựng', 'error');
            }
        },

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

        async loadSavedVocabulary() {
            if (!this.selectedTopic) return;

            this.loading = true;
            this.generatedPrompt = '';
            this.saveResult = null;
            this.viewMode = 'saved';

            try {
                const url = `/vocabulary/topic/${encodeURIComponent(this.selectedTopic)}?level=${this.selectedLevel}`;
                const response = await fetchAPI(url);

                if (response.success) {
                    this.vocabulary = response.vocabulary || [];
                    if (this.vocabulary.length > 0) {
                        Alpine.store('app')?.showToast?.(`Loaded ${response.count} saved words`, 'success');
                    } else {
                        Alpine.store('app')?.showToast?.('No saved vocabulary for this topic/level', 'info');
                    }
                }
            } catch (error) {
                console.error('Failed to load vocabulary:', error);
                Alpine.store('app')?.showToast?.('Failed to load vocabulary', 'error');
            } finally {
                this.loading = false;
            }
        },

        async loadLearnedVocabulary() {
            this.loading = true;
            this.generatedPrompt = '';
            this.saveResult = null;
            this.viewMode = 'learned';

            try {
                // Load ALL learned vocabulary (no topic/level filter)
                const response = await fetchAPI('/vocabulary/learned?limit=200');

                if (response.success) {
                    this.vocabulary = response.vocabulary || [];
                    if (this.vocabulary.length > 0) {
                        Alpine.store('app')?.showToast?.(`Loaded ${response.count} learned words`, 'success');
                    } else {
                        Alpine.store('app')?.showToast?.('No learned vocabulary yet. Click "Learn" on words to add them.', 'info');
                    }
                }
            } catch (error) {
                console.error('Failed to load learned vocabulary:', error);
                Alpine.store('app')?.showToast?.('Failed to load learned vocabulary', 'error');
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
                    // Update local vocabulary state to show it's learned
                    const wordIndex = this.vocabulary.findIndex(v => v.id === vocabId);
                    if (wordIndex !== -1) {
                        this.vocabulary[wordIndex].user_progress = {
                            learned_at: new Date().toISOString(),
                            review_count: 0,
                            mastery_level: 1
                        };
                    }
                    Alpine.store('app')?.showToast?.('Đã thêm vào danh sách học!', 'success');
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
        quizType: 'multiple_choice',
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
        // Matching quiz state
        selectedMatchWord: null,
        matchingAnswers: {},

        async init() {
            // Quiz uses learned vocabulary only, no topics needed
        },

        async startQuiz() {
            this.loading = true;

            try {
                // Generate quiz from all learned vocabulary (use_learned_only is default true in backend)
                const response = await fetchAPI('/quiz/generate', {
                    method: 'POST',
                    body: JSON.stringify({
                        quiz_type: this.quizType,
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
                    alert(response.message || 'Không thể tạo quiz. Hãy học thêm từ mới trước!');
                }
            } catch (error) {
                console.error('Failed to start quiz:', error);
                alert('Không thể tạo quiz. Hãy vào mục Vocabulary và nhấn "Learn" để thêm từ vào danh sách học trước.');
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

        // Matching quiz functions
        selectMatchWord(wordId) {
            this.selectedMatchWord = wordId;
        },

        selectMatchMeaning(meaningId) {
            if (this.selectedMatchWord !== null) {
                this.matchingAnswers[this.selectedMatchWord] = meaningId;
                this.selectedMatchWord = null;
            }
        },

        getMatchedMeaning(wordId) {
            const meaningId = this.matchingAnswers[wordId];
            if (!meaningId) return '';
            const question = this.questions[this.currentQuestion];
            const meaning = question?.meanings?.find(m => m.id === meaningId);
            return meaning ? String.fromCharCode(64 + meaningId) : '';
        },

        isMeaningMatched(meaningId) {
            return Object.values(this.matchingAnswers).includes(meaningId);
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
            } else if (this.quizType === 'matching') {
                answer = { ...this.matchingAnswers };
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
            } else if (this.quizType === 'matching') {
                this.matchingAnswers = saved?.user_answer || {};
                this.selectedMatchWord = null;
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
            this.matchingAnswers = {};
            this.selectedMatchWord = null;
            this.currentQuestion = 0;
            this.timeElapsed = 0;
        }
    }));

    // Translation Page Component
    Alpine.data('translationPage', () => ({
        loading: false,
        // Translation Practice
        practiceTopic: '',
        practiceLevel: '',
        practiceLength: '',
        practiceDirection: '',
        sentenceComplexity: '',
        practicePrompt: '',
        // Conversation Practice
        chatTopic: '',
        chatLevel: '',
        chatStyle: '',
        chatPrompt: '',

        async init() {
            // No initialization needed
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
        },

        generatePracticePrompt() {
            const lengthMap = {
                'short': '5-8 sentences',
                'medium': '13-15 sentences',
                'long': '17-25 sentences'
            };

            const levelDescMap = {
                'A1': 'very simple vocabulary and basic grammar (present tense, simple sentences)',
                'A2': 'elementary vocabulary and simple grammar structures',
                'B1': 'intermediate vocabulary and common grammar patterns',
                'B2': 'upper-intermediate vocabulary with complex sentences',
                'C1': 'advanced vocabulary, idioms, and sophisticated grammar'
            };

            const complexityDescMap = {
                'simple_short': 'simple sentences with 5-10 words each',
                'simple_medium': 'simple sentences with 10-15 words each',
                'simple_long': 'simple sentences with 15-25 words each',
                'compound': 'compound sentences using conjunctions (and, but, or, so, yet)',
                'complex': 'complex sentences with subordinate clauses (because, although, when, if, that)',
                'mixed': 'a natural mix of simple, compound, and complex sentences'
            };

            const sourceLang = this.practiceDirection === 'vi_to_en' ? 'Vietnamese' : 'English';
            const targetLang = this.practiceDirection === 'vi_to_en' ? 'English' : 'Vietnamese';
            const length = lengthMap[this.practiceLength];
            const levelDesc = levelDescMap[this.practiceLevel];
            const complexityDesc = complexityDescMap[this.sentenceComplexity];
            const maxSentences = length.split('-')[1].replace(' sentences', '');

            this.practicePrompt = `You are a language tutor helping me practice ${sourceLang} to ${targetLang} translation.

TASK: Create a translation practice exercise following these requirements:

1. PASSAGE GENERATION:
   - Topic: ${this.practiceTopic}
   - Level: ${this.practiceLevel} (${levelDesc})
   - Number of sentences: ${length}
   - Sentence complexity: ${complexityDesc}
   - Language: Write the passage in ${sourceLang}

   IMPORTANT REQUIREMENTS:
   - All sentences must be COHERENT and form a meaningful, connected passage (not random isolated sentences)
   - Use CONSISTENT tenses throughout the passage (choose appropriate tenses based on the narrative)
   - Sentences should flow naturally and logically from one to another
   - Include transitional words/phrases to connect ideas

2. PRACTICE FORMAT:
   After generating the passage, present it sentence by sentence for me to translate.

   For each sentence:
   - Show the original sentence in ${sourceLang}
   - Wait for my translation to ${targetLang}
   - After I respond:
     • Grade my translation (score out of 10)
     • Point out any errors (grammar, vocabulary, word order, tense, etc.)
     • Explain corrections in detail
     • Provide a model translation for comparison
   - Then move to the next sentence

3. FINAL REVIEW:
   After I complete all sentences:
   - Give an overall score and detailed feedback
   - List common mistakes I made and how to avoid them
   - Comment on my tense usage and consistency
   - Provide a "📚 Vocabulary to Remember" section with:
     • 10-15 important words/phrases from the passage
     • Their meanings in both ${sourceLang} and ${targetLang}
     • Part of speech (noun, verb, adj, etc.)
     • Example sentences showing correct usage

START by generating the ${sourceLang} passage about "${this.practiceTopic}" (${length}, ${complexityDesc}) and present the FIRST sentence for me to translate.

Format:
📝 Sentence 1/${maxSentences}:
[First sentence in ${sourceLang}]

Your translation:`;
        },

        copyPracticePrompt() {
            navigator.clipboard.writeText(this.practicePrompt);
            Alpine.store('app')?.showToast?.('Prompt copied to clipboard!', 'success');
        },

        generateChatPrompt() {
            const levelDescMap = {
                'A1': 'very simple vocabulary and basic grammar, short sentences, common everyday words',
                'A2': 'elementary vocabulary and simple grammar, can discuss familiar topics',
                'B1': 'intermediate vocabulary, can discuss opinions and experiences, uses common idioms',
                'B2': 'upper-intermediate vocabulary, can discuss abstract topics, uses varied sentence structures',
                'C1': 'advanced vocabulary including idioms and nuanced expressions, can discuss complex topics fluently'
            };

            const styleDescMap = {
                'casual': 'a friendly, casual conversation between friends or acquaintances',
                'formal': 'a formal, professional conversation in a business or official setting',
                'roleplay': 'a role-play scenario where you act as a specific character in a situation',
                'debate': 'a discussion/debate where you present arguments and counterarguments on the topic',
                'interview': 'an interview format where you ask and answer questions about the topic'
            };

            const roleplayScenarios = {
                'Personal and Communication': 'meeting a new neighbor or reconnecting with an old friend',
                'Work and Business': 'a job interview or a meeting with a business partner',
                'Meetings and Presentations': 'presenting a project update to your team',
                'Transportation and Travel': 'asking for directions or booking a hotel',
                'Shopping and Money': 'negotiating a price or returning a product',
                'Food and Drink': 'ordering at a restaurant or discussing recipes',
                'Health and Medicine': 'visiting a doctor or discussing healthy habits',
                'School and Education': 'talking to a teacher or discussing study plans'
            };

            const levelDesc = levelDescMap[this.chatLevel];
            const styleDesc = styleDescMap[this.chatStyle];

            let roleplayContext = '';
            if (this.chatStyle === 'roleplay') {
                const scenario = roleplayScenarios[this.chatTopic] || 'a realistic situation related to ' + this.chatTopic;
                roleplayContext = `\n\nROLE-PLAY SCENARIO: Create a specific scenario about "${scenario}". Assign me a role and describe the setting before we begin.`;
            }

            this.chatPrompt = `You are an English conversation partner helping me practice speaking English at ${this.chatLevel} level.

CONVERSATION SETTINGS:
- Topic: ${this.chatTopic}
- My Level: ${this.chatLevel} (${levelDesc})
- Style: ${this.chatStyle} - ${styleDesc}${roleplayContext}

YOUR ROLE AS CONVERSATION PARTNER:
1. Engage in natural, flowing conversation about the topic
2. Match your language complexity to my ${this.chatLevel} level
3. Keep your responses conversational (2-4 sentences typically, unless explaining something)
4. Ask follow-up questions to keep the conversation going
5. Introduce relevant vocabulary naturally in context

LANGUAGE CORRECTION:
After each of my responses:
- If I make grammar or vocabulary errors, briefly note them at the end of your reply
- Format: 📝 Correction: "[my error]" → "[correct form]" (brief explanation)
- If my English is correct, don't mention corrections - just continue the conversation
- Don't interrupt the flow with too many corrections; focus on significant errors

VOCABULARY BUILDING:
- When using a word or phrase that might be new to me, briefly explain it
- Format: 💡 "word/phrase" = meaning or explanation
- Suggest alternative expressions I could use to sound more natural

CONVERSATION FLOW:
- Start by greeting me and introducing the topic with an engaging question
- Guide the conversation to cover different aspects of the topic
- After about 10-15 exchanges, naturally conclude and provide a summary

END OF SESSION (after ~15 exchanges):
Provide a "📚 Session Summary" with:
1. Key vocabulary and phrases we used (with Vietnamese translations)
2. Grammar points I should review
3. Suggestions for improving my conversational English

START the conversation now! Greet me and ask an opening question about "${this.chatTopic}".`;
        },

        copyChatPrompt() {
            navigator.clipboard.writeText(this.chatPrompt);
            Alpine.store('app')?.showToast?.('Prompt copied to clipboard!', 'success');
        }
    }));

    // Flashcards Page Component
    Alpine.data('flashcardsPage', () => ({
        numWords: 10,
        loading: false,
        totalLearned: 0,
        flashcards: [],
        studyActive: false,
        studyComplete: false,
        currentIndex: 0,
        isFlipped: false,
        knownCount: 0,

        async init() {
            await this.checkLearnedCount();
        },

        async checkLearnedCount() {
            try {
                const response = await fetchAPI('/vocabulary/learned?limit=1');
                if (response.success) {
                    this.totalLearned = response.count;
                }
            } catch (error) {
                console.error('Failed to check learned count:', error);
            }
        },

        get currentCard() {
            return this.flashcards[this.currentIndex] || null;
        },

        async startStudy() {
            this.loading = true;

            try {
                const response = await fetchAPI(`/vocabulary/flashcards?limit=${this.numWords}`);

                if (response.success && response.flashcards.length > 0) {
                    this.flashcards = response.flashcards;
                    this.studyActive = true;
                    this.studyComplete = false;
                    this.currentIndex = 0;
                    this.isFlipped = false;
                    this.knownCount = 0;
                } else {
                    alert('Không có từ nào để học. Hãy vào Vocabulary và nhấn "Learn" để thêm từ!');
                }
            } catch (error) {
                console.error('Failed to load flashcards:', error);
                alert('Không thể tải flashcards. Vui lòng thử lại!');
            } finally {
                this.loading = false;
            }
        },

        flipCard() {
            this.isFlipped = !this.isFlipped;
        },

        markCard(known) {
            if (known) {
                this.knownCount++;
            }

            // Move to next card
            if (this.currentIndex < this.flashcards.length - 1) {
                this.currentIndex++;
                this.isFlipped = false;
            } else {
                this.studyComplete = true;
            }
        },

        resetStudy() {
            this.studyActive = false;
            this.studyComplete = false;
            this.flashcards = [];
            this.currentIndex = 0;
            this.isFlipped = false;
            this.knownCount = 0;
        },

        speakWord(word) {
            if (word && 'speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(word);
                utterance.lang = 'en-US';
                speechSynthesis.speak(utterance);
            }
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
