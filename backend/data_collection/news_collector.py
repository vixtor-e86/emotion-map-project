"""
news_collector.py
-----------------
Collects news headlines from NewsData.io API covering 32 countries
WITH DUPLICATE DETECTION.
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
    Collect news from NewsData.io and save to database with duplicate detection.
    Returns: Dictionary with collection statistics
    """
    api_key = Config.NEWSDATA_API_KEY
    
    if not api_key or api_key == "":
        print("❌ NEWS_API_KEY not found in .env file!")
        return {
            'unique_posts': 0,
            'duplicates': 0,
            'total_processed': 0,
            'duplicate_rate': 0,
            'successful_countries': 0,
            'failed_countries': 0
        }
    
    total_posts = 0
    duplicate_posts = 0
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
                    country_posts = 0
                    country_duplicates = 0
                    
                    for article in articles:
                        try:
                            text = f"{article.get('title', '')}. {article.get('description', '')}".strip()
                            
                            # Save to database (duplicate detection is automatic!)
                            post_id = db.insert_raw_post(
                                text=text,
                                source=f"NewsAPI-{country_name}",
                                country=country_name,
                                emotion=None,  # Will be analyzed later
                                emotion_score=None  # Will be analyzed later
                            )
                            
                            if post_id is None:
                                # Post was a duplicate
                                duplicate_posts += 1
                                country_duplicates += 1
                            else:
                                # Post was unique and saved
                                total_posts += 1
                                country_posts += 1
                            
                        except Exception as e:
                            print(f"\n❌ Error saving article: {e}")
                            continue
                    
                    print(f"✅ {country_posts} new, {country_duplicates} duplicates")
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
    
    # Calculate statistics
    total_processed = total_posts + duplicate_posts
    duplicate_rate = round((duplicate_posts / total_processed * 100), 1) if total_processed > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"✅ News API Collection Complete!")
    print(f"{'='*60}")
    print(f"📊 Unique Posts Saved:    {total_posts}")
    print(f"🔄 Duplicates Skipped:    {duplicate_posts}")
    print(f"📈 Total Processed:       {total_processed}")
    print(f"📉 Duplicate Rate:        {duplicate_rate}%")
    print(f"✅ Successful countries:  {successful}/{len(COUNTRIES)}")
    print(f"❌ Failed countries:      {failed}")
    print(f"{'='*60}\n")
    
    return {
        'unique_posts': total_posts,
        'duplicates': duplicate_posts,
        'total_processed': total_processed,
        'duplicate_rate': duplicate_rate,
        'successful_countries': successful,
        'failed_countries': failed
    }

# Test the collector
if __name__ == "__main__":
    print("🚀 Starting News API Collector Test with Duplicate Detection...")
    stats = collect_news_data()
    print(f"\n📊 Final Statistics:")
    print(f"   Unique Posts:     {stats['unique_posts']}")
    print(f"   Duplicates:       {stats['duplicates']}")
    print(f"   Duplicate Rate:   {stats['duplicate_rate']}%")
    print(f"   Successful:       {stats['successful_countries']}")
    print(f"   Failed:           {stats['failed_countries']}")
    print("\n✅ Test Complete!")