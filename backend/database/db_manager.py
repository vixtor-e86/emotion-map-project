"""
db_manager.py
-------------
Handles all database operations for the 5-emotion system.
"""

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
    
    # ============================================
    # RAW POSTS OPERATIONS
    # ============================================
    
    def insert_raw_post(self, text: str, source: str, city: str = None, 
                       country: str = None, continent: str = None,
                       emotion: str = None, emotion_score: float = None):
        """
        Insert a raw post into the database.
        
        Args:
            text: Post content
            source: Source (e.g., "RSS-BBC", "Reddit-r/worldnews", "Twitter")
            city: City name (optional)
            country: Country name (optional)
            continent: Continent name (optional)
            emotion: Emotion classification (joy/anger/sadness/hope/calmness)
            emotion_score: Confidence score (0.0 to 1.0)
        
        Returns:
            Post ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO raw_posts 
            (text, source, city, country, continent, emotion, emotion_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (text, source, city, country, continent, emotion, emotion_score))
        
        conn.commit()
        post_id = cursor.lastrowid
        conn.close()
        
        return post_id
    
    def update_post_emotion(self, post_id: int, emotion: str, emotion_score: float):
        """Update emotion data for a specific post."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE raw_posts 
            SET emotion = ?, emotion_score = ?
            WHERE id = ?
        ''', (emotion, emotion_score, post_id))
        
        conn.commit()
        conn.close()
    
    def update_post_location(self, post_id: int, city: str = None, 
                            country: str = None, continent: str = None):
        """Update location data for a specific post."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE raw_posts 
            SET city = ?, country = ?, continent = ?
            WHERE id = ?
        ''', (city, country, continent, post_id))
        
        conn.commit()
        conn.close()
    
    def get_posts_without_emotion(self) -> List[Dict]:
        """Get all posts that don't have emotion data yet."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, text, source, country
            FROM raw_posts
            WHERE emotion IS NULL
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_posts_without_location(self) -> List[Dict]:
        """Get all posts that don't have location data yet."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, text, source
            FROM raw_posts
            WHERE country IS NULL
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ============================================
    # AGGREGATED EMOTIONS OPERATIONS
    # ============================================
    
    def insert_aggregated_emotions(self, location_name: str, location_type: str,
                                   joy_count: int, anger_count: int, sadness_count: int,
                                   hope_count: int, calmness_count: int,
                                   dominant_emotion: str, avg_emotion_score: float):
        """
        Insert aggregated emotion data for a location.
        
        Args:
            location_name: Name of location (e.g., "USA", "Europe", "Lagos")
            location_type: Type (continent/country/city)
            joy_count: Number of joy posts
            anger_count: Number of anger posts
            sadness_count: Number of sadness posts
            hope_count: Number of hope posts
            calmness_count: Number of calmness posts
            dominant_emotion: Most common emotion
            avg_emotion_score: Average confidence score
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        total_posts = joy_count + anger_count + sadness_count + hope_count + calmness_count
        
        cursor.execute('''
            INSERT INTO aggregated_emotions 
            (location_name, location_type, joy_count, anger_count, sadness_count,
             hope_count, calmness_count, total_posts, dominant_emotion, avg_emotion_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (location_name, location_type, joy_count, anger_count, sadness_count,
              hope_count, calmness_count, total_posts, dominant_emotion, avg_emotion_score))
        
        conn.commit()
        conn.close()
    
    def get_emotion_map_data(self, zoom_level: str = 'country', hours: int = 24) -> List[Dict]:
        """
        Get aggregated emotion data for map visualization.
        
        Args:
            zoom_level: continent/country/city
            hours: Data from last N hours
        
        Returns:
            List of location emotion data
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        time_threshold = datetime.now() - timedelta(hours=hours)
        
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
                timestamp
            FROM aggregated_emotions
            WHERE location_type = ? AND timestamp > ?
            ORDER BY timestamp DESC
        ''', (zoom_level, time_threshold))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def count_emotion(self, country: str, emotion: str) -> int:
        """Count posts with specific emotion for a country."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM raw_posts
            WHERE country = ? AND emotion = ?
            AND timestamp > datetime('now', '-24 hours')
        ''', (country, emotion))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['count'] if result else 0
    
    def get_all_countries(self) -> List[str]:
        """Get list of all countries with posts."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT country
            FROM raw_posts
            WHERE country IS NOT NULL
            AND timestamp > datetime('now', '-24 hours')
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row['country'] for row in rows]
    
    # ============================================
    # STATISTICS & QUERIES
    # ============================================
    
    def get_emotion_stats(self) -> Dict:
        """
        Get global emotion statistics.
        
        Returns:
            Dictionary with emotion percentages and totals
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get emotion counts from last 24 hours
        cursor.execute('''
            SELECT 
                emotion,
                COUNT(*) as count
            FROM raw_posts
            WHERE timestamp > datetime('now', '-24 hours')
            AND emotion IS NOT NULL
            GROUP BY emotion
        ''')
        
        emotion_counts = {row['emotion']: row['count'] for row in cursor.fetchall()}
        
        # Calculate total
        total = sum(emotion_counts.values())
        
        # Calculate percentages
        stats = {
            'total_posts': total,
            'joy_percentage': round((emotion_counts.get('joy', 0) / total * 100), 1) if total > 0 else 0,
            'anger_percentage': round((emotion_counts.get('anger', 0) / total * 100), 1) if total > 0 else 0,
            'sadness_percentage': round((emotion_counts.get('sadness', 0) / total * 100), 1) if total > 0 else 0,
            'hope_percentage': round((emotion_counts.get('hope', 0) / total * 100), 1) if total > 0 else 0,
            'calmness_percentage': round((emotion_counts.get('calmness', 0) / total * 100), 1) if total > 0 else 0,
        }
        
        # Find dominant emotion
        if total > 0:
            stats['dominant_emotion'] = max(emotion_counts, key=emotion_counts.get)
        else:
            stats['dominant_emotion'] = 'none'
        
        # Count countries
        cursor.execute('''
            SELECT COUNT(DISTINCT country) as countries_tracked
            FROM raw_posts
            WHERE country IS NOT NULL
        ''')
        stats.update(dict(cursor.fetchone()))
        
        conn.close()
        return stats
    
    def get_location_details(self, location_name: str) -> Optional[Dict]:
        """
        Get detailed emotion information for a specific location.
        
        Args:
            location_name: Name of location
        
        Returns:
            Dictionary with emotion breakdown and sample posts
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Try to get from aggregated_emotions first
        cursor.execute('''
            SELECT *
            FROM aggregated_emotions
            WHERE location_name = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (location_name,))
        
        row = cursor.fetchone()
        
        if row:
            result = dict(row)
            
            # Get sample posts
            cursor.execute('''
                SELECT text, emotion, emotion_score, timestamp
                FROM raw_posts
                WHERE country = ? OR city = ?
                ORDER BY timestamp DESC
                LIMIT 5
            ''', (location_name, location_name))
            
            sample_posts = [dict(post) for post in cursor.fetchall()]
            result['sample_posts'] = sample_posts
            
            conn.close()
            return result
        
        # If not in aggregated table, calculate from raw_posts
        cursor.execute('''
            SELECT 
                COUNT(*) as total_posts,
                SUM(CASE WHEN emotion = 'joy' THEN 1 ELSE 0 END) as joy_count,
                SUM(CASE WHEN emotion = 'anger' THEN 1 ELSE 0 END) as anger_count,
                SUM(CASE WHEN emotion = 'sadness' THEN 1 ELSE 0 END) as sadness_count,
                SUM(CASE WHEN emotion = 'hope' THEN 1 ELSE 0 END) as hope_count,
                SUM(CASE WHEN emotion = 'calmness' THEN 1 ELSE 0 END) as calmness_count,
                AVG(emotion_score) as avg_score
            FROM raw_posts
            WHERE country = ? OR city = ?
        ''', (location_name, location_name))
        
        stats = dict(cursor.fetchone())
        
        if stats and stats['total_posts'] > 0:
            # Get sample posts
            cursor.execute('''
                SELECT text, emotion, emotion_score, timestamp
                FROM raw_posts
                WHERE country = ? OR city = ?
                ORDER BY timestamp DESC
                LIMIT 5
            ''', (location_name, location_name))
            
            sample_posts = [dict(post) for post in cursor.fetchall()]
            stats['location'] = location_name
            stats['sample_posts'] = sample_posts
            
            conn.close()
            return stats
        
        conn.close()
        return None
    
    # ============================================
    # MAINTENANCE
    # ============================================
    
    def cleanup_old_data(self, days: int = 7):
        """
        Remove data older than specified days.
        
        Args:
            days: Number of days to keep
        
        Returns:
            Number of deleted records
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        threshold = datetime.now() - timedelta(days=days)
        
        cursor.execute('DELETE FROM raw_posts WHERE timestamp < ?', (threshold,))
        deleted_posts = cursor.rowcount
        
        cursor.execute('DELETE FROM aggregated_emotions WHERE timestamp < ?', (threshold,))
        deleted_aggregated = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted_posts + deleted_aggregated

# Initialize global instance
db = DatabaseManager()