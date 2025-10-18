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
    """Get map data for specified zoom level."""
    valid_zoom_levels = ['continent', 'country', 'city']
    
    if zoom_level not in valid_zoom_levels:
        return jsonify({'error': f'Invalid zoom level. Must be one of: {valid_zoom_levels}'}), 400
    
    try:
        hours = request.args.get('hours', default=24, type=int)
        data = db.get_map_data(zoom_level, hours)
        
        # Format data for Plotly
        response = {
            'locations': [item['location_name'] for item in data],
            'sentiment_scores': [item['avg_sentiment_score'] for item in data],
            'hover_text': [
                f"{item['location_name']}: {item['dominant_sentiment']} "
                f"({item['total_posts']} posts)"
                for item in data
            ],
            'post_counts': [item['total_posts'] for item in data],
            'timestamp': datetime.now().isoformat()
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
    """Get global statistics."""
    try:
        stats = db.get_global_stats()
        stats['last_updated'] = datetime.now().isoformat()
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trends', methods=['GET'])
def get_trends():
    """Get sentiment trends over time."""
    try:
        hours = request.args.get('hours', default=24, type=int)
        
        # TODO: Implement time-series aggregation
        # For now, return placeholder
        response = {
            'timestamps': [],
            'sentiment_scores': [],
            'post_counts': [],
            'message': 'Trends endpoint - implementation pending'
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500