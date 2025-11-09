"""
api_routes.py (MULTI-SECTOR EDITION)
-------------------------------------
API endpoints with SECTOR FILTERING support.
All endpoints accept optional '?sector=finance' parameter.
"""

from flask import Blueprint, jsonify, request
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import db
from processing.sector_config import get_sector_info, get_emotion_config, SECTORS

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'Multi-Sector Emotion Map API is running',
        'sectors': list(SECTORS.keys()),
        'timestamp': datetime.now().isoformat()
    })

@api_bp.route('/sectors', methods=['GET'])
def get_sectors():
    """
    Get list of all available sectors with post counts.
    
    Returns:
        JSON array of sectors with metadata
    """
    try:
        sectors = db.get_all_sectors()
        
        # Add sector info
        result = []
        for sector_data in sectors:
            sector_name = sector_data['sector']
            info = get_sector_info(sector_name)
            result.append({
                'id': sector_name,
                'name': info['name'],
                'icon': info['icon'],
                'color': info['color'],
                'description': info['description'],
                'post_count': sector_data['count']
            })
        
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Error in /sectors: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get emotion statistics.
    
    Query params:
        sector: Optional sector filter (finance, health, technology, sports)
    
    Returns:
        JSON with emotion percentages
    """
    try:
        sector = request.args.get('sector', default=None, type=str)
        
        # Validate sector
        if sector and sector not in SECTORS:
            return jsonify({'error': f'Invalid sector: {sector}'}), 400
        
        stats = db.get_emotion_stats(sector=sector)
        
        # Format for frontend
        response = {
            'joy': round(stats.get('joy', 0)),
            'anger': round(stats.get('anger', 0)),
            'sadness': round(stats.get('sadness', 0)),
            'hope': round(stats.get('hope', 0)),
            'calmness': round(stats.get('calmness', 0)),
            'total_posts': stats.get('total_posts', 0),
            'sector': sector or 'all'
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"❌ Error in /stats: {e}")
        return jsonify({
            'joy': 20, 'anger': 20, 'sadness': 20,
            'hope': 20, 'calmness': 20, 'total_posts': 0,
            'sector': sector or 'all'
        })

@api_bp.route('/map-data/<zoom_level>', methods=['GET'])
def get_map_data(zoom_level):
    """
    Get map data for globe visualization with SECTOR FILTERING.
    
    Args:
        zoom_level: 'continent', 'country', or 'city'
    
    Query params:
        sector: Optional sector filter
        hours: Data from last N hours (default: 24)
    
    Returns:
        JSON array of location points with emotions
    """
    try:
        sector = request.args.get('sector', default=None, type=str)
        hours = request.args.get('hours', default=24, type=int)
        
        # Validate sector
        if sector and sector not in SECTORS:
            return jsonify({'error': f'Invalid sector: {sector}'}), 400
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Build SQL query with optional sector filter
        sql = '''
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
                longitude,
                sector
            FROM aggregated_emotions
            WHERE location_type = ?
            AND timestamp > datetime('now', '-' || ? || ' hours')
        '''
        params = [zoom_level, hours]
        
        if sector:
            sql += ' AND sector = ?'
            params.append(sector)
        
        sql += ' ORDER BY total_posts DESC'
        
        cursor.execute(sql, params)
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Transform to frontend format
        map_points = []
        for item in data:
            if not item['latitude'] or not item['longitude']:
                continue
            
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
            
            # Get sector-specific emotion config
            emotion_config = get_emotion_config(item['sector'], dominant_emotion)
            
            map_points.append({
                'lat': item['latitude'],
                'lng': item['longitude'],
                'country': item['location_name'],
                'region': item['location_name'],
                'emotion': dominant_emotion,
                'emotion_label': emotion_config.get('label', dominant_emotion),
                'emotion_emoji': emotion_config.get('emoji', '⚪'),
                'intensity': round(intensity, 2),
                'posts': item['total_posts'],
                'sector': item['sector']
            })
        
        return jsonify(map_points)
        
    except Exception as e:
        print(f"❌ Error in /map-data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/location/<location_name>', methods=['GET'])
def get_location_details(location_name):
    """
    Get detailed information for a specific location.
    
    Query params:
        sector: Optional sector filter
    """
    try:
        sector = request.args.get('sector', default=None, type=str)
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get aggregated data
        sql = '''
            SELECT *
            FROM aggregated_emotions
            WHERE location_name = ?
        '''
        params = [location_name]
        
        if sector:
            sql += ' AND sector = ?'
            params.append(sector)
        
        sql += ' ORDER BY timestamp DESC LIMIT 1'
        
        cursor.execute(sql, params)
        row = cursor.fetchone()
        
        if row:
            data = dict(row)
            
            # Get sample posts
            posts_sql = '''
                SELECT text, emotion, emotion_score, timestamp
                FROM raw_posts
                WHERE country = ? OR city = ?
            '''
            posts_params = [location_name, location_name]
            
            if sector:
                posts_sql += ' AND sector = ?'
                posts_params.append(sector)
            
            posts_sql += ' ORDER BY timestamp DESC LIMIT 5'
            
            cursor.execute(posts_sql, posts_params)
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
            
            # Extract keywords
            keywords = extract_keywords(sample_posts)
            
            response = {
                'country': location_name,
                'region': location_name,
                'emotions': emotion_percentages,
                'keywords': keywords,
                'posts': sample_posts[:3] if sample_posts else ['No posts available'],
                'sector': data.get('sector', 'general')
            }
            
            conn.close()
            return jsonify(response)
        
        conn.close()
        return jsonify({
            'country': location_name,
            'region': location_name,
            'emotions': {'joy': 20, 'anger': 20, 'sadness': 20, 'hope': 20, 'calmness': 20},
            'keywords': ['no', 'data'],
            'posts': ['No data available for this location'],
            'sector': sector or 'general'
        })
    
    except Exception as e:
        print(f"❌ Error in /location: {e}")
        return jsonify({'error': str(e)}), 500

def extract_keywords(posts: list, top_n: int = 5) -> list:
    """Extract top keywords from posts"""
    if not posts:
        return ['no', 'data']
    
    from collections import Counter
    import re
    
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                  'of', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
                  'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
                  'might', 'can', 'it', 'this', 'that', 'these', 'those'}
    
    all_words = []
    for post in posts:
        words = re.findall(r'\b[a-z]{3,}\b', post.lower())
        all_words.extend([w for w in words if w not in stop_words])
    
    counter = Counter(all_words)
    return [word for word, count in counter.most_common(top_n)]

@api_bp.route('/search', methods=['GET'])
def search_emotions():
    """
    Search posts by keyword with optional sector and emotion filter.
    
    Query params:
        q: Search query (required)
        sector: Optional sector filter
        emotion: Optional emotion filter
        limit: Max results (default: 50)
    """
    try:
        query = request.args.get('q', default='')
        sector = request.args.get('sector', default=None, type=str)
        emotion_filter = request.args.get('emotion', default=None)
        limit = request.args.get('limit', default=50, type=int)
        
        if not query:
            return jsonify({'error': 'Query parameter (q) required'}), 400
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        sql = 'SELECT text, source, country, emotion, emotion_score, sector, timestamp FROM raw_posts WHERE text LIKE ?'
        params = [f'%{query}%']
        
        if sector:
            sql += ' AND sector = ?'
            params.append(sector)
        
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
            'sector': sector,
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
    """
    Get emotion trends over time with optional sector filter.
    
    Query params:
        hours: Time window (default: 24)
        sector: Optional sector filter
    """
    try:
        hours = request.args.get('hours', default=24, type=int)
        sector = request.args.get('sector', default=None, type=str)
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        sql = '''
            SELECT 
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                emotion,
                COUNT(*) as count
            FROM raw_posts
            WHERE timestamp > datetime('now', '-' || ? || ' hours')
            AND emotion IS NOT NULL
        '''
        params = [hours]
        
        if sector:
            sql += ' AND sector = ?'
            params.append(sector)
        
        sql += ' GROUP BY hour, emotion ORDER BY hour'
        
        cursor.execute(sql, params)
        
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
        
        timestamps = sorted(list(timestamps))
        response = {'timestamps': timestamps, 'sector': sector}
        
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
            'calmness': [],
            'sector': sector
        })

@api_bp.route('/database-stats', methods=['GET'])
def get_database_stats():
    """Get overall database statistics"""
    try:
        stats = db.get_database_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500