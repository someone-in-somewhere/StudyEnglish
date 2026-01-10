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

// Randomization helpers for varied AI content generation
function getRandomItems(arr, count = 1) {
    const shuffled = [...arr].sort(() => Math.random() - 0.5);
    return count === 1 ? shuffled[0] : shuffled.slice(0, count);
}

function generateVariationSeed() {
    return Math.floor(Math.random() * 10000);
}

// ============================================================================
// LEVEL-APPROPRIATE CONSTANTS (CEFR Framework)
// ============================================================================

// TRANSLATION PRACTICE - Grammar Focus by Level
const TRANSLATION_FOCUS_BY_LEVEL = {
    'A1': [
        'present simple tense (I work, she eats)',
        'basic subject-verb-object word order',
        'simple connectors (and, but, or)',
        'basic time expressions (today, tomorrow, now, every day)',
        'possessive adjectives (my, your, his, her, our, their)',
        'there is / there are constructions',
        'basic prepositions of place (in, on, at, under, next to)'
    ],
    'A2': [
        'past simple tense (I worked, she ate)',
        'future with "will" and "going to"',
        'comparatives and superlatives (bigger, the biggest)',
        'basic cause and effect (because, so)',
        'frequency adverbs (always, usually, sometimes, never)',
        'present continuous for current actions',
        'can/could for ability and permission'
    ],
    'B1': [
        'present perfect tense (I have worked)',
        'first conditional (if + present, will + verb)',
        'basic passive voice (it is made, they were built)',
        'relative clauses with who, which, that',
        'expressing opinions (I think, I believe, In my opinion)',
        'used to for past habits',
        'modal verbs for advice (should, ought to)'
    ],
    'B2': [
        'second conditional (if + past, would + verb)',
        'reported speech (She said that...)',
        'passive voice in various tenses',
        'third conditional (if + past perfect, would have)',
        'advanced connectors (however, nevertheless, furthermore)',
        'wish + past for regrets',
        'modal perfects (could have, should have, might have)'
    ],
    'C1': [
        'mixed conditionals',
        'subjunctive mood (I suggest that he go...)',
        'inversion for emphasis (Not only did he..., Rarely have I...)',
        'advanced passive constructions (is said to be, is believed to have)',
        'cleft sentences for emphasis (It was John who...)',
        'ellipsis and substitution',
        'nuanced modal expressions'
    ]
};

// TRANSLATION PRACTICE - Writing Tones by Level
const TRANSLATION_TONES_BY_LEVEL = {
    'A1': [
        'simple and clear (everyday situations)',
        'friendly and casual (talking to friends)',
        'descriptive basics (describing people, places, things)'
    ],
    'A2': [
        'narrative (telling simple stories)',
        'informative (sharing basic facts)',
        'personal (sharing experiences and feelings)',
        'instructional (giving simple directions)'
    ],
    'B1': [
        'narrative (tell a story with details)',
        'descriptive (paint a vivid picture)',
        'informative (share facts and information)',
        'persuasive (express and support opinions)',
        'reflective (share thoughts and feelings)'
    ],
    'B2': [
        'analytical (examine ideas critically)',
        'argumentative (present and defend a position)',
        'narrative with complexity (multiple perspectives)',
        'formal informative (report-style writing)',
        'reflective and philosophical'
    ],
    'C1': [
        'sophisticated narrative (nuanced storytelling)',
        'academic and analytical',
        'persuasive with rhetorical devices',
        'satirical or ironic',
        'nuanced and subtle expression'
    ]
};

// TRANSLATION PRACTICE - Creative Requirements by Level
const CREATIVE_REQUIREMENTS_BY_LEVEL = {
    'A1': `SIMPLICITY FOCUS:
   - Create a very simple, everyday situation (going to school, eating breakfast, meeting a friend)
   - Use only basic, common vocabulary
   - Keep sentences short and clear
   - Focus on CLARITY over creativity
   - Use familiar contexts that A1 learners can relate to`,
    'A2': `RELATABLE SCENARIO:
   - Create a simple but engaging everyday scenario
   - Include basic emotions and reactions
   - Use common situations (shopping, traveling, working)
   - Add a simple sequence of events
   - Keep vocabulary accessible but slightly varied`,
    'B1': `INTERESTING SCENARIO:
   - Create an engaging scenario with a simple plot
   - Include character motivations and reactions
   - Add a small problem or interesting twist
   - Use varied vocabulary and expressions
   - Make it memorable but not overly complex`,
    'B2': `ENGAGING NARRATIVE:
   - Create a unique, memorable scenario with depth
   - Include multiple perspectives or viewpoints
   - Add complexity through cause-effect relationships
   - Use sophisticated vocabulary naturally
   - Include cultural or social context when appropriate`,
    'C1': `SOPHISTICATED CONTENT:
   - Create nuanced, thought-provoking scenarios
   - Include abstract concepts and complex ideas
   - Use subtle implications and inferences
   - Employ sophisticated literary techniques
   - Challenge the reader intellectually`
};

// TRANSLATION PRACTICE - Vocabulary Examples by Level
const VOCAB_EXAMPLES_BY_LEVEL = {
    'A1': {
        word: 'friend',
        meaning_vi: 'bạn, người bạn',
        pronunciation: '/frend/',
        part_of_speech: 'noun',
        example_en: 'She is my best friend.',
        example_vi: 'Cô ấy là bạn thân nhất của tôi.',
        synonyms: 'buddy, pal'
    },
    'A2': {
        word: 'schedule',
        meaning_vi: 'lịch trình, thời gian biểu',
        pronunciation: '/ˈskedʒuːl/',
        part_of_speech: 'noun',
        example_en: 'I need to check my schedule.',
        example_vi: 'Tôi cần kiểm tra lịch trình của mình.',
        synonyms: 'timetable, agenda'
    },
    'B1': {
        word: 'opportunity',
        meaning_vi: 'cơ hội',
        pronunciation: '/ˌɒpəˈtjuːnɪti/',
        part_of_speech: 'noun',
        example_en: 'This is a great opportunity to learn.',
        example_vi: 'Đây là cơ hội tuyệt vời để học hỏi.',
        synonyms: 'chance, possibility'
    },
    'B2': {
        word: 'collaborate',
        meaning_vi: 'hợp tác, cộng tác',
        pronunciation: '/kəˈlæbəreɪt/',
        part_of_speech: 'verb',
        example_en: 'We need to collaborate with other teams.',
        example_vi: 'Chúng ta cần hợp tác với các đội khác.',
        synonyms: 'cooperate, work together'
    },
    'C1': {
        word: 'nuance',
        meaning_vi: 'sắc thái, nét tinh tế',
        pronunciation: '/ˈnjuːɑːns/',
        part_of_speech: 'noun',
        example_en: 'The nuances of the language are difficult to master.',
        example_vi: 'Các sắc thái của ngôn ngữ rất khó để thành thạo.',
        synonyms: 'subtlety, distinction, shade'
    }
};

// CONVERSATION PRACTICE - Challenges by Level
const CONVERSATION_CHALLENGES_BY_LEVEL = {
    'A1': [
        'Try to answer using complete sentences, not just one word.',
        'Practice using "I like...", "I have...", "I want..." in your responses.',
        'Try to ask me at least one simple question (What? Where? When?).',
        'Use basic greetings and polite phrases (please, thank you, sorry).',
        'Practice saying numbers, days, and times correctly.'
    ],
    'A2': [
        'Try to use past tense when talking about yesterday or last week.',
        'Practice expressing your opinions with "I think..." or "I like... because...".',
        'Use linking words like "and", "but", "because", "so" to connect ideas.',
        'Try to ask follow-up questions to keep the conversation going.',
        'Practice describing people, places, or things with adjectives.'
    ],
    'B1': [
        'Try to use at least 2-3 different tenses in our conversation.',
        'Practice expressing agreement and polite disagreement.',
        'Use a variety of linking words and transitions (however, although, therefore).',
        'Try to paraphrase - express the same idea in different ways.',
        'Practice giving reasons and explanations for your opinions.'
    ],
    'B2': [
        'Try to use some idiomatic expressions naturally in context.',
        'Practice hypothetical language (If I were..., I would have...).',
        'Use sophisticated connectors to structure your arguments.',
        'Try to express nuanced opinions (partly agree, with reservations).',
        'Practice summarizing and synthesizing information.'
    ],
    'C1': [
        'Use advanced vocabulary and idiomatic expressions appropriately.',
        'Practice subtle distinctions in meaning and register.',
        'Employ rhetorical techniques to strengthen your arguments.',
        'Try to use humor, irony, or cultural references naturally.',
        'Practice expressing complex, abstract ideas with precision.'
    ]
};

// CONVERSATION PRACTICE - Personalities (same for all levels, adjusted language complexity)
const CONVERSATION_PERSONALITIES = [
    'friendly and encouraging',
    'curious and inquisitive',
    'professional and polite',
    'enthusiastic and energetic',
    'thoughtful and reflective',
    'patient and supportive'
];

// CONVERSATION PRACTICE - Detailed Personality Descriptions by Level
const PERSONALITY_DESCRIPTIONS = {
    'friendly and encouraging': {
        'A1': 'Be very patient and supportive. Speak slowly and clearly. Celebrate small successes.',
        'A2': 'Be warm and supportive. Give positive reinforcement. Help when they struggle.',
        'B1': 'Be friendly and conversational. Encourage them to express opinions. Be supportive but challenge them.',
        'B2': 'Be engaging and intellectually curious. Push them to elaborate and be more precise.',
        'C1': 'Be a stimulating conversation partner. Challenge their ideas while remaining supportive.'
    },
    'curious and inquisitive': {
        'A1': 'Ask simple questions about their daily life. Show interest in their answers.',
        'A2': 'Ask about their experiences and preferences. Be genuinely interested.',
        'B1': 'Ask thought-provoking questions. Dig deeper into their opinions.',
        'B2': 'Challenge them with probing questions. Explore topics from multiple angles.',
        'C1': 'Engage in intellectual discourse. Ask questions that require nuanced responses.'
    },
    'professional and polite': {
        'A1': 'Be formal but warm. Use simple, polite phrases. Be patient with mistakes.',
        'A2': 'Maintain a professional tone. Model polite language. Be respectful.',
        'B1': 'Be professionally cordial. Use appropriate register. Discuss topics formally.',
        'B2': 'Engage in professional discourse. Use business-appropriate language.',
        'C1': 'Conduct sophisticated professional dialogue. Use nuanced formal register.'
    },
    'enthusiastic and energetic': {
        'A1': 'Show excitement about simple topics. Use encouraging exclamations. Keep energy up.',
        'A2': 'Be lively and engaging. Show genuine enthusiasm for their progress.',
        'B1': 'Bring energy to discussions. Be passionate about topics. Inspire engagement.',
        'B2': 'Be dynamically engaged. Show intellectual enthusiasm.',
        'C1': 'Bring sophisticated enthusiasm. Be passionately engaged with complex ideas.'
    },
    'thoughtful and reflective': {
        'A1': 'Pause to think. Model careful speaking. Be calm and measured.',
        'A2': 'Take time to consider responses. Model thoughtful language.',
        'B1': 'Share reflections and observations. Encourage deeper thinking.',
        'B2': 'Engage in reflective dialogue. Explore philosophical aspects.',
        'C1': 'Engage in deep intellectual reflection. Explore abstract concepts.'
    },
    'patient and supportive': {
        'A1': 'Be extremely patient. Repeat when needed. Never show frustration. Give lots of encouragement.',
        'A2': 'Be patient with mistakes. Provide gentle corrections. Build confidence.',
        'B1': 'Support their growth while challenging them. Be understanding of errors.',
        'B2': 'Balance challenge with support. Help them reach higher levels.',
        'C1': 'Provide sophisticated support. Help refine their advanced skills.'
    }
};

// CONVERSATION PRACTICE - Topic Openers by Level
const CONVERSATION_OPENERS_BY_LEVEL = {
    'A1': {
        'Personal and Communication': [
            'talking about your family',
            'describing your daily routine',
            'introducing yourself to a new neighbor',
            'talking about your hobbies'
        ],
        'Work and Business': [
            'describing your job or school',
            'talking about your workplace',
            'describing a typical work day',
            'talking about your colleagues'
        ],
        'Transportation and Travel': [
            'asking for directions',
            'talking about how you get to work/school',
            'planning a simple trip',
            'at the train station or bus stop'
        ],
        'Shopping and Money': [
            'buying groceries at a store',
            'asking about prices',
            'describing what you want to buy',
            'paying for items'
        ],
        'Food and Drink': [
            'ordering food at a restaurant',
            'talking about your favorite foods',
            'describing what you eat for meals',
            'at a coffee shop'
        ],
        'Health and Medicine': [
            'describing how you feel',
            'at the doctor (simple visit)',
            'talking about healthy habits',
            'describing symptoms simply'
        ],
        'School and Education': [
            'talking about your classes',
            'describing your school/university',
            'talking about your teachers',
            'discussing homework'
        ],
        'Meetings and Presentations': [
            'introducing yourself in a meeting',
            'describing a simple project',
            'asking basic questions in a meeting',
            'talking about your team'
        ]
    },
    'A2': {
        'Personal and Communication': [
            'reconnecting with an old friend',
            'making plans for the weekend',
            'talking about a recent vacation',
            'discussing your neighborhood'
        ],
        'Work and Business': [
            'discussing your job responsibilities',
            'talking about a work project',
            'describing your career goals',
            'meeting a new colleague'
        ],
        'Transportation and Travel': [
            'booking a hotel room',
            'planning a vacation',
            'dealing with travel problems',
            'comparing travel options'
        ],
        'Shopping and Money': [
            'returning an item to a store',
            'comparing products before buying',
            'talking about sales and discounts',
            'discussing your shopping habits'
        ],
        'Food and Drink': [
            'recommending a restaurant',
            'discussing cooking and recipes',
            'talking about eating habits',
            'planning a dinner party'
        ],
        'Health and Medicine': [
            'explaining symptoms to a doctor',
            'discussing exercise routines',
            'talking about healthy eating',
            'discussing sleep habits'
        ],
        'School and Education': [
            'discussing study habits',
            'talking about exams',
            'describing a school project',
            'discussing future studies'
        ],
        'Meetings and Presentations': [
            'preparing for a presentation',
            'discussing meeting outcomes',
            'giving simple feedback',
            'planning a team project'
        ]
    },
    'B1': {
        'Personal and Communication': [
            'discussing life changes and decisions',
            'talking about relationships and friendships',
            'sharing opinions about social issues',
            'discussing cultural differences'
        ],
        'Work and Business': [
            'discussing a new project with a team member',
            'giving and receiving feedback',
            'talking about career development',
            'discussing workplace challenges'
        ],
        'Transportation and Travel': [
            'discussing travel experiences and adventures',
            'comparing different types of travel',
            'dealing with unexpected travel situations',
            'planning a complex trip'
        ],
        'Shopping and Money': [
            'discussing financial goals and budgeting',
            'debating purchase decisions',
            'talking about consumer habits',
            'discussing value for money'
        ],
        'Food and Drink': [
            'discussing food culture and traditions',
            'debating healthy eating choices',
            'sharing and explaining recipes',
            'discussing restaurant experiences'
        ],
        'Health and Medicine': [
            'discussing work-life balance',
            'talking about mental health awareness',
            'comparing healthcare approaches',
            'discussing fitness and wellness goals'
        ],
        'School and Education': [
            'discussing different learning styles',
            'debating education systems',
            'talking about career-education connections',
            'discussing lifelong learning'
        ],
        'Meetings and Presentations': [
            'brainstorming session for a new initiative',
            'presenting project updates',
            'discussing meeting strategies',
            'handling difficult questions'
        ]
    },
    'B2': {
        'Personal and Communication': [
            'discussing personal values and beliefs',
            'analyzing relationship dynamics',
            'debating social media impact on relationships',
            'exploring cultural identity'
        ],
        'Work and Business': [
            'negotiating a business deal',
            'discussing organizational change',
            'analyzing market trends',
            'debating management strategies'
        ],
        'Transportation and Travel': [
            'debating sustainable travel',
            'analyzing tourism impact on communities',
            'discussing future of transportation',
            'comparing travel philosophies'
        ],
        'Shopping and Money': [
            'analyzing consumer psychology',
            'debating ethical consumption',
            'discussing economic trends',
            'exploring investment strategies'
        ],
        'Food and Drink': [
            'analyzing food industry practices',
            'debating food sustainability',
            'discussing culinary traditions and innovation',
            'exploring food and identity'
        ],
        'Health and Medicine': [
            'analyzing healthcare systems',
            'debating medical ethics',
            'discussing mental health in society',
            'exploring alternative medicine'
        ],
        'School and Education': [
            'analyzing education reform',
            'debating technology in education',
            'discussing equal access to education',
            'exploring future of learning'
        ],
        'Meetings and Presentations': [
            'handling complex stakeholder presentations',
            'facilitating difficult discussions',
            'presenting controversial findings',
            'managing cross-cultural meetings'
        ]
    },
    'C1': {
        'Personal and Communication': [
            'exploring philosophical aspects of human connection',
            'analyzing societal shifts in communication',
            'debating authenticity in digital age relationships',
            'examining cross-generational communication gaps'
        ],
        'Work and Business': [
            'analyzing global business ethics',
            'debating future of work and automation',
            'examining corporate social responsibility',
            'discussing leadership philosophies'
        ],
        'Transportation and Travel': [
            'examining globalization through travel lens',
            'debating ethics of tourism',
            'analyzing transportation policy',
            'exploring travel as cultural exchange'
        ],
        'Shopping and Money': [
            'analyzing capitalism and consumerism',
            'debating wealth inequality',
            'examining behavioral economics',
            'exploring alternative economic models'
        ],
        'Food and Drink': [
            'examining food as cultural expression',
            'debating global food systems',
            'analyzing food security challenges',
            'exploring gastronomy and art'
        ],
        'Health and Medicine': [
            'examining bioethics and medical advances',
            'debating healthcare access globally',
            'analyzing public health policy',
            'exploring mind-body connections'
        ],
        'School and Education': [
            'examining education philosophy',
            'debating standardization vs individualization',
            'analyzing education and social mobility',
            'exploring pedagogy innovations'
        ],
        'Meetings and Presentations': [
            'facilitating high-stakes negotiations',
            'presenting to executive leadership',
            'managing crisis communications',
            'leading strategic planning sessions'
        ]
    }
};

// Helper function to get level-appropriate content
function getLevelContent(contentMap, level) {
    return contentMap[level] || contentMap['B1']; // Default to B1 if level not found
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
                    { id: 'schedule', name: 'Study Schedule', icon: 'fas fa-calendar-alt' },
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
                // Fetch progress stats and streak in parallel
                const [progressResp, streakResp] = await Promise.all([
                    fetchAPI('/progress/stats'),
                    fetchAPI('/analytics/streak')
                ]);

                if (progressResp.success) {
                    this.stats.wordsLearned = progressResp.stats.total_words || 0;
                    // Use streak from progress as fallback
                    this.stats.streak = progressResp.stats.current_streak || 0;
                }

                // Override with more accurate streak from analytics
                if (streakResp.success) {
                    this.stats.streak = streakResp.current_streak || 0;
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
        // Quiz history
        quizHistory: [],
        historyLoading: false,
        showHistory: false,

        async init() {
            // Check if coming from flashcards
            if (localStorage.getItem('quizFromFlashcards') === 'true') {
                this.fromFlashcards = true;
                this.studiedWordIds = JSON.parse(localStorage.getItem('lastStudiedWords') || '[]');
                localStorage.removeItem('quizFromFlashcards');

                // Show notification
                Alpine.store('app')?.showToast?.('Quiz loaded with your studied words!', 'success');
            }

            // Load quiz history
            await this.loadQuizHistory();
        },

        async loadQuizHistory() {
            this.historyLoading = true;
            try {
                const response = await fetchAPI('/quiz/history?limit=50');
                if (response.success) {
                    this.quizHistory = response.history || [];
                }
            } catch (error) {
                console.error('Failed to load quiz history:', error);
            } finally {
                this.historyLoading = false;
            }
        },

        async deleteQuiz(quizId) {
            if (!confirm('Bạn có chắc muốn xóa quiz này?')) return;

            try {
                const response = await fetchAPI(`/quiz/${quizId}`, {
                    method: 'DELETE'
                });
                if (response.success) {
                    this.quizHistory = this.quizHistory.filter(q => q.id !== quizId);
                    window.dispatchEvent(new CustomEvent('show-toast', {
                        detail: { message: 'Đã xóa quiz', type: 'success' }
                    }));
                }
            } catch (error) {
                console.error('Failed to delete quiz:', error);
            }
        },

        formatDate(isoDate) {
            if (!isoDate) return '-';
            const date = new Date(isoDate);
            return date.toLocaleDateString('vi-VN', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        getQuizTypeName(type) {
            const types = {
                'multiple_choice': 'Trắc nghiệm',
                'fill_blank': 'Điền từ',
                'matching': 'Nối từ'
            };
            return types[type] || type;
        },

        getScoreColor(score) {
            if (score >= 80) return 'text-green-600 bg-green-100';
            if (score >= 60) return 'text-yellow-600 bg-yellow-100';
            return 'text-red-600 bg-red-100';
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
        promptCopied: false,
        translationHistory: [],
        // Topic Stats
        topicStats: [],
        showTopicStats: false,
        topicStatsLoading: false,
        // JSON Vocabulary
        vocabJson: '',
        vocabSaveResult: '',
        vocabSaveSuccess: false,

        async init() {
            await Promise.all([
                this.loadTranslationHistory(),
                this.loadTopicStats()
            ]);
        },

        async loadTopicStats() {
            this.topicStatsLoading = true;
            try {
                const response = await fetchAPI('/practice/translation/topic-stats');
                if (response.success) {
                    this.topicStats = response.topic_stats || [];
                }
            } catch (error) {
                console.error('Failed to load topic stats:', error);
            } finally {
                this.topicStatsLoading = false;
            }
        },

        getScoreColor(score) {
            if (score >= 8) return 'text-green-600 bg-green-100';
            if (score >= 6) return 'text-yellow-600 bg-yellow-100';
            return 'text-red-600 bg-red-100';
        },

        getDifficultyColor(difficulty) {
            if (difficulty < 0.75) return 'bg-green-100 text-green-700';
            if (difficulty < 0.95) return 'bg-blue-100 text-blue-700';
            if (difficulty <= 1.05) return 'bg-gray-100 text-gray-700';
            if (difficulty <= 1.25) return 'bg-orange-100 text-orange-700';
            return 'bg-red-100 text-red-700';
        },

        formatStatDate(isoDate) {
            if (!isoDate) return '-';
            const date = new Date(isoDate);
            return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
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
                    // Auto refresh topic stats
                    await this.loadTopicStats();
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
                    // Auto refresh topic stats
                    await this.loadTopicStats();
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

            // Perspective options (same for all levels)
            const perspectives = ['first person (I/we)', 'second person (you)', 'third person (he/she/they)'];

            const sourceLang = this.practiceDirection === 'vi_to_en' ? 'Vietnamese' : 'English';
            const targetLang = this.practiceDirection === 'vi_to_en' ? 'English' : 'Vietnamese';
            const length = lengthMap[this.practiceLength];
            const levelDesc = levelDescMap[this.practiceLevel];
            const complexityDesc = complexityDescMap[this.sentenceComplexity];
            const maxSentences = length.split('-')[1].replace(' sentences', '');
            const level = this.practiceLevel;

            // LEVEL-APPROPRIATE random elements for variety
            const variationSeed = generateVariationSeed();
            const levelTones = getLevelContent(TRANSLATION_TONES_BY_LEVEL, level);
            const levelFocus = getLevelContent(TRANSLATION_FOCUS_BY_LEVEL, level);
            const creativeReq = getLevelContent(CREATIVE_REQUIREMENTS_BY_LEVEL, level);
            const vocabExample = getLevelContent(VOCAB_EXAMPLES_BY_LEVEL, level);

            const randomTone = getRandomItems(levelTones);
            const randomFocus = getRandomItems(levelFocus);
            const randomPerspective = getRandomItems(perspectives);

            // Format vocab example for display
            const vocabJson = JSON.stringify([vocabExample], null, 6).replace(/\n/g, '\n   ');

            this.practicePrompt = `You are a language tutor helping me practice ${sourceLang} to ${targetLang} translation.

[Variation #${variationSeed}] - Please create UNIQUE, ORIGINAL content different from any previous sessions.

TASK: Create a translation practice exercise following these requirements:

1. PASSAGE GENERATION:
   - Topic: ${this.practiceTopic}
   - Level: ${this.practiceLevel} (${levelDesc})
   - Number of sentences: ${length}
   - Sentence complexity: ${complexityDesc}
   - Language: Write the passage in ${sourceLang}

   ${creativeReq}

   GRAMMAR & STYLE FOR THIS EXERCISE:
   - Writing tone: ${randomTone}
   - Grammar focus: ${randomFocus}
   - Narrative perspective: ${randomPerspective}

   STRUCTURAL REQUIREMENTS:
   - All sentences must be COHERENT and form a meaningful, connected passage (not random isolated sentences)
   - Use CONSISTENT tenses throughout the passage (appropriate for ${level} level)
   - Sentences should flow naturally and logically from one to another
   - Include transitional words/phrases appropriate for ${level} level

   IMPORTANT: Stay within ${level} level! Do NOT use vocabulary or grammar structures above this level.

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
     • 💡 Suggestions: Tips for improvement (appropriate for ${level} learner)
     • ✅ Model translation: Provide ideal translation
   - Then move to the next sentence

4. FINAL REVIEW:
   After I complete all sentences:
   - 📊 OVERALL SCORE: X.X/10 (can be decimal like 7.5, 8.3, etc.)
   - 📈 Score breakdown by category
   - ❌ Common mistakes I made and how to avoid them
   - ✅ What I did well
   - 📚 Vocabulary to Remember: 10-15 ${level}-appropriate words/phrases with meanings and examples

5. JSON VOCABULARY OUTPUT:
   At the very end, provide a JSON array of ${level}-level vocabulary for me to add to my learning list:
   \`\`\`json
   ${vocabJson}
   \`\`\`
   Include 10-15 important ${level}-level words from this exercise. Each word MUST have all fields: word, meaning_vi, pronunciation (IPA format), part_of_speech, example_en, example_vi, synonyms.
   IMPORTANT: Only include vocabulary appropriate for ${level} level!

START by generating the ${sourceLang} passage about "${this.practiceTopic}" (${length}, ${complexityDesc}) and present the FIRST sentence for me to translate.

Format:
📝 Sentence 1/${maxSentences}:
[First sentence in ${sourceLang}]

Your translation:`;
        },

        copyPracticePrompt(event) {
            navigator.clipboard.writeText(this.practicePrompt);
            Alpine.store('app')?.showToast?.('Đã copy prompt!', 'success');

            // Visual feedback on button
            const btn = event.currentTarget;
            const originalHTML = btn.innerHTML;
            const originalClass = btn.className;

            btn.innerHTML = '<i class="fas fa-check mr-2"></i><span>Copied!</span>';
            btn.className = btn.className.replace('bg-gray-100', 'bg-green-500').replace('hover:bg-gray-200', '').replace('text-gray-700', 'text-white');

            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.className = originalClass;
            }, 2000);
        },

        async parseAndSaveVocab() {
            if (!this.vocabJson) return;

            try {
                // Extract JSON from code block if present
                let jsonStr = this.vocabJson.trim();
                const jsonMatch = jsonStr.match(/```json\s*([\s\S]*?)```/);
                if (jsonMatch) {
                    jsonStr = jsonMatch[1].trim();
                }

                const vocabList = JSON.parse(jsonStr);
                if (!Array.isArray(vocabList) || vocabList.length === 0) {
                    this.vocabSaveResult = 'Không có từ vựng hợp lệ trong JSON';
                    this.vocabSaveSuccess = false;
                    return;
                }

                // Call the direct import endpoint with all vocabulary at once
                const response = await fetchAPI('/import/vocabulary/direct', {
                    method: 'POST',
                    body: JSON.stringify({ vocabulary: vocabList })
                });

                if (response.success) {
                    this.vocabSaveResult = response.message;
                    this.vocabSaveSuccess = response.added > 0;
                    if (response.added > 0) {
                        this.vocabJson = '';
                        // Refresh global stats
                        Alpine.store('app')?.loadStats?.();
                    }
                } else {
                    this.vocabSaveResult = response.message || 'Có lỗi xảy ra';
                    this.vocabSaveSuccess = false;
                }
            } catch (error) {
                console.error('Failed to parse vocab JSON:', error);
                this.vocabSaveResult = 'Lỗi: JSON không hợp lệ';
                this.vocabSaveSuccess = false;
            }
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
        chatPromptCopied: false,
        conversationHistory: [],
        // Topic Stats
        topicStats: [],
        showTopicStats: false,
        topicStatsLoading: false,
        // JSON Vocabulary
        vocabJson: '',
        vocabSaveResult: '',
        vocabSaveSuccess: false,

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
            await Promise.all([
                this.loadConversationHistory(),
                this.loadTopicStats()
            ]);
        },

        async loadTopicStats() {
            this.topicStatsLoading = true;
            try {
                const response = await fetchAPI('/practice/conversation/topic-stats');
                if (response.success) {
                    this.topicStats = response.topic_stats || [];
                }
            } catch (error) {
                console.error('Failed to load topic stats:', error);
            } finally {
                this.topicStatsLoading = false;
            }
        },

        getScoreColor(score) {
            if (score >= 8) return 'text-green-600 bg-green-100';
            if (score >= 6) return 'text-yellow-600 bg-yellow-100';
            return 'text-red-600 bg-red-100';
        },

        getDifficultyColor(difficulty) {
            if (difficulty < 0.75) return 'bg-green-100 text-green-700';
            if (difficulty < 0.95) return 'bg-blue-100 text-blue-700';
            if (difficulty <= 1.05) return 'bg-gray-100 text-gray-700';
            if (difficulty <= 1.25) return 'bg-orange-100 text-orange-700';
            return 'bg-red-100 text-red-700';
        },

        formatStatDate(isoDate) {
            if (!isoDate) return '-';
            const date = new Date(isoDate);
            return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
        },

        getStylesList(styles) {
            if (!styles || Object.keys(styles).length === 0) return '-';
            return Object.entries(styles).map(([style, count]) => `${style}(${count})`).join(', ');
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
                    // Auto refresh topic stats
                    await this.loadTopicStats();
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
                    // Auto refresh topic stats
                    await this.loadTopicStats();
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
            const level = this.chatLevel;

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

            const levelDesc = levelDescMap[level];
            const styleDesc = styleDescMap[this.chatStyle];
            const lengthInfo = lengthMap[this.chatLength];

            // LEVEL-APPROPRIATE random elements for variety
            const variationSeed = generateVariationSeed();
            const randomPersonality = getRandomItems(CONVERSATION_PERSONALITIES);
            const personalityDesc = PERSONALITY_DESCRIPTIONS[randomPersonality]?.[level] || '';

            // Get level-appropriate challenges and openers
            const levelChallenges = getLevelContent(CONVERSATION_CHALLENGES_BY_LEVEL, level);
            const levelOpeners = getLevelContent(CONVERSATION_OPENERS_BY_LEVEL, level);
            const topicOpeners = levelOpeners[this.chatTopic] || [];

            const randomChallenge = getRandomItems(levelChallenges);
            const randomOpener = topicOpeners.length > 0 ? getRandomItems(topicOpeners) : null;

            // Get level-appropriate vocab example
            const vocabExample = getLevelContent(VOCAB_EXAMPLES_BY_LEVEL, level);
            const vocabJson = JSON.stringify([vocabExample], null, 2);

            let roleplayContext = '';
            if (this.chatStyle === 'roleplay') {
                const scenario = randomOpener || 'a realistic situation related to ' + this.chatTopic;
                roleplayContext = `\n\nROLE-PLAY SCENARIO: Create a specific ${level}-appropriate scenario about "${scenario}".
Assign me a role and describe the setting before we begin.
Keep the scenario complexity suitable for ${level} level.`;
            }

            const contextHint = randomOpener && this.chatStyle !== 'roleplay'
                ? `\n- Suggested context: ${randomOpener} (use this as inspiration but feel free to adapt)`
                : '';

            // Level-specific language guidance
            const languageGuidance = {
                'A1': `- Use VERY simple sentences (5-8 words typically)
   - Speak slowly and clearly
   - Use only basic vocabulary (common everyday words)
   - Avoid idioms, phrasal verbs, and complex grammar
   - Repeat or rephrase if I seem confused`,
                'A2': `- Use simple sentences with some compound structures
   - Use everyday vocabulary with occasional new words (explain if needed)
   - Avoid complex idioms, use only basic phrasal verbs
   - Be patient and supportive`,
                'B1': `- Use varied sentence structures
   - Include some common idioms and phrasal verbs
   - Challenge me with new vocabulary in context
   - Encourage me to express opinions`,
                'B2': `- Use natural, fluent English with varied structures
   - Include idiomatic expressions and phrasal verbs
   - Discuss abstract concepts when relevant
   - Push me to be more precise and nuanced`,
                'C1': `- Use sophisticated, natural English
   - Include nuanced expressions, idioms, and cultural references
   - Engage with complex, abstract topics
   - Challenge me to use precise, varied vocabulary`
            };

            this.chatPrompt = `You are an English conversation partner helping me practice speaking English at ${level} level.

[Variation #${variationSeed}] - Please create UNIQUE, ORIGINAL conversation different from any previous sessions.

CONVERSATION SETTINGS:
- Topic: ${this.chatTopic}
- My Level: ${level} (${levelDesc})
- Style: ${this.chatStyle} - ${styleDesc}
- Length: ${lengthInfo.exchanges} exchanges (${lengthInfo.desc} conversation)${contextHint}${roleplayContext}

YOUR PERSONALITY & BEHAVIOR:
- Be ${randomPersonality}
- ${personalityDesc}

PRACTICE CHALLENGE FOR ME (${level} level):
${randomChallenge}

LANGUAGE LEVEL GUIDANCE:
${languageGuidance[level]}

SCORING CRITERIA (for each of my responses, score 0-10 with decimals allowed):
- Communication (3 points): Clear message, appropriate response to context
- Grammar (3 points): Correct tense, sentence structure, word order
- Vocabulary (2 points): Appropriate word choice, variety of expressions
- Fluency (2 points): Natural flow, no awkward phrasing

YOUR ROLE AS CONVERSATION PARTNER:
1. Engage in natural, flowing conversation about the topic
2. STRICTLY match your language complexity to ${level} level
3. Keep your responses conversational (2-4 sentences for lower levels, can be longer for B2/C1)
4. Ask follow-up questions to keep the conversation going
5. Naturally introduce 1-2 new ${level}-appropriate vocabulary items per exchange

AFTER EACH OF MY RESPONSES:
1. Continue the conversation naturally
2. Then provide feedback:
   📊 Score: X.X/10 (Communication X/3, Grammar X/3, Vocabulary X/2, Fluency X/2)
   📝 Corrections (if any): "[error]" → "[correct]"
   💡 Better expression: Suggest ${level}-appropriate alternatives
3. If my English is perfect, just show the score without corrections

CONVERSATION FLOW:
- Track exchange count (e.g., "Exchange 3/${lengthInfo.exchanges.split('-')[1]}")
- After ${lengthInfo.exchanges} exchanges, naturally conclude the conversation

END OF SESSION:
Provide "📊 FINAL ASSESSMENT":
- Overall Score: X.X/10 (can be decimal like 7.5, 8.3)
- Score breakdown by category (average)
- ✅ Strengths: What I did well
- ❌ Areas to improve: Common mistakes with ${level}-appropriate corrections
- 📚 Key Vocabulary: 10-15 ${level}-level words/phrases from our conversation (with Vietnamese translations)
- 💡 Tips: Specific suggestions for a ${level} learner

JSON VOCABULARY OUTPUT:
At the very end, provide a JSON array of ${level}-level vocabulary for me to add to my learning list:
\`\`\`json
${vocabJson}
\`\`\`
Include 10-15 ${level}-appropriate words from our conversation. Each word MUST have all fields: word, meaning_vi, pronunciation (IPA format), part_of_speech, example_en, example_vi, synonyms.
IMPORTANT: Only include vocabulary appropriate for ${level} level!

START the conversation now! Greet me appropriately for ${level} level and ask an opening question about "${this.chatTopic}".

[Exchange 1/${lengthInfo.exchanges.split('-')[1]}]`;
        },

        copyChatPrompt(event) {
            navigator.clipboard.writeText(this.chatPrompt);
            Alpine.store('app')?.showToast?.('Đã copy prompt!', 'success');

            // Visual feedback on button
            const btn = event.currentTarget;
            const originalHTML = btn.innerHTML;
            const originalClass = btn.className;

            btn.innerHTML = '<i class="fas fa-check mr-2"></i><span>Copied!</span>';
            btn.className = btn.className.replace('bg-gray-100', 'bg-green-500').replace('hover:bg-gray-200', '').replace('text-gray-700', 'text-white');

            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.className = originalClass;
            }, 2000);
        },

        async parseAndSaveVocab() {
            if (!this.vocabJson) return;

            try {
                // Extract JSON from code block if present
                let jsonStr = this.vocabJson.trim();
                const jsonMatch = jsonStr.match(/```json\s*([\s\S]*?)```/);
                if (jsonMatch) {
                    jsonStr = jsonMatch[1].trim();
                }

                const vocabList = JSON.parse(jsonStr);
                if (!Array.isArray(vocabList) || vocabList.length === 0) {
                    this.vocabSaveResult = 'Không có từ vựng hợp lệ trong JSON';
                    this.vocabSaveSuccess = false;
                    return;
                }

                // Call the direct import endpoint with all vocabulary at once
                const response = await fetchAPI('/import/vocabulary/direct', {
                    method: 'POST',
                    body: JSON.stringify({ vocabulary: vocabList })
                });

                if (response.success) {
                    this.vocabSaveResult = response.message;
                    this.vocabSaveSuccess = response.added > 0;
                    if (response.added > 0) {
                        this.vocabJson = '';
                        // Refresh global stats
                        Alpine.store('app')?.loadStats?.();
                    }
                } else {
                    this.vocabSaveResult = response.message || 'Có lỗi xảy ra';
                    this.vocabSaveSuccess = false;
                }
            } catch (error) {
                console.error('Failed to parse vocab JSON:', error);
                this.vocabSaveResult = 'Lỗi: JSON không hợp lệ';
                this.vocabSaveSuccess = false;
            }
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

    // Study Schedule Page Component
    Alpine.data('schedulePage', () => ({
        todayCompleted: 0,
        todayTotal: 5,
        weekStreak: 0,
        currentLevel: 'A2',
        weeklyProgress: 0,
        currentDayIndex: new Date().getDay(),

        todaySchedule: [],
        weekPlan: [],
        dailyGoals: [],
        expertTips: [
            "Học từ vựng vào buổi sáng khi não bộ còn tươi mới sẽ giúp ghi nhớ tốt hơn 30%.",
            "Áp dụng quy tắc 20-20-20: Học 20 phút, nghỉ 20 giây, nhìn xa 20 feet để giảm mỏi mắt.",
            "Sử dụng Spaced Repetition (SRS) là phương pháp được khoa học chứng minh hiệu quả nhất.",
            "Kết hợp nghe, nói, đọc, viết trong mỗi buổi học để kích hoạt đa giác quan.",
            "Đặt mục tiêu nhỏ, đạt được sẽ tạo động lực lớn hơn cho các mục tiêu tiếp theo.",
            "Review từ cũ trước khi học từ mới - não bộ cần 5-7 lần lặp lại để ghi nhớ lâu dài.",
            "Thực hành conversation hàng ngày, dù chỉ 5 phút, cũng hiệu quả hơn 1 giờ mỗi tuần.",
            "Học từ vựng theo chủ đề giúp tạo liên kết ngữ nghĩa và nhớ lâu hơn."
        ],
        expertTip: '',

        init() {
            this.loadFromStorage();
            this.generateTodaySchedule();
            this.generateWeekPlan();
            this.loadDailyGoals();
            this.expertTip = this.expertTips[Math.floor(Math.random() * this.expertTips.length)];
            this.loadStats();
        },

        loadFromStorage() {
            const today = new Date().toDateString();
            const saved = localStorage.getItem('scheduleData');
            if (saved) {
                const data = JSON.parse(saved);
                if (data.date === today) {
                    this.todaySchedule = data.todaySchedule || [];
                    this.todayCompleted = this.todaySchedule.filter(s => s.completed).length;
                }
            }
        },

        saveToStorage() {
            const data = {
                date: new Date().toDateString(),
                todaySchedule: this.todaySchedule
            };
            localStorage.setItem('scheduleData', JSON.stringify(data));
        },

        async loadStats() {
            try {
                const response = await fetchAPI('/progress/stats');
                if (response.success) {
                    this.weekStreak = response.stats.current_streak || 0;
                    const totalWords = response.stats.total_words || 0;

                    // Determine level based on words learned
                    if (totalWords >= 3000) this.currentLevel = 'C1';
                    else if (totalWords >= 2000) this.currentLevel = 'B2';
                    else if (totalWords >= 1000) this.currentLevel = 'B1';
                    else if (totalWords >= 500) this.currentLevel = 'A2';
                    else this.currentLevel = 'A1';
                }
            } catch (error) {
                console.error('Failed to load stats:', error);
            }

            // Calculate weekly progress
            this.weeklyProgress = Math.round((this.todayCompleted / this.todayTotal) * 100);
        },

        async loadDailyGoals() {
            this.dailyGoals = [
                { name: 'Từ vựng mới', current: 0, target: 10, color: 'bg-blue-500' },
                { name: 'Flashcard review', current: 0, target: 20, color: 'bg-yellow-500' },
                { name: 'Quiz hoàn thành', current: 0, target: 2, color: 'bg-green-500' },
                { name: 'SRS Review', current: 0, target: 15, color: 'bg-orange-500' },
                { name: 'Phút thực hành', current: 0, target: 30, color: 'bg-purple-500' }
            ];

            try {
                // Fetch all stats in parallel
                const [dailyResp, quizResp, srsResp, flashcardResp, practiceResp] = await Promise.all([
                    fetchAPI('/progress/daily-summary').catch(() => null),
                    fetchAPI('/quiz/stats').catch(() => null),
                    fetchAPI('/srs/stats').catch(() => null),
                    fetchAPI('/flashcards/stats').catch(() => null),
                    fetchAPI('/practice/all/stats').catch(() => null)
                ]);

                // Words learned today from daily summary
                if (dailyResp?.success && dailyResp.summary) {
                    this.dailyGoals[0].current = dailyResp.summary.words_learned || 0;
                    // Quizzes from daily summary
                    this.dailyGoals[2].current = dailyResp.summary.quizzes_completed || 0;
                }

                // Flashcard reviews - check stats response
                if (flashcardResp?.success && flashcardResp.stats) {
                    this.dailyGoals[1].current = flashcardResp.stats.reviewed_today ||
                                                  flashcardResp.stats.cards_reviewed_today ||
                                                  flashcardResp.stats.total_reviews || 0;
                }

                // Quiz stats as fallback
                if (quizResp?.success && quizResp.stats && this.dailyGoals[2].current === 0) {
                    this.dailyGoals[2].current = quizResp.stats.quizzes_today ||
                                                  quizResp.stats.total_quizzes || 0;
                }

                // SRS reviews completed
                if (srsResp?.success && srsResp.stats) {
                    this.dailyGoals[3].current = srsResp.stats.reviewed_today ||
                                                  srsResp.stats.reviews_completed_today || 0;
                }

                // Practice minutes (translation + conversation)
                if (practiceResp?.success && practiceResp.stats) {
                    const transCount = practiceResp.stats.translation?.total ||
                                       practiceResp.stats.translation_count || 0;
                    const convCount = practiceResp.stats.conversation?.total ||
                                      practiceResp.stats.conversation_count || 0;
                    // Estimate ~3 minutes per practice session
                    this.dailyGoals[4].current = Math.min(30, (transCount + convCount) * 3);
                }

                // Also check localStorage for today's activity tracking
                this.loadLocalGoalProgress();

            } catch (e) {
                console.error('Error loading goals:', e);
                this.loadLocalGoalProgress();
            }
        },

        loadLocalGoalProgress() {
            const today = new Date().toDateString();
            const saved = localStorage.getItem('dailyGoalProgress');
            if (saved) {
                const data = JSON.parse(saved);
                if (data.date === today) {
                    // Merge with existing data (take max values)
                    if (data.flashcards) this.dailyGoals[1].current = Math.max(this.dailyGoals[1].current, data.flashcards);
                    if (data.practiceMinutes) this.dailyGoals[4].current = Math.max(this.dailyGoals[4].current, data.practiceMinutes);
                }
            }
        },

        trackGoalProgress(type, value) {
            const today = new Date().toDateString();
            let data = { date: today };
            const saved = localStorage.getItem('dailyGoalProgress');
            if (saved) {
                const parsed = JSON.parse(saved);
                if (parsed.date === today) {
                    data = parsed;
                }
            }
            data[type] = (data[type] || 0) + value;
            localStorage.setItem('dailyGoalProgress', JSON.stringify(data));
        },

        generateTodaySchedule() {
            const dayOfWeek = new Date().getDay();
            const schedules = {
                0: [ // Sunday - Light review day
                    { title: 'SRS Review nhẹ nhàng', time: '09:00', duration: '15 phút', icon: 'fas fa-redo', page: 'srs', description: 'Ôn tập từ đến hạn với SRS', completed: false },
                    { title: 'Flashcards Review', time: '10:00', duration: '10 phút', icon: 'fas fa-clone', page: 'flashcards', description: 'Lật thẻ ôn từ vựng tuần qua', completed: false },
                    { title: 'Xem Analytics tuần', time: '11:00', duration: '5 phút', icon: 'fas fa-chart-line', page: 'analytics', description: 'Đánh giá tiến độ học tập', completed: false }
                ],
                1: [ // Monday - Vocabulary focus
                    { title: 'Học từ vựng mới', time: '07:00', duration: '20 phút', icon: 'fas fa-book', page: 'vocabulary', description: 'Thêm 10 từ mới vào danh sách', completed: false },
                    { title: 'Flashcards Practice', time: '12:00', duration: '15 phút', icon: 'fas fa-clone', page: 'flashcards', description: 'Luyện nhớ từ bằng flashcard', completed: false },
                    { title: 'Quiz kiểm tra', time: '18:00', duration: '10 phút', icon: 'fas fa-question-circle', page: 'quiz', description: 'Làm quiz từ vựng đã học', completed: false },
                    { title: 'SRS Review', time: '20:00', duration: '10 phút', icon: 'fas fa-redo', page: 'srs', description: 'Hoàn thành review SRS', completed: false },
                    { title: 'Translation Practice', time: '21:00', duration: '15 phút', icon: 'fas fa-language', page: 'translation', description: 'Luyện dịch câu Anh-Việt', completed: false }
                ],
                2: [ // Tuesday - Practice focus
                    { title: 'SRS Morning Review', time: '07:00', duration: '10 phút', icon: 'fas fa-redo', page: 'srs', description: 'Ôn tập từ đến hạn buổi sáng', completed: false },
                    { title: 'Conversation Practice', time: '12:00', duration: '20 phút', icon: 'fas fa-comments', page: 'conversation', description: 'Thực hành hội thoại với AI', completed: false },
                    { title: 'Học từ vựng mới', time: '18:00', duration: '15 phút', icon: 'fas fa-book', page: 'vocabulary', description: 'Thêm 5-7 từ mới', completed: false },
                    { title: 'Flashcards Review', time: '20:00', duration: '10 phút', icon: 'fas fa-clone', page: 'flashcards', description: 'Ôn lại từ đã học', completed: false },
                    { title: 'Quiz tổng hợp', time: '21:00', duration: '10 phút', icon: 'fas fa-question-circle', page: 'quiz', description: 'Kiểm tra kiến thức', completed: false }
                ],
                3: [ // Wednesday - Mixed
                    { title: 'Học từ vựng mới', time: '07:00', duration: '20 phút', icon: 'fas fa-book', page: 'vocabulary', description: 'Thêm 10 từ theo chủ đề', completed: false },
                    { title: 'SRS Review', time: '12:00', duration: '15 phút', icon: 'fas fa-redo', page: 'srs', description: 'Review từ đến hạn', completed: false },
                    { title: 'Translation Practice', time: '18:00', duration: '20 phút', icon: 'fas fa-language', page: 'translation', description: 'Luyện dịch nâng cao', completed: false },
                    { title: 'Flashcards', time: '20:00', duration: '10 phút', icon: 'fas fa-clone', page: 'flashcards', description: 'Flashcard từ mới', completed: false },
                    { title: 'Quiz cuối ngày', time: '21:00', duration: '10 phút', icon: 'fas fa-question-circle', page: 'quiz', description: 'Quiz tổng hợp', completed: false }
                ],
                4: [ // Thursday - Conversation focus
                    { title: 'SRS Morning', time: '07:00', duration: '10 phút', icon: 'fas fa-redo', page: 'srs', description: 'Review buổi sáng', completed: false },
                    { title: 'Conversation Practice', time: '12:00', duration: '25 phút', icon: 'fas fa-comments', page: 'conversation', description: 'Hội thoại chuyên sâu', completed: false },
                    { title: 'Học từ vựng', time: '18:00', duration: '15 phút', icon: 'fas fa-book', page: 'vocabulary', description: 'Từ vựng giao tiếp', completed: false },
                    { title: 'Flashcards', time: '20:00', duration: '15 phút', icon: 'fas fa-clone', page: 'flashcards', description: 'Ôn từ flashcard', completed: false },
                    { title: 'Quiz nhanh', time: '21:00', duration: '10 phút', icon: 'fas fa-question-circle', page: 'quiz', description: 'Quiz 10 câu', completed: false }
                ],
                5: [ // Friday - Review & Test
                    { title: 'Học từ mới', time: '07:00', duration: '15 phút', icon: 'fas fa-book', page: 'vocabulary', description: 'Từ vựng cuối tuần', completed: false },
                    { title: 'SRS Complete', time: '12:00', duration: '20 phút', icon: 'fas fa-redo', page: 'srs', description: 'Hoàn thành tất cả SRS', completed: false },
                    { title: 'Quiz tổng tuần', time: '18:00', duration: '15 phút', icon: 'fas fa-question-circle', page: 'quiz', description: 'Quiz ôn tập cả tuần', completed: false },
                    { title: 'Translation', time: '20:00', duration: '15 phút', icon: 'fas fa-language', page: 'translation', description: 'Luyện dịch', completed: false },
                    { title: 'Analytics Review', time: '21:00', duration: '5 phút', icon: 'fas fa-chart-line', page: 'analytics', description: 'Xem tiến độ tuần', completed: false }
                ],
                6: [ // Saturday - Intensive practice
                    { title: 'Vocabulary Sprint', time: '09:00', duration: '25 phút', icon: 'fas fa-book', page: 'vocabulary', description: 'Học 15-20 từ mới', completed: false },
                    { title: 'Flashcards Marathon', time: '10:00', duration: '20 phút', icon: 'fas fa-clone', page: 'flashcards', description: 'Review 30+ flashcards', completed: false },
                    { title: 'Conversation Long', time: '14:00', duration: '30 phút', icon: 'fas fa-comments', page: 'conversation', description: 'Hội thoại dài', completed: false },
                    { title: 'Quiz Challenge', time: '16:00', duration: '15 phút', icon: 'fas fa-question-circle', page: 'quiz', description: 'Quiz 20 câu thử thách', completed: false },
                    { title: 'SRS Catch-up', time: '18:00', duration: '15 phút', icon: 'fas fa-redo', page: 'srs', description: 'Hoàn thành SRS còn lại', completed: false }
                ]
            };

            // Load saved schedule or use default
            const saved = localStorage.getItem('scheduleData');
            if (saved) {
                const data = JSON.parse(saved);
                if (data.date === new Date().toDateString() && data.todaySchedule) {
                    this.todaySchedule = data.todaySchedule;
                    this.todayCompleted = this.todaySchedule.filter(s => s.completed).length;
                    this.todayTotal = this.todaySchedule.length;
                    return;
                }
            }

            this.todaySchedule = schedules[dayOfWeek] || schedules[1];
            this.todayTotal = this.todaySchedule.length;
        },

        generateWeekPlan() {
            const days = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];
            const fullDays = ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
            const today = new Date();

            const taskTemplates = {
                0: [
                    { short: 'Review', type: 'review' },
                    { short: 'Flashcard', type: 'review' },
                    { short: 'Analytics', type: 'practice' }
                ],
                1: [
                    { short: 'Vocabulary', type: 'vocabulary' },
                    { short: 'Quiz', type: 'quiz' },
                    { short: 'Translation', type: 'practice' }
                ],
                2: [
                    { short: 'Conversation', type: 'practice' },
                    { short: 'SRS Review', type: 'review' },
                    { short: 'Quiz', type: 'quiz' }
                ],
                3: [
                    { short: 'Vocabulary', type: 'vocabulary' },
                    { short: 'Translation', type: 'practice' },
                    { short: 'Flashcard', type: 'review' }
                ],
                4: [
                    { short: 'Conversation', type: 'practice' },
                    { short: 'Vocabulary', type: 'vocabulary' },
                    { short: 'Quiz', type: 'quiz' }
                ],
                5: [
                    { short: 'SRS Full', type: 'review' },
                    { short: 'Quiz Tuần', type: 'quiz' },
                    { short: 'Analytics', type: 'practice' }
                ],
                6: [
                    { short: 'Vocab Sprint', type: 'vocabulary' },
                    { short: 'Conversation', type: 'practice' },
                    { short: 'Challenge', type: 'quiz' }
                ]
            };

            this.weekPlan = [];
            for (let i = 0; i < 7; i++) {
                const date = new Date(today);
                date.setDate(today.getDate() - today.getDay() + i);

                this.weekPlan.push({
                    name: days[i],
                    fullName: fullDays[i],
                    date: date.getDate() + '/' + (date.getMonth() + 1),
                    tasks: taskTemplates[i]
                });
            }
        },

        getCurrentDay() {
            const days = ['Chủ nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'];
            return days[new Date().getDay()];
        },

        markCompleted(idx) {
            this.todaySchedule[idx].completed = true;
            this.todayCompleted = this.todaySchedule.filter(s => s.completed).length;
            this.weeklyProgress = Math.round((this.todayCompleted / this.todayTotal) * 100);
            this.saveToStorage();
        },

        goToActivity(page) {
            window.dispatchEvent(new CustomEvent('navigate', { detail: page }));
        },

        showDayDetail(idx) {
            // Could show a modal with detailed schedule for that day
            console.log('Show detail for day:', this.weekPlan[idx]);
        }
    }));
});
