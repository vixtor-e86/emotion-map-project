"""
migrate_to_emotions.py
----------------------
Migrates database from old sentiment system (positive/negative/neutral)
to new 5-emotion system (joy, anger, fear, hope, calmness).

Run this ONCE to update the database structure.
"""

import sqlite3
from pathlib import Path

def migrate_database(db_path='emotion_map.db'):
    """
    Update database schema for 5-emotion system.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Starting database migration to 5-emotion system...\n")
    print("📝 Step 1: Updating raw_posts table...")
    
    # Check if emotion column exists
    cursor.execute("PRAGMA table_info(raw_posts)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'emotion' not in columns:
        # Add new emotion columns
        cursor.execute('ALTER TABLE raw_posts ADD COLUMN emotion TEXT')
        cursor.execute('ALTER TABLE raw_posts ADD COLUMN emotion_score REAL')
        print("   ✅ Added emotion and emotion_score columns")
    else:
        print("   ℹ️ Emotion columns already exist")
    
    # Add index for better performance
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_raw_posts_emotion ON raw_posts(emotion)')
        print("   ✅ Added emotion index")
    except:
        pass
    print("\n📝 Step 2: Creating new aggregated_emotions table...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aggregated_emotions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT NOT NULL,
            location_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            -- New 5-emotion system
            joy_count INTEGER DEFAULT 0,
            anger_count INTEGER DEFAULT 0,
            sadness_count INTEGER DEFAULT 0,
            hope_count INTEGER DEFAULT 0,
            calmness_count INTEGER DEFAULT 0,
            
            total_posts INTEGER DEFAULT 0,
            dominant_emotion TEXT,
            avg_emotion_score REAL,
            
            -- Legacy sentiment fields (keeping for backward compatibility)
            positive_count INTEGER DEFAULT 0,
            negative_count INTEGER DEFAULT 0,
            neutral_count INTEGER DEFAULT 0,
            dominant_sentiment TEXT,
            avg_sentiment_score REAL
        )
    ''')
    print("   ✅ Created aggregated_emotions table")
    
    # Add indexes
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
    print("   ✅ Added indexes")
    
    print("\n📝 Step 3: Checking for old data...")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='aggregated_sentiment'")
    old_table_exists = cursor.fetchone()
    
    if old_table_exists:
        print("   ℹ️ Found old aggregated_sentiment table")
        print("   ⚠️ Old data will be preserved but not migrated automatically")
        print("   ℹ️ You can drop it later with: DROP TABLE aggregated_sentiment")
    else:
        print("   ✅ No old table found, fresh start!")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ Database migration complete!")
    print("="*60)
    print("\nNew structure:")
    print("  • raw_posts: Added emotion columns")
    print("  • aggregated_emotions: New 5-emotion table created")
    print("\nNext steps:")
    print("  1. Update db_manager.py methods")
    print("  2. Create emotion_analyzer.py")
    print("  3. Update API endpoints")
    print("="*60)

if __name__ == '__main__':
    migrate_database()