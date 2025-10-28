"""
aggregator.py
-------------
Aggregates emotion data by location and geocodes ONCE per location.
Creates data for the 3D globe visualization with zoom levels:
- continent: 6 points (Africa, Asia, Europe, etc.)
- country: 40+ points (Nigeria, USA, France, etc.)
- city: 100+ points (Lagos, New York, Paris, etc.)

FIXED: Now properly handles database updates (no duplicate rows!)

Usage:
    python backend/processing/aggregator.py
"""

import sys
import os
from datetime import datetime
import time
from collections import defaultdict

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut
    from database.db_manager import db
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Install with: pip install geopy")
    sys.exit(1)

# Initialize geolocator (used for geocoding)
geolocator = Nominatim(user_agent="pulsenet_emotion_aggregator")

# Cache for geocoded locations (to avoid repeat API calls)
geocode_cache = {}

def get_coordinates(location_name: str, max_retries: int = 3):
    """
    Get lat/lng coordinates for a location (with caching).
    
    Args:
        location_name: Name of location (country or city)
        max_retries: Number of retry attempts
    
    Returns:
        tuple: (latitude, longitude) or (None, None)
    """
    if not location_name:
        return None, None
    
    # Check cache first
    if location_name in geocode_cache:
        return geocode_cache[location_name]
    
    # Rate limiting (1.2 second delay per Geopy terms)
    time.sleep(1.2)
    
    for attempt in range(max_retries):
        try:
            location = geolocator.geocode(location_name, timeout=10)
            if location:
                coords = (location.latitude, location.longitude)
                geocode_cache[location_name] = coords
                return coords
            else:
                geocode_cache[location_name] = (None, None)
                return None, None
                
        except GeocoderTimedOut:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            geocode_cache[location_name] = (None, None)
            return None, None
            
        except Exception as e:
            print(f"   ⚠️  Error geocoding {location_name}: {e}")
            geocode_cache[location_name] = (None, None)
            return None, None
    
    return None, None

def aggregate_by_location(zoom_level: str = 'country'):
    """
    Aggregate posts by location and calculate emotion statistics.
    
    Args:
        zoom_level: 'continent', 'country', or 'city'
    
    Returns:
        dict: {location_name: {emotion_counts, total, dominant, avg_score, lat, lng}}
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Determine grouping column based on zoom level
    if zoom_level == 'continent':
        group_column = 'continent'
    elif zoom_level == 'city':
        group_column = 'city'
    else:  # country (default)
        group_column = 'country'
    
    # Query to get emotion counts by location
    cursor.execute(f'''
        SELECT 
            {group_column} as location,
            emotion,
            COUNT(*) as count,
            AVG(emotion_score) as avg_score
        FROM raw_posts
        WHERE {group_column} IS NOT NULL
        AND emotion IS NOT NULL
        AND timestamp > datetime('now', '-24 hours')
        GROUP BY {group_column}, emotion
    ''')
    
    # Build aggregation dictionary
    aggregated = defaultdict(lambda: {
        'joy_count': 0,
        'anger_count': 0,
        'sadness_count': 0,
        'hope_count': 0,
        'calmness_count': 0,
        'total_posts': 0,
        'emotion_scores': []
    })
    
    for row in cursor.fetchall():
        location = row['location']
        emotion = row['emotion']
        count = row['count']
        avg_score = row['avg_score']
        
        # Add counts
        aggregated[location][f'{emotion}_count'] = count
        aggregated[location]['total_posts'] += count
        aggregated[location]['emotion_scores'].append(avg_score)
    
    conn.close()
    
    # Calculate dominant emotion and average score
    for location, data in aggregated.items():
        emotion_counts = {
            'joy': data['joy_count'],
            'anger': data['anger_count'],
            'sadness': data['sadness_count'],
            'hope': data['hope_count'],
            'calmness': data['calmness_count']
        }
        
        # Dominant emotion
        data['dominant_emotion'] = max(emotion_counts.items(), key=lambda x: x[1])[0]
        
        # Average emotion score
        scores = data['emotion_scores']
        data['avg_emotion_score'] = sum(scores) / len(scores) if scores else 0.5
        
        # Remove temporary field
        del data['emotion_scores']
    
    return dict(aggregated)

def clear_old_aggregated_data(zoom_level: str = None):
    """
    Delete old aggregated data (either all or for specific zoom level).
    
    Args:
        zoom_level: If provided, only delete that zoom level. Otherwise delete all.
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    
    if zoom_level:
        cursor.execute('DELETE FROM aggregated_emotions WHERE location_type = ?', (zoom_level,))
        print(f"   🗑️  Cleared old {zoom_level} data")
    else:
        cursor.execute('DELETE FROM aggregated_emotions')
        print(f"   🗑️  Cleared all old aggregated data")
    
    conn.commit()
    conn.close()

def save_aggregated_data(zoom_level: str, aggregated: dict, silent: bool = False):
    """
    Save aggregated data to database with geocoding.
    Uses INSERT OR REPLACE to avoid duplicates.
    
    Args:
        zoom_level: 'continent', 'country', or 'city'
        aggregated: Dictionary of aggregated data
        silent: If True, minimal output
    """
    if not silent:
        print(f"\n📍 Geocoding {len(aggregated)} locations...")
        print("-"*70)
    
    geocoded = 0
    failed = 0
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    for location_name, data in aggregated.items():
        try:
            # Geocode location
            lat, lng = get_coordinates(location_name)
            
            if lat and lng:
                geocoded += 1
                status = "✓"
            else:
                failed += 1
                status = "✗"
                lat, lng = 0.0, 0.0  # Fallback coordinates
            
            if not silent:
                print(f"   {status} {location_name:30s} → ({lat:8.4f}, {lng:8.4f})")
            
            # ✅ FIX: Use INSERT OR REPLACE to avoid duplicates
            # This will update if (location_name, location_type) already exists
            cursor.execute('''
                INSERT OR REPLACE INTO aggregated_emotions 
                (location_name, location_type, joy_count, anger_count, 
                 sadness_count, hope_count, calmness_count, total_posts,
                 dominant_emotion, avg_emotion_score, latitude, longitude, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                location_name,
                zoom_level,
                data['joy_count'],
                data['anger_count'],
                data['sadness_count'],
                data['hope_count'],
                data['calmness_count'],
                data['total_posts'],
                data['dominant_emotion'],
                data['avg_emotion_score'],
                lat,
                lng
            ))
            
        except Exception as e:
            if not silent:
                print(f"   ❌ Error saving {location_name}: {e}")
            failed += 1
            continue
    
    conn.commit()
    conn.close()
    
    if not silent:
        print("-"*70)
        print(f"   Successfully geocoded: {geocoded}/{len(aggregated)}")
        print(f"   Failed to geocode: {failed}/{len(aggregated)}")

def process_all_zoom_levels(silent: bool = False, clear_before: bool = True):
    """
    Process aggregation for all zoom levels.
    
    Args:
        silent: If True, minimal output (for background tasks)
        clear_before: If True, delete old data before inserting new (default: True)
    """
    
    if not silent:
        print("\n" + "="*60)
        print("DATA AGGREGATOR")
        print("="*60)
    
    # ✅ OPTION 1: Clear all old data before processing (clean slate)
    if clear_before:
        if not silent:
            print("\n🗑️  Clearing old aggregated data...")
        clear_old_aggregated_data()  # Delete everything
    
    zoom_levels = ['continent', 'country', 'city']
    start_time = datetime.now()
    
    for zoom in zoom_levels:
        if not silent:
            print(f"\nProcessing {zoom}...")
        
        # ✅ OPTION 2: Clear only this zoom level's data (if not clearing all)
        # Uncomment this if you want per-zoom-level clearing instead:
        # if not clear_before:
        #     clear_old_aggregated_data(zoom)
        
        # Aggregate data
        aggregated = aggregate_by_location(zoom)
        
        if not aggregated:
            if not silent:
                print(f"  No data for {zoom}")
            continue
        
        if not silent:
            print(f"  Found {len(aggregated)} locations")
        
        # Save to database (with geocoding)
        save_aggregated_data(zoom, aggregated, silent)
        
        if not silent:
            print(f"  ✓ {zoom.capitalize()} complete")
    
    # Final statistics
    elapsed = (datetime.now() - start_time).total_seconds()
    
    if not silent:
        print(f"\n✓ Aggregation complete in {elapsed:.1f}s")
        print("="*60)
    
    return True

if __name__ == '__main__':
    try:
        # You can control the behavior here:
        # clear_before=True  → Deletes ALL old data before processing (RECOMMENDED)
        # clear_before=False → Uses INSERT OR REPLACE (updates existing rows)
        process_all_zoom_levels(clear_before=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()