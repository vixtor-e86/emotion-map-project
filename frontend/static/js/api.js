/* ============================================
   MULTI-SECTOR API INTEGRATION
   Handles API calls with sector filtering
   ============================================ */

// API Configuration
const API_BASE = '/api';

// Current active sector (global state)
window.currentSector = 'finance';

// Sector-specific emotion configurations
const SECTOR_EMOTION_CONFIGS = {
    finance: {
        joy: { color: '#10b981', emoji: '🟢', label: 'Strong Bullish' },
        hope: { color: '#34d399', emoji: '📈', label: 'Optimistic' },
        calmness: { color: '#94a3b8', emoji: '⚪', label: 'Neutral' },
        sadness: { color: '#f87171', emoji: '📉', label: 'Cautious' },
        anger: { color: '#ef4444', emoji: '🔴', label: 'Strong Bearish' }
    },
    health: {
        joy: { color: '#10b981', emoji: '💚', label: 'Healthy' },
        hope: { color: '#34d399', emoji: '🌱', label: 'Recovering' },
        calmness: { color: '#94a3b8', emoji: '😌', label: 'Stable' },
        sadness: { color: '#f87171', emoji: '😟', label: 'Concerned' },
        anger: { color: '#ef4444', emoji: '😤', label: 'Critical' }
    },
    technology: {
        joy: { color: '#8b5cf6', emoji: '🚀', label: 'Innovative' },
        hope: { color: '#a78bfa', emoji: '💡', label: 'Optimistic' },
        calmness: { color: '#94a3b8', emoji: '🧘', label: 'Stable' },
        sadness: { color: '#f87171', emoji: '😔', label: 'Disappointed' },
        anger: { color: '#ef4444', emoji: '🐛', label: 'Frustrated' }
    },
    sports: {
        joy: { color: '#f59e0b', emoji: '🎉', label: 'Excited' },
        hope: { color: '#fbbf24', emoji: '🔥', label: 'Hopeful' },
        calmness: { color: '#94a3b8', emoji: '😐', label: 'Neutral' },
        sadness: { color: '#f87171', emoji: '😢', label: 'Disappointed' },
        anger: { color: '#ef4444', emoji: '😡', label: 'Frustrated' }
    }
};

// Sector metadata
const SECTORS = {
    finance: { name: 'Finance', icon: '💰', description: 'Market Sentiment & Economic Trends' },
    health: { name: 'Health', icon: '🏥', description: 'Healthcare & Wellness Insights' },
    technology: { name: 'Technology', icon: '💻', description: 'Tech Innovation & Digital Trends' },
    sports: { name: 'Sports', icon: '⚽', description: 'Sports News & Fan Sentiment' }
};

/* ============================================
   API FUNCTIONS
   ============================================ */

/**
 * Get emotion config for current sector
 */
function getEmotionConfig(emotion) {
    const sector = window.currentSector || 'finance';
    return SECTOR_EMOTION_CONFIGS[sector][emotion] || {
        color: '#94a3b8',
        emoji: '⚪',
        label: emotion
    };
}

/**
 * Get all emotion configs for current sector
 */
function getAllEmotionConfigs() {
    const sector = window.currentSector || 'finance';
    return SECTOR_EMOTION_CONFIGS[sector];
}

/**
 * Get sector info
 */
function getSectorInfo(sector) {
    return SECTORS[sector] || SECTORS.finance;
}

/**
 * Health check
 */
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        console.log('✅ Backend health:', data);
        return data;
    } catch (error) {
        console.error('❌ Backend connection failed:', error);
        return null;
    }
}

/**
 * Fetch available sectors
 */
async function fetchSectors() {
    try {
        const response = await fetch(`${API_BASE}/sectors`);
        const data = await response.json();
        console.log('📂 Available sectors:', data);
        return data;
    } catch (error) {
        console.error('❌ Error fetching sectors:', error);
        return Object.keys(SECTORS).map(id => ({
            id,
            ...SECTORS[id],
            post_count: 0
        }));
    }
}

/**
 * Fetch global statistics for current sector
 */
async function fetchGlobalStats(sector = null) {
    try {
        const activeSector = sector || window.currentSector;
        const response = await fetch(`${API_BASE}/stats?sector=${activeSector}`);
        const data = await response.json();
        console.log(`📊 Stats for ${activeSector}:`, data);
        return data;
    } catch (error) {
        console.warn('⚠️ Using fallback stats');
        return {
            joy: 20, anger: 20, sadness: 20,
            hope: 20, calmness: 20, total_posts: 0,
            sector: sector || window.currentSector
        };
    }
}

/**
 * Fetch map data for current sector
 */
async function fetchMapData(zoomLevel = 'country', sector = null) {
    try {
        const activeSector = sector || window.currentSector;
        const response = await fetch(`${API_BASE}/map-data/${zoomLevel}?sector=${activeSector}`);
        const data = await response.json();
        console.log(`🗺️ Map data for ${activeSector} (${zoomLevel}):`, data.length, 'points');
        return data;
    } catch (error) {
        console.warn('⚠️ Using fallback map data');
        return [];
    }
}

/**
 * Fetch location details
 */
async function fetchLocationDetails(location, sector = null) {
    try {
        const activeSector = sector || window.currentSector;
        const response = await fetch(`${API_BASE}/location/${encodeURIComponent(location)}?sector=${activeSector}`);
        const data = await response.json();
        console.log('📍 Location details:', data);
        return data;
    } catch (error) {
        console.error('❌ Error fetching location details:', error);
        return {
            country: location,
            region: location,
            emotions: { joy: 20, anger: 20, sadness: 20, hope: 20, calmness: 20 },
            keywords: ['no', 'data'],
            posts: ['No data available'],
            sector: sector || window.currentSector
        };
    }
}

/**
 * Search with sector filter
 */
async function searchEmotions(query, emotionFilter = null, sector = null) {
    try {
        const activeSector = sector || window.currentSector;
        let url = `${API_BASE}/search?q=${encodeURIComponent(query)}&sector=${activeSector}`;
        
        if (emotionFilter) {
            url += `&emotion=${emotionFilter}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        console.log('🔍 Search results:', data);
        return data;
    } catch (error) {
        console.error('❌ Search failed:', error);
        return { results: [], count: 0 };
    }
}

/**
 * Fetch trends
 */
async function fetchTrends(hours = 24, sector = null) {
    try {
        const activeSector = sector || window.currentSector;
        const response = await fetch(`${API_BASE}/trends?hours=${hours}&sector=${activeSector}`);
        const data = await response.json();
        console.log('📈 Trends data:', data);
        return data;
    } catch (error) {
        console.warn('⚠️ Trends endpoint not available');
        return null;
    }
}

/**
 * Refresh all data for current sector
 */
async function refreshData(sector = null) {
    console.log('🔄 Refreshing data...');
    
    try {
        const activeSector = sector || window.currentSector;
        
        const [stats, mapData] = await Promise.all([
            fetchGlobalStats(activeSector),
            fetchMapData('country', activeSector)
        ]);
        
        return { stats, mapData, sector: activeSector };
    } catch (error) {
        console.error('❌ Refresh failed:', error);
        return null;
    }
}

/**
 * Filter map data by active emotion filters
 */
function filterMapData(data, activeFilters) {
    if (!activeFilters || activeFilters.length === 0) {
        return data;
    }
    return data.filter(point => activeFilters.includes(point.emotion));
}

/* ============================================
   EXPORT
   ============================================ */

window.EmotionMapAPI = {
    checkHealth,
    fetchSectors,
    fetchGlobalStats,
    fetchMapData,
    fetchLocationDetails,
    searchEmotions,
    fetchTrends,
    refreshData,
    filterMapData,
    getEmotionConfig,
    getAllEmotionConfigs,
    getSectorInfo,
    API_BASE,
    SECTORS
};

console.log('✅ Multi-Sector API module loaded');