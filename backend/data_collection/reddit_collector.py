"""
reddit_collector.py
-------------------
Collects posts from 50+ global subreddits using Reddit's API (via PRAW)
and saves them to database.
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

# Active Global Subreddits
SUBREDDITS = [
    "worldnews", "news", "AskReddit", "worldpolitics", "TodayILearned", "technology",
    "usa", "canada", "mexico", "northamerica", "nyc", "california",
    "unitedkingdom", "france", "germany", "italy", "spain", "netherlands",
    "sweden", "norway", "poland", "ireland", "portugal", "europe", "switzerland", "finland",
    "nigeria", "southafrica", "ghana", "kenya", "africa", "Egypt", "Morocco",
    "india", "pakistan", "bangladesh", "philippines", "japan", "china",
    "malaysia", "indonesia", "singapore", "vietnam", "thailand", "southkorea",
    "brazil", "argentina", "colombia", "venezuela", "chile", "peru",
    "australia", "newzealand", "oceania"
]

# Map subreddit to country
SUBREDDIT_COUNTRY_MAP = {
    "worldnews": "International", "news": "International", "technology": "International",
    "usa": "United States", "nyc": "United States", "california": "United States",
    "canada": "Canada", "mexico": "Mexico",
    "unitedkingdom": "United Kingdom", "france": "France", "germany": "Germany",
    "italy": "Italy", "spain": "Spain", "netherlands": "Netherlands",
    "sweden": "Sweden", "norway": "Norway", "poland": "Poland",
    "ireland": "Ireland", "portugal": "Portugal", "europe": "International",
    "switzerland": "Switzerland", "finland": "Finland",
    "nigeria": "Nigeria", "southafrica": "South Africa", "ghana": "Ghana",
    "kenya": "Kenya", "africa": "International", "Egypt": "Egypt", "Morocco": "Morocco",
    "india": "India", "pakistan": "Pakistan", "bangladesh": "Bangladesh",
    "philippines": "Philippines", "japan": "Japan", "china": "China",
    "malaysia": "Malaysia", "indonesia": "Indonesia", "singapore": "Singapore",
    "vietnam": "Vietnam", "thailand": "Thailand", "southkorea": "South Korea",
    "brazil": "Brazil", "argentina": "Argentina", "colombia": "Colombia",
    "venezuela": "Venezuela", "chile": "Chile", "peru": "Peru",
    "australia": "Australia", "newzealand": "New Zealand", "oceania": "International"
}

def create_reddit_instance():
    """Create Reddit API instance using credentials from .env"""
    reddit = praw.Reddit(
        client_id=Config.REDDIT_CLIENT_ID,
        client_secret=Config.REDDIT_CLIENT_SECRET,
        user_agent=Config.REDDIT_USER_AGENT
    )
    return reddit

def collect_reddit_data(limit_per_sub=20, retries=2):

    """
    Collect data from Reddit and save to database.
    Returns: Number of posts collected
    """
    reddit = create_reddit_instance()
    total_posts = 0
    skipped_subreddits = []
    
    print(f"\n📱 Starting Reddit data collection from {len(SUBREDDITS)} subreddits...\n")
    
    for sub in SUBREDDITS:
        attempt = 0
        while attempt <= retries:
            try:
                subreddit = reddit.subreddit(sub)
                print(f"📡 Collecting from r/{sub}...")
                
                for post in subreddit.top(time_filter="day", limit=limit_per_sub):
                    try:
                        country = SUBREDDIT_COUNTRY_MAP.get(sub, "International")
                        
                        # Save to database
                        db.insert_raw_post(
                            text=post.title,
                            source=f"Reddit-r/{sub}",
                            country=country,
                            sentiment=None,  # Will be analyzed later
                            sentiment_score=None
                        )
                        
                        total_posts += 1
                        
                    except Exception as e:
                        print(f"❌ Error saving post from r/{sub}: {e}")
                        continue
                
                print(f"✅ r/{sub} complete ({total_posts} total so far)")
                time.sleep(random.uniform(2, 4))  # Rate limit protection
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
    
    print(f"\n✅ Reddit Collection Complete: {total_posts} posts saved to database")
    return total_posts

# Test the collector
if __name__ == "__main__":
    print("🚀 Starting Reddit Collector Test...")
    count = collect_reddit_data(limit_per_sub=20)
    print(f"✅ Test Complete: {count} posts collected")
