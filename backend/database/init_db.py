"""
init_db.py
----------
Initializes the SQLite database with the 5-emotion system.
Creates raw_posts and aggregated_emotions tables.

Run this ONCE to set up the database:
    python backend/database/init_db.py
"""

import sqlite3
import os
from pathlib import Path

def initialize_database(db_path='emotion_map.db'):
    """
    Initialize the SQLite database with all required tables.
    Uses the 5-emotion system: joy, anger, sadness, hope, calmness
    """
    
    # Create database directory if it doesn't exist
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Check if database already exists
    db_exists = os.path.exists(db_path)
    if db_exists:
        print(f"⚠️  Database '{db_path}' already exists!")
        response = input("Do you want to DELETE it and create a new one? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Cancelled. Existing database kept.")
            return
        else:
            os.remove(db_path)
            print(f"🗑️  Deleted existing database")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n🔨 Creating database: {db_path}")
    print("="*60)
    
    # ============================================
    # TABLE 1: raw_posts
    # Stores individual posts from all sources
    # ============================================
    print("\n📝 Creating raw_posts table...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            source TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            -- Location data
            city TEXT,
            country TEXT,
            continent TEXT,
            
            -- 5-emotion system
            emotion TEXT,
            emotion_score REAL,
            
            -- Legacy sentiment (for backward compatibility, optional)
            sentiment TEXT,
            sentiment_score REAL
        )
    ''')
    
    print("   ✅ raw_posts table created")
    
    # Create indexes for better query performance
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_raw_posts_timestamp 
        ON raw_posts(timestamp)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_raw_posts_country 
        ON raw_posts(country)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_raw_posts_emotion 
        ON raw_posts(emotion)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_raw_posts_source 
        ON raw_posts(source)
    ''')
    
    print("   ✅ Indexes created for raw_posts")
    
    # ============================================
    # TABLE 2: aggregated_emotions (NEW 5-EMOTION TABLE)
    # Stores aggregated emotion data by location
    # ============================================
    print("\n📝 Creating aggregated_emotions table...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aggregated_emotions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT NOT NULL,
            location_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            -- 5-emotion counts (JOY, ANGER, SADNESS, HOPE, CALMNESS)
            joy_count INTEGER DEFAULT 0,
            anger_count INTEGER DEFAULT 0,
            sadness_count INTEGER DEFAULT 0,
            hope_count INTEGER DEFAULT 0,
            calmness_count INTEGER DEFAULT 0,
            
            -- Summary statistics
            total_posts INTEGER DEFAULT 0,
            dominant_emotion TEXT,
            avg_emotion_score REAL
        )
    ''')
    
    print("   ✅ aggregated_emotions table created")
    
    # Create indexes for better query performance
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_aggregated_location 
        ON aggregated_emotions(location_name, location_type)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_aggregated_timestamp 
        ON aggregated_emotions(timestamp)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_aggregated_emotion 
        ON aggregated_emotions(dominant_emotion)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_aggregated_type 
        ON aggregated_emotions(location_type)
    ''')
    
    print("   ✅ Indexes created for aggregated_emotions")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ Database initialized successfully!")
    print("="*60)
    
    print("\n📊 Database Schema:")
    print("\nTable 1: raw_posts")
    print("  - Stores: Individual posts from Twitter, Reddit, News, RSS")
    print("  - Columns: text, source, timestamp, city, country, continent")
    print("  - Emotions: emotion (joy/anger/sadness/hope/calmness), emotion_score")
    print("  - Indexes: timestamp, country, emotion, source")
    
    print("\nTable 2: aggregated_emotions")
    print("  - Stores: Emotion counts grouped by location")
    print("  - Columns: joy_count, anger_count, sadness_count, hope_count, calmness_count")
    print("  - Summary: total_posts, dominant_emotion, avg_emotion_score")
    print("  - Location types: continent, country, city")
    print("  - Indexes: location, timestamp, dominant_emotion, location_type")
    
    print("\n" + "="*60)
    print(f"📁 Database file: {db_path}")
    print(f"📏 Size: {os.path.getsize(db_path)} bytes")
    print("="*60)
    


if __name__ == '__main__':
    initialize_database()