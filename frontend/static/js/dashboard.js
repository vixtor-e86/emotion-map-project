/* ============================================
   MULTI-SECTOR DASHBOARD LOGIC
   Handles sector switching and UI updates
   ============================================ */

// Global state - DECLARE ONCE ONLY
window.currentSector = 'finance';
window.activeFilters = [];
window.searchTimeout = null;
window.currentMapData = [];

/* ============================================
   INITIALIZATION
   ============================================ */

async function initialize() {
    console.log('🚀 Initializing Multi-Sector Dashboard...');
    
    try {
        // Check backend health
        await window.EmotionMapAPI.checkHealth();
        
        // Fetch initial data for finance sector
        const stats = await window.EmotionMapAPI.fetchGlobalStats('finance');
        const mapData = await window.EmotionMapAPI.fetchMapData('country', 'finance');
        
        // Update UI
        updateGlobalStats(stats);
        updateEmotionFilterLabels('finance');
        updateSectorDescription('finance');
        updateTime();
        
        // Initialize globe
        window.EmotionMapGlobe.initGlobe(mapData);
        window.currentMapData = mapData;
        
        // Setup event listeners
        setupEventListeners();
        
        // Start periodic updates
        startPeriodicUpdates();
        
        // Hide loading
        setTimeout(() => {
            document.getElementById('loadingOverlay').classList.add('hidden');
        }, 2000);
        
        console.log('✅ Dashboard initialized!');
        
    } catch (error) {
        console.error('❌ Initialization failed:', error);
    }
}

/* ============================================
   SECTOR SWITCHING
   ============================================ */

async function switchSector(newSector) {
    console.log(`🔄 Switching to ${newSector} sector...`);
    
    // Update global state
    window.currentSector = newSector;
    
    // Update active tab
    document.querySelectorAll('.sector-tab').forEach(tab => {
        if (tab.dataset.sector === newSector) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Update emotion filter labels
    updateEmotionFilterLabels(newSector);
    
    // Update sector description
    updateSectorDescription(newSector);
    
    // Fetch new data
    const [stats, mapData] = await Promise.all([
        window.EmotionMapAPI.fetchGlobalStats(newSector),
        window.EmotionMapAPI.fetchMapData('country', newSector)
    ]);
    
    // Update UI
    updateGlobalStats(stats);
    window.EmotionMapGlobe.updateGlobeData(mapData);
    window.currentMapData = mapData;
    
    // Clear active filters
    window.activeFilters = [];
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    console.log(`✅ Switched to ${newSector}`);
}

function updateEmotionFilterLabels(sector) {
    const configs = window.EmotionMapAPI.getAllEmotionConfigs();
    
    const joyBtn = document.getElementById('filterJoy');
    const hopeBtn = document.getElementById('filterHope');
    const calmnessBtn = document.getElementById('filterCalmness');
    const sadnessBtn = document.getElementById('filterSadness');
    const angerBtn = document.getElementById('filterAnger');
    
    if (joyBtn) {
        joyBtn.querySelector('.filter-emoji').textContent = configs.joy.emoji;
        joyBtn.querySelector('.filter-label-text').textContent = configs.joy.label;
    }
    
    if (hopeBtn) {
        hopeBtn.querySelector('.filter-emoji').textContent = configs.hope.emoji;
        hopeBtn.querySelector('.filter-label-text').textContent = configs.hope.label;
    }
    
    if (calmnessBtn) {
        calmnessBtn.querySelector('.filter-emoji').textContent = configs.calmness.emoji;
        calmnessBtn.querySelector('.filter-label-text').textContent = configs.calmness.label;
    }
    
    if (sadnessBtn) {
        sadnessBtn.querySelector('.filter-emoji').textContent = configs.sadness.emoji;
        sadnessBtn.querySelector('.filter-label-text').textContent = configs.sadness.label;
    }
    
    if (angerBtn) {
        angerBtn.querySelector('.filter-emoji').textContent = configs.anger.emoji;
        angerBtn.querySelector('.filter-label-text').textContent = configs.anger.label;
    }
}

function updateSectorDescription(sector) {
    const sectorInfo = window.EmotionMapAPI.getSectorInfo(sector);
    const descEl = document.getElementById('sectorDescription');
    if (descEl) {
        descEl.textContent = sectorInfo.description;
    }
}

/* ============================================
   UI UPDATE FUNCTIONS
   ============================================ */

function updateGlobalStats(stats) {
    const container = document.getElementById('emotionStats');
    if (!container) return;
    
    container.innerHTML = '';
    
    const emotions = ['joy', 'anger', 'sadness', 'hope', 'calmness'];
    
    emotions.forEach(emotion => {
        const config = window.EmotionMapAPI.getEmotionConfig(emotion);
        const value = stats[emotion] || 0;
        
        const statDiv = document.createElement('div');
        statDiv.className = 'emotion-stat';
        statDiv.innerHTML = `
            <span class="emotion-icon">${config.emoji}</span>
            <span class="emotion-value">${Math.round(value)}%</span>
        `;
        container.appendChild(statDiv);
    });
    
    console.log('📊 Updated global stats');
}

function updateTime() {
    const timeDisplay = document.getElementById('timeDisplay');
    if (!timeDisplay) return;
    
    const now = new Date();
    timeDisplay.textContent = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

/* ============================================
   REGION DRAWER
   ============================================ */

async function openRegionDrawer(country) {
    const drawer = document.getElementById('regionDrawer');
    if (!drawer) return;
    
    const data = await window.EmotionMapAPI.fetchLocationDetails(country);
    
    // Update title
    document.getElementById('drawerTitle').textContent = data.country || country;
    document.getElementById('drawerSubtitle').textContent = data.region || '';
    
    // Update sector badge
    const badge = document.getElementById('drawerSectorBadge');
    if (badge) {
        const sectorInfo = window.EmotionMapAPI.getSectorInfo(data.sector || window.currentSector);
        badge.innerHTML = `${sectorInfo.icon} ${sectorInfo.name}`;
        badge.setAttribute('data-sector', data.sector || window.currentSector);
    }
    
    // Update emotion breakdown
    updateEmotionBreakdown(data.emotions || {});
    
    // Update keywords
    updateKeywords(data.keywords || []);
    
    // Update posts
    updatePosts(data.posts || []);
    
    // Open drawer
    drawer.classList.add('open');
    
    console.log('📂 Opened drawer for:', country);
}

function closeRegionDrawer() {
    const drawer = document.getElementById('regionDrawer');
    if (drawer) {
        drawer.classList.remove('open');
    }
}

function updateEmotionBreakdown(emotions) {
    const container = document.getElementById('emotionBreakdown');
    if (!container) return;
    
    container.innerHTML = '';
    
    Object.entries(emotions)
        .sort((a, b) => b[1] - a[1])
        .forEach(([emotion, value]) => {
            const config = window.EmotionMapAPI.getEmotionConfig(emotion);
            
            const item = document.createElement('div');
            item.className = 'emotion-item';
            item.innerHTML = `
                <div class="emotion-label">
                    <span class="emotion-name">
                        <span>${config.emoji}</span>
                        <span>${config.label}</span>
                    </span>
                    <span class="emotion-percentage">${value}%</span>
                </div>
                <div class="emotion-bar">
                    <div class="emotion-bar-fill" style="width: ${value}%; background: ${config.color};"></div>
                </div>
            `;
            container.appendChild(item);
        });
}

function updateKeywords(keywords) {
    const container = document.getElementById('keywordsContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    keywords.forEach(keyword => {
        const tag = document.createElement('div');
        tag.className = 'keyword-tag';
        tag.textContent = `#${keyword}`;
        container.appendChild(tag);
    });
}

function updatePosts(posts) {
    const container = document.getElementById('postsContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (posts.length === 0) {
        container.innerHTML = '<p style="color: #666;">No recent posts available</p>';
        return;
    }
    
    posts.forEach(post => {
        const card = document.createElement('div');
        card.className = 'post-card';
        card.textContent = `"${post}"`;
        container.appendChild(card);
    });
}

/* ============================================
   EVENT LISTENERS
   ============================================ */

function setupEventListeners() {
    // Sector tabs
    document.querySelectorAll('.sector-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const sector = tab.dataset.sector;
            switchSector(sector);
        });
    });
    
    // Close drawer
    const closeBtn = document.getElementById('closeDrawer');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeRegionDrawer);
    }
    
    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', handleRefresh);
    }
    
    // Search
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }
    
    // Filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => handleFilterClick(btn));
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboard);
}

async function handleRefresh() {
    const btn = document.getElementById('refreshBtn');
    if (!btn) return;
    
    btn.style.transform = 'rotate(360deg)';
    
    console.log('🔄 Refreshing data...');
    
    const result = await window.EmotionMapAPI.refreshData();
    
    if (result) {
        updateGlobalStats(result.stats);
        window.EmotionMapGlobe.updateGlobeData(result.mapData);
        window.currentMapData = result.mapData;
        updateTime();
    }
    
    setTimeout(() => {
        btn.style.transform = 'rotate(0deg)';
    }, 500);
}

function handleSearch(e) {
    clearTimeout(window.searchTimeout);
    
    const query = e.target.value.trim();
    const suggestionsContainer = document.getElementById('searchSuggestions');
    
    if (query.length < 2) {
        if (suggestionsContainer) suggestionsContainer.style.display = 'none';
        return;
    }
    
    const suggestions = window.currentMapData
        .filter(country => country.country.toLowerCase().includes(query.toLowerCase()))
        .slice(0, 5);
    
    if (suggestionsContainer && suggestions.length > 0) {
        suggestionsContainer.innerHTML = suggestions.map(country => {
            const config = window.EmotionMapAPI.getEmotionConfig(country.emotion);
            return `
                <div class="search-suggestion" data-lat="${country.lat}" data-lng="${country.lng}" data-country="${country.country}">
                    <span style="font-size: 1.2rem; margin-right: 0.5rem;">${config.emoji}</span>
                    <span style="flex: 1;">${country.country}</span>
                    <span style="font-size: 0.8rem; color: #666;">${country.posts} posts</span>
                </div>
            `;
        }).join('');
        suggestionsContainer.style.display = 'block';
        
        document.querySelectorAll('.search-suggestion').forEach(item => {
            item.addEventListener('click', () => {
                const lat = parseFloat(item.dataset.lat);
                const lng = parseFloat(item.dataset.lng);
                const country = item.dataset.country;
                
                window.EmotionMapGlobe.flyToLocation(lat, lng, 1.5);
                e.target.value = country;
                suggestionsContainer.style.display = 'none';
                setTimeout(() => openRegionDrawer(country), 1200);
            });
        });
    } else if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
    }
}

function handleFilterClick(btn) {
    const emotion = btn.dataset.emotion;
    
    if (window.activeFilters.includes(emotion)) {
        window.activeFilters = window.activeFilters.filter(e => e !== emotion);
        btn.classList.remove('active');
    } else {
        window.activeFilters.push(emotion);
        btn.classList.add('active');
    }
    
    window.EmotionMapGlobe.filterGlobeByEmotion(window.activeFilters);
    
    console.log('🎯 Active filters:', window.activeFilters);
}

function handleKeyboard(e) {
    if (e.code === 'Space') {
        e.preventDefault();
        window.EmotionMapGlobe.toggleRotation();
    }
    
    if (e.code === 'Escape') {
        closeRegionDrawer();
    }
    
    // Sector shortcuts: 1-4
    if (['Digit1', 'Digit2', 'Digit3', 'Digit4'].includes(e.code)) {
        const sectors = ['finance', 'health', 'technology', 'sports'];
        const index = parseInt(e.code.replace('Digit', '')) - 1;
        if (sectors[index]) {
            switchSector(sectors[index]);
        }
    }
}

/* ============================================
   PERIODIC UPDATES
   ============================================ */

function startPeriodicUpdates() {
    setInterval(updateTime, 60000);
    
    setInterval(async () => {
        console.log('⏰ Auto-refresh triggered');
        const result = await window.EmotionMapAPI.refreshData();
        if (result) {
            updateGlobalStats(result.stats);
            window.EmotionMapGlobe.updateGlobeData(result.mapData);
            window.currentMapData = result.mapData;
        }
    }, 3600000); // 60 minutes
}

/* ============================================
   EXPORT TO WINDOW
   ============================================ */

window.openRegionDrawer = openRegionDrawer;

/* ============================================
   START APPLICATION
   ============================================ */

window.addEventListener('load', initialize);

console.log('📱 Multi-Sector Dashboard script loaded');