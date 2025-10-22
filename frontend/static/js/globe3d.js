/* ============================================
   EMOTION MAP - 3D GLOBE VISUALIZATION
   Uses Globe.gl for rendering emotion data
   ============================================ */

let globe = null;
let currentMapData = [];

/* ============================================
   GLOBE INITIALIZATION
   ============================================ */

/**
 * Initialize the 3D globe with emotion visualization
 * @param {Array} mapData - Array of emotion data points from API
 */
function initGlobe(mapData = []) {
    const container = document.getElementById('globe-container');
    
    if (!container) {
        console.error('❌ Globe container not found');
        return;
    }

    currentMapData = mapData;
    
    // Initialize Globe.gl
    globe = Globe()
        // Globe textures
        .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
        .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png')
        .backgroundImageUrl('https://unpkg.com/three-globe/example/img/night-sky.png')
        
        // Hexbin visualization (better than bars!)
        .hexBinPointsData(currentMapData)
        .hexBinPointLat(d => d.lat)
        .hexBinPointLng(d => d.lng)
        .hexBinPointWeight(d => d.intensity || 0.5)
        .hexBinResolution(4)
        .hexMargin(0.3)
        .hexAltitude(d => {
            // Slight elevation based on intensity
            const avgIntensity = d.sumWeight / d.points.length;
            return avgIntensity * 0.15;
        })
        .hexTopColor(d => {
            // Color based on dominant emotion
            const emotions = {};
            d.points.forEach(p => {
                emotions[p.emotion] = (emotions[p.emotion] || 0) + 1;
            });
            const dominantEmotion = Object.keys(emotions).reduce((a, b) => 
                emotions[a] > emotions[b] ? a : b
            );
            return window.EmotionMapAPI.EMOTION_CONFIG[dominantEmotion]?.color || '#00A8FF';
        })
        .hexSideColor(d => {
            // Slightly darker side color
            const emotions = {};
            d.points.forEach(p => {
                emotions[p.emotion] = (emotions[p.emotion] || 0) + 1;
            });
            const dominantEmotion = Object.keys(emotions).reduce((a, b) => 
                emotions[a] > emotions[b] ? a : b
            );
            const color = window.EmotionMapAPI.EMOTION_CONFIG[dominantEmotion]?.color || '#00A8FF';
            return color + 'AA'; // Add transparency
        })
        .hexBinMerge(true)
        .hexTransitionDuration(1000)
        .hexLabel(d => {
            // Tooltip on hover
            const emotions = {};
            d.points.forEach(p => {
                emotions[p.emotion] = (emotions[p.emotion] || 0) + 1;
            });
            const dominantEmotion = Object.keys(emotions).reduce((a, b) => 
                emotions[a] > emotions[b] ? a : b
            );
            const config = window.EmotionMapAPI.EMOTION_CONFIG[dominantEmotion];
            const avgIntensity = Math.round((d.sumWeight / d.points.length) * 100);
            
            return `
                <div style="
                    background: rgba(0,0,0,0.9); 
                    padding: 12px 16px; 
                    border-radius: 8px; 
                    color: white; 
                    font-size: 14px;
                    font-family: 'Inter', sans-serif;
                    border: 1px solid ${config.color};
                ">
                    <div style="font-weight: 700; margin-bottom: 6px;">
                        ${config.emoji} ${config.label}
                    </div>
                    <div style="color: #a0a0a0;">
                        Intensity: ${avgIntensity}%<br/>
                        ${d.points.length} data point${d.points.length > 1 ? 's' : ''}
                    </div>
                </div>
            `;
        })
        .onHexClick(hex => {
            // Handle hexagon click - open region drawer
            handleHexClick(hex);
        })
        (container);

    // Globe controls configuration
    setupGlobeControls();
    
    console.log('✅ Globe initialized with', currentMapData.length, 'data points');
}

/* ============================================
   GLOBE CONTROLS
   ============================================ */

/**
 * Configure globe rotation and interaction controls
 */
function setupGlobeControls() {
    if (!globe) return;

    // Enable auto-rotation
    globe.controls().autoRotate = true;
    globe.controls().autoRotateSpeed = 0.3;
    
    // Pause rotation when user interacts
    globe.controls().addEventListener('start', () => {
        globe.controls().autoRotate = false;
    });
    
    // Resume rotation after 3 seconds of inactivity
    let rotationTimeout;
    globe.controls().addEventListener('end', () => {
        clearTimeout(rotationTimeout);
        rotationTimeout = setTimeout(() => {
            globe.controls().autoRotate = true;
        }, 3000);
    });

    // Enable zoom controls
    globe.controls().enableZoom = true;
    globe.controls().minDistance = 200;
    globe.controls().maxDistance = 800;
}

/**
 * Toggle auto-rotation on/off
 */
function toggleRotation() {
    if (!globe) return;
    globe.controls().autoRotate = !globe.controls().autoRotate;
    console.log('🔄 Auto-rotation:', globe.controls().autoRotate ? 'ON' : 'OFF');
}

/* ============================================
   DATA UPDATE FUNCTIONS
   ============================================ */

/**
 * Update globe with new map data
 * @param {Array} mapData - New emotion data from API
 */
function updateGlobeData(mapData) {
    if (!globe) {
        console.warn('⚠️ Globe not initialized, initializing now...');
        initGlobe(mapData);
        return;
    }

    currentMapData = mapData;
    globe.hexBinPointsData(mapData);
    console.log('🔄 Globe updated with', mapData.length, 'data points');
}

/**
 * Filter globe data by emotion
 * @param {Array} activeFilters - Array of emotion names to show
 */
function filterGlobeByEmotion(activeFilters) {
    if (!globe) return;

    let filteredData = currentMapData;
    
    if (activeFilters && activeFilters.length > 0) {
        filteredData = currentMapData.filter(point => 
            activeFilters.includes(point.emotion)
        );
        console.log('🎯 Filtered to', filteredData.length, 'points with emotions:', activeFilters);
    } else {
        console.log('🎯 Showing all', filteredData.length, 'data points');
    }
    
    globe.hexBinPointsData(filteredData);
}

/* ============================================
   INTERACTION HANDLERS
   ============================================ */

/**
 * Handle hexagon click - determine region and open drawer
 * @param {Object} hex - Clicked hexagon data
 */
function handleHexClick(hex) {
    if (!hex || !hex.points || hex.points.length === 0) return;

    // Get the most common country from points in this hex
    const countries = {};
    hex.points.forEach(point => {
        const country = point.country || 'Unknown';
        countries[country] = (countries[country] || 0) + 1;
    });

    const mostCommonCountry = Object.keys(countries).reduce((a, b) => 
        countries[a] > countries[b] ? a : b
    );

    console.log('🖱️ Clicked region:', mostCommonCountry);
    
    // Open region drawer (function from dashboard.js)
    if (typeof openRegionDrawer === 'function') {
        openRegionDrawer(mostCommonCountry);
    } else {
        console.warn('⚠️ openRegionDrawer function not found');
    }
}

/**
 * Fly to specific coordinates on the globe
 * @param {Number} lat - Latitude
 * @param {Number} lng - Longitude
 * @param {Number} altitude - Camera altitude (default: 2)
 */
function flyToLocation(lat, lng, altitude = 2) {
    if (!globe) return;

    globe.pointOfView(
        { lat, lng, altitude },
        1000 // Animation duration in ms
    );

    console.log(`✈️ Flying to ${lat}, ${lng}`);
}

/* ============================================
   UTILITY FUNCTIONS
   ============================================ */

/**
 * Get current globe instance
 * @returns {Object} Globe instance
 */
function getGlobe() {
    return globe;
}

/**
 * Destroy globe instance (cleanup)
 */
function destroyGlobe() {
    if (globe) {
        globe = null;
        currentMapData = [];
        console.log('🗑️ Globe destroyed');
    }
}

/* ============================================
   EXPORT FOR USE IN OTHER FILES
   ============================================ */

window.EmotionMapGlobe = {
    initGlobe,
    updateGlobeData,
    filterGlobeByEmotion,
    toggleRotation,
    flyToLocation,
    getGlobe,
    destroyGlobe
};