"""
rss_collector.py (FINANCE EDITION)
-----------------------------------
Collects news from FINANCE-SPECIFIC RSS feeds + filters general news for finance content.
Hybrid approach: Keep general feeds but prioritize finance content.
"""
    
import feedparser
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import db
from processing.finance_config import (
    FINANCE_RSS_FEEDS, 
    is_finance_related,
    extract_tickers
)

# Original general feeds (we'll filter these for finance content)
GENERAL_RSS_FEEDS = {
    "BBC World News": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Reuters": "http://feeds.reuters.com/reuters/topNews",
    "CNN": "http://rss.cnn.com/rss/edition_world.rss",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
}

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
        "Bloomberg": "United States",
        "MarketWatch": "United States",
        "CNBC": "United States",
        "Reuters": "International",
        "WSJ": "United States",
        "CoinDesk": "International",
        "Cointelegraph": "International",
        "Financial Times": "United Kingdom",
        "Forbes": "United States",
        "Seeking Alpha": "United States",
        "Motley Fool": "United States",
        "Benzinga": "United States",
        "BBC": "United Kingdom",
        "CNN": "United States",
        "Al Jazeera": "Qatar",
    }
    for key, country in mapping.items():
        if key.lower() in source.lower():
            return country
    return "International"

def collect_rss_data():
    """
    Collect data from finance RSS feeds + filter general feeds for finance content.
    Returns: Dictionary with collection statistics
    """
    total_posts = 0
    duplicate_posts = 0
    finance_posts = 0
    filtered_posts = 0
    
    print(f"\n📡 Starting FINANCE RSS data collection...\n")
    
    # ===== PART 1: Finance-Specific Feeds (Always save) =====
    print("=" * 60)
    print("🎯 FINANCE-SPECIFIC FEEDS")
    print("=" * 60)
    
    for source, url in FINANCE_RSS_FEEDS.items():
        print(f"📡 Fetching: {source}...", end=' ')
        entries = parse_feed(url)
        
        feed_posts = 0
        feed_duplicates = 0
        
        for entry in entries:
            try:
                text = entry.get("title", "No title available")
                country = guess_country_from_source(source)
                
                # Extract tickers if present
                tickers = extract_tickers(text)
                ticker_text = f" [{', '.join(tickers)}]" if tickers else ""
                
                # Save to database
                post_id = db.insert_raw_post(
                    text=text + ticker_text,
                    source=f"Finance-RSS-{source}",
                    country=country,
                    emotion=None,
                    emotion_score=None
                )
                
                if post_id is None:
                    duplicate_posts += 1
                    feed_duplicates += 1
                else:
                    total_posts += 1
                    finance_posts += 1
                    feed_posts += 1
                
            except Exception as e:
                print(f"\n❌ Error saving post from {source}: {e}")
                continue
        
        print(f"✅ {feed_posts} new, {feed_duplicates} duplicates")
    
    # ===== PART 2: General Feeds (Filter for finance) =====
    print("\n" + "=" * 60)
    print("🔍 GENERAL FEEDS (Finance Filter)")
    print("=" * 60)
    
    for source, url in GENERAL_RSS_FEEDS.items():
        print(f"📡 Fetching: {source}...", end=' ')
        entries = parse_feed(url)
        
        feed_posts = 0
        feed_duplicates = 0
        feed_filtered = 0
        
        for entry in entries:
            try:
                text = entry.get("title", "No title available")
                
                # FILTER: Only save if finance-related
                if not is_finance_related(text):
                    feed_filtered += 1
                    filtered_posts += 1
                    continue
                
                country = guess_country_from_source(source)
                tickers = extract_tickers(text)
                ticker_text = f" [{', '.join(tickers)}]" if tickers else ""
                
                post_id = db.insert_raw_post(
                    text=text + ticker_text,
                    source=f"General-RSS-{source}",
                    country=country,
                    emotion=None,
                    emotion_score=None
                )
                
                if post_id is None:
                    duplicate_posts += 1
                    feed_duplicates += 1
                else:
                    total_posts += 1
                    finance_posts += 1
                    feed_posts += 1
                
            except Exception as e:
                print(f"\n❌ Error saving post from {source}: {e}")
                continue
        
        print(f"✅ {feed_posts} new, {feed_duplicates} dup, {feed_filtered} filtered")
    
    # Calculate statistics
    total_processed = total_posts + duplicate_posts + filtered_posts
    duplicate_rate = round((duplicate_posts / total_processed * 100), 1) if total_processed > 0 else 0
    finance_rate = round((finance_posts / total_posts * 100), 1) if total_posts > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"✅ Finance RSS Collection Complete!")
    print(f"{'='*60}")
    print(f"📊 Finance Posts Saved:   {finance_posts}")
    print(f"📈 Total Unique Posts:    {total_posts}")
    print(f"🔄 Duplicates Skipped:    {duplicate_posts}")
    print(f"🚫 Filtered Out:          {filtered_posts}")
    print(f"📉 Duplicate Rate:        {duplicate_rate}%")
    print(f"🎯 Finance Rate:          {finance_rate}%")
    print(f"{'='*60}\n")
    
    return {
        'unique_posts': total_posts,
        'finance_posts': finance_posts,
        'duplicates': duplicate_posts,
        'filtered': filtered_posts,
        'total_processed': total_processed,
        'duplicate_rate': duplicate_rate,
        'finance_rate': finance_rate
    }

# Test the collector
if __name__ == "__main__":
    print("🚀 Starting Finance RSS Collector Test...")
    stats = collect_rss_data()
    print(f"\n📊 Final Statistics:")
    print(f"   Finance Posts:    {stats['finance_posts']}")
    print(f"   Total Unique:     {stats['unique_posts']}")
    print(f"   Duplicates:       {stats['duplicates']}")
    print(f"   Filtered:         {stats['filtered']}")
    print(f"   Finance Rate:     {stats['finance_rate']}%")
    print("\n✅ Test Complete!")