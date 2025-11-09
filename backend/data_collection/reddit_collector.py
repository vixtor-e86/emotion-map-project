"""
reddit_collector.py (MULTI-SECTOR EDITION)
-------------------------------------------
Collects posts from Reddit for ALL 4 SECTORS:
- Finance, Health, Technology, Sports

Each post is automatically tagged with its sector.
"""

import praw
import prawcore
import time
import random
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import db
from config import Config
from processing.sector_config import (
    SUBREDDITS,
    detect_sector,
    extract_tickers,
    get_sector_info
)

# Map subreddit to country
SUBREDDIT_COUNTRY_MAP = {
    # Finance
    "wallstreetbets": "United States",
    "stocks": "International",
    "investing": "International",
    "StockMarket": "United States",
    "CryptoCurrency": "International",
    "Bitcoin": "International",
    "ethereum": "International",
    
    # Health
    "Health": "International",
    "fitness": "International",
    "nutrition": "International",
    "mentalhealth": "International",
    "medical": "International",
    
    # Technology
    "technology": "International",
    "tech": "International",
    "programming": "International",
    "MachineLearning": "International",
    "cybersecurity": "International",
    
    # Sports
    "sports": "International",
    "soccer": "International",
    "football": "International",
    "nba": "United States",
    "nfl": "United States",
    "PremierLeague": "United Kingdom",
}

def create_reddit_instance():
    """Create Reddit API instance using credentials from .env"""
    reddit = praw.Reddit(
        client_id=Config.REDDIT_CLIENT_ID,
        client_secret=Config.REDDIT_CLIENT_SECRET,
        user_agent=Config.REDDIT_USER_AGENT
    )
    return reddit

def collect_sector_reddit_data(sector: str, reddit, limit_per_sub=30, retries=2):
    """
    Collect Reddit data for a specific sector.
    
    Args:
        sector: Sector name ('finance', 'health', 'technology', 'sports')
        reddit: Reddit API instance
        limit_per_sub: Posts per subreddit
        retries: Number of retries
    
    Returns:
        dict: Collection statistics
    """
    if sector not in SUBREDDITS:
        print(f"❌ Unknown sector: {sector}")
        return None
    
    sector_info = get_sector_info(sector)
    subreddits = SUBREDDITS[sector]
    
    total_posts = 0
    duplicate_posts = 0
    skipped_subreddits = []
    
    print(f"\n{sector_info['icon']} {sector_info['name'].upper()} SUBREDDITS")
    print("=" * 60)
    
    for sub in subreddits:
        attempt = 0
        while attempt <= retries:
            try:
                subreddit = reddit.subreddit(sub)
                print(f"📡 r/{sub}...", end=' ')
                
                sub_posts = 0
                sub_duplicates = 0
                
                for post in subreddit.hot(limit=limit_per_sub):
                    try:
                        text = post.title
                        
                        # Verify sector (skip if wrong sector)
                        detected_sector = detect_sector(text)
                        if detected_sector != sector and detected_sector != 'general':
                            continue
                        
                        country = SUBREDDIT_COUNTRY_MAP.get(sub, "International")
                        
                        # Extract tickers if finance
                        if sector == 'finance':
                            tickers = extract_tickers(text)
                            if tickers:
                                text = text + f" [{', '.join(tickers)}]"
                        
                        # Save to database with SECTOR tag
                        post_id = db.insert_raw_post(
                            text=text,
                            source=f"{sector.capitalize()}-Reddit-r/{sub}",
                            country=country,
                            emotion=None,
                            emotion_score=None,
                            sector=sector  # ← SECTOR TAG!
                        )
                        
                        if post_id is None:
                            duplicate_posts += 1
                            sub_duplicates += 1
                        else:
                            total_posts += 1
                            sub_posts += 1
                        
                    except Exception as e:
                        continue
                
                print(f"✅ {sub_posts} new, {sub_duplicates} dup")
                time.sleep(random.uniform(2, 4))
                break
                
            except prawcore.exceptions.Forbidden:
                print(f"⚠️ Access forbidden (403)")
                skipped_subreddits.append(f"{sub} - Forbidden")
                break
                
            except Exception as e:
                attempt += 1
                if attempt > retries:
                    print(f"❌ Failed after retries")
                    skipped_subreddits.append(f"{sub} - Failed")
                    break
                else:
                    time.sleep(3)
    
    return {
        'sector': sector,
        'unique_posts': total_posts,
        'duplicates': duplicate_posts,
        'skipped': len(skipped_subreddits)
    }

def collect_all_sectors_reddit(limit_per_sub=30):
    """
    Collect Reddit data from ALL 4 SECTORS.
    
    Args:
        limit_per_sub: Posts per subreddit
    
    Returns:
        dict: Statistics for all sectors
    """
    print("\n" + "="*60)
    print("📱 MULTI-SECTOR REDDIT DATA COLLECTION")
    print("="*60)
    
    # Create Reddit instance once
    reddit = create_reddit_instance()
    
    all_stats = {}
    total_unique = 0
    total_duplicates = 0
    total_skipped = 0
    
    # Collect from each sector
    for sector in ['finance', 'health', 'technology', 'sports']:
        stats = collect_sector_reddit_data(sector, reddit, limit_per_sub)
        if stats:
            all_stats[sector] = stats
            total_unique += stats['unique_posts']
            total_duplicates += stats['duplicates']
            total_skipped += stats['skipped']
    
    # Final summary
    total_processed = total_unique + total_duplicates
    duplicate_rate = round((total_duplicates / total_processed * 100), 1) if total_processed > 0 else 0
    
    print("\n" + "="*60)
    print("✅ MULTI-SECTOR REDDIT COLLECTION COMPLETE!")
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
    print(f"   Skipped Subreddits:   {total_skipped}")
    print("="*60 + "\n")
    
    return {
        'by_sector': all_stats,
        'total_unique': total_unique,
        'total_duplicates': total_duplicates,
        'total_processed': total_processed,
        'duplicate_rate': duplicate_rate,
        'total_skipped': total_skipped
    }

# Test the collector
if __name__ == "__main__":
    print("🚀 Starting Multi-Sector Reddit Collector...")
    stats = collect_all_sectors_reddit(limit_per_sub=20)
    
    print("\n📊 Final Report:")
    print(f"   Sectors Collected: {len(stats['by_sector'])}")
    print(f"   Total New Posts:   {stats['total_unique']}")
    print(f"   Duplicate Rate:    {stats['duplicate_rate']}%")
    print(f"   Skipped Subs:      {stats['total_skipped']}")
    print("\n✅ Collection Complete!")