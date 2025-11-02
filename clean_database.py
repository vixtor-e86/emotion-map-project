"""
clean_database.py
-----------------
Clears all data from database tables while preserving the schema.
This removes all posts and aggregated emotions but keeps the table structure intact.

Usage:
    python clean_database.py
"""

import sqlite3
import os

def clean_database(db_path='emotion_map.db'):
    """
    Clear all data from database tables without dropping the tables.
    Preserves the schema and indexes.
    """
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database '{db_path}' not found!")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Looking for: {os.path.abspath(db_path)}")
        return False
    
    # Get current database size
    original_size = os.path.getsize(db_path)
    
    print(f"\n🗑️  Database Cleanup Utility")
    print("="*60)
    print(f"📁 Database: {db_path}")
    print(f"📊 Current size: {original_size:,} bytes ({original_size/1024:.2f} KB)")
    print("="*60)
    
    # Safety confirmation
    print("\n⚠️  WARNING: This will DELETE ALL DATA from:")
    print("   - raw_posts table")
    print("   - aggregated_emotions table")
    print("\n   The table structure and indexes will be preserved.")
    
    response = input("\n❓ Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Cancelled. No data was deleted.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get row counts before deletion
        print("\n📊 Current data:")
        cursor.execute("SELECT COUNT(*) FROM raw_posts")
        raw_posts_count = cursor.fetchone()[0]
        print(f"   - raw_posts: {raw_posts_count:,} rows")
        
        cursor.execute("SELECT COUNT(*) FROM aggregated_emotions")
        aggregated_count = cursor.fetchone()[0]
        print(f"   - aggregated_emotions: {aggregated_count:,} rows")
        
        total_rows = raw_posts_count + aggregated_count
        
        if total_rows == 0:
            print("\n✅ Database is already empty!")
            conn.close()
            return True
        
        # Delete all data from tables
        print(f"\n🗑️  Deleting {total_rows:,} total rows...")
        
        cursor.execute("DELETE FROM raw_posts")
        deleted_raw = cursor.rowcount
        print(f"   ✅ Deleted {deleted_raw:,} rows from raw_posts")
        
        cursor.execute("DELETE FROM aggregated_emotions")
        deleted_agg = cursor.rowcount
        print(f"   ✅ Deleted {deleted_agg:,} rows from aggregated_emotions")
        
        # Reset autoincrement counters
        print("\n🔄 Resetting auto-increment counters...")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='raw_posts'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='aggregated_emotions'")
        print("   ✅ Counters reset")
        
        # Commit changes
        conn.commit()
        
        # Vacuum to reclaim space
        print("\n🧹 Vacuuming database to reclaim space...")
        cursor.execute("VACUUM")
        print("   ✅ Database optimized")
        
        conn.close()
        
        # Get new database size
        new_size = os.path.getsize(db_path)
        space_freed = original_size - new_size
        
        print("\n" + "="*60)
        print("✅ Database cleaned successfully!")
        print("="*60)
        print(f"\n📊 Results:")
        print(f"   - Rows deleted: {total_rows:,}")
        print(f"   - Original size: {original_size:,} bytes ({original_size/1024:.2f} KB)")
        print(f"   - New size: {new_size:,} bytes ({new_size/1024:.2f} KB)")
        print(f"   - Space freed: {space_freed:,} bytes ({space_freed/1024:.2f} KB)")
        print(f"   - Reduction: {(space_freed/original_size*100):.1f}%")
        
        # Verify tables are empty
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM raw_posts")
        verify_raw = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM aggregated_emotions")
        verify_agg = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"\n✅ Verification:")
        print(f"   - raw_posts: {verify_raw} rows")
        print(f"   - aggregated_emotions: {verify_agg} rows")
        
        if verify_raw == 0 and verify_agg == 0:
            print("\n🎉 All tables are clean and ready for new data!")
        else:
            print("\n⚠️  Warning: Some data may still remain")
        
        print("="*60)
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def quick_clean(db_path='emotion_map.db'):
    """
    Quick clean without confirmation (use with caution!).
    Useful for automation/scripts.
    """
    if not os.path.exists(db_path):
        print(f"❌ Database '{db_path}' not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM raw_posts")
        cursor.execute("DELETE FROM aggregated_emotions")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('raw_posts', 'aggregated_emotions')")
        cursor.execute("VACUUM")
        
        conn.commit()
        conn.close()
        
        print("✅ Database cleaned (quick mode)")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    import sys
    
    # Check for quick mode flag
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        quick_clean()
    else:
        clean_database()