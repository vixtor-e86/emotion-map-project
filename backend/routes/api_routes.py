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
        'timestamp': datetime.now().isoformat()
    })

@api_bp.route('/map-data/<zoom_level>', methods=['GET'])
def get_map_data(zoom_level):
    """Get map data for specified zoom level (UPDATED FOR 5-EMOTION SYSTEM)."""
    valid_zoom_levels = ['continent', 'country', 'city']
    
    if zoom_level not in valid_zoom_levels:
        return jsonify({'error': f'Invalid zoom level. Must be one of: {valid_zoom_levels}'}), 400
    
    try:
        hours = request.args.get('hours', default=24, type=int)
        
        # Try new emotion system first
        try:
            data = db.get_emotion_map_data(zoom_level, hours)
            
            # Format data for 3D Globe visualization
            response = {
                'locations': [item['location_name'] for item in data],
                'emotions': [item['dominant_emotion'] for item in data],
                'emotion_scores': [item['avg_emotion_score'] if item['avg_emotion_score'] else 0.5 for item in data],
                'joy_counts': [item['joy_count'] for item in data],
                'anger_counts': [item['anger_count'] for item in data],
                'sadness_counts': [item['sadness_count'] for item in data],
                'hope_counts': [item['hope_count'] for item in data],
                'calmness_counts': [item['calmness_count'] for item in data],
                'hover_text': [
                    f"{item['location_name']}: {item['dominant_emotion']} "
                    f"({item['total_posts']} posts)"
                    for item in data
                ],
                'post_counts': [item['total_posts'] for item in data],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            # Fallback to old sentiment system if emotion data not available
            print(f"⚠️ Emotion data not available, using legacy sentiment: {e}")
            data = db.get_map_data(zoom_level, hours)
            
            # Format with legacy sentiment data
            response = {
                'locations': [item['location_name'] for item in data],
                'sentiment_scores': [item['avg_sentiment_score'] if item.get('avg_sentiment_score') else 0 for item in data],
                'hover_text': [
                    f"{item['location_name']}: {item.get('dominant_sentiment', 'unknown')} "
                    f"({item['total_posts']} posts)"
                    for item in data
                ],
                'post_counts': [item['total_posts'] for item in data],
                'timestamp': datetime.now().isoformat(),
                'legacy_mode': True
            }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/location/<location_name>', methods=['GET'])
def get_location_details(location_name):
    """Get detailed information for a specific location."""
    try:
        details = db.get_location_details(location_name)
        
        if details:
            return jsonify(details)
        else:
            return jsonify({'error': 'Location not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get global emotion statistics (UPDATED FOR 5-EMOTION SYSTEM)."""
    try:
        # Try new emotion system first
        try:
            stats = db.get_emotion_stats()
            stats['last_updated'] = datetime.now().isoformat()
            stats['system'] = '5-emotion'  # Indicator that we're using new system
            
        except Exception as e:
            # Fallback to old sentiment system
            print(f"⚠️ Emotion stats not available, using legacy sentiment: {e}")
            stats = db.get_global_stats()
            stats['last_updated'] = datetime.now().isoformat()
            stats['system'] = 'legacy-sentiment'
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/emotions', methods=['GET'])
def get_emotion_breakdown():
    """Get detailed emotion breakdown by location (NEW ENDPOINT)."""
    try:
        location = request.args.get('location', default=None)
        hours = request.args.get('hours', default=24, type=int)
        
        if location:
            # Get emotion breakdown for specific location
            details = db.get_location_details(location)
            if not details:
                return jsonify({'error': 'Location not found'}), 404
            
            response = {
                'location': location,
                'emotions': {
                    'joy': details.get('joy_count', 0),
                    'anger': details.get('anger_count', 0),
                    'sadness': details.get('sadness_count', 0),
                    'hope': details.get('hope_count', 0),
                    'calmness': details.get('calmness_count', 0)
                },
                'dominant': details.get('dominant_emotion', 'unknown'),
                'total_posts': details.get('total_posts', 0)
            }
        else:
            # Get global emotion breakdown
            stats = db.get_emotion_stats()
            response = {
                'location': 'Global',
                'emotions': {
                    'joy': f"{stats.get('joy_percentage', 0)}%",
                    'anger': f"{stats.get('anger_percentage', 0)}%",
                    'sadness': f"{stats.get('sadness_percentage', 0)}%",
                    'hope': f"{stats.get('hope_percentage', 0)}%",
                    'calmness': f"{stats.get('calmness_percentage', 0)}%"
                },
                'dominant': stats.get('dominant_emotion', 'none'),
                'total_posts': stats.get('total_posts', 0)
            }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trends', methods=['GET'])
def get_trends():
    """Get emotion trends over time (UPDATED FOR 5-EMOTION SYSTEM)."""
    try:
        hours = request.args.get('hours', default=24, type=int)
        emotion = request.args.get('emotion', default=None)  # Filter by specific emotion
        
        # TODO: Implement time-series aggregation with emotions
        # For now, return placeholder with proper structure
        response = {
            'timestamps': [],
            'emotion_data': {
                'joy': [],
                'anger': [],
                'sadness': [],
                'hope': [],
                'calmness': []
            },
            'post_counts': [],
            'hours': hours,
            'filtered_emotion': emotion,
            'message': 'Trends endpoint - implementation pending (emotion system ready)'
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/search', methods=['GET'])
def search_emotions():
    """Search posts by keyword and filter by emotion (NEW ENDPOINT)."""
    try:
        query = request.args.get('query', default='')
        emotion_filter = request.args.get('emotion', default=None)
        limit = request.args.get('limit', default=50, type=int)
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
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