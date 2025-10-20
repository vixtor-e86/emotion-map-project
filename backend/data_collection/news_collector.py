"""
news_collector.py
-----------------
Collects news headlines from NewsData.io API covering 32 countries.
"""

import requests
import time
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import db
from config import Config

# 32 Countries
COUNTRIES = [
    'us', 'ca', 'mx',  # North America
    'br', 'ar', 'co', 've',  # South America
    'gb', 'de', 'fr', 'it', 'es', 'ru', 'pl', 'nl', 'se', 'no',  # Europe
    'cn', 'in', 'jp', 'kr', 'id', 'th', 'sg', 'my',  # Asia
    'za', 'ng', 'eg', 'ma', 'ke', 'tz', 'et', 'gh',  # Africa
    'au', 'nz'  # Oceania
]

COUNTRY_NAMES = {
    'us': 'United States', 'ca': 'Canada', 'mx': 'Mexico',
    'br': 'Brazil', 'ar': 'Argentina', 'co': 'Colombia', 've': 'Venezuela',
    'gb': 'United Kingdom', 'de': 'Germany', 'fr': 'France', 'it': 'Italy',
    'es': 'Spain', 'ru': 'Russia', 'pl': 'Poland', 'nl': 'Netherlands',
    'se': 'Sweden', 'no': 'Norway', 'cn': 'China', 'in': 'India',
    'jp': 'Japan', 'kr': 'South Korea', 'id': 'Indonesia', 'th': 'Thailand',
    'sg': 'Singapore', 'my': 'Malaysia', 'za': 'South Africa', 'ng': 'Nigeria',
    'eg': 'Egypt', 'ma': 'Morocco', 'ke': 'Kenya', 'tz': 'Tanzania',
    'et': 'Ethiopia', 'gh': 'Ghana', 'au': 'Australia', 'nz': 'New Zealand'
}

API_URL = "https://newsdata.io/api/1/news"

def collect_news_data():
    """
    Collect news from NewsData.io and save to database.
    Returns: Number of posts collected
    """
    api_key = Config.NEWSDATA_API_KEY
    
    if not api_key or api_key == "":
        print("❌ NEWS_API_KEY not found in .env file!")
        return 0
    
    total_posts = 0
    successful = 0
    failed = 0
    
    print(f"\n📰 Starting News API collection from {len(COUNTRIES)} countries...\n")
    
    for idx, country_code in enumerate(COUNTRIES, 1):
        country_name = COUNTRY_NAMES.get(country_code, country_code.upper())
        print(f"[{idx}/{len(COUNTRIES)}] 📡 {country_name}...", end=' ')
        
        try:
            response = requests.get(
                API_URL,
                params={
                    'apikey': api_key,
                    'country': country_code,
                    'language': 'en'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    articles = data.get('results', [])
                    
                    for article in articles:
                        try:
                            text = f"{article.get('title', '')}. {article.get('description', '')}".strip()
                            
                            # Save to database
                            db.insert_raw_post(
                                text=text,
                                source=f"NewsAPI-{country_name}",
                                country=country_name,
                                sentiment=None,
                                sentiment_score=None
                            )
                            
                            total_posts += 1
                            
                        except Exception as e:
                            print(f"\n❌ Error saving article: {e}")
                            continue
                    
                    print(f"✅ {len(articles)} articles")
                    successful += 1
                    
                else:
                    print(f"⚠️ API error")
                    failed += 1
            
            elif response.status_code == 429:
                print(f"⚠️ Rate limit reached! Stopping.")
                break
            
            else:
                print(f"⚠️ HTTP {response.status_code}")
                failed += 1
            
            # Respectful delay
            time.sleep(2)
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"✅ News API Collection Complete!")
    print(f"{'='*60}")
    print(f"📊 Total articles: {total_posts}")
    print(f"✅ Successful countries: {successful}/{len(COUNTRIES)}")
    print(f"❌ Failed countries: {failed}")
    print(f"{'='*60}\n")
    
    return total_posts

# Test the collector
if __name__ == "__main__":
    print("🚀 Starting News API Collector Test...")
    count = collect_news_data()
    print(f"✅ Test Complete: {count} posts collected")