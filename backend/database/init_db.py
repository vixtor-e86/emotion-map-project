import sqlite3
import os
from pathlib import Path

def initialize_database(db_path='emotion_map.db'):
    """Initialize the SQLite database with required tables."""
    
    # Create database directory if it doesn't exist
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create raw_posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            source TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            city TEXT,
            country TEXT,
            continent TEXT,
            sentiment TEXT,
            sentiment_score REAL
        )
    ''')
    
    # Create aggregated_sentiment table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aggregated_sentiment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT NOT NULL,
            location_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            positive_count INTEGER DEFAULT 0,
            negative_count INTEGER DEFAULT 0,
            neutral_count INTEGER DEFAULT 0,
            total_posts INTEGER DEFAULT 0,
            dominant_sentiment TEXT,
            avg_sentiment_score REAL
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_raw_posts_timestamp ON raw_posts(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_raw_posts_country ON raw_posts(country)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_aggregated_location ON aggregated_sentiment(location_name, location_type)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized successfully at {db_path}")

if __name__ == '__main__':
    initialize_database()