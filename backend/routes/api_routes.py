from flask import Blueprint, jsonify, request
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

# TEMPORARY: Mock coordinates for testing (until Geopy is implemented)
MOCK_COORDINATES = {
    'Nigeria': {'lat': 9.0820, 'lng': 8.6753},
    'USA': {'lat': 37.0902, 'lng': -95.7129},
    'United States': {'lat': 37.0902, 'lng': -95.7129},
    'UK': {'lat': 55.3781, 'lng': -3.4360},
    'United Kingdom': {'lat': 55.3781, 'lng': -3.4360},
    'France': {'lat': 46.2276, 'lng': 2.2137},
    'Germany': {'lat': 51.1657, 'lng': 10.4515},
    'Brazil': {'lat': -14.2350, 'lng': -51.9253},
    'India': {'lat': 20.5937, 'lng': 78.9629},
    'Japan': {'lat': 36.2048, 'lng': 138.2529},
    'Australia': {'lat': -25.2744, 'lng': 133.7751},
    'Canada': {'lat': 56.1304, 'lng': -106.3468},
    'South Africa': {'lat': -30.5595, 'lng': 22.9375},
    'Mexico': {'lat': 23.6345, 'lng': -102.5528},
    'China': {'lat': 35.8617, 'lng': 104.1954},
}

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
    """Get global emotion statistics - FIXED FORMAT FOR FRONTEND."""
    try:
        # Try new emotion system first
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
            
        except Exception as e:
            # Fallback to mock data if emotion stats not available
            print(f"⚠️ Emotion stats not available, using mock data: {e}")
            response = {
                'joy': 64,
                'anger': 21,
                'sadness': 10,
                'hope': 3,
                'calmness': 2
            }
        
        return jsonify(response)
    
    except Exception as e:
        # Return mock data on error
        return jsonify({
            'joy': 64,
            'anger': 21,
            'sadness': 10,
            'hope': 3,
            'calmness': 2
        })

@api_bp.route('/map-data/<zoom_level>', methods=['GET'])
def get_map_data(zoom_level):
    """Get map data for globe - FIXED FORMAT FOR FRONTEND."""
    try:
        hours = request.args.get('hours', default=24, type=int)
        
        # Try to get emotion data
        try:
            data = db.get_emotion_map_data(zoom_level, hours)
            
            # Transform to frontend format
            map_points = []
            for item in data:
                location = item['location_name']
                coords = MOCK_COORDINATES.get(location, {'lat': 0, 'lng': 0})
                
                # Get dominant emotion and its count
                emotions = {
                    'joy': item.get('joy_count', 0),
                    'anger': item.get('anger_count', 0),
                    'sadness': item.get('sadness_count', 0),
                    'hope': item.get('hope_count', 0),
                    'calmness': item.get('calmness_count', 0)
                }
                
                dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                total = sum(emotions.values()) or 1
                intensity = emotions[dominant_emotion] / total
                
                map_points.append({
                    'lat': coords['lat'],
                    'lng': coords['lng'],
                    'country': location,
                    'region': location,  # TODO: Add region when available
                    'emotion': dominant_emotion,
                    'intensity': round(intensity, 2),
                    'posts': item['total_posts']
                })
            
            return jsonify(map_points)
            
        except Exception as e:
            print(f"⚠️ Emotion data not available, using mock data: {e}")
            # Return mock data
            return jsonify([
                {'lat': 9.0820, 'lng': 8.6753, 'country': 'Nigeria', 'emotion': 'anger', 'intensity': 0.85, 'posts': 120},
                {'lat': 40.7128, 'lng': -74.0060, 'country': 'USA', 'emotion': 'joy', 'intensity': 0.80, 'posts': 340},
                {'lat': 48.8566, 'lng': 2.3522, 'country': 'France', 'emotion': 'hope', 'intensity': 0.60, 'posts': 180},
                {'lat': -23.5505, 'lng': -46.6333, 'country': 'Brazil', 'emotion': 'joy', 'intensity': 0.90, 'posts': 210},
                {'lat': 51.5074, 'lng': -0.1278, 'country': 'UK', 'emotion': 'calmness', 'intensity': 0.55, 'posts': 190},
                {'lat': 35.6762, 'lng': 139.6503, 'country': 'Japan', 'emotion': 'calmness', 'intensity': 0.70, 'posts': 150}
            ])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/location/<location_name>', methods=['GET'])
def get_location_details(location_name):
    """Get detailed information for a specific location - FIXED FORMAT."""
    try:
        details = db.get_location_details(location_name)
        
        if details:
            # Transform to frontend format
            emotions = {
                'joy': details.get('joy_count', 0),
                'anger': details.get('anger_count', 0),
                'sadness': details.get('sadness_count', 0),
                'hope': details.get('hope_count', 0),
                'calmness': details.get('calmness_count', 0)
            }
            
            total = sum(emotions.values()) or 1
            emotion_percentages = {k: round((v / total) * 100) for k, v in emotions.items()}
            
            response = {
                'country': location_name,
                'region': details.get('region', location_name),
                'emotions': emotion_percentages,
                'keywords': details.get('keywords', ['data', 'news', 'updates']),
                'posts': details.get('sample_posts', ['No posts available yet'])
            }
            
            return jsonify(response)
        else:
            # Return mock data for location
            return jsonify({
                'country': location_name,
                'region': location_name,
                'emotions': {'joy': 50, 'anger': 20, 'sadness': 15, 'hope': 10, 'calmness': 5},
                'keywords': ['news', 'updates', 'trending'],
                'posts': ['Sample post 1', 'Sample post 2']
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/search', methods=['GET'])
def search_emotions():
    """Search posts by keyword and filter by emotion."""
    try:
        query = request.args.get('q', default='')  # Changed from 'query' to 'q'
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
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trends', methods=['GET'])
def get_trends():
    """Get emotion trends over time."""
    try:
        hours = request.args.get('hours', default=24, type=int)
        
        # TODO: Implement time-series aggregation
        response = {
            'timestamps': [],
            'joy': [],
            'anger': [],
            'sadness': [],
            'hope': [],
            'calmness': [],
            'message': 'Trends endpoint - implementation pending'
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/emotions', methods=['GET'])
def get_emotion_breakdown():
    """Get detailed emotion breakdown by location."""
    try:
        location = request.args.get('location', default=None)
        
        if location:
            # Redirect to location details endpoint
            return get_location_details(location)
        else:
            # Return global stats
            return get_stats()
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500