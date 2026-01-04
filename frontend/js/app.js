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
                    { id: 'translation', name: 'Translation Practice', icon: 'fas fa-language' },
                    { id: 'conversation', name: 'Conversation Practice', icon: 'fas fa-comments' },
                    { id: 'flashcards', name: 'Flashcards', icon: 'fas fa-clone' },
                    { id: 'export', name: 'Export/Import', icon: 'fas fa-file-export' },
                    { id: 'analytics', name: 'Analytics', icon: 'fas fa-chart-line' },
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
                'translation': { title: 'Translation Practice', desc: 'Practice translation with AI' },
                'conversation': { title: 'Conversation Practice', desc: 'Practice English conversation with AI' },
                'srs': { title: 'Spaced Repetition', desc: 'Review words for long-term memory' },
                'flashcards': { title: 'Flashcards', desc: 'Study with flashcards' },
                'export': { title: 'Export/Import', desc: 'Export and import vocabulary data' },
                'analytics': { title: 'Analytics', desc: 'View your learning progress and statistics' },
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
            dueReviews: 0,
            // Practice stats
            translationSessions: 0,
            translationAvg: 0,
            conversationSessions: 0,
            conversationAvg: 0,
            flashcardSessions: 0,
            flashcardKnown: 0,
            srsTotal: 0,
            srsSuccessRate: 0
        },
        recentActivity: [],
        recommendations: [],
        progressChart: null,
        topicsChart: null,

        practiceChartData: [],

        async init() {
            await this.loadDashboardData();
            await this.loadPracticeStats();
            await this.loadRecentActivity();
            await this.loadRecommendations();
            this.initCharts();
        },

        async loadRecommendations() {
            try {
                const response = await fetchAPI('/recommendations');
                if (response.success) {
                    this.recommendations = response.recommendations;
                }
            } catch (error) {
                console.error('Failed to load recommendations:', error);
            }
        },

        goToRecommendation(rec) {
            const actionMap = {
                'quiz': 'quiz',
                'flashcards': 'flashcards',
                'srs': 'srs',
                'translation': 'translation',
                'conversation': 'conversation',
                'vocabulary': 'vocabulary'
            };
            const page = actionMap[rec.action] || 'dashboard';
            window.dispatchEvent(new CustomEvent('navigate', { detail: page }));
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
                }

                if (srsRes.success) {
                    this.dashStats.dueReviews = srsRes.stats.due_now || 0;
                    this.dashStats.srsTotal = srsRes.stats.total_cards || 0;
                    const total = (srsRes.stats.total_reviews || 0);
                    const correct = (srsRes.stats.correct_reviews || 0);
                    this.dashStats.srsSuccessRate = total > 0 ? Math.round((correct / total) * 100) : 0;
                }
            } catch (error) {
                console.error('Failed to load dashboard data:', error);
            }
        },

        async loadPracticeStats() {
            try {
                const response = await fetchAPI('/practice/all/stats');
                if (response.success) {
                    this.dashStats.translationSessions = response.stats.translation.total;
                    this.dashStats.translationAvg = response.stats.translation.avg_score || '-';
                    this.dashStats.conversationSessions = response.stats.conversation.total;
                    this.dashStats.conversationAvg = response.stats.conversation.avg_score || '-';
                    // Store chart data for later use
                    this.practiceChartData = response.chart_data;
                }
            } catch (error) {
                console.error('Failed to load practice stats:', error);
            }

            // Load Flashcard stats (still from localStorage as it's session-based)
            const flashcardStats = JSON.parse(localStorage.getItem('flashcardStats') || '{"sessions": 0, "totalKnown": 0, "totalCards": 0}');
            this.dashStats.flashcardSessions = flashcardStats.sessions || 0;
            if (flashcardStats.totalCards > 0) {
                this.dashStats.flashcardKnown = Math.round((flashcardStats.totalKnown / flashcardStats.totalCards) * 100);
            } else {
                this.dashStats.flashcardKnown = 0;
            }
        },

        async loadRecentActivity() {
            try {
                const response = await fetchAPI('/practice/recent?limit=10');
                if (response.success) {
                    this.recentActivity = response.activity;
                }
            } catch (error) {
                console.error('Failed to load recent activity:', error);
            }
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

        initCharts() {
            // Progress Chart - Practice Score Trend
            const progressCtx = document.getElementById('progressChart');
            if (progressCtx) {
                // Use API data if available
                const last7Days = [];
                const translationScores = [];
                const conversationScores = [];

                if (this.practiceChartData && this.practiceChartData.length > 0) {
                    // Use API chart data
                    this.practiceChartData.forEach(day => {
                        const date = new Date(day.date);
                        last7Days.push(date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }));
                        translationScores.push(day.translation);
                        conversationScores.push(day.conversation);
                    });
                } else {
                    // Fallback: generate empty days
                    for (let i = 6; i >= 0; i--) {
                        const date = new Date();
                        date.setDate(date.getDate() - i);
                        last7Days.push(date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }));
                        translationScores.push(null);
                        conversationScores.push(null);
                    }
                }

                this.progressChart = new Chart(progressCtx, {
                    type: 'line',
                    data: {
                        labels: last7Days,
                        datasets: [{
                            label: 'Translation',
                            data: translationScores,
                            borderColor: '#8B5CF6',
                            tension: 0.4,
                            fill: false,
                            spanGaps: true
                        }, {
                            label: 'Conversation',
                            data: conversationScores,
                            borderColor: '#3B82F6',
                            tension: 0.4,
                            fill: false,
                            spanGaps: true
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: true, position: 'top' }
                        },
                        scales: {
                            y: { beginAtZero: true, max: 10 }
                        }
                    }
                });
            }

            // Topics Chart
            const topicsCtx = document.getElementById('topicsChart');
            if (topicsCtx) {
                this.loadTopicsData().then(topicsData => {
                    this.topicsChart = new Chart(topicsCtx, {
                        type: 'doughnut',
                        data: {
                            labels: topicsData.labels,
                            datasets: [{
                                data: topicsData.data,
                                backgroundColor: [
                                    '#3B82F6',
                                    '#10B981',
                                    '#F59E0B',
                                    '#8B5CF6',
                                    '#EF4444',
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
                });
            }
        },

        async loadTopicsData() {
            try {
                const response = await fetchAPI('/vocabulary/user?limit=1000');
                if (response.success && response.vocabulary) {
                    // Count words by topic
                    const topicCounts = {};
                    response.vocabulary.forEach(word => {
                        const topic = word.topic || 'Other';
                        // Shorten topic name
                        const shortTopic = topic.split(' and ')[0].split(' ')[0];
                        topicCounts[shortTopic] = (topicCounts[shortTopic] || 0) + 1;
                    });

                    // Sort by count and take top 5
                    const sortedTopics = Object.entries(topicCounts)
                        .sort((a, b) => b[1] - a[1])
                        .slice(0, 5);

                    // Calculate "Other" if there are more topics
                    const otherCount = Object.entries(topicCounts)
                        .sort((a, b) => b[1] - a[1])
                        .slice(5)
                        .reduce((sum, [_, count]) => sum + count, 0);

                    if (otherCount > 0) {
                        sortedTopics.push(['Other', otherCount]);
                    }

                    return {
                        labels: sortedTopics.map(([topic]) => topic),
                        data: sortedTopics.map(([_, count]) => count)
                    };
                }
            } catch (error) {
                console.error('Failed to load topics data:', error);
            }
            // Return default data if failed
            return {
                labels: ['No Data'],
                data: [1]
            };
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
        // Flashcard integration
        fromFlashcards: false,
        studiedWordIds: [],

        async init() {
            // Check if coming from flashcards
            if (localStorage.getItem('quizFromFlashcards') === 'true') {
                this.fromFlashcards = true;
                this.studiedWordIds = JSON.parse(localStorage.getItem('lastStudiedWords') || '[]');
                localStorage.removeItem('quizFromFlashcards');

                // Show notification
                Alpine.store('app')?.showToast?.('Quiz loaded with your studied words!', 'success');
            }
        },

        async startQuiz() {
            this.loading = true;

            try {
                // Build request body
                const body = {
                    quiz_type: this.quizType,
                    num_questions: parseInt(this.numQuestions)
                };

                // If coming from flashcards, include studied word IDs
                if (this.fromFlashcards && this.studiedWordIds.length > 0) {
                    body.vocabulary_ids = this.studiedWordIds;
                }

                // Generate quiz from all learned vocabulary (use_learned_only is default true in backend)
                const response = await fetchAPI('/quiz/generate', {
                    method: 'POST',
                    body: JSON.stringify(body)
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
        practiceScore: '',
        translationHistory: [],

        async init() {
            await this.loadTranslationHistory();
        },

        async loadTranslationHistory() {
            try {
                const response = await fetchAPI('/practice/translation');
                if (response.success) {
                    this.translationHistory = response.history;
                }
            } catch (error) {
                console.error('Failed to load translation history:', error);
            }
        },

        async saveTranslationHistory() {
            if (!this.practiceScore) return;

            try {
                const response = await fetchAPI('/practice/translation', {
                    method: 'POST',
                    body: JSON.stringify({
                        topic: this.practiceTopic,
                        level: this.practiceLevel,
                        direction: this.practiceDirection,
                        length: this.practiceLength,
                        complexity: this.sentenceComplexity,
                        score: parseFloat(this.practiceScore)
                    })
                });

                if (response.success) {
                    this.translationHistory.unshift(response.practice);
                    this.practiceScore = '';
                    Alpine.store('app')?.showToast?.('Đã lưu vào lịch sử!', 'success');
                }
            } catch (error) {
                console.error('Failed to save translation history:', error);
                Alpine.store('app')?.showToast?.('Không thể lưu!', 'error');
            }
        },

        async deleteTranslationHistory(index) {
            const item = this.translationHistory[index];
            if (!item || !item.id) return;

            try {
                const response = await fetchAPI(`/practice/translation/${item.id}`, {
                    method: 'DELETE'
                });

                if (response.success) {
                    this.translationHistory.splice(index, 1);
                    Alpine.store('app')?.showToast?.('Đã xóa!', 'success');
                }
            } catch (error) {
                console.error('Failed to delete:', error);
            }
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

2. SCORING CRITERIA (for each sentence, score 0-10 with decimals allowed):
   - Accuracy (4 points): Meaning preserved, no mistranslation
   - Grammar (3 points): Correct tense, word order, sentence structure
   - Vocabulary (2 points): Appropriate word choice, natural expressions
   - Fluency (1 point): Natural flow, no awkward phrasing

3. PRACTICE FORMAT:
   After generating the passage, present it sentence by sentence for me to translate.

   For each sentence:
   - Show the original sentence in ${sourceLang}
   - Wait for my translation to ${targetLang}
   - After I respond:
     • 📊 Score: X.X/10 (breakdown: Accuracy X/4, Grammar X/3, Vocabulary X/2, Fluency X/1)
     • ❌ Errors: List specific errors with corrections
     • 💡 Suggestions: Tips for improvement
     • ✅ Model translation: Provide ideal translation
   - Then move to the next sentence

4. FINAL REVIEW:
   After I complete all sentences:
   - 📊 OVERALL SCORE: X.X/10 (can be decimal like 7.5, 8.3, etc.)
   - 📈 Score breakdown by category
   - ❌ Common mistakes I made and how to avoid them
   - ✅ What I did well
   - 📚 Vocabulary to Remember: 10-15 important words/phrases with meanings and examples

START by generating the ${sourceLang} passage about "${this.practiceTopic}" (${length}, ${complexityDesc}) and present the FIRST sentence for me to translate.

Format:
📝 Sentence 1/${maxSentences}:
[First sentence in ${sourceLang}]

Your translation:`;
        },

        copyPracticePrompt() {
            navigator.clipboard.writeText(this.practicePrompt);
            Alpine.store('app')?.showToast?.('Prompt copied to clipboard!', 'success');
        }
    }));

    // Conversation Page Component
    Alpine.data('conversationPage', () => ({
        chatTopic: '',
        chatLevel: '',
        chatStyle: '',
        chatLength: '',
        chatPrompt: '',
        chatScore: '',
        conversationHistory: [],

        styleNames: {
            'casual': 'Casual',
            'formal': 'Formal',
            'roleplay': 'Role-play',
            'debate': 'Debate',
            'interview': 'Interview'
        },

        lengthNames: {
            'short': 'Short',
            'medium': 'Medium',
            'long': 'Long'
        },

        async init() {
            await this.loadConversationHistory();
        },

        async loadConversationHistory() {
            try {
                const response = await fetchAPI('/practice/conversation');
                if (response.success) {
                    this.conversationHistory = response.history;
                }
            } catch (error) {
                console.error('Failed to load conversation history:', error);
            }
        },

        async saveConversationHistory() {
            if (!this.chatScore) return;

            try {
                const response = await fetchAPI('/practice/conversation', {
                    method: 'POST',
                    body: JSON.stringify({
                        topic: this.chatTopic,
                        level: this.chatLevel,
                        style: this.styleNames[this.chatStyle] || this.chatStyle,
                        length: this.lengthNames[this.chatLength] || this.chatLength,
                        score: parseFloat(this.chatScore)
                    })
                });

                if (response.success) {
                    this.conversationHistory.unshift(response.practice);
                    this.chatScore = '';
                    Alpine.store('app')?.showToast?.('Đã lưu vào lịch sử!', 'success');
                }
            } catch (error) {
                console.error('Failed to save conversation history:', error);
                Alpine.store('app')?.showToast?.('Không thể lưu!', 'error');
            }
        },

        async deleteConversationHistory(index) {
            const item = this.conversationHistory[index];
            if (!item || !item.id) return;

            try {
                const response = await fetchAPI(`/practice/conversation/${item.id}`, {
                    method: 'DELETE'
                });

                if (response.success) {
                    this.conversationHistory.splice(index, 1);
                    Alpine.store('app')?.showToast?.('Đã xóa!', 'success');
                }
            } catch (error) {
                console.error('Failed to delete:', error);
            }
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

            const lengthMap = {
                'short': { exchanges: '5-8', desc: 'short' },
                'medium': { exchanges: '10-15', desc: 'medium' },
                'long': { exchanges: '18-25', desc: 'extended' }
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
            const lengthInfo = lengthMap[this.chatLength];

            let roleplayContext = '';
            if (this.chatStyle === 'roleplay') {
                const scenario = roleplayScenarios[this.chatTopic] || 'a realistic situation related to ' + this.chatTopic;
                roleplayContext = `\n\nROLE-PLAY SCENARIO: Create a specific scenario about "${scenario}". Assign me a role and describe the setting before we begin.`;
            }

            this.chatPrompt = `You are an English conversation partner helping me practice speaking English at ${this.chatLevel} level.

CONVERSATION SETTINGS:
- Topic: ${this.chatTopic}
- My Level: ${this.chatLevel} (${levelDesc})
- Style: ${this.chatStyle} - ${styleDesc}
- Length: ${lengthInfo.exchanges} exchanges (${lengthInfo.desc} conversation)${roleplayContext}

SCORING CRITERIA (for each of my responses, score 0-10 with decimals allowed):
- Communication (3 points): Clear message, appropriate response to context
- Grammar (3 points): Correct tense, sentence structure, word order
- Vocabulary (2 points): Appropriate word choice, variety of expressions
- Fluency (2 points): Natural flow, no awkward phrasing

YOUR ROLE AS CONVERSATION PARTNER:
1. Engage in natural, flowing conversation about the topic
2. Match your language complexity to my ${this.chatLevel} level
3. Keep your responses conversational (2-4 sentences typically)
4. Ask follow-up questions to keep the conversation going

AFTER EACH OF MY RESPONSES:
1. Continue the conversation naturally
2. Then provide feedback:
   📊 Score: X.X/10 (Communication X/3, Grammar X/3, Vocabulary X/2, Fluency X/2)
   📝 Corrections (if any): "[error]" → "[correct]"
   💡 Better expression: Suggest more natural ways to say what I meant
3. If my English is perfect, just show the score without corrections

CONVERSATION FLOW:
- Track exchange count (e.g., "Exchange 3/${lengthInfo.exchanges.split('-')[1]}")
- After ${lengthInfo.exchanges} exchanges, naturally conclude the conversation

END OF SESSION:
Provide "📊 FINAL ASSESSMENT":
- Overall Score: X.X/10 (can be decimal like 7.5, 8.3)
- Score breakdown by category (average)
- ✅ Strengths: What I did well
- ❌ Areas to improve: Common mistakes with corrections
- 📚 Key Vocabulary: 10-15 useful words/phrases from our conversation (with Vietnamese translations)
- 💡 Tips: Specific suggestions for improvement

START the conversation now! Greet me and ask an opening question about "${this.chatTopic}".

[Exchange 1/${lengthInfo.exchanges.split('-')[1]}]`;
        },

        copyChatPrompt() {
            navigator.clipboard.writeText(this.chatPrompt);
            Alpine.store('app')?.showToast?.('Prompt copied to clipboard!', 'success');
        }
    }));

    // Export/Import Page Component
    Alpine.data('exportPage', () => ({
        exportStats: {
            total_vocabulary: 0,
            learned_vocabulary: 0,
            by_topic: {},
            by_level: {}
        },
        exportLearnedOnly: true,
        dragOver: false,
        importing: false,
        importResult: null,

        async init() {
            await this.loadExportStats();
        },

        async loadExportStats() {
            try {
                const response = await fetchAPI('/export/stats');
                if (response.success) {
                    this.exportStats = response.stats;
                }
            } catch (error) {
                console.error('Failed to load export stats:', error);
            }
        },

        exportData(format) {
            const learnedParam = this.exportLearnedOnly ? 'learned_only=true' : 'learned_only=false';
            const url = `/api/export/vocabulary/${format}?${learnedParam}`;

            // Create a temporary link to download
            const link = document.createElement('a');
            link.href = url;
            link.download = `vocabulary_export.${format === 'anki' ? 'txt' : format}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            Alpine.store('app')?.showToast?.(`Exporting ${format.toUpperCase()}...`, 'success');
        },

        handleDrop(event) {
            this.dragOver = false;
            const file = event.dataTransfer.files[0];
            if (file) {
                this.importFile(file);
            }
        },

        handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                this.importFile(file);
            }
        },

        async importFile(file) {
            this.importing = true;
            this.importResult = null;

            const formData = new FormData();
            formData.append('file', file);

            try {
                let endpoint = '/api/import/vocabulary/json';
                if (file.name.endsWith('.csv')) {
                    endpoint = '/api/import/vocabulary/csv';
                }

                const response = await fetch(endpoint, {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                this.importResult = result;

                if (result.success) {
                    await this.loadExportStats();
                    Alpine.store('app')?.showToast?.(`Imported ${result.added} words!`, 'success');
                }
            } catch (error) {
                console.error('Import failed:', error);
                this.importResult = {
                    success: false,
                    message: 'Import failed: ' + error.message
                };
            } finally {
                this.importing = false;
            }
        }
    }));

    // Analytics Page Component
    Alpine.data('analyticsPage', () => ({
        summary: {
            total_words_learned: 0,
            total_quizzes: 0,
            average_quiz_score: 0
        },
        streak: {
            current_streak: 0,
            longest_streak: 0,
            total_active_days: 0
        },
        heatmapData: [],
        heatmapWeeks: [],
        maxCount: 1,
        weeklyStats: [],
        monthlyStats: [],
        weeklyChart: null,
        scoreChart: null,

        async init() {
            await Promise.all([
                this.loadSummary(),
                this.loadStreak(),
                this.loadHeatmap(),
                this.loadWeeklyStats(),
                this.loadMonthlyStats()
            ]);
            this.initCharts();
        },

        async loadSummary() {
            try {
                const response = await fetchAPI('/analytics/summary');
                if (response.success) {
                    this.summary = response.summary;
                }
            } catch (error) {
                console.error('Failed to load summary:', error);
            }
        },

        async loadStreak() {
            try {
                const response = await fetchAPI('/analytics/streak');
                if (response.success) {
                    this.streak = response;
                }
            } catch (error) {
                console.error('Failed to load streak:', error);
            }
        },

        async loadHeatmap() {
            try {
                const response = await fetchAPI('/analytics/heatmap?days=365');
                if (response.success) {
                    this.heatmapData = response.heatmap;
                    this.maxCount = response.max_count || 1;
                    this.processHeatmap();
                }
            } catch (error) {
                console.error('Failed to load heatmap:', error);
            }
        },

        processHeatmap() {
            // Group into weeks (columns) with days (rows)
            const weeks = [];
            let currentWeek = [];

            // Pad first week to start on Sunday
            if (this.heatmapData.length > 0) {
                const firstDate = new Date(this.heatmapData[0].date);
                const firstDay = firstDate.getDay();
                for (let i = 0; i < firstDay; i++) {
                    currentWeek.push({ date: null, count: 0 });
                }
            }

            for (const day of this.heatmapData) {
                currentWeek.push(day);
                if (currentWeek.length === 7) {
                    weeks.push(currentWeek);
                    currentWeek = [];
                }
            }

            // Push remaining days
            if (currentWeek.length > 0) {
                while (currentWeek.length < 7) {
                    currentWeek.push({ date: null, count: 0 });
                }
                weeks.push(currentWeek);
            }

            this.heatmapWeeks = weeks;
        },

        getHeatmapColor(count) {
            if (count === 0) return '#ebedf0';
            const intensity = count / this.maxCount;
            if (intensity <= 0.25) return '#9be9a8';
            if (intensity <= 0.5) return '#40c463';
            if (intensity <= 0.75) return '#30a14e';
            return '#216e39';
        },

        async loadWeeklyStats() {
            try {
                const response = await fetchAPI('/analytics/weekly');
                if (response.success) {
                    this.weeklyStats = response.weeks;
                }
            } catch (error) {
                console.error('Failed to load weekly stats:', error);
            }
        },

        async loadMonthlyStats() {
            try {
                const response = await fetchAPI('/analytics/monthly');
                if (response.success) {
                    this.monthlyStats = response.months;
                }
            } catch (error) {
                console.error('Failed to load monthly stats:', error);
            }
        },

        initCharts() {
            // Weekly Progress Chart
            const weeklyCtx = document.getElementById('weeklyChart');
            if (weeklyCtx && this.weeklyStats.length > 0) {
                this.weeklyChart = new Chart(weeklyCtx, {
                    type: 'bar',
                    data: {
                        labels: this.weeklyStats.map(w => {
                            const date = new Date(w.week_start);
                            return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
                        }),
                        datasets: [{
                            label: 'Words Learned',
                            data: this.weeklyStats.map(w => w.words_learned),
                            backgroundColor: '#3B82F6',
                            borderRadius: 4
                        }, {
                            label: 'Quizzes',
                            data: this.weeklyStats.map(w => w.quizzes),
                            backgroundColor: '#10B981',
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'bottom' } },
                        scales: { y: { beginAtZero: true } }
                    }
                });
            }

            // Score Trends Chart
            const scoreCtx = document.getElementById('scoreChart');
            if (scoreCtx && this.weeklyStats.length > 0) {
                this.scoreChart = new Chart(scoreCtx, {
                    type: 'line',
                    data: {
                        labels: this.weeklyStats.map(w => {
                            const date = new Date(w.week_start);
                            return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
                        }),
                        datasets: [{
                            label: 'Quiz Avg Score',
                            data: this.weeklyStats.map(w => w.quiz_avg || null),
                            borderColor: '#8B5CF6',
                            backgroundColor: 'rgba(139, 92, 246, 0.1)',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'bottom' } },
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100,
                                title: { display: true, text: 'Score %' }
                            }
                        }
                    }
                });
            }
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
        // Swipe state
        touchStartX: 0,
        touchStartY: 0,
        touchEndX: 0,
        touchEndY: 0,
        swipeDirection: null,
        isSwiping: false,

        async init() {
            await this.checkLearnedCount();
            this.setupSwipeListeners();
        },

        setupSwipeListeners() {
            // Add touch listeners when study is active
            this.$watch('studyActive', (active) => {
                if (active) {
                    this.$nextTick(() => {
                        const card = document.querySelector('.flashcard-swipe');
                        if (card) {
                            card.addEventListener('touchstart', (e) => this.handleTouchStart(e), { passive: true });
                            card.addEventListener('touchmove', (e) => this.handleTouchMove(e), { passive: true });
                            card.addEventListener('touchend', (e) => this.handleTouchEnd(e), { passive: true });
                        }
                    });
                }
            });
        },

        handleTouchStart(e) {
            this.touchStartX = e.changedTouches[0].screenX;
            this.touchStartY = e.changedTouches[0].screenY;
            this.isSwiping = true;
        },

        handleTouchMove(e) {
            if (!this.isSwiping) return;
            this.touchEndX = e.changedTouches[0].screenX;
            this.touchEndY = e.changedTouches[0].screenY;
        },

        handleTouchEnd(e) {
            if (!this.isSwiping) return;
            this.isSwiping = false;

            const diffX = this.touchEndX - this.touchStartX;
            const diffY = this.touchEndY - this.touchStartY;

            // Only detect horizontal swipes (ignore vertical)
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    // Swipe right = Know
                    this.swipeCard(true);
                } else {
                    // Swipe left = Don't Know
                    this.swipeCard(false);
                }
            }
        },

        swipeCard(known) {
            this.swipeDirection = known ? 'right' : 'left';
            setTimeout(() => {
                this.markCard(known);
                this.swipeDirection = null;
            }, 300);
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
                this.saveFlashcardStats();
            }
        },

        saveFlashcardStats() {
            // Save flashcard session stats for dashboard
            const stats = JSON.parse(localStorage.getItem('flashcardStats') || '{"sessions": 0, "totalKnown": 0, "totalCards": 0}');
            stats.sessions++;
            stats.totalKnown += this.knownCount;
            stats.totalCards += this.flashcards.length;
            localStorage.setItem('flashcardStats', JSON.stringify(stats));

            // Save studied word IDs for quiz suggestion
            const studiedIds = this.flashcards.map(f => f.id);
            localStorage.setItem('lastStudiedWords', JSON.stringify(studiedIds));
        },

        goToQuizWithStudiedWords() {
            // Navigate to quiz page - it will auto-detect studied words
            localStorage.setItem('quizFromFlashcards', 'true');
            window.dispatchEvent(new CustomEvent('navigate', { detail: 'quiz' }));
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
