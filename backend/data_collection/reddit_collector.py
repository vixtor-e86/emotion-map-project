"""
reddit_collector.py (FINANCE EDITION)
--------------------------------------
Collects from FINANCE-SPECIFIC subreddits + filters general subs for finance content.
Hybrid approach: Keep general subs but prioritize finance discussions.
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
from processing.finance_config import (
    FINANCE_SUBREDDITS,
    is_finance_related,
    extract_tickers
)

# General subreddits (we'll filter for finance content)
GENERAL_SUBREDDITS = [
    "worldnews", "news", "technology", "business",
    "usa", "unitedkingdom", "canada", "europe"
]

# Map subreddit to country
SUBREDDIT_COUNTRY_MAP = {
    # Finance-specific
    "wallstreetbets": "United States",
    "stocks": "International",
    "investing": "International",
    "StockMarket": "United States",
    "CryptoCurrency": "International",
    "Bitcoin": "International",
    "ethereum": "International",
    "Daytrading": "International",
    "swingtrading": "International",
    "options": "United States",
    "personalfinance": "United States",
    "CanadianInvestor": "Canada",
    "UKInvesting": "United Kingdom",
    "IndiaInvestments": "India",
    
    # General
    "worldnews": "International",
    "news": "International",
    "technology": "International",
    "business": "International",
    "usa": "United States",
    "unitedkingdom": "United Kingdom",
    "canada": "Canada",
    "europe": "International"
}

def create_reddit_instance():
    """Create Reddit API instance using credentials from .env"""
    reddit = praw.Reddit(
        client_id=Config.REDDIT_CLIENT_ID,
        client_secret=Config.REDDIT_CLIENT_SECRET,
        user_agent=Config.REDDIT_USER_AGENT
    )
    return reddit

def collect_reddit_data(limit_per_sub=50, retries=2):
    """
    Collect finance data from Reddit with filtering.
    Returns: Dictionary with collection statistics
    """
    reddit = create_reddit_instance()
    total_posts = 0
    duplicate_posts = 0
    finance_posts = 0
    filtered_posts = 0
    skipped_subreddits = []
    
    print(f"\n📱 Starting FINANCE Reddit collection...\n")
    
    # ===== PART 1: Finance-Specific Subreddits (Always save) =====
    print("=" * 60)
    print("🎯 FINANCE-SPECIFIC SUBREDDITS")
    print("=" * 60)
    
    for sub in FINANCE_SUBREDDITS:
        attempt = 0
        while attempt <= retries:
            try:
                subreddit = reddit.subreddit(sub)
                print(f"📡 Collecting from r/{sub}...")
                
                sub_posts = 0
                sub_duplicates = 0
                
                for post in subreddit.hot(limit=limit_per_sub):
                    try:
                        country = SUBREDDIT_COUNTRY_MAP.get(sub, "International")
                        
                        # Extract tickers
                        text = post.title
                        tickers = extract_tickers(text)
                        ticker_text = f" [{', '.join(tickers)}]" if tickers else ""
                        
                        # Save to database
                        post_id = db.insert_raw_post(
                            text=text + ticker_text,
                            source=f"Finance-Reddit-r/{sub}",
                            country=country,
                            emotion=None,
                            emotion_score=None
                        )
                        
                        if post_id is None:
                            duplicate_posts += 1
                            sub_duplicates += 1
                        else:
                            total_posts += 1
                            finance_posts += 1
                            sub_posts += 1
                        
                    except Exception as e:
                        print(f"❌ Error saving post from r/{sub}: {e}")
                        continue
                
                print(f"✅ r/{sub}: {sub_posts} new, {sub_duplicates} duplicates")
                time.sleep(random.uniform(2, 4))
                break
                
            except prawcore.exceptions.Forbidden:
                print(f"⚠️ Skipping r/{sub}: Access forbidden (403)")
                skipped_subreddits.append(f"{sub} - Forbidden (403)")
                break
                
            except Exception as e:
                attempt += 1
                print(f"❌ Error fetching r/{sub} (attempt {attempt}): {e}")
                if attempt > retries:
                    skipped_subreddits.append(f"{sub} - Failed after retries")
                    break
                else:
                    time.sleep(3)
    
    # ===== PART 2: General Subreddits (Filter for finance) =====
    print("\n" + "=" * 60)
    print("🔍 GENERAL SUBREDDITS (Finance Filter)")
    print("=" * 60)
    
    for sub in GENERAL_SUBREDDITS:
        attempt = 0
        while attempt <= retries:
            try:
                subreddit = reddit.subreddit(sub)
                print(f"📡 Collecting from r/{sub}...")
                
                sub_posts = 0
                sub_duplicates = 0
                sub_filtered = 0
                
                for post in subreddit.hot(limit=limit_per_sub):
                    try:
                        text = post.title
                        
                        # FILTER: Only save if finance-related
                        if not is_finance_related(text):
                            sub_filtered += 1
                            filtered_posts += 1
                            continue
                        
                        country = SUBREDDIT_COUNTRY_MAP.get(sub, "International")
                        tickers = extract_tickers(text)
                        ticker_text = f" [{', '.join(tickers)}]" if tickers else ""
                        
                        post_id = db.insert_raw_post(
                            text=text + ticker_text,
                            source=f"General-Reddit-r/{sub}",
                            country=country,
                            emotion=None,
                            emotion_score=None
                        )
                        
                        if post_id is None:
                            duplicate_posts += 1
                            sub_duplicates += 1
                        else:
                            total_posts += 1
                            finance_posts += 1
                            sub_posts += 1
                        
                    except Exception as e:
                        print(f"❌ Error saving post from r/{sub}: {e}")
                        continue
                
                print(f"✅ r/{sub}: {sub_posts} new, {sub_duplicates} dup, {sub_filtered} filtered")
                time.sleep(random.uniform(2, 4))
                break
                
            except prawcore.exceptions.Forbidden:
                print(f"⚠️ Skipping r/{sub}: Access forbidden (403)")
                skipped_subreddits.append(f"{sub} - Forbidden (403)")
                break
                
            except Exception as e:
                attempt += 1
                print(f"❌ Error fetching r/{sub} (attempt {attempt}): {e}")
                if attempt > retries:
                    skipped_subreddits.append(f"{sub} - Failed after retries")
                    break
                else:
                    time.sleep(3)
    
    # Log skipped subreddits
    if skipped_subreddits:
        with open("skipped_subreddits.log", "w") as log_file:
            log_file.write("\n".join(skipped_subreddits))
        print(f"\n⚠️ Logged {len(skipped_subreddits)} skipped subreddits")
    
    # Calculate statistics
    total_processed = total_posts + duplicate_posts + filtered_posts
    duplicate_rate = round((duplicate_posts / total_processed * 100), 1) if total_processed > 0 else 0
    finance_rate = round((finance_posts / total_posts * 100), 1) if total_posts > 0 else 0
    
    print(f"\n" + "="*60)
    print(f"✅ Finance Reddit Collection Complete!")
    print(f"="*60)
    print(f"📊 Finance Posts Saved:   {finance_posts}")
    print(f"📈 Total Unique Posts:    {total_posts}")
    print(f"🔄 Duplicates Skipped:    {duplicate_posts}")
    print(f"🚫 Filtered Out:          {filtered_posts}")
    print(f"📉 Duplicate Rate:        {duplicate_rate}%")
    print(f"🎯 Finance Rate:          {finance_rate}%")
    print(f"⚠️  Skipped Subreddits:   {len(skipped_subreddits)}")
    print(f"="*60 + "\n")
    
    return {
        'unique_posts': total_posts,
        'finance_posts': finance_posts,
        'duplicates': duplicate_posts,
        'filtered': filtered_posts,
        'total_processed': total_processed,
        'duplicate_rate': duplicate_rate,
        'finance_rate': finance_rate,
        'skipped_subreddits': len(skipped_subreddits)
    }

# Test the collector
if __name__ == "__main__":
    print("🚀 Starting Finance Reddit Collector Test...")
    stats = collect_reddit_data(limit_per_sub=20)
    
    print("\n📊 Final Statistics:")
    print(f"   Finance Posts:    {stats['finance_posts']}")
    print(f"   Total Unique:     {stats['unique_posts']}")
    print(f"   Duplicates:       {stats['duplicates']}")
    print(f"   Filtered:         {stats['filtered']}")
    print(f"   Finance Rate:     {stats['finance_rate']}%")
    print(f"   Skipped Subs:     {stats['skipped_subreddits']}")
    print("\n✅ Test Complete!")