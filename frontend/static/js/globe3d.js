/* ============================================
   MULTI-SECTOR GLOBE 3D - FIXED
   3D Globe with sector-aware emotion configs
   ============================================ */

let globe = null;

/* ============================================
   GLOBE INITIALIZATION
   ============================================ */

function initGlobe(mapData = []) {
    const container = document.getElementById('globe-container');
    
    if (!container) {
        console.error('❌ Globe container not found');
        return;
    }

    console.log('🌍 Initializing globe with', mapData.length, 'data points');
    window.currentMapData = mapData;
    
    // Initialize Globe.gl with LABELS
    globe = Globe()
        .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
        .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png')
        .backgroundImageUrl('https://unpkg.com/three-globe/example/img/night-sky.png')
        
        // LABELS
        .labelsData(mapData)
        .labelLat(d => d.lat)
        .labelLng(d => d.lng)
        .labelText(d => d.country)
        .labelSize(d => {
            const size = Math.log(d.posts + 1) * 0.5;
            return Math.max(size, 0.5);
        })
        .labelDotRadius(d => {
            return (d.intensity || 0.5) * 0.8;
        })
        .labelColor(d => {
            // SAFE: Use multi-sector emotion config
            try {
                const config = window.EmotionMapAPI.getEmotionConfig(d.emotion);
                return config ? config.color : '#94a3b8';
            } catch (e) {
                console.warn('Error getting color for', d.emotion, e);
                return '#94a3b8';
            }
        })
        .labelResolution(2)
        .labelAltitude(0.01)
        
        // POINTS
        .pointsData(mapData)
        .pointLat(d => d.lat)
        .pointLng(d => d.lng)
        .pointColor(d => {
            try {
                const config = window.EmotionMapAPI.getEmotionConfig(d.emotion);
                return config ? config.color : '#94a3b8';
            } catch (e) {
                return '#94a3b8';
            }
        })
        .pointAltitude(d => (d.intensity || 0.5) * 0.15)
        .pointRadius(d => {
            const posts = d.posts || 1;
            return Math.log(posts + 1) * 0.3;
        })
        .pointLabel(d => {
            // SAFE: Get emotion config with fallback
            let config, emoji, label, color;
            try {
                config = window.EmotionMapAPI.getEmotionConfig(d.emotion);
                emoji = config ? config.emoji : '⚪';
                label = config ? config.label : d.emotion;
                color = config ? config.color : '#94a3b8';
            } catch (e) {
                console.warn('Error getting config for', d.emotion, e);
                emoji = '⚪';
                label = d.emotion || 'Unknown';
                color = '#94a3b8';
            }
            
            const intensity = Math.round((d.intensity || 0) * 100);
            
            return `
                <div style="
                    background: rgba(0,0,0,0.9); 
                    padding: 12px 16px; 
                    border-radius: 8px; 
                    color: white; 
                    font-size: 14px;
                    font-family: 'Inter', sans-serif;
                    border: 2px solid ${color};
                    min-width: 180px;
                ">
                    <div style="font-weight: 700; margin-bottom: 8px; font-size: 16px;">
                        ${emoji} ${d.country}
                    </div>
                    <div style="color: #a0a0a0; font-size: 13px;">
                        <strong style="color: ${color};">${label}</strong><br/>
                        Intensity: ${intensity}%<br/>
                        ${d.posts.toLocaleString()} posts
                    </div>
                </div>
            `;
        })
        .onPointClick(point => {
            handleCountryClick(point);
        })
        
        // RINGS
        .ringsData(mapData.filter(d => d.posts > 10))
        .ringLat(d => d.lat)
        .ringLng(d => d.lng)
        .ringMaxRadius(d => Math.log(d.posts + 1) * 0.5)
        .ringPropagationSpeed(2)
        .ringRepeatPeriod(d => 2000 + Math.random() * 1000)
        .ringColor(d => {
            try {
                const config = window.EmotionMapAPI.getEmotionConfig(d.emotion);
                return () => config ? config.color : '#94a3b8';
            } catch (e) {
                return () => '#94a3b8';
            }
        })
        
        (container);

    setupGlobeControls();
    
    console.log('✅ Globe initialized with multi-sector support');
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

    window.currentMapData = mapData;
    
    // Update all layers
    globe.labelsData(mapData);
    globe.pointsData(mapData);
    globe.ringsData(mapData.filter(d => d.posts > 10));
    
    console.log('🔄 Globe updated with', mapData.length, 'data points');
}

function filterGlobeByEmotion(activeFilters) {
    if (!globe) return;

    let filteredData = window.currentMapData;
    
    if (activeFilters && activeFilters.length > 0) {
        filteredData = window.currentMapData.filter(point => 
            activeFilters.includes(point.emotion)
        );
        console.log('🎯 Filtered to', filteredData.length, 'countries with emotions:', activeFilters);
    } else {
        console.log('🎯 Showing all', filteredData.length, 'countries');
    }
    
    // Update all layers with filtered data
    globe.labelsData(filteredData);
    globe.pointsData(filteredData);
    globe.ringsData(filteredData.filter(d => d.posts > 10));
}

/* ============================================
   INTERACTION HANDLERS
   ============================================ */

function handleCountryClick(point) {
    if (!point) return;

    const country = point.country;
    console.log('🖱️ Clicked country:', country);
    
    // SAFE: Check if function exists
    if (typeof window.openRegionDrawer === 'function') {
        window.openRegionDrawer(country);
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
        window.currentMapData = [];
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

console.log('✅ Multi-Sector Globe3D module loaded');