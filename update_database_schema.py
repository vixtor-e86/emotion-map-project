"""
update_database_schema.py
--------------------------
Adds latitude and longitude columns to aggregated_emotions table.
Run this ONCE before using the processing pipeline.

Usage:
    python update_database_schema.py
"""

import sqlite3
import os

def update_schema(db_path='emotion_map.db'):
    """Add lat/lng columns to aggregated_emotions table."""
    
    if not os.path.exists(db_path):
        print(f"❌ Database '{db_path}' not found!")
        print("   Run: python backend/database/init_db.py first")
        return False
    
    print(f"\n🔧 Updating database schema: {db_path}")
    print("="*60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(aggregated_emotions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'latitude' in columns and 'longitude' in columns:
            print("✅ Columns 'latitude' and 'longitude' already exist!")
            return True
        
        # Add latitude column
        if 'latitude' not in columns:
            print("📍 Adding 'latitude' column...")
            cursor.execute('''
                ALTER TABLE aggregated_emotions 
                ADD COLUMN latitude REAL
            ''')
            print("   ✅ Added latitude")
        
        # Add longitude column
        if 'longitude' not in columns:
            print("📍 Adding 'longitude' column...")
            cursor.execute('''
                ALTER TABLE aggregated_emotions 
                ADD COLUMN longitude REAL
            ''')
            print("   ✅ Added longitude")
        
        # Create index for lat/lng queries
        print("📍 Creating spatial index...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_aggregated_coordinates
            ON aggregated_emotions(latitude, longitude)
        ''')
        print("   ✅ Spatial index created")
        
        conn.commit()
        
        # Verify schema
        print("\n📋 Updated Schema:")
        cursor.execute("PRAGMA table_info(aggregated_emotions)")
        for col in cursor.fetchall():
            print(f"   - {col[1]} ({col[2]})")
        
        print("\n" + "="*60)
        print("✅ Database schema updated successfully!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error updating schema: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == '__main__':
    success = update_schema()
    
    if success:
        print("\n🚀 Next steps:")
        print("   1. Run emotion analyzer:")
        print("      python backend/processing/emotion_analyzer.py")
        print("   2. Run location extractor:")
        print("      python backend/processing/location_extractor.py")
        print("   3. Run aggregator:")
        print("      python backend/processing/aggregator.py")
    else:
        print("\n❌ Schema update failed. Please check the error above.")