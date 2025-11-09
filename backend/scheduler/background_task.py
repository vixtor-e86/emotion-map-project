"""
background_task.py (MULTI-SECTOR EDITION)
------------------------------------------
Schedules and manages automatic data collection for ALL 4 SECTORS.

Tasks:
- Run ALL collectors every hour (60 minutes)
- RSS, News, Reddit (all sectors)
- Process emotions with sector awareness
- Extract locations and aggregate data
- Log execution time and status
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all collectors (NOW MULTI-SECTOR!)
from data_collection.rss_collector import collect_all_sectors_rss
from data_collection.news_collector import collect_news_data
from data_collection.reddit_collector import collect_all_sectors_reddit

# Import processing functions (NOW SECTOR-AWARE!)
from processing.emotion_analyzer import process_all_sectors as analyze_emotions
from processing.location_extractor import process_posts as extract_locations
from processing.aggregator import process_all_zoom_levels as aggregate_data

# Set up logging
logging.basicConfig(
    filename="data_collection.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def process_emotions():
    """Analyze emotions in new posts (ALL SECTORS)."""
    try:
        logging.info("Starting multi-sector emotion analysis...")
        processed = analyze_emotions(silent=True)
        logging.info(f"Emotion analysis: {processed} posts across all sectors")
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
    """Aggregate data by location and sector."""
    try:
        logging.info("Starting data aggregation...")
        aggregate_data(silent=True, clear_before=True)
        logging.info("Data aggregation complete")
        return True
    except Exception as e:
        logging.error(f"Data aggregation failed: {e}")
        return False

def run_data_collection():
    """
    Runs the MULTI-SECTOR data collection pipeline.
    Collects from: RSS (4 sectors), News (auto-sector), Reddit (4 sectors)
    Then processes: Emotions, Locations, Aggregation
    """
    try:
        logging.info("=" * 50)
        logging.info("Starting MULTI-SECTOR data collection pipeline...")
        print(f"\n🚀 Starting Multi-Sector Collection - {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        start_time = datetime.now()
        
        # PHASE 1: COLLECT DATA (ALL SECTORS)
        print("\n1️⃣ RSS Feeds (Finance, Health, Technology, Sports)...")
        rss_stats = collect_all_sectors_rss()
        rss_count = rss_stats.get('total_unique', 0) if isinstance(rss_stats, dict) else 0
        rss_by_sector = rss_stats.get('by_sector', {}) if isinstance(rss_stats, dict) else {}
        
        # Log RSS stats
        logging.info(f"RSS: {rss_count} unique posts")
        for sector, sector_stats in rss_by_sector.items():
            logging.info(f"  - {sector}: {sector_stats['unique_posts']} posts")

        print("\n2️⃣ News API (Auto-sector detection)...")
        news_stats = collect_news_data()
        news_count = news_stats.get('unique_posts', 0) if isinstance(news_stats, dict) else 0
        news_by_sector = news_stats.get('by_sector', {}) if isinstance(news_stats, dict) else {}
        
        # Log News stats
        logging.info(f"News: {news_count} unique posts")
        for sector, count in news_by_sector.items():
            if count > 0:
                logging.info(f"  - {sector}: {count} posts")

        print("\n3️⃣ Reddit (Finance, Health, Technology, Sports)...")
        reddit_stats = collect_all_sectors_reddit(limit_per_sub=20)
        reddit_count = reddit_stats.get('total_unique', 0) if isinstance(reddit_stats, dict) else 0
        reddit_by_sector = reddit_stats.get('by_sector', {}) if isinstance(reddit_stats, dict) else {}
        
        # Log Reddit stats
        logging.info(f"Reddit: {reddit_count} unique posts")
        for sector, sector_stats in reddit_by_sector.items():
            logging.info(f"  - {sector}: {sector_stats['unique_posts']} posts")
        
        # Calculate total
        total_count = rss_count + news_count + reddit_count
        
        # PHASE 2: PROCESS DATA (only if new posts collected)
        if total_count > 0:
            print("\n" + "="*60)
            print("PROCESSING COLLECTED DATA")
            print("="*60)
            
            print("\n4️⃣ Analyzing emotions (sector-aware)...")
            processed_emotions = process_emotions()
            
            print("\n5️⃣ Extracting locations...")
            processed_locations = process_locations()
            
            print("\n6️⃣ Aggregating data by sector & location...")
            process_aggregation()
            
            print(f"\n✅ Processing complete: {processed_emotions} posts analyzed")
        else:
            print("\n⚠️  No new posts collected - skipping processing")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Final summary
        logging.info(f"✅ Collection successful: {total_count} unique posts in {duration:.2f}s")
        
        print("\n" + "="*60)
        print("✅ MULTI-SECTOR COLLECTION COMPLETE!")
        print("="*60)
        
        print(f"\n📊 Total Posts Collected: {total_count}")
        
        # Show breakdown by source
        print(f"\nBy Source:")
        print(f"   📡 RSS:     {rss_count:3d} posts")
        print(f"   📰 News:    {news_count:3d} posts")
        print(f"   📱 Reddit:  {reddit_count:3d} posts")
        
        # Show breakdown by sector (combining all sources)
        print(f"\nBy Sector:")
        all_sectors = {'finance': 0, 'health': 0, 'technology': 0, 'sports': 0, 'general': 0}
        
        # Aggregate counts from all sources
        for sector in all_sectors.keys():
            rss_sector = rss_by_sector.get(sector, {}).get('unique_posts', 0) if rss_by_sector else 0
            news_sector = news_by_sector.get(sector, 0) if news_by_sector else 0
            reddit_sector = reddit_by_sector.get(sector, {}).get('unique_posts', 0) if reddit_by_sector else 0
            all_sectors[sector] = rss_sector + news_sector + reddit_sector
        
        for sector, count in sorted(all_sectors.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                icons = {'finance': '💰', 'health': '🏥', 'technology': '💻', 'sports': '⚽', 'general': '🌐'}
                print(f"   {icons.get(sector, '📌')} {sector.capitalize():12s}: {count:3d} posts")
        
        print(f"\n⏱️  Duration: {duration:.2f}s")
        print(f"⏰ Next run in 60 minutes")
        print("="*60 + "\n")
        
    except Exception as e:
        logging.error(f"❌ Data collection failed: {e}")
        print(f"\n❌ Error in pipeline: {e}")
        import traceback
        traceback.print_exc()

def start_scheduler():
    """
    Initializes the APScheduler background job.
    Runs MULTI-SECTOR collection every 60 minutes.
    """
    scheduler = BackgroundScheduler()
    
    # Run every 60 minutes
    scheduler.add_job(run_data_collection, "interval", minutes=60)
    scheduler.start()
    
    logging.info("🚀 Multi-Sector Scheduler started. Collecting data every 60 minutes.")
    
    print("\n" + "="*60)
    print("🚀 MULTI-SECTOR BACKGROUND SCHEDULER STARTED")
    print("="*60)
    print("⏰ Collection interval: Every 60 minutes")
    print("📂 Sectors tracked: Finance, Health, Technology, Sports")
    print("📊 Sources: RSS, News, Reddit")
    print("⚙️  Processing: Emotions, Locations, Aggregation")
    print("📝 Logs: data_collection.log")
    print("="*60 + "\n")

    return scheduler

# Test the scheduler
if __name__ == "__main__":
    print("🧪 Testing MULTI-SECTOR pipeline once...")
    run_data_collection()