"""
rss_collector.py
----------------
Collects news data from multiple RSS feeds across the world,
standardizes the format, and stores in database WITH DUPLICATE DETECTION.
"""
    
import feedparser
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import db

# 🌍 RSS feeds from different regions
RSS_FEEDS = {
    "BBC World News": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Reuters": "http://feeds.reuters.com/reuters/topNews",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "NHK World": "https://www3.nhk.or.jp/rss/news/cat0.xml",
    "CNN": "http://rss.cnn.com/rss/edition_world.rss",
    # "The Guardian": "https://www.theguardian.com/world/rss",
    "DW": "https://rss.dw.com/rdf/rss-en-all",
    "France 24": "https://www.france24.com/en/rss",
    "Infobae": "https://www.infobae.com/america/rss.xml",
    "The Times of India": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "ABC Australia": "https://www.abc.net.au/news/feed/51120/rss.xml",
    # "CBC Canada": "https://www.cbc.ca/cmlink/rss-world",
    "Sky News": "https://feeds.skynews.com/feeds/rss/world.xml",
    "New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "The Independent (UK)": "https://www.independent.co.uk/news/world/rss",
    "Africa News": "https://www.africanews.com/feed/",
    "The Hindu": "https://www.thehindu.com/news/international/feeder/default.rss",
    "ARAB News": "https://www.arabnews.com/rss.xml",
    "Russia Today": "https://www.rt.com/rss/news/",
    "China Daily": "https://www.chinadaily.com.cn/rss/world_rss.xml",
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
        "BBC": "United Kingdom",
        "Reuters": "International",
        "CNN": "United States",
        "Al Jazeera": "Qatar",
        "NHK": "Japan",
        "DW": "Germany",
        "France 24": "France",
        "Times of India": "India",
        "ABC Australia": "Australia",
        "CBC": "Canada",
        "Africa News": "International",
        "ARAB": "Saudi Arabia",
        "Russia Today": "Russia",
        "China Daily": "China",
        "Guardian": "United Kingdom",
        "Sky News": "United Kingdom",
        "New York Times": "United States",
        "Independent": "United Kingdom",
        "Hindu": "India",
        "Infobae": "Argentina",
    }
    for key, country in mapping.items():
        if key.lower() in source.lower():
            return country
    return "International"

def collect_rss_data():
    """
    Collect data from all RSS feeds and save to database with duplicate detection.
    Returns: Dictionary with collection statistics
    """
    total_posts = 0
    duplicate_posts = 0
    
    print(f"\n📡 Starting RSS data collection from {len(RSS_FEEDS)} feeds...\n")
    
    for source, url in RSS_FEEDS.items():
        print(f"📡 Fetching: {source}...", end=' ')
        entries = parse_feed(url)
        
        feed_posts = 0
        feed_duplicates = 0
        
        for entry in entries:
            try:
                text = entry.get("title", "No title available")
                country = guess_country_from_source(source)
                
                # Save to database (duplicate detection is automatic!)
                post_id = db.insert_raw_post(
                    text=text,
                    source=f"RSS-{source}",
                    country=country,
                    emotion=None,  # Will be analyzed later
                    emotion_score=None  # Will be analyzed later
                )
                
                if post_id is None:
                    # Post was a duplicate
                    duplicate_posts += 1
                    feed_duplicates += 1
                else:
                    # Post was unique and saved
                    total_posts += 1
                    feed_posts += 1
                
            except Exception as e:
                print(f"\n❌ Error saving post from {source}: {e}")
                continue
        
        print(f"✅ {feed_posts} new, {feed_duplicates} duplicates (Total: {total_posts} unique)")
    
    # Calculate statistics
    total_processed = total_posts + duplicate_posts
    duplicate_rate = round((duplicate_posts / total_processed * 100), 1) if total_processed > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"✅ RSS Collection Complete!")
    print(f"{'='*60}")
    print(f"📊 Unique Posts Saved:    {total_posts}")
    print(f"🔄 Duplicates Skipped:    {duplicate_posts}")
    print(f"📈 Total Processed:       {total_processed}")
    print(f"📉 Duplicate Rate:        {duplicate_rate}%")
    print(f"{'='*60}\n")
    
    return {
        'unique_posts': total_posts,
        'duplicates': duplicate_posts,
        'total_processed': total_processed,
        'duplicate_rate': duplicate_rate
    }

# Test the collector independently
if __name__ == "__main__":
    print("🚀 Starting RSS Collector Test with Duplicate Detection...")
    stats = collect_rss_data()
    print(f"\n📊 Final Statistics:")
    print(f"   Unique Posts:     {stats['unique_posts']}")
    print(f"   Duplicates:       {stats['duplicates']}")
    print(f"   Duplicate Rate:   {stats['duplicate_rate']}%")
    print("\n✅ Test Complete!")