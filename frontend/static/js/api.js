/* ============================================
   EMOTION MAP - API INTEGRATION
   Connects frontend to Flask backend
   ============================================ */

// API Configuration
const API_BASE = 'http://localhost:5000/api';

// Emotion Configuration
const EMOTION_CONFIG = {
    joy: { color: '#10b981', emoji: '🟢', label: 'Strong Bullish', sentiment: 'bullish', score: 85 },
    anger: { color: '#ef4444', emoji: '🔴', label: 'Strong Bearish', sentiment: 'bearish', score: 25 },
    sadness: { color: '#f87171', emoji: '📉', label: 'Cautious', sentiment: 'bearish', score: 35 },
    hope: { color: '#34d399', emoji: '📈', label: 'Optimistic', sentiment: 'bullish', score: 75 },
    calmness: { color: '#94a3b8', emoji: '⚪', label: 'Neutral', sentiment: 'neutral', score: 50 }
};

/* ============================================
   API FUNCTIONS
   ============================================ */

/**
 * API INTEGRATION POINT 1: Health Check
 * Checks if backend is running
 * Endpoint: GET /api/health
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
 * API INTEGRATION POINT 2: Fetch Global Statistics
 * Gets overall emotion percentages worldwide
 * Endpoint: GET /api/stats
 * 
 * Expected Response Format:
 * {
 *   joy: 64,
 *   anger: 21,
 *   sadness: 10,
 *   hope: 3,
 *   calmness: 2
 * }
 */
async function fetchGlobalStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();
        console.log('📊 Global stats from API:', data);
        return data;
    } catch (error) {
        console.warn('⚠️ Using mock global stats (backend not connected)');
        // Mock data fallback
        return {
            joy: 64,
            anger: 21,
            sadness: 10,
            hope: 3,
            calmness: 2
        };
    }
}

/**
 * API INTEGRATION POINT 3: Fetch Map Data
 * Gets emotion data for all locations
 * Endpoint: GET /api/map-data/:zoom_level
 * 
 * Expected Response Format:
 * [
 *   {
 *     lat: 6.5244,
 *     lng: 3.3792,
 *     country: "Nigeria",
 *     region: "Lagos",
 *     emotion: "anger",
 *     intensity: 0.65,    // 0.0 to 1.0
 *     posts: 120
 *   },
 *   ...
 * ]
 */
async function fetchMapData(zoomLevel = 'country') {
    try {
        const response = await fetch(`${API_BASE}/map-data/${zoomLevel}`);
        const data = await response.json();
        console.log('🗺️ Map data from API:', data);
        return data;
    } catch (error) {
        console.warn('⚠️ Using mock map data (backend not connected)');
        // Mock data fallback
        return [
            { lat: 9.0820, lng: 8.6753, country: 'Nigeria', emotion: 'anger', intensity: 0.85, posts: 120 },
            { lat: 40.7128, lng: -74.0060, country: 'USA', emotion: 'joy', intensity: 0.80, posts: 340 },
            { lat: 48.8566, lng: 2.3522, country: 'France', emotion: 'hope', intensity: 0.60, posts: 180 },
            { lat: -23.5505, lng: -46.6333, country: 'Brazil', emotion: 'joy', intensity: 0.90, posts: 210 },
            { lat: 51.5074, lng: -0.1278, country: 'UK', emotion: 'calmness', intensity: 0.55, posts: 190 },
            { lat: 35.6762, lng: 139.6503, country: 'Japan', emotion: 'calmness', intensity: 0.70, posts: 150 }
        ];
    }
}

/**
 * API INTEGRATION POINT 4: Fetch Location Details
 * Gets detailed emotion breakdown for a specific location
 * Endpoint: GET /api/location/:location_name
 * 
 * Expected Response Format:
 * {
 *   country: "Nigeria",
 *   region: "Lagos",
 *   emotions: {
 *     anger: 65,
 *     joy: 20,
 *     sadness: 10,
 *     hope: 3,
 *     calmness: 2
 *   },
 *   keywords: ["protests", "economy", "fuel"],
 *   posts: [
 *     "The situation is difficult...",
 *     "We need change..."
 *   ]
 * }
 */
async function fetchLocationDetails(location) {
    try {
        const response = await fetch(`${API_BASE}/location/${encodeURIComponent(location)}`);
        const data = await response.json();
        console.log('📍 Location details from API:', data);
        return data;
    } catch (error) {
        console.warn('⚠️ Using mock region data (backend not connected)');
        // Mock data fallback
        const mockData = {
            'Nigeria': {
                country: 'Nigeria',
                region: 'Lagos',
                emotions: { anger: 65, joy: 20, sadness: 10, hope: 3, calmness: 2 },
                keywords: ['protests', 'economy', 'fuel prices'],
                posts: ['The situation is getting worse', 'We need change now']
            },
            'USA': {
                country: 'USA',
                region: 'New York',
                emotions: { joy: 70, hope: 15, calmness: 10, anger: 3, sadness: 2 },
                keywords: ['celebration', 'tech', 'innovation'],
                posts: ['Best day ever!', 'Amazing vibes today']
            }
        };
        return mockData[location] || mockData['Nigeria'];
    }
}

/**
 * API INTEGRATION POINT 5: Search Emotions
 * Search for locations/topics with optional emotion filter
 * Endpoint: GET /api/search?q=query&emotion=filter
 * 
 * Parameters:
 * - query: Search term (location, topic, keyword)
 * - emotionFilter: Optional emotion filter (joy, anger, etc.)
 * 
 * Expected Response Format:
 * [
 *   {
 *     country: "Nigeria",
 *     emotion: "anger",
 *     posts: 45,
 *     ...
 *   },
 *   ...
 * ]
 */
async function searchEmotions(query, emotionFilter = null) {
    try {
        let url = `${API_BASE}/search?q=${encodeURIComponent(query)}`;
        if (emotionFilter) {
            url += `&emotion=${emotionFilter}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        console.log('🔍 Search results:', data);
        return data;
    } catch (error) {
        console.error('❌ Search failed:', error);
        return [];
    }
}

/**
 * API INTEGRATION POINT 6: Fetch Emotion Trends
 * Gets emotion trends over time
 * Endpoint: GET /api/trends?hours=24
 * 
 * Expected Response Format:
 * {
 *   timestamps: ["2025-10-22 10:00", "2025-10-22 11:00", ...],
 *   joy: [64, 62, 65, ...],
 *   anger: [21, 23, 20, ...],
 *   ...
 * }
 */
async function fetchTrends(hours = 24) {
    try {
        const response = await fetch(`${API_BASE}/trends?hours=${hours}`);
        const data = await response.json();
        console.log('📈 Trends data:', data);
        return data;
    } catch (error) {
        console.warn('⚠️ Trends endpoint not available');
        return null;
    }
}

/**
 * API INTEGRATION POINT 7: Refresh Data
 * Triggers backend to refresh emotion data
 * Note: Backend refreshes automatically every 60 minutes
 */
async function refreshData() {
    console.log('🔄 Refreshing all data...');
    
    try {
        // Fetch all data in parallel
        const [stats, mapData] = await Promise.all([
            fetchGlobalStats(),
            fetchMapData()
        ]);
        
        return { stats, mapData };
    } catch (error) {
        console.error('❌ Refresh failed:', error);
        return null;
    }
}

/* ============================================
   UTILITY FUNCTIONS
   ============================================ */

/**
 * Filter map data by active emotion filters
 */
function filterMapData(data, activeFilters) {
    if (!activeFilters || activeFilters.length === 0) {
        return data;
    }
    return data.filter(point => activeFilters.includes(point.emotion));
}

/**
 * Handle API errors gracefully
 */
function handleApiError(error, context) {
    console.error(`API Error in ${context}:`, error);
    // You can add user-friendly error messages here
    return null;
}

/* ============================================
   EXPORT FOR USE IN OTHER FILES
   ============================================ */

// Make functions available globally
window.EmotionMapAPI = {
    checkHealth,
    fetchGlobalStats,
    fetchMapData,
    fetchLocationDetails,
    searchEmotions,
    fetchTrends,
    refreshData,
    filterMapData,
    EMOTION_CONFIG,
    API_BASE
};