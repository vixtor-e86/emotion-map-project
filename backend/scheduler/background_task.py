"""
background_tasks.py
-------------------
Schedules and manages the automatic data collection pipeline.

Tasks:
- Run ALL collectors every hour (60 minutes)
- RSS, News, Reddit, Twitter
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

# Set up logging
logging.basicConfig(
    filename="data_collection.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_data_collection():
    """
    Runs the full data collection pipeline.
    Collects from: RSS, News, Reddit, Twitter
    """
    try:
        logging.info("=" * 50)
        logging.info("Starting data collection pipeline...")
        print(f"\n🚀 Starting collection - {datetime.now().strftime('%H:%M:%S')}")
        start_time = datetime.now()
        
        # Collect from all sources
        print("\n1️⃣ RSS Feeds...")
        RSS = collect_rss_data()
        logging.info(f"RSS: {RSS} posts")

        print("\n2️⃣ News API...")
        News = collect_news_data()
        logging.info(f"News: {News} posts")

        print("\n3️⃣ Reddit...")
        Reddit = collect_reddit_data(limit_per_sub=20)
        logging.info(f"Reddit: {Reddit} posts")
        
        # Calculate totals
        post_count = RSS + News + Reddit

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logging.info(f"âœ… Collection successful: {post_count} posts in {duration:.2f}s")
        print(f"\nâœ… Collection complete: {post_count} total posts in {duration:.1f}s")
        print(f"   - RSS: {RSS}")
        print(f"   - News: {News}")
        print(f"   - Reddit: {Reddit}")
        print(f"âœ… Next run in 60 minutes\n")
        
    except Exception as e:
        logging.error(f"âŒ Data collection failed: {e}")
        print(f"âŒ Error in pipeline: {e}")

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
    print("🚀 Scheduler started - collecting data every 60 minutes.")
    print("📍 Sources: RSS, News, Reddit")

    return scheduler

# Test the scheduler
if __name__ == "__main__":
    print("🧪 Testing data collection once...")
    run_data_collection()
