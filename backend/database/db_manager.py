"""
db_manager.py (MULTI-SECTOR EDITION)
-------------------------------------
Database manager with support for multiple sectors:
- Finance, Health, Technology, Sports

All functions now accept optional 'sector' parameter.
"""

import sqlite3
from datetime import datetime
import os

DB_PATH = 'emotion_map.db'

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def insert_raw_post(self, text, source, country, emotion=None, emotion_score=None, 
                       city=None, continent=None, sector='general'):
        """
        Insert a new post into database with DUPLICATE DETECTION and SECTOR support.
        
        Args:
            text: Post text
            source: Data source (e.g., 'RSS-Bloomberg', 'Reddit-r/wallstreetbets')
            country: Country name
            emotion: Detected emotion (optional, can be analyzed later)
            emotion_score: Confidence score (optional)
            city: City name (optional)
            continent: Continent name (optional)
            sector: Sector category (finance, health, technology, sports)
        
        Returns:
            int: Post ID if inserted successfully, None if duplicate
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check for duplicate (first 200 characters)
            text_preview = text[:200] if len(text) > 200 else text
            
            cursor.execute('''
                SELECT id FROM raw_posts 
                WHERE substr(text, 1, 200) = ?
                AND sector = ?
            ''', (text_preview, sector))
            
            if cursor.fetchone():
                # Duplicate found
                conn.close()
                return None
            
            # Insert new post
            cursor.execute('''
                INSERT INTO raw_posts (
                    text, source, country, emotion, emotion_score, 
                    city, continent, sector, timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (text, source, country, emotion, emotion_score, 
                  city, continent, sector, datetime.now()))
            
            post_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return post_id
            
        except Exception as e:
            print(f"Error inserting post: {e}")
            conn.close()
            return None
    
    def get_posts_without_emotion(self, sector=None):
        """
        Get all posts that don't have emotion analysis yet.
        
        Args:
            sector: Optional sector filter
        
        Returns:
            list: List of posts without emotions
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if sector:
            cursor.execute('''
                SELECT id, text, sector
                FROM raw_posts
                WHERE emotion IS NULL
                AND sector = ?
                ORDER BY timestamp DESC
            ''', (sector,))
        else:
            cursor.execute('''
                SELECT id, text, sector
                FROM raw_posts
                WHERE emotion IS NULL
                ORDER BY timestamp DESC
            ''')
        
        posts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return posts
    
    def update_post_emotion(self, post_id, emotion, emotion_score):
        """Update emotion for a specific post"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE raw_posts
            SET emotion = ?, emotion_score = ?
            WHERE id = ?
        ''', (emotion, emotion_score, post_id))
        
        conn.commit()
        conn.close()
    
    def get_emotion_stats(self, sector=None):
        """
        Get global emotion statistics with percentages.
        
        Args:
            sector: Optional sector filter
        
        Returns:
            dict: Emotion percentages
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if sector:
            cursor.execute('''
                SELECT 
                    emotion,
                    COUNT(*) as count
                FROM raw_posts
                WHERE emotion IS NOT NULL
                AND sector = ?
                GROUP BY emotion
            ''', (sector,))
        else:
            cursor.execute('''
                SELECT 
                    emotion,
                    COUNT(*) as count
                FROM raw_posts
                WHERE emotion IS NOT NULL
                GROUP BY emotion
            ''')
        
        results = cursor.fetchall()
        conn.close()
        
        # Calculate percentages
        total = sum(row['count'] for row in results)
        if total == 0:
            return {
                'joy': 0, 'anger': 0, 'sadness': 0, 
                'hope': 0, 'calmness': 0
            }
        
        stats = {
            'joy': 0, 'anger': 0, 'sadness': 0, 
            'hope': 0, 'calmness': 0
        }
        
        for row in results:
            emotion = row['emotion']
            percentage = (row['count'] / total) * 100
            stats[emotion] = percentage
            stats[f'{emotion}_count'] = row['count']
        
        stats['total_posts'] = total
        return stats
    
    def get_posts_by_location(self, location_name, location_type='country', sector=None):
        """
        Get posts for a specific location.
        
        Args:
            location_name: Location name
            location_type: 'continent', 'country', or 'city'
            sector: Optional sector filter
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        column_map = {
            'continent': 'continent',
            'country': 'country',
            'city': 'city'
        }
        
        column = column_map.get(location_type, 'country')
        
        if sector:
            cursor.execute(f'''
                SELECT text, emotion, emotion_score, timestamp
                FROM raw_posts
                WHERE {column} = ?
                AND sector = ?
                ORDER BY timestamp DESC
                LIMIT 100
            ''', (location_name, sector))
        else:
            cursor.execute(f'''
                SELECT text, emotion, emotion_score, timestamp
                FROM raw_posts
                WHERE {column} = ?
                ORDER BY timestamp DESC
                LIMIT 100
            ''', (location_name,))
        
        posts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return posts
    
    def insert_aggregated_emotion(self, location_name, location_type, 
                                  joy_count, anger_count, sadness_count,
                                  hope_count, calmness_count, total_posts,
                                  dominant_emotion, avg_emotion_score,
                                  latitude=None, longitude=None, sector='general'):
        """
        Insert aggregated emotion data for a location with SECTOR support.
        
        Args:
            location_name: Name of location
            location_type: 'continent', 'country', or 'city'
            joy_count: Number of joy posts
            anger_count: Number of anger posts
            sadness_count: Number of sadness posts
            hope_count: Number of hope posts
            calmness_count: Number of calmness posts
            total_posts: Total posts for this location
            dominant_emotion: Most common emotion
            avg_emotion_score: Average confidence score
            latitude: Optional latitude
            longitude: Optional longitude
            sector: Sector category
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if entry exists for this location + sector
            cursor.execute('''
                SELECT id FROM aggregated_emotions
                WHERE location_name = ?
                AND location_type = ?
                AND sector = ?
            ''', (location_name, location_type, sector))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                cursor.execute('''
                    UPDATE aggregated_emotions
                    SET joy_count = ?,
                        anger_count = ?,
                        sadness_count = ?,
                        hope_count = ?,
                        calmness_count = ?,
                        total_posts = ?,
                        dominant_emotion = ?,
                        avg_emotion_score = ?,
                        latitude = ?,
                        longitude = ?,
                        timestamp = ?
                    WHERE id = ?
                ''', (joy_count, anger_count, sadness_count, hope_count, 
                      calmness_count, total_posts, dominant_emotion, 
                      avg_emotion_score, latitude, longitude, 
                      datetime.now(), existing['id']))
            else:
                # Insert new
                cursor.execute('''
                    INSERT INTO aggregated_emotions (
                        location_name, location_type,
                        joy_count, anger_count, sadness_count,
                        hope_count, calmness_count, total_posts,
                        dominant_emotion, avg_emotion_score,
                        latitude, longitude, sector, timestamp
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (location_name, location_type,
                      joy_count, anger_count, sadness_count,
                      hope_count, calmness_count, total_posts,
                      dominant_emotion, avg_emotion_score,
                      latitude, longitude, sector, datetime.now()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error inserting aggregated emotion: {e}")
            conn.close()
            return False
    
    def get_aggregated_data(self, location_type='country', sector=None):
        """
        Get aggregated emotion data for map visualization.
        
        Args:
            location_type: 'continent', 'country', or 'city'
            sector: Optional sector filter
        
        Returns:
            list: Aggregated data points
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if sector:
            cursor.execute('''
                SELECT * FROM aggregated_emotions
                WHERE location_type = ?
                AND sector = ?
                ORDER BY total_posts DESC
            ''', (location_type, sector))
        else:
            cursor.execute('''
                SELECT * FROM aggregated_emotions
                WHERE location_type = ?
                ORDER BY total_posts DESC
            ''', (location_type,))
        
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return data
    
    def get_all_sectors(self):
        """Get list of all sectors in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT sector, COUNT(*) as count
            FROM raw_posts
            WHERE sector IS NOT NULL
            GROUP BY sector
            ORDER BY count DESC
        ''')
        
        sectors = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return sectors
    
    def get_database_stats(self):
        """Get overall database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total posts
        cursor.execute("SELECT COUNT(*) as total FROM raw_posts")
        total_posts = cursor.fetchone()['total']
        
        # Posts by sector
        cursor.execute('''
            SELECT sector, COUNT(*) as count
            FROM raw_posts
            GROUP BY sector
        ''')
        by_sector = {row['sector']: row['count'] for row in cursor.fetchall()}
        
        # Posts with emotions
        cursor.execute("SELECT COUNT(*) FROM raw_posts WHERE emotion IS NOT NULL")
        with_emotions = cursor.fetchone()[0]
        
        # Unique countries
        cursor.execute("SELECT COUNT(DISTINCT country) FROM raw_posts WHERE country IS NOT NULL")
        countries = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_posts': total_posts,
            'by_sector': by_sector,
            'with_emotions': with_emotions,
            'unique_countries': countries
        }

# Create global instance
db = DatabaseManager()