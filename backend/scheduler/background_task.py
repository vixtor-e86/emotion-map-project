"""
background_tasks.py
-------------------
Schedules and manages the automatic data collection pipeline.

Tasks:
- Run RSS collector every hour (60 minutes)
- Log execution time and status
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_collection.rss_collector import collect_rss_data

# Set up logging
logging.basicConfig(
    filename="data_collection.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_data_collection():
    """
    Runs the full data collection pipeline.
    Currently collects RSS data.
    """
    try:
        logging.info("=" * 50)
        logging.info("Starting data collection pipeline...")
        start_time = datetime.now()
        
        # Collect RSS data
        post_count = collect_rss_data()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logging.info(f"✅ Collection successful: {post_count} posts in {duration:.2f}s")
        print(f"✅ Data collection complete: {post_count} posts")
        
    except Exception as e:
        logging.error(f"❌ Data collection failed: {e}")
        print(f"❌ Error in pipeline: {e}")

def start_scheduler():
    """
    Initializes the APScheduler background job.
    Runs every 60 minutes.
    """
    scheduler = BackgroundScheduler()
    
    # Run every 60 minutes (as per your .env settings)
    scheduler.add_job(run_data_collection, "interval", minutes=60)
    scheduler.start()
    
    logging.info("🚀 Scheduler started. Collecting data every 60 minutes.")
    print("🚀 Scheduler started – collecting RSS data every 60 minutes.")
    
    return scheduler

# Test the scheduler
if __name__ == "__main__":
    print("Testing data collection once...")
    run_data_collection()
