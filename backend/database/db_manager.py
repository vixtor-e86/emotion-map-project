import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class DatabaseManager:
    """Handles all database operations."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
    
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def insert_raw_post(self, text: str, source: str, city: str = None, 
                       country: str = None, continent: str = None,
                       sentiment: str = None, sentiment_score: float = None):
        """Insert a raw post into the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO raw_posts 
            (text, source, city, country, continent, sentiment, sentiment_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (text, source, city, country, continent, sentiment, sentiment_score))
        
        conn.commit()
        post_id = cursor.lastrowid
        conn.close()
        
        return post_id
    
    def insert_aggregated_data(self, location_name: str, location_type: str,
                              positive_count: int, negative_count: int,
                              neutral_count: int, dominant_sentiment: str,
                              avg_sentiment_score: float):
        """Insert aggregated sentiment data."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        total_posts = positive_count + negative_count + neutral_count
        
        cursor.execute('''
            INSERT INTO aggregated_sentiment 
            (location_name, location_type, positive_count, negative_count,
             neutral_count, total_posts, dominant_sentiment, avg_sentiment_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (location_name, location_type, positive_count, negative_count,
              neutral_count, total_posts, dominant_sentiment, avg_sentiment_score))
        
        conn.commit()
        conn.close()
    
    def get_map_data(self, zoom_level: str = 'country', hours: int = 24) -> List[Dict]:
        """Get aggregated data for map visualization."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        time_threshold = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT 
                location_name,
                location_type,
                positive_count,
                negative_count,
                neutral_count,
                total_posts,
                dominant_sentiment,
                avg_sentiment_score,
                timestamp
            FROM aggregated_sentiment
            WHERE location_type = ? AND timestamp > ?
            ORDER BY timestamp DESC
        ''', (zoom_level, time_threshold))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_location_details(self, location_name: str) -> Optional[Dict]:
        """Get detailed information for a specific location."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT *
            FROM aggregated_sentiment
            WHERE location_name = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (location_name,))
        
        row = cursor.fetchone()
        
        if row:
            # Get sample posts
            cursor.execute('''
                SELECT text, sentiment, sentiment_score, timestamp
                FROM raw_posts
                WHERE country = ? OR city = ?
                ORDER BY timestamp DESC
                LIMIT 5
            ''', (location_name, location_name))
            
            sample_posts = [dict(post) for post in cursor.fetchall()]
            
            result = dict(row)
            result['sample_posts'] = sample_posts
            
            conn.close()
            return result
        
        conn.close()
        return None
    
    def get_global_stats(self) -> Dict:
        """Get global statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_posts,
                AVG(sentiment_score) as avg_sentiment
            FROM raw_posts
            WHERE timestamp > datetime('now', '-24 hours')
        ''')
        
        stats = dict(cursor.fetchone())
        
        cursor.execute('''
            SELECT COUNT(DISTINCT location_name) as countries_tracked
            FROM aggregated_sentiment
            WHERE location_type = 'country'
        ''')
        
        stats.update(dict(cursor.fetchone()))
        
        conn.close()
        return stats
    
    def cleanup_old_data(self, days: int = 7):
        """Remove data older than specified days."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        threshold = datetime.now() - timedelta(days=days)
        
        cursor.execute('DELETE FROM raw_posts WHERE timestamp < ?', (threshold,))
        cursor.execute('DELETE FROM aggregated_sentiment WHERE timestamp < ?', (threshold,))
        
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        
        return deleted_count

# Initialize global instance
db = DatabaseManager()