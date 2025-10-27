/* ============================================
   EMOTION MAP - 3D GLOBE WITH LABELS
   No external dependencies - works offline!
   ============================================ */

let globe = null;
let currentMapData = [];

/* ============================================
   GLOBE INITIALIZATION
   ============================================ */

/**
 * Initialize the 3D globe with emotion labels
 * @param {Array} mapData - Array of emotion data points from API
 */
function initGlobe(mapData = []) {
    const container = document.getElementById('globe-container');
    
    if (!container) {
        console.error('❌ Globe container not found');
        return;
    }

    console.log('🌍 Initializing globe with', mapData.length, 'data points');
    currentMapData = mapData;
    
    // Get emotion config
    const EMOTION_CONFIG = window.EmotionMapAPI.EMOTION_CONFIG;
    
    // Initialize Globe.gl with LABELS - Simple and reliable!
    globe = Globe()
        // Globe textures
        .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
        .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png')
        .backgroundImageUrl('https://unpkg.com/three-globe/example/img/night-sky.png')
        
        // LABELS - Show country names with colored backgrounds
        .labelsData(currentMapData)
        .labelLat(d => d.lat)
        .labelLng(d => d.lng)
        .labelText(d => d.country)
        .labelSize(d => {
            // Size based on post count
            const size = Math.log(d.posts + 1) * 0.5;
            return Math.max(size, 0.5);
        })
        .labelDotRadius(d => {
            // Dot size based on intensity
            return (d.intensity || 0.5) * 0.8;
        })
        .labelColor(d => {
            const config = EMOTION_CONFIG[d.emotion];
            return config ? config.color : '#00A8FF';
        })
        .labelResolution(2)
        .labelAltitude(0.01)
        
        // POINTS - Colored dots for each country
        .pointsData(currentMapData)
        .pointLat(d => d.lat)
        .pointLng(d => d.lng)
        .pointColor(d => {
            const config = EMOTION_CONFIG[d.emotion];
            return config ? config.color : '#00A8FF';
        })
        .pointAltitude(d => (d.intensity || 0.5) * 0.15)
        .pointRadius(d => {
            const posts = d.posts || 1;
            return Math.log(posts + 1) * 0.3;
        })
        .pointLabel(d => {
            const config = EMOTION_CONFIG[d.emotion];
            const intensity = Math.round((d.intensity || 0) * 100);
            
            return `
                <div style="
                    background: rgba(0,0,0,0.9); 
                    padding: 12px 16px; 
                    border-radius: 8px; 
                    color: white; 
                    font-size: 14px;
                    font-family: 'Inter', sans-serif;
                    border: 2px solid ${config ? config.color : '#00A8FF'};
                    min-width: 180px;
                ">
                    <div style="font-weight: 700; margin-bottom: 8px; font-size: 16px;">
                        ${config ? config.emoji : '🌍'} ${d.country}
                    </div>
                    <div style="color: #a0a0a0; font-size: 13px;">
                        <strong style="color: ${config ? config.color : '#00A8FF'};">${config ? config.label : 'Unknown'}</strong><br/>
                        Intensity: ${intensity}%<br/>
                        ${d.posts.toLocaleString()} posts
                    </div>
                </div>
            `;
        })
        .onPointClick(point => {
            handleCountryClick(point);
        })
        
        // RINGS - Add pulsing rings around high-activity countries
        .ringsData(currentMapData.filter(d => d.posts > 100))
        .ringLat(d => d.lat)
        .ringLng(d => d.lng)
        .ringMaxRadius(d => Math.log(d.posts + 1) * 0.5)
        .ringPropagationSpeed(2)
        .ringRepeatPeriod(d => 2000 + Math.random() * 1000)
        .ringColor(d => {
            const config = EMOTION_CONFIG[d.emotion];
            return () => config ? config.color : '#00A8FF';
        })
        
        (container);

    // Globe controls configuration
    setupGlobeControls();
    
    console.log('✅ Globe initialized with labels and points (no external files needed!)');
}

/* ============================================
   GLOBE CONTROLS
   ============================================ */

function setupGlobeControls() {
    if (!globe) return;

    globe.controls().autoRotate = true;
    globe.controls().autoRotateSpeed = 0.3;
    
    globe.controls().addEventListener('start', () => {
        globe.controls().autoRotate = false;
    });
    
    let rotationTimeout;
    globe.controls().addEventListener('end', () => {
        clearTimeout(rotationTimeout);
        rotationTimeout = setTimeout(() => {
            globe.controls().autoRotate = true;
        }, 3000);
    });

    globe.controls().enableZoom = true;
    globe.controls().minDistance = 200;
    globe.controls().maxDistance = 800;
}

function toggleRotation() {
    if (!globe) return;
    globe.controls().autoRotate = !globe.controls().autoRotate;
    console.log('🔄 Auto-rotation:', globe.controls().autoRotate ? 'ON' : 'OFF');
}

/* ============================================
   DATA UPDATE FUNCTIONS
   ============================================ */

function updateGlobeData(mapData) {
    if (!globe) {
        console.warn('⚠️ Globe not initialized, initializing now...');
        initGlobe(mapData);
        return;
    }

    currentMapData = mapData;
    
    // Update all layers
    globe.labelsData(mapData);
    globe.pointsData(mapData);
    globe.ringsData(mapData.filter(d => d.posts > 100));
    
    console.log('🔄 Globe updated with', mapData.length, 'data points');
}

function filterGlobeByEmotion(activeFilters) {
    if (!globe) return;

    let filteredData = currentMapData;
    
    if (activeFilters && activeFilters.length > 0) {
        filteredData = currentMapData.filter(point => 
            activeFilters.includes(point.emotion)
        );
        console.log('🎯 Filtered to', filteredData.length, 'countries with emotions:', activeFilters);
    } else {
        console.log('🎯 Showing all', filteredData.length, 'countries');
    }
    
    // Update all layers with filtered data
    globe.labelsData(filteredData);
    globe.pointsData(filteredData);
    globe.ringsData(filteredData.filter(d => d.posts > 100));
}

/* ============================================
   INTERACTION HANDLERS
   ============================================ */

function handleCountryClick(point) {
    if (!point) return;

    const country = point.country;
    console.log('🖱️ Clicked country:', country);
    
    if (typeof openRegionDrawer === 'function') {
        openRegionDrawer(country);
    } else {
        console.warn('⚠️ openRegionDrawer function not found');
    }
}

function flyToLocation(lat, lng, altitude = 2) {
    if (!globe) return;
    globe.pointOfView({ lat, lng, altitude }, 1000);
    console.log(`✈️ Flying to ${lat}, ${lng}`);
}

/* ============================================
   UTILITY FUNCTIONS
   ============================================ */

function getGlobe() {
    return globe;
}

function destroyGlobe() {
    if (globe) {
        globe = null;
        currentMapData = [];
        console.log('🗑️ Globe destroyed');
    }
}

/* ============================================
   EXPORT
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

console.log('✅ Globe3D module loaded (Labels + Points + Rings)');