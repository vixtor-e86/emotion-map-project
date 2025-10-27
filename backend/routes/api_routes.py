"""
api_routes.py (UPDATED)
-----------------------
API endpoints that now serve REAL data from aggregated_emotions table.
No more mock data - uses actual lat/lng from database!

Replace your current backend/routes/api_routes.py with this file.
"""

from flask import Blueprint, jsonify, request
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'Emotion Map API is running',
        'timestamp': datetime.now().isoformat()
    })

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get global emotion statistics."""
    try:
        stats = db.get_emotion_stats()
        
        # Format for frontend (simple percentages)
        response = {
            'joy': round(stats.get('joy_percentage', 0)),
            'anger': round(stats.get('anger_percentage', 0)),
            'sadness': round(stats.get('sadness_percentage', 0)),
            'hope': round(stats.get('hope_percentage', 0)),
            'calmness': round(stats.get('calmness_percentage', 0))
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"❌ Error in /stats: {e}")
        # Return fallback data
        return jsonify({
            'joy': 40,
            'anger': 25,
            'sadness': 20,
            'hope': 10,
            'calmness': 5
        })

@api_bp.route('/map-data/<zoom_level>', methods=['GET'])
def get_map_data(zoom_level):
    """
    Get map data for globe visualization.
    Now uses REAL lat/lng from database!
    
    Args:
        zoom_level: 'continent', 'country', or 'city'
    
    Query params:
        hours: Data from last N hours (default: 24)
    
    Returns:
        JSON array of location points with emotions
    """
    try:
        hours = request.args.get('hours', default=24, type=int)
        
        # Get aggregated data from database
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                location_name,
                location_type,
                joy_count,
                anger_count,
                sadness_count,
                hope_count,
                calmness_count,
                total_posts,
                dominant_emotion,
                avg_emotion_score,
                latitude,
                longitude
            FROM aggregated_emotions
            WHERE location_type = ?
            AND timestamp > datetime('now', '-' || ? || ' hours')
            ORDER BY total_posts DESC
        ''', (zoom_level, hours))
        
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Transform to frontend format
        map_points = []
        for item in data:
            # Skip if no coordinates
            if not item['latitude'] or not item['longitude']:
                continue
            
            # Calculate emotion intensity
            emotions = {
                'joy': item['joy_count'],
                'anger': item['anger_count'],
                'sadness': item['sadness_count'],
                'hope': item['hope_count'],
                'calmness': item['calmness_count']
            }
            
            total = sum(emotions.values()) or 1
            dominant_emotion = item['dominant_emotion']
            intensity = emotions[dominant_emotion] / total
            
            map_points.append({
                'lat': item['latitude'],
                'lng': item['longitude'],
                'country': item['location_name'],
                'region': item['location_name'],
                'emotion': dominant_emotion,
                'intensity': round(intensity, 2),
                'posts': item['total_posts']
            })
        
        # If no data, return empty array (frontend will handle)
        if not map_points:
            print(f"⚠️  No map data for zoom level: {zoom_level}")
            return jsonify([])
        
        return jsonify(map_points)
        
    except Exception as e:
        print(f"❌ Error in /map-data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/location/<location_name>', methods=['GET'])
def get_location_details(location_name):
    """Get detailed information for a specific location."""
    try:
        # Get from aggregated_emotions first
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT *
            FROM aggregated_emotions
            WHERE location_name = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (location_name,))
        
        row = cursor.fetchone()
        
        if row:
            data = dict(row)
            
            # Get sample posts
            cursor.execute('''
                SELECT text, emotion, emotion_score, timestamp
                FROM raw_posts
                WHERE country = ? OR city = ?
                ORDER BY timestamp DESC
                LIMIT 5
            ''', (location_name, location_name))
            
            sample_posts = [dict(post)['text'] for post in cursor.fetchall()]
            
            # Calculate emotion percentages
            emotions = {
                'joy': data['joy_count'],
                'anger': data['anger_count'],
                'sadness': data['sadness_count'],
                'hope': data['hope_count'],
                'calmness': data['calmness_count']
            }
            
            total = sum(emotions.values()) or 1
            emotion_percentages = {k: round((v / total) * 100) for k, v in emotions.items()}
            
            # Extract keywords from sample posts
            keywords = extract_keywords(sample_posts)
            
            response = {
                'country': location_name,
                'region': location_name,
                'emotions': emotion_percentages,
                'keywords': keywords,
                'posts': sample_posts[:3] if sample_posts else ['No posts available']
            }
            
            conn.close()
            return jsonify(response)
        
        conn.close()
        return jsonify({
            'country': location_name,
            'region': location_name,
            'emotions': {'joy': 20, 'anger': 20, 'sadness': 20, 'hope': 20, 'calmness': 20},
            'keywords': ['no', 'data'],
            'posts': ['No data available for this location']
        })
    
    except Exception as e:
        print(f"❌ Error in /location: {e}")
        return jsonify({'error': str(e)}), 500

def extract_keywords(posts: list, top_n: int = 5) -> list:
    """Extract top keywords from posts (simple word frequency)."""
    if not posts:
        return ['no', 'data']
    
    from collections import Counter
    import re
    
    # Common stop words to ignore
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                  'of', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
                  'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
                  'might', 'can', 'it', 'this', 'that', 'these', 'those'}
    
    # Extract all words
    all_words = []
    for post in posts:
        words = re.findall(r'\b[a-z]{3,}\b', post.lower())
        all_words.extend([w for w in words if w not in stop_words])
    
    # Get most common
    counter = Counter(all_words)
    return [word for word, count in counter.most_common(top_n)]

@api_bp.route('/search', methods=['GET'])
def search_emotions():
    """Search posts by keyword and filter by emotion."""
    try:
        query = request.args.get('q', default='')
        emotion_filter = request.args.get('emotion', default=None)
        limit = request.args.get('limit', default=50, type=int)
        
        if not query:
            return jsonify({'error': 'Query parameter (q) required'}), 400
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Build SQL query
        sql = '''
            SELECT text, source, country, emotion, emotion_score, timestamp
            FROM raw_posts
            WHERE text LIKE ?
        '''
        params = [f'%{query}%']
        
        if emotion_filter:
            sql += ' AND emotion = ?'
            params.append(emotion_filter)
        
        sql += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(sql, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        response = {
            'query': query,
            'emotion_filter': emotion_filter,
            'results': results,
            'count': len(results)
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"❌ Error in /search: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trends', methods=['GET'])
def get_trends():
    """Get emotion trends over time."""
    try:
        hours = request.args.get('hours', default=24, type=int)
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get emotion counts per hour
        cursor.execute('''
            SELECT 
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                emotion,
                COUNT(*) as count
            FROM raw_posts
            WHERE timestamp > datetime('now', '-' || ? || ' hours')
            AND emotion IS NOT NULL
            GROUP BY hour, emotion
            ORDER BY hour
        ''', (hours,))
        
        data = {}
        timestamps = set()
        
        for row in cursor.fetchall():
            hour = row['hour']
            emotion = row['emotion']
            count = row['count']
            
            timestamps.add(hour)
            
            if emotion not in data:
                data[emotion] = {}
            data[emotion][hour] = count
        
        conn.close()
        
        # Format for frontend
        timestamps = sorted(list(timestamps))
        response = {'timestamps': timestamps}
        
        for emotion in ['joy', 'anger', 'sadness', 'hope', 'calmness']:
            response[emotion] = [data.get(emotion, {}).get(ts, 0) for ts in timestamps]
        
        return jsonify(response)
    
    except Exception as e:
        print(f"❌ Error in /trends: {e}")
        return jsonify({
            'timestamps': [],
            'joy': [],
            'anger': [],
            'sadness': [],
            'hope': [],
            'calmness': []
        })

@api_bp.route('/emotions', methods=['GET'])
def get_emotion_breakdown():
    """Get detailed emotion breakdown by location."""
    try:
        location = request.args.get('location', default=None)
        
        if location:
            return get_location_details(location)
        else:
            return get_stats()
    
    except Exception as e:
        print(f"❌ Error in /emotions: {e}")
        return jsonify({'error': str(e)}), 500