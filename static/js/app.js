/* Client-side application logic for GitHub Trending Dashboard */

const LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Rust": "#dea584", "Go": "#00ADD8", "Java": "#b07219", "C++": "#f34b7d",
    "C": "#555", "C#": "#178600", "Swift": "#F05138", "Kotlin": "#A97BFF",
    "Ruby": "#701516", "PHP": "#4F5D95", "Shell": "#89e051", "Dart": "#00B4AB",
};

const T = {
    en: {
        title: "🔥 GitHub Trending",
        subtitle: "Discover the hottest repositories right now",
        searchPlaceholder: "Search repositories...",
        duration: { day: "Today", week: "This Week", month: "This Month", year: "This Year" },
        allLanguages: "All Languages",
        sort: { stars: "⭐ Stars", forks: "🍴 Forks", updated: "🕐 Updated", hotness: "🔥 Hotness" },
        source: { api: "GitHub API", trending: "Trending Page" },
        minStars: "⭐ Min:",
        refresh: "Refresh",
        found: "repositories found",
        autoRefresh: "Auto-refresh (60s)",
        loading: "Loading trending repositories...",
        noRepos: "No repos found",
        tryFilters: "Try different filters",
        error: "Error",
        tryAgain: "Try Again",
        footer: 'Powered by <a href="https://docs.github.com/en/rest" target="_blank">GitHub API</a> • Built with 🔥 GitHub Trending CLI',
        noDesc: "No description",
        starsLabel: { day: "stars today", week: "stars this week", month: "stars this month", year: "stars this year" },
        tweetsTitle: "📊 Repo Details Hub",
        openTwitter: "Open in X/Twitter",
        simulated: "Simulated",
        noTweets: "No tweets found",
        errorTweets: "Error loading tweets",
        analytics: "📊 Analytics",
        chartLang: "Languages Distribution",
        chartStars: "Top Repositories by Stars",
        statRepos: "Total Repositories",
        statAvgStars: "Average Stars",
        statTopLang: "Top Language",
        noData: "No Data",
        limitLabel: "Limit:",
        limitOptions: { 10: "10 Repos", 25: "25 Repos", 50: "50 Repos", 100: "100 Repos", 250: "250 Repos", 500: "500 Repos" },
        aiBubbleTitle: "Gemini AI Agent",
        aiOnlineStatus: "Online • Ready to assist",
        aiPlaceholder: "Ask anything about trending repos...",
        aiSend: "Send",
        aiGlobalContext: "Global context: analyzing current page",
        aiRepoContext: "Context: analyzing {name}",
        aiClearContext: "Reset to Global",
        aiHelpGreeting: "Hello! I am your Gemini AI Coding Agent. Ask me questions about the trending repositories currently loaded on this page, or click 🤖 AI on any repository card to summarize it!",
        apiKeyTitle: "Gemini API Key Settings",
        apiKeyDesc: "Provide your Google Gemini API key to enable AI features. It is stored locally in your browser.",
        apiKeyPlaceholder: "Enter Gemini API Key...",
        apiKeySave: "Save Key",
        apiKeyCancel: "Cancel",
        apiKeySavedAlert: "API Key saved successfully!",
        aiButtonLabel: "AI",
        aiLoading: "Thinking...",
        sidebarTrendsTitle: "🔥 Dev Community Trends",
        sidebarAiTipText: "Click 🤖 AI on any repository to get a quick summary, installation tips, and technical architecture reviews instantly.",
        popularTopics: "Popular Topics:",
        minStarsOptions: {
            0: "Any Stars",
            100: "> 100 ⭐",
            1000: "> 1k ⭐",
            5000: "> 5k ⭐",
            10000: "> 10k ⭐",
            50000: "> 50k ⭐",
            "custom": "Custom..."
        },
        modalAltSearch: "Alt Search:",
        modalAiOpinion: "🤖 AI Sentiment",
        modalAiOpinionLoading: "Analyzing community discussions...",
        modalAiOpinionHeader: "🤖 AI Community Sentiment Analysis",
        advToggle: "Advanced",
        advTopic: "Topic / Tag",
        advAuthor: "Owner / Author",
        advMinForks: "Min Forks",
        advMaxStars: "Max Stars",
        advExcludeOrg: "Exclude Big Tech",
        presetDefault: "🔍 Default Search",
        presetSecurity: "🛡️ Security & Audits",
        presetBypasses: "🔓 Bypasses & Hacks",
        presetHidden: "👁️ Hidden / Obscure",
        presetNetwork: "🌐 Network & Proxy",
        presetObscureAuthors: "👤 Obscure / Independent Authors",
        deepSearchLabel: "🕵️ Deep / Obscure Search",
        chipSuggest: "🚀 Suggest Hot Repos",
        chipExplain: "🔥 Explain Trends",
        chipDigest: "📋 Daily Digest",
        chipHelp: "❓ Help Guide",
        twitterProxy: "Twitter Proxy",
        twitterProxyOptions: {
            "direct": "X.com (Direct)",
            "https://xcancel.com": "xcancel.com (Proxy)",
            "https://nitter.catsarch.com": "nitter.catsarch.com",
            "https://nitter.tiekoetter.com": "nitter.tiekoetter.com",
            "https://nitter.kareem.one": "nitter.kareem.one"
        },
        companionChatTab: "Assistant",
        companionTrendsTab: "Community Trends",
        sidebarTitles: {
            search: "Search",
            presets: "Presets",
            duration: "Duration",
            language: "Language",
            sort: "Sort By",
            source: "Source",
            limit: "Limit",
            minStars: "Min Stars",
            advanced: "Advanced Filters"
        }
    },
    ru: {
        title: "🔥 Тренды GitHub",
        subtitle: "Открывайте самые популярные репозитории прямо сейчас",
        searchPlaceholder: "Поиск репозиториев...",
        duration: { day: "Сегодня", week: "На этой неделе", month: "В этом месяце", year: "В этом году" },
        allLanguages: "Все языки",
        sort: { stars: "⭐ Звезды", forks: "🍴 Форки", updated: "🕐 Обновлено", hotness: "🔥 Горячие" },
        source: { api: "GitHub API", trending: "Страница трендов" },
        minStars: "⭐ Мин:",
        refresh: "Обновить",
        found: "репозиториев найдено",
        autoRefresh: "Автообновление (60с)",
        loading: "Загрузка трендовых репозиториев...",
        noRepos: "Репозитории не найдены",
        tryFilters: "Попробуйте другие фильтры",
        error: "Ошибка",
        tryAgain: "Повторить",
        footer: 'Работает на <a href="https://docs.github.com/en/rest" target="_blank">GitHub API</a> • Создано с помощью 🔥 GitHub Trending CLI',
        noDesc: "Нет описания",
        starsLabel: { day: "звезд сегодня", week: "звезд на этой неделе", month: "звезд в этом месяце", year: "звезд в этом году" },
        tweetsTitle: "📊 Панель информации о проекте",
        openTwitter: "Открыть в X/Twitter",
        simulated: "Смоделировано",
        noTweets: "Упоминаний не найдено",
        errorTweets: "Ошибка при загрузке твитов",
        analytics: "📊 Аналитика",
        chartLang: "Распределение по языкам",
        chartStars: "Топ репозиториев по звездам",
        statRepos: "Всего репозиториев",
        statAvgStars: "Среднее число звезд",
        statTopLang: "Популярный язык",
        noData: "Нет данных",
        limitLabel: "Лимит:",
        limitOptions: { 10: "10 репо", 25: "25 репо", 50: "50 репо", 100: "100 репо", 250: "250 репо", 500: "500 репо" },
        aiBubbleTitle: "ИИ Агент Gemini",
        aiOnlineStatus: "В сети • Готов помочь",
        aiPlaceholder: "Спросите меня о трендах...",
        aiSend: "Отправить",
        aiGlobalContext: "Глобальный контекст: анализ страницы",
        aiRepoContext: "Контекст: анализ {name}",
        aiClearContext: "Сбросить к глобальному",
        aiHelpGreeting: "Привет! Я твой ИИ-помощник Gemini. Задавай мне вопросы о текущих трендовых репозиториях на странице или нажми 🤖 ИИ на карточке любого репозитория, чтобы получить его краткую сводку!",
        apiKeyTitle: "Настройки ключа Gemini API",
        apiKeyDesc: "Введите ваш Google Gemini API ключ для работы ИИ-агента. Он сохраняется локально в вашем браузере.",
        apiKeyPlaceholder: "Введите Gemini API Ключ...",
        apiKeySave: "Сохранить",
        apiKeyCancel: "Отмена",
        apiKeySavedAlert: "API Ключ успешно сохранен!",
        aiButtonLabel: "ИИ",
        aiLoading: "Думаю...",
        sidebarTrendsTitle: "🔥 Тренды сообщества",
        sidebarAiTipText: "Нажмите 🤖 ИИ на любом репозитории, чтобы мгновенно получить краткое описание, инструкции по установке и технический разбор.",
        popularTopics: "Популярные темы:",
        minStarsOptions: {
            0: "Любые звезды",
            100: "> 100 ⭐",
            1000: "> 1k ⭐",
            5000: "> 5k ⭐",
            10000: "> 10k ⭐",
            50000: "> 50k ⭐",
            "custom": "Свой лимит..."
        },
        modalAltSearch: "Альтернативный поиск:",
        modalAiOpinion: "🤖 Анализ мнений ИИ",
        modalAiOpinionLoading: "Анализирую обсуждения в сообществе...",
        modalAiOpinionHeader: "🤖 ИИ-анализ мнений сообщества разработчиков",
        advToggle: "Фильтры",
        advTopic: "Тема / Тег",
        advAuthor: "Автор / Организация",
        advMinForks: "Мин. форков",
        advMaxStars: "Макс. звёзд",
        advExcludeOrg: "Без IT-гигантов",
        presetDefault: "🔍 Поиск по умолчанию",
        presetSecurity: "🛡️ Безопасность и аудит",
        presetBypasses: "🔓 Обходы и взломы",
        presetHidden: "👁️ Скрытые / Малоизвестные",
        presetNetwork: "🌐 Сети и прокси",
        presetObscureAuthors: "👤 Скрытые / Независимые авторы",
        deepSearchLabel: "🕵️ Скрытый поиск",
        chipSuggest: "🚀 Рекомендовать тренды",
        chipExplain: "🔥 Объяснить темы",
        chipDigest: "📋 Дайджест дня",
        chipHelp: "❓ Справка ИИ",
        twitterProxy: "Прокси Twitter",
        twitterProxyOptions: {
            "direct": "X.com (Напрямую)",
            "https://xcancel.com": "xcancel.com (Прокси)",
            "https://nitter.catsarch.com": "nitter.catsarch.com",
            "https://nitter.tiekoetter.com": "nitter.tiekoetter.com",
            "https://nitter.kareem.one": "nitter.kareem.one"
        },
        companionChatTab: "Ассистент",
        companionTrendsTab: "Тренды сообщества",
        sidebarTitles: {
            search: "Поиск",
            presets: "Шаблоны",
            duration: "Период",
            language: "Язык",
            sort: "Сортировка",
            source: "Источник",
            limit: "Лимит",
            minStars: "Мин. звёзд",
            advanced: "Доп. фильтры"
        }
    }
};

// Application State
let currentLang = localStorage.getItem("lang") || "en";
let autoTimer = null;
let lastFetchedRepos = null;
let lastFetchedSource = "api";
let analyticsVisible = false;
let historyVisible = false;
let langChartInstance = null;
let starsChartInstance = null;
let aiHistory = [];
let aiSelectedRepo = null;
let activeTagFilter = null;
let selectedCompareRepos = [];
let currentModalTab = 'summary';
let currentOpenRepoName = '';
let currentOpenRepoIndex = -1;
let growthChartInstance = null;
let currentDetailsRepoObj = null;

// DOM Helper
const $ = id => document.getElementById(id);

// Initialize Event Listeners when loaded
window.addEventListener('DOMContentLoaded', () => {
    const searchInput = $('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keydown', e => { if (e.key === 'Enter') fetchRepos() });
    }
    
    const autoRefresh = $('autoRefresh');
    if (autoRefresh) {
        autoRefresh.addEventListener('change', e => {
            if (e.target.checked) {
                fetchRepos();
                autoTimer = setInterval(fetchRepos, 60000);
            } else {
                clearInterval(autoTimer);
                autoTimer = null;
            }
        });
    }

    // Set up companion sidebar tabs
    document.querySelectorAll('.companion-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            switchCompanionTab(tabId);
        });
    });

    // Close modals on outside click
    window.addEventListener('click', e => {
        const tweetsModal = $('tweetsModal');
        if (e.target === tweetsModal) closeModal();
        
        const apiKeyModal = $('apiKeyModal');
        if (e.target === apiKeyModal) closeApiKeyModal();
        
        const compareModal = $('compareModal');
        if (e.target === compareModal) closeCompareModal();
    });

    // Initialize state
    applyLanguage();
    fetchRepos();
    fetchTwitterTrends();
});

// Translation Management
function changeLang(lang) {
    currentLang = lang;
    localStorage.setItem("lang", lang);
    applyLanguage();
    fetchTwitterTrends();
}

function applyLanguage() {
    const lang = currentLang;
    const t = T[lang];
    
    $('titleText').textContent = t.title;
    $('subtitleText').textContent = t.subtitle;
    $('searchInput').placeholder = t.searchPlaceholder;
    
    // Update duration options
    const durSelect = $('durationSelect');
    if (durSelect) {
        durSelect.options[0].text = t.duration.day;
        durSelect.options[1].text = t.duration.week;
        durSelect.options[2].text = t.duration.month;
        durSelect.options[3].text = t.duration.year;
    }
    
    // Update language select first option
    const langSelect = $('languageSelect');
    if (langSelect) langSelect.options[0].text = t.allLanguages;
    
    // Update sort options
    const sortSelect = $('sortSelect');
    if (sortSelect) {
        sortSelect.options[0].text = t.sort.stars;
        sortSelect.options[1].text = t.sort.forks;
        sortSelect.options[2].text = t.sort.updated;
        sortSelect.options[3].text = t.sort.hotness;
    }
    
    // Update source options
    const srcSelect = $('sourceSelect');
    if (srcSelect) {
        srcSelect.options[0].text = t.source.api;
        srcSelect.options[1].text = t.source.trending;
    }
    
    // Update limit options
    const limitSelect = $('limitSelect');
    if (limitSelect) {
        for (let i = 0; i < limitSelect.options.length; i++) {
            const val = limitSelect.options[i].value;
            limitSelect.options[i].text = t.limitOptions[val] || (val + " Repos");
        }
    }
    
    // Update min stars options
    const minStarsSelect = $('minStarsSelect');
    if (minStarsSelect) {
        for (let i = 0; i < minStarsSelect.options.length; i++) {
            const val = minStarsSelect.options[i].value;
            minStarsSelect.options[i].text = t.minStarsOptions[val] || val;
        }
    }
    
    // Update other labels
    $('minStarsLabelText').textContent = t.minStars;
    $('btnRefresh').textContent = t.refresh;
    $('repositoriesFoundText').textContent = t.found;
    $('autoRefreshLabelText').textContent = t.autoRefresh;
    $('footerText').innerHTML = t.footer;
    
    // Translate sidebar titles if available
    if (t.sidebarTitles) {
        if ($('searchTitle')) $('searchTitle').textContent = t.sidebarTitles.search;
        if ($('presetsTitle')) $('presetsTitle').textContent = t.sidebarTitles.presets;
        if ($('durationTitle')) $('durationTitle').textContent = t.sidebarTitles.duration;
        if ($('languageTitle')) $('languageTitle').textContent = t.sidebarTitles.language;
        if ($('sortTitle')) $('sortTitle').textContent = t.sidebarTitles.sort;
        if ($('sourceTitle')) $('sourceTitle').textContent = t.sidebarTitles.source;
        if ($('limitTitle')) $('limitTitle').textContent = t.sidebarTitles.limit;
        if ($('minStarsTitle')) $('minStarsTitle').textContent = t.sidebarTitles.minStars;
    }
    
    // Sidebar elements
    $('sidebarTrendsTitle').innerHTML = `<span>🔥</span> ${t.sidebarTrendsTitle}`;
    $('sidebarAiTipText').textContent = t.sidebarAiTipText;
    
    // Modal static elements
    $('modalTitleText').textContent = t.tweetsTitle;
    $('modalTwitterLink').textContent = t.openTwitter;
    $('modalAltSearchText').textContent = t.modalAltSearch;
    
    // Tab translations
    if ($('tabBtnSummary')) $('tabBtnSummary').textContent = currentLang === 'ru' ? 'ℹ️ Обзор' : 'ℹ️ Summary';
    if ($('tabBtnDiscussions')) $('tabBtnDiscussions').textContent = currentLang === 'ru' ? '💬 Обсуждения' : '💬 Discussions';
    if ($('tabBtnSecurity')) $('tabBtnSecurity').textContent = currentLang === 'ru' ? '🛡️ Аудит ИИ' : '🛡️ Security Audit';
    if ($('tabBtnGrowth')) $('tabBtnGrowth').textContent = currentLang === 'ru' ? '📈 Рост' : '📈 Growth';

    // Archive translations
    if ($('btnHistory')) $('btnHistory').textContent = currentLang === 'ru' ? '📜 Архив' : '📜 Archive';
    if ($('historyTitleText')) $('historyTitleText').textContent = currentLang === 'ru' ? '📜 Архив трендов (SQLite)' : '📜 Historical Snapshots (SQLite)';
    
    // Analytics translations
    $('btnAnalytics').textContent = t.analytics;
    $('chartLangTitle').textContent = t.chartLang;
    $('chartStarsTitle').textContent = t.chartStars;
    $('statTotalReposLabel').textContent = t.statRepos;
    $('statAvgStarsLabel').textContent = t.statAvgStars;
    $('statTopLangLabel').textContent = t.statTopLang;
    
    // API Key settings translations
    $('apiKeyModalTitleText').textContent = t.apiKeyTitle;
    $('apiKeyModalDescText').textContent = t.apiKeyDesc;
    $('apiKeyInput').placeholder = t.apiKeyPlaceholder;
    $('apiKeySaveBtnText').textContent = t.apiKeySave;
    $('apiKeyCancelBtnText').textContent = t.apiKeyCancel;
    
    // AI panel translations
    $('aiAgentTitleText').textContent = t.aiBubbleTitle;
    $('aiAgentStatusText').textContent = t.aiOnlineStatus;
    $('aiChatInput').placeholder = t.aiPlaceholder;
    $('aiChatSendBtn').textContent = t.aiSend;
    $('aiContextClearBtn').textContent = t.aiClearContext;
    
    // Advanced filters panel
    $('advTopicLabel').textContent = t.advTopic;
    $('advAuthorLabel').textContent = t.advAuthor;
    $('advMinForksLabel').textContent = t.advMinForks;
    if ($('advMaxStarsLabel')) $('advMaxStarsLabel').textContent = t.advMaxStars;
    if ($('advExcludeOrgLabel')) $('advExcludeOrgLabel').textContent = t.advExcludeOrg;
    if ($('deepSearchLabel')) $('deepSearchLabel').textContent = t.deepSearchLabel;
    $('btnAdvancedToggle').innerHTML = `⚙️ ${t.advToggle}`;

    // Presets
    const presetsSelect = $('queryPresetsSelect');
    if (presetsSelect && presetsSelect.options.length >= 6) {
        presetsSelect.options[0].textContent = t.presetDefault;
        presetsSelect.options[1].textContent = t.presetSecurity;
        presetsSelect.options[2].textContent = t.presetBypasses;
        presetsSelect.options[3].textContent = t.presetHidden;
        presetsSelect.options[4].textContent = t.presetNetwork;
        presetsSelect.options[5].textContent = t.presetObscureAuthors;
    }
    
    // AI companion tab headers translation
    const companionTabBtns = document.querySelectorAll('.companion-tab-btn');
    if (companionTabBtns.length >= 2) {
        companionTabBtns[0].textContent = t.companionChatTab || "Assistant";
        companionTabBtns[1].textContent = t.companionTrendsTab || "Community Trends";
    }
    
    // AI chips
    $('chipSuggestText').textContent = t.chipSuggest;
    $('chipExplainText').textContent = t.chipExplain;
    $('chipDigestText').textContent = t.chipDigest;
    $('chipHelpText').textContent = t.chipHelp;

    // Topics cloud
    const topicsCloudTitle = $('topicsCloudTitle');
    if (topicsCloudTitle) topicsCloudTitle.textContent = t.popularTopics;
    
    // Toggle active state on switcher buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });

    // Update preset items in left sidebar if they exist
    document.querySelectorAll('.preset-item').forEach(item => {
        const presetVal = item.dataset.preset;
        if (presetVal === 'all') item.innerHTML = `<span>🔍</span> ${t.presetDefault}`;
        else if (presetVal === 'security') item.innerHTML = `<span>🛡️</span> ${t.presetSecurity}`;
        else if (presetVal === 'bypasses') item.innerHTML = `<span>🔓</span> ${t.presetBypasses}`;
        else if (presetVal === 'hidden') item.innerHTML = `<span>👁️</span> ${t.presetHidden}`;
        else if (presetVal === 'network') item.innerHTML = `<span>🌐</span> ${t.presetNetwork}`;
        else if (presetVal === 'obscure_authors') item.innerHTML = `<span>👤</span> ${t.presetObscureAuthors}`;
    });
    
    // Update twitter proxy select
    const proxySelect = $('twitterProxySelect');
    if (proxySelect) {
        proxySelect.value = localStorage.getItem("twitter_proxy") || "direct";
        for (let i = 0; i < proxySelect.options.length; i++) {
            const val = proxySelect.options[i].value;
            proxySelect.options[i].text = t.twitterProxyOptions[val] || val;
        }
    }
    updateTwitterButtonLabel();

    // Re-render
    if (lastFetchedRepos) {
        renderRepos(lastFetchedRepos, lastFetchedSource);
    }
    updateAiContextUI();
}

// Twitter Proxy URL Builder
function getTwitterUrl(target, isSearch = false) {
    const proxy = localStorage.getItem("twitter_proxy") || "direct";
    if (isSearch) {
        const query = encodeURIComponent(target);
        return proxy === "direct" ? `https://x.com/search?q=${query}` : `${proxy}/search?q=${query}`;
    }
    
    if (!target) return '#';
    if (proxy === "direct") {
        let clean = target;
        const nitterMatch = clean.match(/https?:\/\/([^\/]+)/);
        if (nitterMatch && nitterMatch[1] !== 'x.com' && nitterMatch[1] !== 'twitter.com') {
            clean = clean.replace(/https?:\/\/[^\/]+/, 'https://x.com');
        }
        return clean;
    } else {
        return target.replace(/https?:\/\/[^\/]+/, proxy);
    }
}

function changeTwitterProxy() {
    const val = $('twitterProxySelect').value;
    localStorage.setItem("twitter_proxy", val);
    
    const modal = $('tweetsModal');
    if (modal && modal.classList.contains('open')) {
        const repoName = $('modalSubtitle').textContent;
        $('modalTwitterLink').href = getTwitterUrl(repoName, true);
        openTweets(repoName);
    }
    
    updateTwitterButtonLabel();
    fetchTwitterTrends();
}

function updateTwitterButtonLabel() {
    const proxy = localStorage.getItem("twitter_proxy") || "direct";
    const btn = $('modalTwitterLink');
    if (!btn) return;
    
    if (proxy === "direct") {
        btn.textContent = currentLang === 'ru' ? "Открыть в X/Twitter" : "Open in X/Twitter";
    } else {
        const domain = proxy.replace('https://', '');
        btn.textContent = currentLang === 'ru' ? `Открыть в ${domain}` : `Open in ${domain}`;
    }
}

// Sidebar Dropdown Inputs change triggers
function onMinStarsChange() {
    const select = $('minStarsSelect');
    const customInput = $('minStarsCustomInput');
    if (select && select.value === 'custom') {
        customInput.style.display = 'inline-block';
        customInput.focus();
    } else {
        if (customInput) customInput.style.display = 'none';
        fetchRepos();
    }
}

// Collapsible Panel Toggles
function toggleAnalytics() {
    const panel = $('analyticsPanel');
    const btn = $('btnAnalytics');
    analyticsVisible = !analyticsVisible;
    if (analyticsVisible) {
        panel.style.display = 'flex';
        btn.classList.add('active');
        updateCharts();
        
        // Hide archive if visible to save space
        if (historyVisible) toggleHistoryPanel();
    } else {
        panel.style.display = 'none';
        btn.classList.remove('active');
    }
}

function toggleHistoryPanel() {
    const panel = $('historyPanel');
    const btn = $('btnHistory');
    if (!panel) return;
    
    historyVisible = !historyVisible;
    if (historyVisible) {
        panel.style.display = 'block';
        btn.classList.add('active');
        fetchHistory();
        
        // Hide analytics if visible
        if (analyticsVisible) toggleAnalytics();
    } else {
        panel.style.display = 'none';
        btn.classList.remove('active');
    }
}

function toggleAdvancedFilters() {
    const panel = $('advancedFiltersPanel');
    const btn = $('btnAdvancedToggle');
    const isHidden = panel.style.display === 'none';
    panel.style.display = isHidden ? 'flex' : 'none';
    btn.classList.toggle('active', isHidden);
}

// Chart.js Visualizations
function updateCharts() {
    if (!analyticsVisible || !lastFetchedRepos || lastFetchedRepos.length === 0) return;

    const repos = lastFetchedRepos;
    const t = T[currentLang];

    // Stats calculations
    const totalRepos = repos.length;
    const avgStars = Math.round(repos.reduce((sum, r) => sum + (r.stargazers_count || 0), 0) / totalRepos);
    
    const langCounts = {};
    repos.forEach(r => {
        const l = r.language || (currentLang === 'ru' ? 'Неизвестный' : 'Unknown');
        langCounts[l] = (langCounts[l] || 0) + 1;
    });
    
    let topLang = t.noData;
    let maxCount = 0;
    Object.entries(langCounts).forEach(([l, count]) => {
        if (count > maxCount) {
            maxCount = count;
            topLang = l;
        }
    });

    $('statTotalRepos').textContent = totalRepos;
    $('statAvgStars').textContent = avgStars.toLocaleString();
    $('statTopLang').textContent = topLang;

    // Charts styling defaults
    Chart.defaults.color = '#a1a1aa';
    Chart.defaults.borderColor = '#27272a';

    // Doughnut chart (Languages)
    const langLabels = Object.keys(langCounts);
    const langData = Object.values(langCounts);
    const langColors = langLabels.map(l => LANG_COLORS[l] || '#71717a');

    if (langChartInstance) langChartInstance.destroy();
    
    const ctxLang = $('languagesChart').getContext('2d');
    langChartInstance = new Chart(ctxLang, {
        type: 'doughnut',
        data: {
            labels: langLabels,
            datasets: [{
                data: langData,
                backgroundColor: langColors,
                borderWidth: 1,
                borderColor: '#18181b'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 8,
                        usePointStyle: true,
                        font: { family: 'Inter', size: 9 }
                    }
                }
            }
        }
    });

    // Bar chart (Top Stars)
    const topRepos = [...repos].sort((a, b) => (b.stargazers_count || 0) - (a.stargazers_count || 0)).slice(0, 5);
    const repoLabels = topRepos.map(r => {
        const name = r.full_name || 'unknown';
        return name.split('/')[1] || name;
    });
    const repoStars = topRepos.map(r => r.stargazers_count || 0);

    if (starsChartInstance) starsChartInstance.destroy();

    const ctxStars = $('starsChart').getContext('2d');
    starsChartInstance = new Chart(ctxStars, {
        type: 'bar',
        data: {
            labels: repoLabels,
            datasets: [{
                label: currentLang === 'ru' ? 'Звезды' : 'Stars',
                data: repoStars,
                backgroundColor: 'rgba(99, 102, 241, 0.8)',
                hoverBackgroundColor: 'rgba(99, 102, 241, 1)',
                borderRadius: 4,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#27272a' },
                    ticks: {
                        callback: value => value >= 1000 ? (value / 1000) + 'k' : value,
                        font: { family: 'Inter', size: 9 }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { family: 'Inter', size: 9 } }
                }
            }
        }
    });
}

// Data Fetching and Presets
async function fetchRepos() {
    const c = $('content');
    const t = T[currentLang];
    c.innerHTML = `<div class="loading"><div class="spinner"></div><p style="color:var(--text-dim)">${t.loading}</p></div>`;
    
    const limitVal = $('limitSelect') ? $('limitSelect').value : '25';
    const p = new URLSearchParams({
        duration: $('durationSelect').value,
        limit: limitVal,
        sort: $('sortSelect').value,
        source: $('sourceSelect').value,
    });
    
    const lang = $('languageSelect').value;
    if (lang) p.set('language', lang);
    
    const q = $('searchInput').value.trim();
    if (q) p.set('query', q);
    
    const deepSearch = $('deepSearchCheckbox') ? $('deepSearchCheckbox').checked : false;
    if (deepSearch) p.set('deep_search', 'true');
    
    let ms = 0;
    const selectVal = $('minStarsSelect') ? $('minStarsSelect').value : '0';
    if (selectVal === 'custom') {
        ms = parseInt($('minStarsCustomInput').value) || 0;
    } else {
        ms = parseInt(selectVal) || 0;
    }
    if (ms > 0) p.set('min_stars', ms);

    const topicVal = $('advTopicInput') ? $('advTopicInput').value.trim() : '';
    if (topicVal) p.set('topic', topicVal);

    const authorVal = $('advAuthorInput') ? $('advAuthorInput').value.trim() : '';
    if (authorVal) p.set('author', authorVal);
    
    const forksVal = $('advMinForksInput') ? $('advMinForksInput').value.trim() : '';
    if (forksVal) p.set('min_forks', forksVal);

    const maxStarsVal = $('advMaxStarsInput') ? $('advMaxStarsInput').value.trim() : '';
    if (maxStarsVal) p.set('max_stars', maxStarsVal);

    const excludeOrg = $('advExcludeOrgCheckbox') ? $('advExcludeOrgCheckbox').checked : false;
    if (excludeOrg) p.set('exclude_org', 'true');

    // Preset configurations
    const preset = $('queryPresetsSelect').value;
    if (preset === 'security') {
        p.set('topic', 'security');
        if (!p.has('query')) p.set('query', '"exploit poc" OR "redteam tool" OR "vulnerability scanner" OR cve-202 OR rce-poc');
    } else if (preset === 'bypasses') {
        if (!p.has('query')) p.set('query', '"av bypass" OR "edr bypass" OR "waf evasion" OR "sandbox escape" OR unhooking OR lpe-poc');
        // Target obscure/hidden bypasses by limiting star count range
        p.set('min_stars', 5);
        if (!maxStarsVal) p.set('max_stars', 800);
    } else if (preset === 'hidden') {
        p.set('min_stars', 2);
        if (!maxStarsVal) p.set('max_stars', 350);
        p.set('exclude_org', 'true');
        if (!p.has('query')) p.set('query', 'experimental OR undocumented OR "zero-day" OR shellcode OR payload');
    } else if (preset === 'network') {
        if (!p.has('query')) p.set('query', 'tunneling OR reverse-proxy OR dns-over-https OR proxy-evasion');
    } else if (preset === 'obscure_authors') {
        p.set('min_stars', 2);
        if (!maxStarsVal) p.set('max_stars', 400);
        p.set('exclude_org', 'true');
        if (!p.has('query')) p.set('query', '"exploit" OR "bypass" OR "evasion"');
    }

    try {
        const r = await fetch('/api/trending?' + p);
        if (!r.ok) {
            try {
                const d = await r.json();
                showError(d.error || `HTTP ${r.status}: ${r.statusText}`);
            } catch (jsonErr) {
                const text = await r.text();
                showError(`HTTP ${r.status}: ${text.substring(0, 150)}`);
            }
            return;
        }
        const d = await r.json();
        if (d.error) {
            showError(d.error);
            return;
        }
        lastFetchedRepos = d.repos;
        lastFetchedSource = d.source;
        renderRepos(d.repos, d.source);
        fetchTwitterTrends();
    } catch (e) {
        console.error("fetchRepos error:", e);
        showError((currentLang === 'ru' ? 'Не удалось подключиться. Сервер запущен?' : 'Failed to connect. Is the server running?') + '<br><small style="color:var(--text-dim); font-size:0.75rem;">' + esc(e.toString()) + '</small>');
    }
}

function renderRepos(repos, source) {
    const c = $('content');
    const t = T[currentLang];
    
    updateTagsCloud(repos);
    
    let displayList = repos;
    if (activeTagFilter) {
        displayList = repos.filter(r => {
            const matchesLang = r.language && r.language.toLowerCase() === activeTagFilter;
            const matchesTopic = r.topics && r.topics.map(x => x.toLowerCase()).includes(activeTagFilter);
            return matchesLang || matchesTopic;
        });
    }
    
    $('resultCount').textContent = displayList.length;
    
    let sourceText = '';
    if (source === 'trending') {
        sourceText = currentLang === 'ru' ? '(Страница трендов)' : '(Trending page)';
    } else {
        sourceText = currentLang === 'ru' ? '(Поиск API)' : '(Search API)';
    }
    if (activeTagFilter) {
        sourceText += ` [Tag: #${activeTagFilter}]`;
    }
    $('sourceLabel').textContent = sourceText;

    if (!displayList.length) {
        c.innerHTML = `<div class="error-box"><h3>${t.noRepos}</h3><p>${t.tryFilters}</p></div>`;
        if (analyticsVisible) updateCharts();
        return;
    }
    c.innerHTML = '<div class="grid">' + displayList.map((r, i) => card(r, i, source)).join('') + '</div>';
    
    if (analyticsVisible) updateCharts();
}

function updateTagsCloud(repos) {
    const container = $('tagsCloud');
    const list = $('tagsCloudList');
    if (!container || !list) return;
    
    const counts = {};
    repos.forEach(r => {
        if (r.language) {
            const l = r.language.toLowerCase();
            counts[l] = (counts[l] || 0) + 1;
        }
        if (r.topics && Array.isArray(r.topics)) {
            r.topics.forEach(topic => {
                const t = topic.toLowerCase();
                counts[t] = (counts[t] || 0) + 1;
            });
        }
    });
    
    const sortedTags = Object.entries(counts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15);
        
    if (sortedTags.length === 0) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'flex';
    list.innerHTML = sortedTags.map(([tag, count]) => {
        const isActive = activeTagFilter === tag;
        const activeClass = isActive ? 'active' : '';
        return `<span class="tag-chip ${activeClass}" onclick="toggleTagFilter('${esc(tag)}')">${esc(tag)} <span style="opacity: 0.6; font-size: 0.65rem;">(${count})</span></span>`;
    }).join('');
}

function toggleTagFilter(tag) {
    activeTagFilter = activeTagFilter === tag ? null : tag;
    if (lastFetchedRepos) {
        renderRepos(lastFetchedRepos, lastFetchedSource);
    }
}

function showError(m) {
    const t = T[currentLang];
    $('content').innerHTML = `<div class="error-box"><h3>❌ ${t.error}</h3><p>${m}</p><button class="btn btn-sm" style="margin-top:12px;" onclick="fetchRepos()">${t.tryAgain}</button></div>`;
    $('resultCount').textContent = '0';
}

// Card HTML Builder
function card(r, i, source) {
    const n = r.full_name || 'unknown';
    const u = r.html_url || 'https://github.com/' + n;
    const d = r.description || T[currentLang].noDesc;
    const s = (r.stargazers_count || 0).toLocaleString();
    const f = (r.forks_count || 0).toLocaleString();
    const l = r.language || '';
    const lc = LANG_COLORS[l] || '#71717a';
    const sp = r.stars_period || 0;
    
    let badge = '';
    if (sp > 0) {
        const dur = $('durationSelect').value;
        const localizedLabel = T[currentLang].starsLabel[dur] || 'stars';
        badge = `<span class="badge-hot">🔥 ${sp.toLocaleString()} ${localizedLabel}</span>`;
    }
    
    let freshBadge = '';
    const updatedAtStr = r.updated_at || r.pushed_at;
    if (updatedAtStr) {
        try {
            const diffMs = new Date() - new Date(updatedAtStr);
            const diffHours = diffMs / (1000 * 60 * 60);
            if (diffHours <= 24) {
                freshBadge = `<span class="badge-fresh">⚡ Active</span>`;
            }
        } catch (e) {}
    } else if (source === 'trending' || sp > 0) {
        freshBadge = `<span class="badge-fresh">⚡ Active</span>`;
    }

    let badgesHtml = '';
    if (badge || freshBadge) {
        badgesHtml = `<div class="badge-row">${badge} ${freshBadge}</div>`;
    }
    
    const bb = r.built_by || [];
    const builtByAvatars = bb.length > 0 ?
        `<div class="built-by">
            ${bb.map(user => `<img class="avatar" src="https://github.com/${user}.png?size=40" title="${esc(user)}" alt="${esc(user)}">`).join('')}
         </div>` : '';

    const isChecked = selectedCompareRepos.find(x => x.full_name === n) ? 'checked' : '';
    const compareCheckbox = `
        <div class="compare-checkbox-wrapper" onclick="event.stopPropagation();">
            <input type="checkbox" id="compare_chk_${i}" class="compare-checkbox" ${isChecked} onchange="onCompareCheckChange(this, ${i})">
            <span>Compare</span>
        </div>
    `;

    return `<div class="card" style="animation-delay:${i * 0.03}s;">
        ${compareCheckbox}
        <div class="card-header" style="padding-right: 70px;">
            <a class="card-name" href="${u}" target="_blank">${esc(n)}</a>
            ${badgesHtml}
        </div>
        <p class="card-desc">${esc(d)}</p>
        <div class="card-footer-row">
            ${builtByAvatars}
            <button class="btn-tweets" onclick="openRepoDetailsHub(event, ${i})">📊 Info & AI</button>
        </div>
        <div class="card-meta" style="margin-top: 14px;">
            <span class="meta-item meta-stars">
                <svg width="12" height="12" fill="currentColor" viewBox="0 0 16 16"><path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/></svg>
                ${s}
            </span>
            <span class="meta-item meta-forks">
                <svg width="12" height="12" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M5 3.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm0 2.122a2.25 2.25 0 10-1.5 0v2.506a2.25 2.25 0 001.072 1.907l2.062 1.238a.75.75 0 10.772-1.285l-2.062-1.238a.75.75 0 01-.344-.636V5.372zM11.25 5a.75.75 0 100-1.5.75.75 0 000 1.5zM8.5 10.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm2.25-4.878v2.506a2.25 2.25 0 01-1.072 1.907l-2.062 1.238a.75.75 0 11-.772-1.285l2.062-1.238a.75.75 0 00.344-.636V5.372a2.25 2.25 0 111.5 0z"></path></svg>
                ${f}
            </span>
            ${l ? `<span class="meta-item meta-lang"><span class="lang-dot" style="background:${lc}"></span> ${l}</span>` : ''}
        </div>
    </div>`;
}

// Open Discussions and Sentiment
async function openTweets(repoName) {
    const container = $('modalDiscussionsContainer');
    if (!container) return;
    container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    
    try {
        const r = await fetch(`/api/tweets?q=${encodeURIComponent(repoName)}`);
        const d = await r.json();
        
        const isMocked = d.tweets && d.tweets.length > 0 && d.tweets[0].is_mock === "true";
        if (isMocked) {
            container.innerHTML = `
                <div style="text-align:center; padding:12px; color:var(--text-dim); font-size:0.8rem; border:1px dashed var(--border); border-radius:8px; margin-bottom:12px; background:rgba(255,255,255,0.01);">
                    ⚠️ ${currentLang === 'ru' ? 'Связь с Twitter/X недоступна. Запускаю ИИ-анализ мнений сообщества разработчиков...' : 'Twitter/X API down. Launching AI community opinion analysis...'}
                </div>
                <div class="loading"><div class="spinner"></div></div>
            `;
            setTimeout(() => { analyzeSentimentForRepo() }, 600);
        } else if (d.tweets && d.tweets.length > 0) {
            container.innerHTML = d.tweets.map(t => {
                const badge = t.is_mock === "true" ? `<span class="tweet-badge-mock" style="background:rgba(99,102,241,0.1); color:var(--accent); border:1px solid rgba(99,102,241,0.2); font-size:0.65rem; padding:1px 6px; border-radius:4px;">${T[currentLang].simulated}</span>` : '';
                return `<div class="tweet-card">
                    <div class="tweet-header">
                        <a class="tweet-author" href="${getTwitterUrl(t.url)}" target="_blank">${esc(t.author)}</a>
                        <div style="display:flex; gap: 8px; align-items:center;">
                            ${badge}
                            <span class="tweet-date">${esc(t.date)}</span>
                        </div>
                    </div>
                    <p class="tweet-text">${esc(t.text)}</p>
                </div>`;
            }).join('');
        } else {
            container.innerHTML = `<p style="text-align:center;color:var(--text-dim);padding:20px;">${T[currentLang].noTweets}</p>`;
        }
    } catch (e) {
        container.innerHTML = `<p style="text-align:center;color:var(--red);padding:20px;">${T[currentLang].errorTweets}</p>`;
    }
}

async function analyzeSentimentForRepo() {
    const repoName = currentOpenRepoName;
    const container = $('modalDiscussionsContainer');
    const t = T[currentLang];
    
    container.innerHTML = `<div class="loading"><div class="spinner" style="margin-bottom:8px;"></div><p style="color:var(--text-dim);font-size:0.8rem;">${t.modalAiOpinionLoading}</p></div>`;
    
    const repoObj = currentDetailsRepoObj;
    const desc = repoObj ? repoObj.description : "";
    const lang = repoObj ? repoObj.language : "";
    
    const query = currentLang === 'ru'
        ? `Каковы отзывы разработчиков, общее мнение (sentiment) и обсуждения вокруг репозитория '${repoName}' на GitHub, Reddit и в соцсетях? Что людям нравится, а что критикуют? Сделай структурированный и краткий разбор мнений сообщества на русском языке.`
        : `What are the developer reviews, general sentiment, and discussions around the repository '${repoName}' on GitHub, Reddit, and social media? What do people like, and what are the criticisms? Provide a structured, concise analysis of community opinions in English.`;
        
    const key = localStorage.getItem("gemini_api_key") || "";
    const payload = {
        name: repoName,
        description: desc,
        language: lang,
        query: query
    };
    
    try {
        const headers = { 'Content-Type': 'application/json' };
        if (key) headers['X-Gemini-Key'] = key;
        
        const r = await fetch('/api/ai/summarize', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(payload)
        });
        
        const d = await r.json();
        
        if (d.error) {
            container.innerHTML = `<p style="text-align:center;color:var(--red);padding:20px;">❌ Error: ${esc(d.error)}</p>`;
            if (d.error.includes("Missing GEMINI_API_KEY")) openApiKeyModal();
        } else if (d.summary) {
            container.innerHTML = `
                <div style="background: rgba(99, 102, 241, 0.03); border: 1px solid rgba(99, 102, 241, 0.15); border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <h4 style="font-size: 0.88rem; font-weight: 700; margin-bottom: 12px; color: var(--accent); display:flex; align-items:center; gap:6px;">
                        <span>📊</span> ${t.modalAiOpinionHeader}
                    </h4>
                    <div style="font-size:0.85rem; line-height:1.6; color:var(--text); word-break:break-word;">
                        ${renderMarkdown(d.summary)}
                    </div>
                </div>
            `;
        }
    } catch (e) {
        container.innerHTML = `<p style="text-align:center;color:var(--red);padding:20px;">❌ Failed: ${e.message}</p>`;
    }
}

// Modal Controllers
function closeModal() {
    $('tweetsModal').classList.remove('open');
}

// Side Panel / AI Chat Controller
function toggleAiChat() {
    const pane = $('aiChatPane');
    if (!pane) return;
    
    pane.classList.toggle('closed');
    const isClosed = pane.classList.contains('closed');
    
    // Switch companion panel state
    if (!isClosed) {
        if ($('aiChatMessages').children.length === 0) {
            resetAiChat();
        }
    }
}

function resetAiChat() {
    aiHistory = [];
    const t = T[currentLang];
    $('aiChatMessages').innerHTML = `
        <div style="background: rgba(99, 102, 241, 0.05); border: 1px solid rgba(99, 102, 241, 0.15); padding: 12px; border-radius: 8px; line-height: 1.4; color: var(--text); font-size:0.8rem;">
            ${t.aiHelpGreeting}
        </div>
    `;
    updateAiContextUI();
}

function switchCompanionTab(tabId) {
    document.querySelectorAll('.companion-tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabId);
    });
    $('companionChatContent').style.display = tabId === 'chat' ? 'flex' : 'none';
    $('companionTrendsContent').style.display = tabId === 'trends' ? 'block' : 'none';
}

function updateAiContextUI() {
    const clearBtn = $('aiContextClearBtn');
    const labelText = $('aiContextLabel');
    const t = T[currentLang];
    
    if (aiSelectedRepo) {
        labelText.textContent = t.aiRepoContext.replace('{name}', aiSelectedRepo.full_name || aiSelectedRepo.name);
        if (clearBtn) clearBtn.style.display = 'inline-block';
    } else {
        labelText.textContent = t.aiGlobalContext;
        if (clearBtn) clearBtn.style.display = 'none';
    }
}

function clearAiContext() {
    aiSelectedRepo = null;
    updateAiContextUI();
}

function openApiKeyModal() {
    $('apiKeyModal').classList.add('open');
    $('apiKeyInput').value = localStorage.getItem("gemini_api_key") || "";
}

function closeApiKeyModal() {
    $('apiKeyModal').classList.remove('open');
}

function saveApiKey() {
    const key = $('apiKeyInput').value.trim();
    localStorage.setItem("gemini_api_key", key);
    closeApiKeyModal();
    alert(T[currentLang].apiKeySavedAlert);
    if (key && aiHistory.length === 0) {
        resetAiChat();
    }
}

function triggerRepoAi(event, index) {
    if (event) event.stopPropagation();
    if (!lastFetchedRepos || !lastFetchedRepos[index]) return;
    
    aiSelectedRepo = lastFetchedRepos[index];
    const pane = $('aiChatPane');
    if (pane) pane.classList.remove('closed'); // Ensure it is open
    
    switchCompanionTab('chat');
    updateAiContextUI();
    
    // Auto-generate query to summarize
    const repoName = aiSelectedRepo.full_name || aiSelectedRepo.name;
    const initialQuery = currentLang === 'ru' 
        ? `Сделай краткий обзор репозитория ${repoName}`
        : `Provide a quick summary of repository ${repoName}`;
    
    appendAiMessage('user', initialQuery);
    executeAiQuery(initialQuery);
}

function appendAiMessage(role, text) {
    const container = $('aiChatMessages');
    const isUser = role === 'user';
    const messageClass = isUser ? 'user' : 'model';
    
    const div = document.createElement('div');
    div.className = `chat-msg ${messageClass}`;
    div.innerHTML = renderMarkdown(text);
    
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function renderMarkdown(text) {
    let html = esc(text);
    
    // Replace code blocks: ```code```
    html = html.replace(/```([\s\S]*?)```/g, '<pre style="background:rgba(0,0,0,0.3); padding:8px 12px; border-radius:6px; overflow-x:auto; font-family:monospace; font-size:0.78rem; margin:8px 0; border:1px solid var(--border); white-space:pre-wrap; color:var(--text)"><code>$1</code></pre>');
    
    // Replace inline code: `code`
    html = html.replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.06); padding:2px 4px; border-radius:4px; font-family:monospace; font-size:0.8rem; color:#f43f5e;">$1</code>');
    
    // Replace bold: **text**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Replace bullet points
    html = html.split('\n').map(line => {
        const trimmed = line.trim();
        if (trimmed.startsWith('* ') || trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
            return `<li style="margin-left: 12px; list-style-type: disc; font-size:0.82rem;">${trimmed.substring(2)}</li>`;
        }
        return line;
    }).join('\n');
    
    // Replace newlines with <br>
    html = html.replace(/\n/g, '<br>');
    return html;
}

async function sendAiChatMessage() {
    const input = $('aiChatInput');
    const query = input.value.trim();
    if (!query) return;
    
    input.value = '';
    appendAiMessage('user', query);
    aiHistory.push({ role: 'user', text: query });
    
    await executeAiQuery(query);
}

async function executeAiQuery(query) {
    const container = $('aiChatMessages');
    const t = T[currentLang];
    
    const typingDiv = document.createElement('div');
    typingDiv.id = 'aiTypingIndicator';
    typingDiv.className = 'chat-msg model';
    typingDiv.style.color = 'var(--text-muted)';
    typingDiv.style.display = 'flex';
    typingDiv.style.alignItems = 'center';
    typingDiv.style.gap = '8px';
    typingDiv.innerHTML = `<div class="spinner" style="width:12px; height:12px; border-width:2px; margin:0;"></div> <span>${t.aiLoading}</span>`;
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
    
    const key = localStorage.getItem("gemini_api_key") || "";
    
    const payload = {
        query: query,
        history: aiHistory.slice(0, -1)
    };
    
    if (aiSelectedRepo) {
        payload.name = aiSelectedRepo.full_name || aiSelectedRepo.name;
        payload.description = aiSelectedRepo.description;
        payload.language = aiSelectedRepo.language;
    } else if (lastFetchedRepos) {
        payload.repos = lastFetchedRepos;
    }
    
    try {
        const headers = { 'Content-Type': 'application/json' };
        if (key) headers['X-Gemini-Key'] = key;
        
        const r = await fetch('/api/ai/summarize', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(payload)
        });
        
        const d = await r.json();
        
        const indicator = $('aiTypingIndicator');
        if (indicator) indicator.remove();
        
        if (d.error) {
            appendAiMessage('model', `❌ Error: ${d.error}`);
            if (d.error.includes("Missing GEMINI_API_KEY")) openApiKeyModal();
        } else if (d.summary) {
            appendAiMessage('model', d.summary);
            aiHistory.push({ role: 'model', text: d.summary });
        }
    } catch (e) {
        const indicator = $('aiTypingIndicator');
        if (indicator) indicator.remove();
        appendAiMessage('model', `❌ Failed: ${e.message}`);
    }
}

// Sidebar Twitter Trends loader
async function fetchTwitterTrends() {
    const container = $('twitterTrendsList');
    if (!container) return;
    
    try {
        const r = await fetch('/api/trends');
        const d = await r.json();
        
        if (d.trends && d.trends.length > 0) {
            container.innerHTML = d.trends.map(tr => {
                const trendUrl = getTwitterUrl(tr.name, true);
                return `<a class="trend-item" href="${trendUrl}" target="_blank" onclick="searchByTrend(event, '${esc(tr.name)}')">
                    <span class="trend-name">${esc(tr.name)}</span>
                    <span class="trend-tweets">${esc(tr.tweet_count)}</span>
                </a>`;
            }).join('');
        } else {
            container.innerHTML = `<p style="text-align:center; color:var(--text-muted); font-size:0.75rem; padding:10px;">${currentLang === 'ru' ? 'Не удалось загрузить тренды' : 'No trends available'}</p>`;
        }
    } catch (e) {
        container.innerHTML = `<p style="text-align:center; color:var(--red); font-size:0.75rem; padding:10px;">${currentLang === 'ru' ? 'Ошибка загрузки трендов' : 'Error loading trends'}</p>`;
    }
}

function searchByTrend(event, trendName) {
    if (event) event.preventDefault();
    const searchInput = $('searchInput');
    if (searchInput) {
        const query = trendName.startsWith('#') ? trendName.substring(1) : trendName;
        searchInput.value = query;
        fetchRepos();
        
        // Open AI agent and ask it to explain the trend
        const pane = $('aiChatPane');
        if (pane) {
            pane.classList.remove('closed');
            switchCompanionTab('chat');
            const explainQuery = currentLang === 'ru'
                ? `Объясни, почему тема ${trendName} сейчас популярна среди разработчиков. Какие репозитории на этой странице к ней относятся и какую пользу они приносят?`
                : `Explain why the topic ${trendName} is currently trending among developers. Which repositories on this page relate to it and what benefits do they provide?`;
            
            appendAiMessage('user', explainQuery);
            executeAiQuery(explainQuery);
        }
    }
}

function sendQuickAiQuery(type) {
    let query = '';
    
    if (type === 'suggest') {
        query = currentLang === 'ru'
            ? "Проанализируй список репозиториев на этой странице и порекомендуй 3 самых интересных или быстрорастущих проекта. Объясни простыми словами, почему на них стоит обратить внимание."
            : "Analyze the list of repositories on this page and recommend 3 particularly interesting or fast-growing projects. Explain in simple terms why they are worth looking at.";
    } else if (type === 'explain') {
        query = currentLang === 'ru'
            ? "Какие главные технологические темы или паттерны объединяют трендовые репозитории на этой странице? Сделай краткий обзор текущих направлений развития."
            : "What are the main technological themes or patterns that unite the trending repositories on this page? Provide a brief summary of the current directions of development.";
    } else if (type === 'digest') {
        query = currentLang === 'ru'
            ? "Сгенерируй технологический дайджест дня по текущим трендовым репозиториям. Расскажи, какие темы сегодня в лидерах, выдели 2-3 ключевых проекта, опиши их архитектуру и практическую пользу для разработчика."
            : "Generate a daily tech digest based on the current trending repositories. Explain which topics are leading today, highlight 2-3 key projects, and describe their architecture and practical benefits for developers.";
    } else {
        query = currentLang === 'ru'
            ? "Расскажи, какими возможностями ты обладаешь как ИИ-помощник и как ты можешь помочь мне анализировать код и находить полезные проекты?"
            : "Tell me, what capabilities do you have as an AI assistant and how can you help me analyze code and find useful projects?";
    }
    
    const pane = $('aiChatPane');
    if (pane) pane.classList.remove('closed');
    switchCompanionTab('chat');
    
    appendAiMessage('user', query);
    aiHistory.push({ role: 'user', text: query });
    executeAiQuery(query);
}

function esc(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
}

// Search Preset Configurations
function applyPresetQuery(presetValue) {
    // If called from a custom button list, presetValue is passed, otherwise read from select dropdown
    const select = $('queryPresetsSelect');
    if (presetValue !== undefined) {
        select.value = presetValue;
    }
    const preset = select.value;
    
    const searchInput = $('searchInput');
    const maxStarsInput = $('advMaxStarsInput');
    const excludeOrgCheckbox = $('advExcludeOrgCheckbox');
    const deepSearchCheckbox = $('deepSearchCheckbox');
    
    // Sync UI elements style class for visual feedback
    document.querySelectorAll('.preset-item').forEach(item => {
        item.classList.toggle('active', item.dataset.preset === preset);
    });

    if (maxStarsInput) maxStarsInput.value = '';
    if (excludeOrgCheckbox) excludeOrgCheckbox.checked = false;
    if (deepSearchCheckbox) {
        if (preset === 'bypasses' || preset === 'hidden' || preset === 'obscure_authors') {
            deepSearchCheckbox.checked = true;
        } else {
            deepSearchCheckbox.checked = false;
        }
    }
    
    if (preset !== 'all') {
        const sourceSelect = $('sourceSelect');
        if (sourceSelect) sourceSelect.value = 'api';
    }

    if (preset === 'all') {
        searchInput.value = '';
    } else if (preset === 'security') {
        searchInput.value = '"exploit poc" OR "redteam tool" OR "vulnerability scanner" OR cve-202 OR rce-poc';
    } else if (preset === 'bypasses') {
        searchInput.value = '"av bypass" OR "edr bypass" OR "waf evasion" OR "sandbox escape" OR unhooking OR lpe-poc';
        if (maxStarsInput) maxStarsInput.value = '800';
    } else if (preset === 'hidden') {
        searchInput.value = 'experimental OR undocumented OR "zero-day" OR shellcode OR payload';
        if (maxStarsInput) maxStarsInput.value = '350';
        if (excludeOrgCheckbox) excludeOrgCheckbox.checked = true;
    } else if (preset === 'network') {
        searchInput.value = 'tunneling OR reverse-proxy OR dns-over-https OR proxy-evasion';
    } else if (preset === 'obscure_authors') {
        searchInput.value = '"exploit" OR "bypass" OR "evasion"';
        if (maxStarsInput) maxStarsInput.value = '400';
        if (excludeOrgCheckbox) excludeOrgCheckbox.checked = true;
    }
    
    fetchRepos();
}

// Side-by-Side Comparison
function onCompareCheckChange(chk, index) {
    if (!lastFetchedRepos || !lastFetchedRepos[index]) return;
    const repoObj = lastFetchedRepos[index];
    const fullName = repoObj.full_name || repoObj.name;
    
    if (chk.checked) {
        if (selectedCompareRepos.length >= 3) {
            alert(currentLang === 'ru' ? 'Максимум 3 репозитория для сравнения!' : 'Maximum of 3 repositories can be compared!');
            chk.checked = false;
            return;
        }
        if (!selectedCompareRepos.find(x => x.full_name === fullName)) {
            selectedCompareRepos.push(repoObj);
        }
    } else {
        selectedCompareRepos = selectedCompareRepos.filter(x => x.full_name !== fullName);
    }
    
    updateCompareBar();
}

function updateCompareBar() {
    const bar = $('compareBar');
    const barText = $('compareBarText');
    if (!bar || !barText) return;
    
    if (selectedCompareRepos.length > 0) {
        bar.style.display = 'flex';
        barText.textContent = currentLang === 'ru' 
            ? `Выбрано: ${selectedCompareRepos.length}` 
            : `Selected: ${selectedCompareRepos.length}`;
    } else {
        bar.style.display = 'none';
    }
}

function clearRepoCompare() {
    selectedCompareRepos = [];
    document.querySelectorAll('.compare-checkbox').forEach(chk => chk.checked = false);
    updateCompareBar();
}

async function runAiComparison() {
    if (selectedCompareRepos.length < 2) {
        alert(currentLang === 'ru' ? 'Выберите как минимум 2 репозитория для сравнения!' : 'Please select at least 2 repositories to compare!');
        return;
    }
    
    const modal = $('compareModal');
    const container = $('compareModalContent');
    if (!modal || !container) return;
    
    modal.classList.add('open');
    container.innerHTML = '<div class="loading"><div class="spinner"></div><p style="color: var(--text-muted); font-size:0.8rem; margin-top:8px;">Generating side-by-side AI comparison with Gemini...</p></div>';
    
    const api_key = localStorage.getItem("gemini_api_key") || "";
    const headers = { "Content-Type": "application/json" };
    if (api_key) headers["X-Gemini-Key"] = api_key;
    
    try {
        const r = await fetch('/api/ai/compare', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ repos: selectedCompareRepos })
        });
        const d = await r.json();
        
        if (d.error) {
            container.innerHTML = `<p style="color: var(--red); font-size: 0.88rem; text-align: center;">❌ ${d.error}</p>`;
            return;
        }
        
        container.innerHTML = renderMarkdown(d.comparison);
    } catch (e) {
        container.innerHTML = `<p style="color: var(--red); font-size: 0.85rem;">Error loading comparison: ${e}</p>`;
    }
}

function closeCompareModal() {
    $('compareModal').classList.remove('open');
}

// Hub Modal details
async function openRepoDetailsHub(event, index) {
    if (event) event.stopPropagation();
    if (!lastFetchedRepos || !lastFetchedRepos[index]) return;
    
    currentDetailsRepoObj = lastFetchedRepos[index];
    currentOpenRepoName = currentDetailsRepoObj.full_name || currentDetailsRepoObj.name;
    currentOpenRepoIndex = index;
    
    const modal = $('tweetsModal');
    if (!modal) return;
    
    modal.classList.add('open');
    
    const subtitle = $('modalSubtitle');
    if (subtitle) {
        subtitle.innerHTML = `<a href="${currentDetailsRepoObj.html_url || 'https://github.com/'+currentOpenRepoName}" target="_blank" style="color: var(--blue); text-decoration: none;">${esc(currentOpenRepoName)}</a>`;
    }
    
    // Clear security audit tab container to original state
    const secContainer = $('modalSecurityContainer');
    if (secContainer) {
        secContainer.innerHTML = `
            <p style="color: var(--text-dim); text-align: center; font-size: 0.82rem; max-width: 500px;" id="securityIntroText">${currentLang === 'ru' ? 'Запустите автоматический ИИ-аудит зависимостей проекта (package.json, Cargo.toml, requirements.txt, go.mod и др.) для оценки рисков и безопасности.' : 'Run an automated AI audit of the repository\'s dependency manifest (package.json, Cargo.toml, requirements.txt, go.mod, etc.) to evaluate dependency risk and security health.'}</p>
            <button class="btn btn-accent btn-sm" onclick="runSecurityAudit()" style="margin-top: 12px; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);" id="runSecurityAuditBtn">🔍 Run Security Audit</button>
        `;
    }

    // Switch to summary tab first
    switchModalTab('summary');
}

function switchModalTab(tabId) {
    currentModalTab = tabId;
    
    // Toggle active classes on tab buttons
    document.querySelectorAll('.modal-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeBtn = $('tabBtn' + tabId.charAt(0).toUpperCase() + tabId.slice(1));
    if (activeBtn) activeBtn.classList.add('active');

    // Toggle active tab content panels
    document.querySelectorAll('.tab-panel-content').forEach(panel => {
        panel.style.display = 'none';
    });
    
    const activePanel = $('tabContent' + tabId.charAt(0).toUpperCase() + tabId.slice(1));
    if (activePanel) activePanel.style.display = 'block';

    // Load content dynamically depending on the tab
    if (tabId === 'summary') {
        loadSummaryTab();
    } else if (tabId === 'discussions') {
        loadSocialDiscussions();
    } else if (tabId === 'growth') {
        loadGrowthChart();
    }
}

async function loadSummaryTab() {
    const summaryContent = $('modalSummaryAiContent');
    if (!summaryContent) return;
    
    summaryContent.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    
    const api_key = localStorage.getItem("gemini_api_key") || "";
    const headers = { "Content-Type": "application/json" };
    if (api_key) headers["X-Gemini-Key"] = api_key;
    
    try {
        const r = await fetch('/api/ai/summarize', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                name: currentDetailsRepoObj.full_name || currentDetailsRepoObj.name,
                description: currentDetailsRepoObj.description,
                language: currentDetailsRepoObj.language
            })
        });
        const d = await r.json();
        
        if (d.error) {
            summaryContent.innerHTML = `<p style="color: var(--red); font-size: 0.85rem;">${esc(d.error)}</p>`;
            return;
        }
        
        summaryContent.innerHTML = renderMarkdown(d.summary);
    } catch (e) {
        summaryContent.innerHTML = `<p style="color: var(--red); font-size: 0.85rem;">Error fetching summary: ${e}</p>`;
    }
}

async function loadSocialDiscussions() {
    const container = $('modalDiscussionsContainer');
    if (!container) return;
    
    container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    
    try {
        const repoName = currentOpenRepoName;
        const r = await fetch(`/api/social/discussions?repo=${encodeURIComponent(repoName)}`);
        const d = await r.json();
        
        let html = '';
        
        // Hacker News
        html += `<h4 style="margin: 5px 0; color: #ff6600; font-size: 0.88rem; border-bottom: 1px solid rgba(255,102,0,0.2); padding-bottom: 4px;">🧡 Hacker News</h4>`;
        if (d.hn && d.hn.length > 0) {
            html += d.hn.map(item => `
                <div style="padding: 10px 12px; background: rgba(255,102,0,0.03); border-left: 3px solid #ff6600; border-radius: 6px; margin-bottom: 8px; font-size: 0.8rem;">
                    <a href="${item.url}" target="_blank" style="color: var(--text); font-weight: 600; text-decoration: none; display: block; margin-bottom: 4px;">${esc(item.title)}</a>
                    <span style="color: var(--text-muted); font-size: 0.72rem;">⭐ ${item.score} pts • 💬 ${item.comments} comments • 📅 ${item.date}</span>
                </div>
            `).join('');
        } else {
            html += `<p style="font-size: 0.78rem; color: var(--text-muted); font-style: italic; margin-bottom: 12px; padding: 4px 0;">${currentLang === 'ru' ? 'Обсуждений на Hacker News не найдено.' : 'No Hacker News discussions found.'}</p>`;
        }
        
        // Reddit
        html += `<h4 style="margin: 15px 0 5px; color: #ff4500; font-size: 0.88rem; border-bottom: 1px solid rgba(255,69,0,0.2); padding-bottom: 4px;">🤖 Reddit</h4>`;
        if (d.reddit && d.reddit.length > 0) {
            html += d.reddit.map(item => `
                <div style="padding: 10px 12px; background: rgba(255,69,0,0.03); border-left: 3px solid #ff4500; border-radius: 6px; margin-bottom: 8px; font-size: 0.8rem;">
                    <a href="${item.url}" target="_blank" style="color: var(--text); font-weight: 600; text-decoration: none; display: block; margin-bottom: 4px;">${esc(item.title)}</a>
                    <span style="color: var(--text-muted); font-size: 0.72rem;">⬆️ ${item.score} upvotes • 💬 ${item.comments} comments • 📅 ${item.date}</span>
                </div>
            `).join('');
        } else {
            html += `<p style="font-size: 0.78rem; color: var(--text-muted); font-style: italic; margin-bottom: 12px; padding: 4px 0;">${currentLang === 'ru' ? 'Постов на Reddit не найдено.' : 'No Reddit posts found.'}</p>`;
        }
        
        // Twitter/X (Nitter)
        html += `<h4 style="margin: 15px 0 5px; color: var(--blue); font-size: 0.88rem; border-bottom: 1px solid rgba(96,165,250,0.2); padding-bottom: 4px;">💬 Twitter Mentions</h4>`;
        if (d.twitter && d.twitter.length > 0) {
            html += d.twitter.map(t => `
                <div style="padding: 10px 12px; background: rgba(96,165,250,0.02); border-left: 3px solid var(--blue); border-radius: 6px; margin-bottom: 8px; font-size: 0.8rem;">
                    <div style="display:flex; justify-content:space-between; margin-bottom: 4px;">
                        <a href="${t.url}" target="_blank" style="color: var(--blue); font-weight: 600; text-decoration: none;">${esc(t.author)}</a>
                        <span style="color: var(--text-muted); font-size: 0.7rem;">${esc(t.date)}</span>
                    </div>
                    <p style="margin: 0; color: var(--text); line-height: 1.4;">${esc(t.text)}</p>
                </div>
            `).join('');
        } else {
            html += `<p style="font-size: 0.78rem; color: var(--text-muted); font-style: italic; padding: 4px 0;">${currentLang === 'ru' ? 'Упоминаний в Twitter не найдено.' : 'No Twitter mentions found.'}</p>`;
        }
        
        container.innerHTML = html;
        
        // Update Alt links in the Discussions panel
        $('modalTwitterLink').href = getTwitterUrl(repoName, true);
        $('modalGithubSearchLink').href = `https://github.com/search?q=${encodeURIComponent(repoName)}&type=discussions`;
        $('modalBlueskySearchLink').href = `https://bsky.app/search?q=${encodeURIComponent(repoName)}`;
        $('modalGoogleSearchLink').href = `https://www.google.com/search?q=${encodeURIComponent(repoName + " github discussions reviews")}`;
    } catch (e) {
        container.innerHTML = `<p style="color: var(--red); font-size: 0.85rem;">Error loading discussions: ${e}</p>`;
    }
}

async function runSecurityAudit() {
    const container = $('modalSecurityContainer');
    if (!container) return;
    
    container.innerHTML = '<div class="loading"><div class="spinner"></div><p style="color: var(--text-muted); font-size:0.8rem; margin-top:8px;">Analyzing manifest file with Gemini AI...</p></div>';
    
    const api_key = localStorage.getItem("gemini_api_key") || "";
    const headers = { "Content-Type": "application/json" };
    if (api_key) headers["X-Gemini-Key"] = api_key;
    
    try {
        const repoName = currentOpenRepoName;
        const r = await fetch('/api/ai/security', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ name: repoName })
        });
        const d = await r.json();
        
        if (d.error) {
            container.innerHTML = `
                <div style="display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 20px;">
                    <p style="color: var(--red); font-size: 0.88rem; text-align: center;">❌ ${d.error}</p>
                    <button class="btn btn-sm" onclick="runSecurityAudit()" style="margin-top:0;">Try Again</button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px dashed var(--border); padding-bottom: 8px; margin-bottom: 12px; width:100%;">
                <span style="font-size: 0.78rem; color: var(--text-muted);">File audited: <code>${esc(d.file_found)}</code></span>
                <span style="font-size: 0.75rem; font-weight: 700; color: var(--green); background: rgba(16,185,129,0.08); padding: 2px 8px; border-radius: 4px;">AI Audited</span>
            </div>
            <div style="font-size: 0.85rem; line-height: 1.6; color: var(--text); width: 100%;">
                ${renderMarkdown(d.security_audit)}
            </div>
        `;
    } catch (e) {
        container.innerHTML = `<p style="color: var(--red); font-size: 0.85rem;">Error running audit: ${e}</p>`;
    }
}

async function loadGrowthChart() {
    const canvas = $('growthChart');
    if (!canvas) return;
    
    if (growthChartInstance) {
        growthChartInstance.destroy();
        growthChartInstance = null;
    }
    
    const repoName = currentOpenRepoName;
    try {
        const r = await fetch(`/api/history/trends?repo=${encodeURIComponent(repoName)}`);
        const d = await r.json();
        
        if (d.error || !d.trends || d.trends.length === 0) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#71717a';
            ctx.font = '13px Inter';
            ctx.textAlign = 'center';
            ctx.fillText(currentLang === 'ru' ? 'Нет исторических данных для этого репозитория.' : 'No historical tracking data available yet.', canvas.width / 2, canvas.height / 2);
            return;
        }
        
        const labels = d.trends.map(t => {
            const date = new Date(t.scraped_at);
            return date.toLocaleDateString(currentLang === 'ru' ? 'ru-RU' : 'en-US', {month: 'short', day: 'numeric', hour: '2-digit'});
        });
        const starsData = d.trends.map(t => t.stars);
        const hypeData = d.trends.map(t => t.hype_score);
        
        growthChartInstance = new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Stars',
                        data: starsData,
                        borderColor: '#fbbf24',
                        backgroundColor: 'rgba(251, 191, 36, 0.05)',
                        borderWidth: 1.5,
                        tension: 0.2,
                        yAxisID: 'yStars'
                    },
                    {
                        label: 'Hype Score',
                        data: hypeData,
                        borderColor: '#60a5fa',
                        backgroundColor: 'rgba(96, 165, 250, 0.05)',
                        borderWidth: 1.5,
                        tension: 0.2,
                        yAxisID: 'yHype'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#a1a1aa',
                            font: { family: 'Inter', size: 10 }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.03)' },
                        ticks: { color: '#71717a', font: { family: 'Inter', size: 9 } }
                    },
                    yStars: {
                        position: 'left',
                        grid: { color: 'rgba(255,255,255,0.03)' },
                        ticks: { color: '#fbbf24', font: { family: 'Inter', size: 9 } },
                        title: { display: true, text: 'Stars', color: '#fbbf24', font: { family: 'Inter', size: 9 } }
                    },
                    yHype: {
                        position: 'right',
                        grid: { drawOnChartArea: false },
                        ticks: { color: '#60a5fa', font: { family: 'Inter', size: 9 } },
                        title: { display: true, text: 'Hype Score', color: '#60a5fa', font: { family: 'Inter', size: 9 } }
                    }
                }
            }
        });
    } catch (e) {
        console.error("Failed to load growth chart", e);
    }
}

async function fetchHistory() {
    const container = $('historyTableContainer');
    if (!container) return;
    
    const searchVal = $('historySearchInput') ? $('historySearchInput').value.trim() : '';
    let url = '/api/history?limit=50';
    if (searchVal) url += `&search=${encodeURIComponent(searchVal)}`;
    
    try {
        const r = await fetch(url);
        const d = await r.json();
        
        if (d.error || !d.history || d.history.length === 0) {
            container.innerHTML = `<p style="color:var(--text-muted); text-align:center; padding: 20px;">${currentLang === 'ru' ? 'Архивная история пуста или ничего не найдено.' : 'Archive history is empty or no records match.'}</p>`;
            return;
        }
        
        let html = `
            <table class="history-table">
                <thead>
                    <tr>
                        <th>Repository</th>
                        <th>Language</th>
                        <th>Stars</th>
                        <th>Forks</th>
                        <th>Hype Score</th>
                        <th>Archived At</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        d.history.forEach(item => {
            const date = new Date(item.scraped_at).toLocaleString(currentLang === 'ru' ? 'ru-RU' : 'en-US');
            html += `
                <tr>
                    <td><a href="${item.html_url}" target="_blank">${esc(item.full_name)}</a></td>
                    <td>${esc(item.language || 'N/A')}</td>
                    <td>⭐ ${(item.stars || 0).toLocaleString()}</td>
                    <td>🍴 ${(item.forks || 0).toLocaleString()}</td>
                    <td>🔥 ${(item.hype_score || 0).toFixed(1)}</td>
                    <td style="color: var(--text-muted);">${date}</td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        container.innerHTML = html;
    } catch (e) {
        container.innerHTML = `<p style="color: var(--red); font-size:0.85rem; padding: 20px;">Error loading history: ${e}</p>`;
    }
}

// ============================================================
// SPRINT 1 FEATURES
// ============================================================

// --- 1. VELOCITY RADAR ---
function calculateVelocity(repo) {
    const starsPeriod = repo.stars_period || 0;
    const starsTotal = repo.stargazers_count || repo.stars || 1;
    const velocityPct = (starsPeriod / starsTotal) * 100;
    
    let trend = 'declining';
    let label = '';
    
    if (velocityPct > 1) {
        trend = 'rising';
        label = `🚀 ${velocityPct.toFixed(1)}%`;
    } else if (velocityPct > 0.1) {
        trend = 'stable';
        label = `📊 ${velocityPct.toFixed(1)}%`;
    } else if (starsPeriod > 0) {
        trend = 'stable';
        label = `📊 ${velocityPct.toFixed(2)}%`;
    } else {
        trend = 'declining';
        label = '—';
    }
    
    return { trend, label, velocityPct };
}

function renderVelocityBadge(repo) {
    const v = calculateVelocity(repo);
    if (v.trend === 'declining' && v.label === '—') return '';
    
    const trendLabel = currentLang === 'ru' 
        ? { rising: 'взлёт', stable: 'стабильно', declining: 'затухает' }
        : { rising: 'rising', stable: 'stable', declining: 'fading' };
    
    return `<span class="velocity-badge ${v.trend}" title="${trendLabel[v.trend]}">
        <span class="pulse-dot"></span>
        ${v.label}
    </span>`;
}

// --- 2. TRUST SCORE ---
const trustScoreCache = {};

async function fetchTrustScore(repoName) {
    if (trustScoreCache[repoName]) return trustScoreCache[repoName];
    
    try {
        const r = await fetch(`/api/repo/trust-score?repo=${encodeURIComponent(repoName)}`);
        if (!r.ok) return null;
        const data = await r.json();
        trustScoreCache[repoName] = data;
        return data;
    } catch (e) {
        console.warn('Trust score fetch failed for', repoName, e);
        return null;
    }
}

function gradeToClass(grade) {
    if (!grade) return 'grade-loading';
    const g = grade.replace('+', '-plus').toLowerCase();
    return `grade-${g}`;
}

function renderTrustTooltip(data) {
    if (!data || !data.breakdown) return '';
    const bd = data.breakdown;
    const rows = Object.entries(bd).map(([key, info]) => {
        const pct = (info.score / info.max) * 100;
        const color = pct >= 80 ? '#34d399' : pct >= 50 ? '#fbbf24' : '#f87171';
        const label = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
        return `<div class="trust-tooltip-row">
            <span style="color:var(--text-dim)">${label}</span>
            <div style="display:flex;align-items:center;gap:6px;">
                <div class="trust-tooltip-bar"><div class="trust-tooltip-bar-fill" style="width:${pct}%;background:${color}"></div></div>
                <span style="color:var(--text);font-weight:600;font-size:0.7rem;">${info.score}/${info.max}</span>
            </div>
        </div>`;
    }).join('');
    
    return `<div class="trust-tooltip">
        <div style="font-weight:700;margin-bottom:8px;color:var(--text);font-size:0.82rem;">Trust Score: ${data.trust_score}/100</div>
        ${rows}
    </div>`;
}

async function loadTrustBadge(repoName, badgeId) {
    const badge = document.getElementById(badgeId);
    if (!badge) return;
    
    const data = await fetchTrustScore(repoName);
    if (!data) {
        badge.style.display = 'none';
        return;
    }
    
    badge.className = `trust-badge ${gradeToClass(data.grade)}`;
    badge.innerHTML = `🛡️ ${data.grade}${renderTrustTooltip(data)}`;
}

// --- 3. WATCHLIST SYSTEM ---
function getWatchlist() {
    try {
        return JSON.parse(localStorage.getItem('github_trending_watchlist') || '[]');
    } catch {
        return [];
    }
}

function saveWatchlist(list) {
    localStorage.setItem('github_trending_watchlist', JSON.stringify(list));
    updateWatchlistBadge();
}

function isInWatchlist(repoName) {
    return getWatchlist().some(w => w.full_name === repoName);
}

function toggleWatchRepo(event, index) {
    if (event) event.stopPropagation();
    if (!lastFetchedRepos || !lastFetchedRepos[index]) return;
    
    const repo = lastFetchedRepos[index];
    const repoName = repo.full_name || repo.name;
    let wl = getWatchlist();
    
    if (isInWatchlist(repoName)) {
        wl = wl.filter(w => w.full_name !== repoName);
    } else {
        wl.push({
            full_name: repoName,
            html_url: repo.html_url || `https://github.com/${repoName}`,
            stars_at_save: repo.stargazers_count || repo.stars || 0,
            language: repo.language || '',
            saved_at: new Date().toISOString()
        });
    }
    
    saveWatchlist(wl);
    
    // Update button state
    const btn = document.getElementById(`watchBtn_${index}`);
    if (btn) {
        btn.className = `watchlist-btn ${isInWatchlist(repoName) ? 'saved' : ''}`;
        btn.innerHTML = isInWatchlist(repoName) ? '🔔' : '🔕';
    }
    
    // Re-render watchlist panel if visible
    if ($('watchlistPanel') && $('watchlistPanel').classList.contains('visible')) {
        renderWatchlistPanel();
    }
}

function updateWatchlistBadge() {
    const badge = $('watchlistCountBadge');
    const wl = getWatchlist();
    if (badge) {
        if (wl.length > 0) {
            badge.style.display = 'inline-flex';
            badge.textContent = wl.length;
        } else {
            badge.style.display = 'none';
        }
    }
}

function toggleWatchlistPanel() {
    const panel = $('watchlistPanel');
    if (!panel) return;
    
    panel.classList.toggle('visible');
    if (panel.classList.contains('visible')) {
        renderWatchlistPanel();
    }
}

function renderWatchlistPanel() {
    const container = $('watchlistItems');
    const milestonesContainer = $('watchlistMilestones');
    if (!container) return;
    
    const wl = getWatchlist();
    
    if (wl.length === 0) {
        container.innerHTML = `<p style="color:var(--text-muted); font-size:0.8rem; text-align:center; padding:12px;">${currentLang === 'ru' ? 'Список наблюдения пуст. Нажмите 🔕 на карточке репозитория, чтобы добавить.' : 'Watchlist is empty. Click 🔕 on a repo card to add.'}</p>`;
        if (milestonesContainer) milestonesContainer.innerHTML = '';
        return;
    }
    
    // Check milestones for repos currently in view
    let milestonesHtml = '';
    if (lastFetchedRepos && milestonesContainer) {
        wl.forEach(savedRepo => {
            const currentRepo = lastFetchedRepos.find(r => (r.full_name || r.name) === savedRepo.full_name);
            if (currentRepo) {
                const currentStars = currentRepo.stargazers_count || currentRepo.stars || 0;
                const savedStars = savedRepo.stars_at_save || 0;
                const diff = currentStars - savedStars;
                if (diff > 0) {
                    milestonesHtml += `<div class="watchlist-milestone">
                        🎉 <strong>${esc(savedRepo.full_name)}</strong> ${currentLang === 'ru' ? `набрал +${diff.toLocaleString()} ⭐ с момента добавления!` : `gained +${diff.toLocaleString()} ⭐ since you added it!`}
                    </div>`;
                }
            }
        });
        milestonesContainer.innerHTML = milestonesHtml;
    }
    
    container.innerHTML = wl.map(w => {
        const date = new Date(w.saved_at).toLocaleDateString(currentLang === 'ru' ? 'ru-RU' : 'en-US');
        return `<div class="watchlist-item">
            <div class="watchlist-item-info">
                <a class="watchlist-item-name" href="${w.html_url}" target="_blank">${esc(w.full_name)}</a>
            </div>
            <div class="watchlist-item-stats">
                <span>⭐ ${(w.stars_at_save || 0).toLocaleString()}</span>
                <span>${w.language || '?'}</span>
                <span style="color:var(--text-muted)">${date}</span>
                <button onclick="removeFromWatchlist('${esc(w.full_name)}')" style="background:none;border:none;color:var(--red);cursor:pointer;font-size:0.75rem;padding:0 4px;" title="Remove">✕</button>
            </div>
        </div>`;
    }).join('');
}

function removeFromWatchlist(repoName) {
    let wl = getWatchlist();
    wl = wl.filter(w => w.full_name !== repoName);
    saveWatchlist(wl);
    renderWatchlistPanel();
    
    // Update button on card if visible
    if (lastFetchedRepos) {
        lastFetchedRepos.forEach((r, i) => {
            if ((r.full_name || r.name) === repoName) {
                const btn = document.getElementById(`watchBtn_${i}`);
                if (btn) {
                    btn.className = 'watchlist-btn';
                    btn.innerHTML = '🔕';
                }
            }
        });
    }
}

function clearWatchlist() {
    if (!confirm(currentLang === 'ru' ? 'Очистить весь список наблюдения?' : 'Clear the entire watchlist?')) return;
    saveWatchlist([]);
    renderWatchlistPanel();
    
    // Reset all watchlist buttons on cards
    document.querySelectorAll('.watchlist-btn').forEach(btn => {
        btn.className = 'watchlist-btn';
        btn.innerHTML = '🔕';
    });
}

function exportWatchlist() {
    const wl = getWatchlist();
    if (wl.length === 0) return;
    
    const dataStr = JSON.stringify(wl, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `github_watchlist_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// --- 4. DIGEST GENERATOR ---
let lastDigestMarkdown = '';

function openDigestModal() {
    $('digestModal').classList.add('open');
}

function closeDigestModal() {
    $('digestModal').classList.remove('open');
}

async function generateDigest() {
    const container = $('digestContent');
    if (!container) return;
    
    if (!lastFetchedRepos || lastFetchedRepos.length === 0) {
        container.innerHTML = `<p style="color:var(--red); text-align:center;">${currentLang === 'ru' ? 'Сначала загрузите репозитории.' : 'Load some repositories first.'}</p>`;
        return;
    }
    
    container.innerHTML = '<div class="loading"><div class="spinner"></div><p style="color:var(--text-muted);font-size:0.8rem;margin-top:8px;">Generating digest with AI...</p></div>';
    
    const top10 = [...lastFetchedRepos]
        .sort((a, b) => (b.stargazers_count || 0) - (a.stargazers_count || 0))
        .slice(0, 10);
    
    const repoList = top10.map(r => 
        `- ${r.full_name || r.name} (${r.language || '?'}): ${r.description || 'No description'} [⭐ ${(r.stargazers_count || r.stars || 0).toLocaleString()}]`
    ).join('\n');
    
    const query = currentLang === 'ru'
        ? `Сгенерируй красивый еженедельный дайджест трендовых репозиториев GitHub в формате Markdown newsletter. Включи:\n\n1. Заголовок с датой (## 🔥 GitHub Trending Weekly — дата)\n2. Краткое вступление (1-2 предложения)\n3. Для каждого из топ-10 репозиториев: название со ссылкой, 2-3 предложения описания, язык, звёзды, почему стоит обратить внимание\n4. Раздел "Тренды недели" (какие технологии/темы доминируют)\n5. Заключение\n\nВот список репозиториев:\n${repoList}\n\nФормат: чистый Markdown, используй эмодзи, пиши компактно и информативно.`
        : `Generate a beautiful weekly digest of trending GitHub repositories in Markdown newsletter format. Include:\n\n1. Title with date (## 🔥 GitHub Trending Weekly — date)\n2. Brief intro (1-2 sentences)\n3. For each of the top 10 repos: name with link, 2-3 sentence description, language, stars, why it's worth checking out\n4. "Trends of the Week" section (which technologies/topics dominate)\n5. Conclusion\n\nRepository list:\n${repoList}\n\nFormat: clean Markdown, use emojis, be concise and informative.`;
    
    const key = localStorage.getItem("gemini_api_key") || "";
    const headers = { 'Content-Type': 'application/json' };
    if (key) headers['X-Gemini-Key'] = key;
    
    try {
        const r = await fetch('/api/ai/summarize', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                query: query,
                repos: top10
            })
        });
        const d = await r.json();
        
        if (d.error) {
            container.innerHTML = `<p style="color:var(--red);text-align:center;">❌ ${esc(d.error)}</p>`;
            if (d.error.includes("Missing GEMINI_API_KEY")) openApiKeyModal();
            return;
        }
        
        lastDigestMarkdown = d.summary || '';
        container.innerHTML = renderMarkdown(lastDigestMarkdown);
    } catch (e) {
        container.innerHTML = `<p style="color:var(--red);text-align:center;">Error: ${e.message}</p>`;
    }
}

function copyDigest() {
    if (!lastDigestMarkdown) {
        alert(currentLang === 'ru' ? 'Сначала сгенерируйте дайджест.' : 'Generate a digest first.');
        return;
    }
    navigator.clipboard.writeText(lastDigestMarkdown).then(() => {
        const btn = $('digestCopyBtn');
        const orig = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => btn.textContent = orig, 2000);
    });
}

function downloadDigest() {
    if (!lastDigestMarkdown) {
        alert(currentLang === 'ru' ? 'Сначала сгенерируйте дайджест.' : 'Generate a digest first.');
        return;
    }
    const blob = new Blob([lastDigestMarkdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `github_trending_digest_${new Date().toISOString().split('T')[0]}.md`;
    a.click();
    URL.revokeObjectURL(url);
}

// --- ENHANCED CARD RENDERING (Velocity + Watchlist + Trust Score) ---
// Override the original card function to include new features
const _originalCard = card;
card = function(r, i, source) {
    const n = r.full_name || 'unknown';
    const u = r.html_url || 'https://github.com/' + n;
    const d = r.description || T[currentLang].noDesc;
    const s = (r.stargazers_count || 0).toLocaleString();
    const f = (r.forks_count || 0).toLocaleString();
    const l = r.language || '';
    const lc = LANG_COLORS[l] || '#71717a';
    const sp = r.stars_period || 0;
    
    let badge = '';
    if (sp > 0) {
        const dur = $('durationSelect').value;
        const localizedLabel = T[currentLang].starsLabel[dur] || 'stars';
        badge = `<span class="badge-hot">🔥 ${sp.toLocaleString()} ${localizedLabel}</span>`;
    }
    
    let freshBadge = '';
    const updatedAtStr = r.updated_at || r.pushed_at;
    if (updatedAtStr) {
        try {
            const diffMs = new Date() - new Date(updatedAtStr);
            const diffHours = diffMs / (1000 * 60 * 60);
            if (diffHours <= 24) {
                freshBadge = `<span class="badge-fresh">⚡ Active</span>`;
            }
        } catch (e) {}
    } else if (source === 'trending' || sp > 0) {
        freshBadge = `<span class="badge-fresh">⚡ Active</span>`;
    }

    // Velocity Badge
    const velocityHtml = renderVelocityBadge(r);
    
    // Trust Score Badge (loads async)
    const trustBadgeId = `trust_${i}`;
    const trustBadgeHtml = `<span id="${trustBadgeId}" class="trust-badge grade-loading" style="font-size:0.6rem;">🛡️ ...</span>`;
    
    // Lazy-load trust score after render
    setTimeout(() => loadTrustBadge(n, trustBadgeId), 300 + i * 150);

    let badgesHtml = '';
    if (badge || freshBadge || velocityHtml || trustBadgeHtml) {
        badgesHtml = `<div class="badge-row" style="flex-wrap:wrap;gap:4px;">${badge} ${freshBadge} ${velocityHtml} ${trustBadgeHtml}</div>`;
    }
    
    const bb = r.built_by || [];
    const builtByAvatars = bb.length > 0 ?
        `<div class="built-by">
            ${bb.map(user => `<img class="avatar" src="https://github.com/${user}.png?size=40" title="${esc(user)}" alt="${esc(user)}">`).join('')}
         </div>` : '';

    const isChecked = selectedCompareRepos.find(x => x.full_name === n) ? 'checked' : '';
    const compareCheckbox = `
        <div class="compare-checkbox-wrapper" onclick="event.stopPropagation();">
            <input type="checkbox" id="compare_chk_${i}" class="compare-checkbox" ${isChecked} onchange="onCompareCheckChange(this, ${i})">
            <span>Compare</span>
        </div>
    `;
    
    // Watchlist button
    const isSaved = isInWatchlist(n);
    const watchlistBtn = `<button id="watchBtn_${i}" class="watchlist-btn ${isSaved ? 'saved' : ''}" onclick="toggleWatchRepo(event, ${i})" title="${isSaved ? 'Remove from Watchlist' : 'Add to Watchlist'}">${isSaved ? '🔔' : '🔕'}</button>`;

    return `<div class="card" style="animation-delay:${i * 0.03}s;">
        ${watchlistBtn}
        ${compareCheckbox}
        <div class="card-header" style="padding-right: 70px;">
            <a class="card-name" href="${u}" target="_blank">${esc(n)}</a>
            ${badgesHtml}
        </div>
        <p class="card-desc">${esc(d)}</p>
        <div class="card-footer-row">
            ${builtByAvatars}
            <button class="btn-tweets" onclick="openRepoDetailsHub(event, ${i})">📊 Info & AI</button>
        </div>
        <div class="card-meta" style="margin-top: 14px;">
            <span class="meta-item meta-stars">
                <svg width="12" height="12" fill="currentColor" viewBox="0 0 16 16"><path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/></svg>
                ${s}
            </span>
            <span class="meta-item meta-forks">
                <svg width="12" height="12" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M5 3.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm0 2.122a2.25 2.25 0 10-1.5 0v2.506a2.25 2.25 0 001.072 1.907l2.062 1.238a.75.75 0 10.772-1.285l-2.062-1.238a.75.75 0 01-.344-.636V5.372zM11.25 5a.75.75 0 100-1.5.75.75 0 000 1.5zM8.5 10.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm2.25-4.878v2.506a2.25 2.25 0 01-1.072 1.907l-2.062 1.238a.75.75 0 11-.772-1.285l2.062-1.238a.75.75 0 00.344-.636V5.372a2.25 2.25 0 111.5 0z"></path></svg>
                ${f}
            </span>
            ${l ? `<span class="meta-item meta-lang"><span class="lang-dot" style="background:${lc}"></span> ${l}</span>` : ''}
        </div>
    </div>`;
};

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar-filters');
    if (sidebar) {
        sidebar.classList.toggle('open');
    }
}

// Initialize watchlist badge on load
window.addEventListener('DOMContentLoaded', () => {
    updateWatchlistBadge();
    
    // Close digest modal and sidebar on outside click
    window.addEventListener('click', e => {
        const digestModal = $('digestModal');
        if (e.target === digestModal) closeDigestModal();
        
        const sidebar = document.querySelector('.sidebar-filters');
        const toggleBtn = $('btnSidebarToggle');
        if (sidebar && sidebar.classList.contains('open') && !sidebar.contains(e.target) && (!toggleBtn || !toggleBtn.contains(e.target))) {
            sidebar.classList.remove('open');
        }
    });
});

