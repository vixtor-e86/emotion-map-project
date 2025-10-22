/* ============================================
   EMOTION MAP - DASHBOARD LOGIC
   Main application controller
   ============================================ */

// Global state
let activeFilters = [];
let searchTimeout = null;

/* ============================================
   INITIALIZATION
   ============================================ */

/**
 * Initialize the entire dashboard
 */
async function initialize() {
    console.log('🚀 Initializing Emotion Map Dashboard...');
    
    try {
        // Check backend health
        await window.EmotionMapAPI.checkHealth();
        
        // Fetch initial data
        const stats = await window.EmotionMapAPI.fetchGlobalStats();
        const mapData = await window.EmotionMapAPI.fetchMapData();
        
        // Update UI components
        updateGlobalStats(stats);
        updateTime();
        
        // Initialize 3D globe
        window.EmotionMapGlobe.initGlobe(mapData);
        
        // Setup event listeners
        setupEventListeners();
        
        // Start periodic updates
        startPeriodicUpdates();
        
        // Hide loading overlay
        setTimeout(() => {
            document.getElementById('loadingOverlay').classList.add('hidden');
        }, 2000);
        
        console.log('✅ Dashboard initialized successfully!');
        console.log('💡 TIP: Click any hexagon to see region details');
        
    } catch (error) {
        console.error('❌ Initialization failed:', error);
        document.getElementById('loadingOverlay').querySelector('.loading-text').textContent = 
            'Failed to load. Check if backend is running.';
    }
}

/* ============================================
   UI UPDATE FUNCTIONS
   ============================================ */

/**
 * Update global emotion statistics in top bar
 * @param {Object} stats - Emotion percentages from API
 */
function updateGlobalStats(stats) {
    const container = document.getElementById('emotionStats');
    if (!container) return;
    
    container.innerHTML = '';
    
    Object.entries(stats).forEach(([emotion, value]) => {
        const config = window.EmotionMapAPI.EMOTION_CONFIG[emotion];
        if (!config) return;
        
        const statDiv = document.createElement('div');
        statDiv.className = 'emotion-stat';
        statDiv.innerHTML = `
            <span class="emotion-icon">${config.emoji}</span>
            <span class="emotion-value">${value}%</span>
        `;
        container.appendChild(statDiv);
    });
    
    console.log('📊 Updated global stats:', stats);
}

/**
 * Update current time display
 */
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
   REGION DRAWER FUNCTIONS
   ============================================ */

/**
 * Open region details drawer
 * @param {String} country - Country name
 */
async function openRegionDrawer(country) {
    const drawer = document.getElementById('regionDrawer');
    if (!drawer) return;
    
    // Fetch location details from API
    const data = await window.EmotionMapAPI.fetchLocationDetails(country);
    
    // Update drawer title
    document.getElementById('drawerTitle').textContent = data.country || country;
    document.getElementById('drawerSubtitle').textContent = data.region || '';
    
    // Update emotion breakdown
    updateEmotionBreakdown(data.emotions || {});
    
    // Update keywords
    updateKeywords(data.keywords || []);
    
    // Update sample posts
    updatePosts(data.posts || []);
    
    // Open drawer
    drawer.classList.add('open');
    
    console.log('📂 Opened drawer for:', country);
}

/**
 * Close region drawer
 */
function closeRegionDrawer() {
    const drawer = document.getElementById('regionDrawer');
    if (drawer) {
        drawer.classList.remove('open');
    }
}

/**
 * Update emotion breakdown bars in drawer
 */
function updateEmotionBreakdown(emotions) {
    const container = document.getElementById('emotionBreakdown');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Sort emotions by value (highest first)
    Object.entries(emotions)
        .sort((a, b) => b[1] - a[1])
        .forEach(([emotion, value]) => {
            const config = window.EmotionMapAPI.EMOTION_CONFIG[emotion];
            if (!config) return;
            
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

/**
 * Update trending keywords in drawer
 */
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

/**
 * Update sample posts in drawer
 */
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

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Close drawer button
    const closeBtn = document.getElementById('closeDrawer');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeRegionDrawer);
    }

    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', handleRefresh);
    }

    // Search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => handleFilterClick(btn));
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboard);
}

/**
 * Handle refresh button click
 */
async function handleRefresh() {
    const btn = document.getElementById('refreshBtn');
    if (!btn) return;
    
    // Animate button
    btn.style.transform = 'rotate(360deg)';
    
    console.log('🔄 Refreshing data...');
    
    // Fetch fresh data
    const result = await window.EmotionMapAPI.refreshData();
    
    if (result) {
        updateGlobalStats(result.stats);
        window.EmotionMapGlobe.updateGlobeData(result.mapData);
        updateTime();
    }
    
    // Reset button animation
    setTimeout(() => {
        btn.style.transform = 'rotate(0deg)';
    }, 500);
}

/**
 * Handle search input
 */
function handleSearch(e) {
    clearTimeout(searchTimeout);
    
    const query = e.target.value.trim();
    
    if (query.length < 3) return;
    
    searchTimeout = setTimeout(async () => {
        console.log('🔍 Searching for:', query);
        const results = await window.EmotionMapAPI.searchEmotions(query);
        
        // TODO: Display search results or filter globe
        if (results && results.length > 0) {
            console.log('📍 Found', results.length, 'results');
            // You can update the globe to show only search results
        }
    }, 500);
}

/**
 * Handle emotion filter button click
 */
function handleFilterClick(btn) {
    const emotion = btn.dataset.emotion;
    
    if (activeFilters.includes(emotion)) {
        // Remove filter
        activeFilters = activeFilters.filter(e => e !== emotion);
        btn.classList.remove('active');
    } else {
        // Add filter
        activeFilters.push(emotion);
        btn.classList.add('active');
    }
    
    // Update globe with filtered data
    window.EmotionMapGlobe.filterGlobeByEmotion(activeFilters);
    
    console.log('🎯 Active filters:', activeFilters);
}

/**
 * Handle keyboard shortcuts
 */
function handleKeyboard(e) {
    // Press Space to toggle rotation
    if (e.code === 'Space') {
        e.preventDefault();
        window.EmotionMapGlobe.toggleRotation();
    }
    
    // Press Escape to close drawer
    if (e.code === 'Escape') {
        closeRegionDrawer();
    }
}

/* ============================================
   PERIODIC UPDATES
   ============================================ */

/**
 * Start periodic data updates
 */
function startPeriodicUpdates() {
    // Update time every minute
    setInterval(updateTime, 60000);
    
    // Auto-refresh data every 60 minutes (backend refreshes every 60 min)
    setInterval(async () => {
        console.log('⏰ Auto-refresh triggered');
        const result = await window.EmotionMapAPI.refreshData();
        if (result) {
            updateGlobalStats(result.stats);
            window.EmotionMapGlobe.updateGlobeData(result.mapData);
        }
    }, 3600000); // 60 minutes in milliseconds
}

/* ============================================
   EXPOSE FUNCTIONS GLOBALLY
   ============================================ */

// Make drawer function available to globe3d.js
window.openRegionDrawer = openRegionDrawer;

/* ============================================
   START APPLICATION
   ============================================ */

// Initialize when page loads
window.addEventListener('load', initialize);

console.log('📱 Dashboard script loaded');