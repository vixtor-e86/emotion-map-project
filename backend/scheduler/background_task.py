"""
background_tasks.py
-------------------
Schedules and manages the automatic data collection pipeline.

Tasks:
- Run ALL collectors every hour (60 minutes)
- RSS, News, Reddit
- Process emotions, locations, and aggregate data
- Log execution time and status
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all collectors
from data_collection.rss_collector import collect_rss_data
from data_collection.news_collector import collect_news_data
from data_collection.reddit_collector import collect_reddit_data

# Import processing functions
from processing.emotion_analyzer import process_posts as analyze_emotions
from processing.location_extractor import process_posts as extract_locations
from processing.aggregator import process_all_zoom_levels as aggregate_data

# Set up logging
logging.basicConfig(
    filename="data_collection.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def process_emotions():
    """Analyze emotions in new posts."""
    try:
        logging.info("Starting emotion analysis...")
        processed = analyze_emotions(silent=True)
        logging.info(f"Emotion analysis: {processed} posts")
        return processed
    except Exception as e:
        logging.error(f"Emotion analysis failed: {e}")
        return 0

def process_locations():
    """Extract locations from posts."""
    try:
        logging.info("Starting location extraction...")
        processed = extract_locations(silent=True)
        logging.info(f"Location extraction: {processed} posts")
        return processed
    except Exception as e:
        logging.error(f"Location extraction failed: {e}")
        return 0

def process_aggregation():
    """Aggregate data by location."""
    try:
        logging.info("Starting data aggregation...")
        aggregate_data(silent=True, clear_before=True)  # ✅ Added clear_before parameter
        logging.info("Data aggregation complete")
        return True
    except Exception as e:
        logging.error(f"Data aggregation failed: {e}")
        return False

def run_data_collection():
    """
    Runs the full data collection pipeline.
    Collects from: RSS, News, Reddit
    Then processes: Emotions, Locations, Aggregation
    """
    try:
        logging.info("=" * 50)
        logging.info("Starting data collection pipeline...")
        print(f"\n🚀 Starting collection - {datetime.now().strftime('%H:%M:%S')}")
        start_time = datetime.now()
        
        # PHASE 1: COLLECT DATA
        print("\n1️⃣ RSS Feeds...")
        rss_stats = collect_rss_data()
        rss_count = rss_stats.get('unique_posts', 0) if isinstance(rss_stats, dict) else rss_stats
        logging.info(f"RSS: {rss_count} unique posts ({rss_stats.get('duplicates', 0)} duplicates)")

        print("\n2️⃣ News API...")
        news_stats = collect_news_data()
        news_count = news_stats.get('unique_posts', 0) if isinstance(news_stats, dict) else news_stats
        logging.info(f"News: {news_count} unique posts ({news_stats.get('duplicates', 0)} duplicates)")

        print("\n3️⃣ Reddit...")
        reddit_stats = collect_reddit_data(limit_per_sub=20)
        reddit_count = reddit_stats.get('unique_posts', 0) if isinstance(reddit_stats, dict) else reddit_stats
        logging.info(f"Reddit: {reddit_count} unique posts ({reddit_stats.get('duplicates', 0)} duplicates)")
        
        # ✅ FIX: Calculate total post count
        post_count = rss_count + news_count + reddit_count
        
        # PHASE 2: PROCESS DATA (only if new posts collected)
        if post_count > 0:
            print("\n4️⃣ Processing emotions...")
            processed_emotions = process_emotions()
            
            print("\n5️⃣ Extracting locations...")
            processed_locations = process_locations()
            
            print("\n6️⃣ Aggregating data...")
            process_aggregation()
            
            print(f"✓ Processing complete: {processed_emotions} posts analyzed")
        else:
            print("\n⚠️  No new posts - skipping processing")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logging.info(f"✓ Collection successful: {post_count} unique posts in {duration:.2f}s")
        print(f"\n{'='*60}")
        print(f"✅ Collection Complete!")
        print(f"{'='*60}")
        print(f"   📊 Total Unique Posts: {post_count}")
        print(f"   - RSS: {rss_count}")
        print(f"   - News: {news_count}")
        print(f"   - Reddit: {reddit_count}")
        print(f"   ⏱️  Duration: {duration:.2f}s")
        print(f"   ⏰ Next run in 60 minutes")
        print(f"{'='*60}\n")
        
    except Exception as e:
        logging.error(f"✗ Data collection failed: {e}")
        print(f"✗ Error in pipeline: {e}")
        import traceback
        traceback.print_exc()

def start_scheduler():
    """
    Initializes the APScheduler background job.
    Runs every 60 minutes.
    """
    scheduler = BackgroundScheduler()
    
    # Run every 60 minutes
    scheduler.add_job(run_data_collection, "interval", minutes=60)
    scheduler.start()
    
    logging.info("🚀 Scheduler started. Collecting data every 60 minutes.")
    print("\n" + "="*60)
    print("🚀 BACKGROUND SCHEDULER STARTED")
    print("="*60)
    print("⏰ Collection interval: Every 60 minutes")
    print("📊 Sources: RSS, News, Reddit")
    print("⚙️  Processing: Emotions, Locations, Aggregation")
    print("📝 Logs: data_collection.log")
    print("="*60 + "\n")

    return scheduler

# Test the scheduler
if __name__ == "__main__":
    print("🧪 Testing full pipeline once...")
    run_data_collection()