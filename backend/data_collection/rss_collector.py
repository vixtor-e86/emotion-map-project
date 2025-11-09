"""
rss_collector.py (MULTI-SECTOR EDITION)
----------------------------------------
Collects news from RSS feeds for ALL 4 SECTORS:
- Finance, Health, Technology, Sports

Each post is automatically tagged with its sector.
"""
    
import feedparser
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import db
from processing.sector_config import (
    RSS_FEEDS,
    detect_sector,
    extract_tickers,
    get_sector_info
)

def parse_feed(url):
    """Safely parse RSS feed."""
    try:
        feed = feedparser.parse(url)
        if feed.bozo:
            print(f"⚠️ Invalid feed: {url}")
            return []
        return feed.entries
    except Exception as e:
        print(f"❌ Error reading {url}: {e}")
        return []

def guess_country_from_source(source):
    """Map source to country."""
    mapping = {
        # Finance
        "Bloomberg": "United States",
        "MarketWatch": "United States",
        "CNBC": "United States",
        "Reuters": "International",
        "CoinDesk": "International",
        "Forbes": "United States",
        
        # Health
        "WHO": "International",
        "CDC": "United States",
        "WebMD": "United States",
        "Healthline": "United States",
        
        # Technology
        "TechCrunch": "United States",
        "The Verge": "United States",
        "Wired": "United States",
        "Ars Technica": "United States",
        "Engadget": "United States",
        "MIT": "United States",
        
        # Sports
        "ESPN": "United States",
        "BBC Sport": "United Kingdom",
        "Sky Sports": "United Kingdom",
        "Goal": "International",
        "Sports Illustrated": "United States",
    }
    
    for key, country in mapping.items():
        if key.lower() in source.lower():
            return country
    return "International"

def collect_sector_rss_data(sector: str):
    """
    Collect RSS data for a specific sector.
    
    Args:
        sector: Sector name ('finance', 'health', 'technology', 'sports')
    
    Returns:
        dict: Collection statistics
    """
    if sector not in RSS_FEEDS:
        print(f"❌ Unknown sector: {sector}")
        return None
    
    sector_info = get_sector_info(sector)
    feeds = RSS_FEEDS[sector]
    
    total_posts = 0
    duplicate_posts = 0
    
    print(f"\n{sector_info['icon']} {sector_info['name'].upper()} RSS FEEDS")
    print("=" * 60)
    
    for source, url in feeds.items():
        print(f"📡 Fetching: {source}...", end=' ')
        entries = parse_feed(url)
        
        feed_posts = 0
        feed_duplicates = 0
        
        for entry in entries:
            try:
                text = entry.get("title", "No title available")
                
                # Verify it's actually about this sector
                detected_sector = detect_sector(text)
                if detected_sector != sector and detected_sector != 'general':
                    # Skip if it's clearly from another sector
                    continue
                
                country = guess_country_from_source(source)
                
                # Extract tickers if finance
                tickers = []
                if sector == 'finance':
                    tickers = extract_tickers(text)
                    ticker_text = f" [{', '.join(tickers)}]" if tickers else ""
                    text = text + ticker_text
                
                # Save to database with SECTOR tag
                post_id = db.insert_raw_post(
                    text=text,
                    source=f"{sector.capitalize()}-RSS-{source}",
                    country=country,
                    emotion=None,
                    emotion_score=None,
                    sector=sector  # ← SECTOR TAG!
                )
                
                if post_id is None:
                    duplicate_posts += 1
                    feed_duplicates += 1
                else:
                    total_posts += 1
                    feed_posts += 1
                
            except Exception as e:
                print(f"\n❌ Error saving post from {source}: {e}")
                continue
        
        print(f"✅ {feed_posts} new, {feed_duplicates} duplicates")
    
    return {
        'sector': sector,
        'unique_posts': total_posts,
        'duplicates': duplicate_posts
    }

def collect_all_sectors_rss():
    """
    Collect RSS data from ALL 4 SECTORS.
    
    Returns:
        dict: Statistics for all sectors
    """
    print("\n" + "="*60)
    print("🌐 MULTI-SECTOR RSS DATA COLLECTION")
    print("="*60)
    
    all_stats = {}
    total_unique = 0
    total_duplicates = 0
    
    # Collect from each sector
    for sector in ['finance', 'health', 'technology', 'sports']:
        stats = collect_sector_rss_data(sector)
        if stats:
            all_stats[sector] = stats
            total_unique += stats['unique_posts']
            total_duplicates += stats['duplicates']
    
    # Final summary
    total_processed = total_unique + total_duplicates
    duplicate_rate = round((total_duplicates / total_processed * 100), 1) if total_processed > 0 else 0
    
    print("\n" + "="*60)
    print("✅ MULTI-SECTOR RSS COLLECTION COMPLETE!")
    print("="*60)
    
    print("\n📊 Summary by Sector:")
    for sector, stats in all_stats.items():
        sector_info = get_sector_info(sector)
        print(f"   {sector_info['icon']} {sector_info['name']:12s}: {stats['unique_posts']:3d} posts")
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total Unique Posts:   {total_unique}")
    print(f"   Total Duplicates:     {total_duplicates}")
    print(f"   Total Processed:      {total_processed}")
    print(f"   Duplicate Rate:       {duplicate_rate}%")
    print("="*60 + "\n")
    
    return {
        'by_sector': all_stats,
        'total_unique': total_unique,
        'total_duplicates': total_duplicates,
        'total_processed': total_processed,
        'duplicate_rate': duplicate_rate
    }

# Test the collector
if __name__ == "__main__":
    print("🚀 Starting Multi-Sector RSS Collector...")
    stats = collect_all_sectors_rss()
    
    print("\n📊 Final Report:")
    print(f"   Sectors Collected: {len(stats['by_sector'])}")
    print(f"   Total New Posts:   {stats['total_unique']}")
    print(f"   Duplicate Rate:    {stats['duplicate_rate']}%")
    print("\n✅ Collection Complete!")