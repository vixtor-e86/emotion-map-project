"""
db_manager.py
-------------
Handles all database operations for the 5-emotion system.
NOW WITH BUILT-IN DUPLICATE DETECTION!
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys
import os
import hashlib
import re

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class DatabaseManager:
    """Handles all database operations with duplicate detection."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.enable_duplicate_check = True  # Toggle duplicate detection
    
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ============================================
    # DUPLICATE DETECTION METHODS
    # ============================================
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for duplicate comparison."""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'http\S+|www.\S+', '', text)  # Remove URLs
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
        text = ' '.join(text.split())  # Remove extra whitespace
        return text.strip()
    
    def create_text_hash(self, text: str, length: int = 200) -> str:
        """Create hash from first N characters of normalized text."""
        normalized = self.normalize_text(text)
        truncated = normalized[:length]
        return hashlib.md5(truncated.encode()).hexdigest()
    
    def is_duplicate(self, text: str) -> bool:
        """
        Check if post is duplicate using hash-based detection.
        
        Args:
            text: Post content to check
        
        Returns:
            True if duplicate exists, False if unique
        """
        if not self.enable_duplicate_check:
            return False
        
        if not text or len(text.strip()) < 10:
            return False
        
        text_hash = self.create_text_hash(text)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check recent posts (last 7 days) for same hash
        cursor.execute('''
            SELECT id, text FROM raw_posts 
            WHERE timestamp > datetime('now', '-7 days')
            LIMIT 1000
        ''')
        
        posts = cursor.fetchall()
        conn.close()
        
        for post in posts:
            post_hash = self.create_text_hash(post['text'])
            if post_hash == text_hash:
                return True
        
        return False
    
    # ============================================
    # RAW POSTS OPERATIONS (UPDATED)
    # ============================================
    
    def insert_raw_post(self, text: str, source: str, city: str = None, 
                       country: str = None, continent: str = None,
                       emotion: str = None, emotion_score: float = None,
                       skip_duplicate_check: bool = False):
        """
        Insert a raw post into the database with duplicate detection.
        
        Args:
            text: Post content
            source: Source (e.g., "RSS-BBC", "Reddit-r/worldnews")
            city: City name (optional)
            country: Country name (optional)
            continent: Continent name (optional)
            emotion: Emotion classification (joy/anger/sadness/hope/calmness)
            emotion_score: Confidence score (0.0 to 1.0)
            skip_duplicate_check: Set to True to bypass duplicate detection
        
        Returns:
            Post ID if inserted, None if duplicate
        """
        # Check for duplicates (unless explicitly skipped)
        if not skip_duplicate_check and self.is_duplicate(text):
            return None  # Duplicate found, skip insertion
        
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
    # DUPLICATE MANAGEMENT
    # ============================================
    
    def get_duplicate_stats(self) -> Dict:
        """Get statistics about duplicates in database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total posts
        cursor.execute('SELECT COUNT(*) as total FROM raw_posts')
        total = cursor.fetchone()['total']
        
        # Recent posts
        cursor.execute('''
            SELECT COUNT(*) as recent 
            FROM raw_posts 
            WHERE timestamp > datetime('now', '-1 day')
        ''')
        recent = cursor.fetchone()['recent']
        
        # Estimate duplicates
        cursor.execute('''
            SELECT COUNT(*) as dups
            FROM (
                SELECT LOWER(SUBSTR(text, 1, 200)) as normalized, COUNT(*) as cnt
                FROM raw_posts
                GROUP BY normalized
                HAVING cnt > 1
            )
        ''')
        duplicates = cursor.fetchone()['dups']
        
        conn.close()
        
        return {
            'total_posts': total,
            'recent_posts_24h': recent,
            'potential_duplicates': duplicates,
            'duplicate_rate': round((duplicates / total * 100), 1) if total > 0 else 0
        }
    
    def clean_duplicates(self, dry_run: bool = True) -> int:
        """
        Remove duplicate posts (keeps oldest entry).
        
        Args:
            dry_run: If True, only count duplicates without deleting
        
        Returns:
            Number of duplicates found/removed
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, text, timestamp
            FROM raw_posts
            ORDER BY timestamp ASC
        ''')
        
        posts = cursor.fetchall()
        seen_hashes = {}
        to_delete = []
        
        for post in posts:
            text_hash = self.create_text_hash(post['text'])
            
            if text_hash in seen_hashes:
                to_delete.append(post['id'])
            else:
                seen_hashes[text_hash] = post['id']
        
        if not dry_run and to_delete:
            cursor.executemany(
                'DELETE FROM raw_posts WHERE id = ?',
                [(pid,) for pid in to_delete]
            )
            conn.commit()
        
        conn.close()
        
        return len(to_delete)
    
    # ============================================
    # AGGREGATED EMOTIONS OPERATIONS
    # ============================================
    
    def insert_aggregated_emotions(self, location_name: str, location_type: str,
                                   joy_count: int, anger_count: int, sadness_count: int,
                                   hope_count: int, calmness_count: int,
                                   dominant_emotion: str, avg_emotion_score: float):
        """Insert aggregated emotion data for a location."""
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
        """Get aggregated emotion data for map visualization."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        time_threshold = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT 
                location_name, location_type, joy_count, anger_count, sadness_count,
                hope_count, calmness_count, total_posts, dominant_emotion,
                avg_emotion_score, timestamp
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
        """Get global emotion statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT emotion, COUNT(*) as count
            FROM raw_posts
            WHERE timestamp > datetime('now', '-24 hours')
            AND emotion IS NOT NULL
            GROUP BY emotion
        ''')
        
        emotion_counts = {row['emotion']: row['count'] for row in cursor.fetchall()}
        total = sum(emotion_counts.values())
        
        stats = {
            'total_posts': total,
            'joy_percentage': round((emotion_counts.get('joy', 0) / total * 100), 1) if total > 0 else 0,
            'anger_percentage': round((emotion_counts.get('anger', 0) / total * 100), 1) if total > 0 else 0,
            'sadness_percentage': round((emotion_counts.get('sadness', 0) / total * 100), 1) if total > 0 else 0,
            'hope_percentage': round((emotion_counts.get('hope', 0) / total * 100), 1) if total > 0 else 0,
            'calmness_percentage': round((emotion_counts.get('calmness', 0) / total * 100), 1) if total > 0 else 0,
        }
        
        if total > 0:
            stats['dominant_emotion'] = max(emotion_counts, key=emotion_counts.get)
        else:
            stats['dominant_emotion'] = 'none'
        
        cursor.execute('''
            SELECT COUNT(DISTINCT country) as countries_tracked
            FROM raw_posts
            WHERE country IS NOT NULL
        ''')
        stats.update(dict(cursor.fetchone()))
        
        conn.close()
        return stats
    
    def get_location_details(self, location_name: str) -> Optional[Dict]:
        """Get detailed emotion information for a specific location."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM aggregated_emotions
            WHERE location_name = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (location_name,))
        
        row = cursor.fetchone()
        
        if row:
            result = dict(row)
            
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
        """Remove data older than specified days."""
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