"""
news_collector.py (MULTI-SECTOR EDITION)
-----------------------------------------
Collects news from NewsData.io API with AUTOMATIC SECTOR DETECTION.
Each article is analyzed and tagged with appropriate sector.
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
from processing.sector_config import detect_sector, get_sector_info

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
    Collect news from NewsData.io with AUTOMATIC SECTOR DETECTION.
    Each article is analyzed and tagged with appropriate sector.
    
    Returns: Dictionary with collection statistics by sector
    """
    api_key = Config.NEWSDATA_API_KEY
    
    if not api_key or api_key == "":
        print("❌ NEWS_API_KEY not found in .env file!")
        return {
            'unique_posts': 0,
            'duplicates': 0,
            'total_processed': 0,
            'by_sector': {},
            'duplicate_rate': 0
        }
    
    total_posts = 0
    duplicate_posts = 0
    successful = 0
    failed = 0
    sector_counts = {'finance': 0, 'health': 0, 'technology': 0, 'sports': 0, 'general': 0}
    
    print("\n" + "="*60)
    print("📰 NEWS API COLLECTION (Multi-Sector)")
    print("="*60)
    print(f"Collecting from {len(COUNTRIES)} countries...\n")
    
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
                            title = article.get('title', '')
                            description = article.get('description', '')
                            text = f"{title}. {description}".strip()
                            
                            # Detect sector from content
                            sector = detect_sector(text)
                            
                            # Save to database with SECTOR tag
                            post_id = db.insert_raw_post(
                                text=text,
                                source=f"News-{country_name}",
                                country=country_name,
                                emotion=None,
                                emotion_score=None,
                                sector=sector  # ← SECTOR TAG!
                            )
                            
                            if post_id is None:
                                duplicate_posts += 1
                                country_duplicates += 1
                            else:
                                total_posts += 1
                                country_posts += 1
                                sector_counts[sector] += 1
                            
                        except Exception as e:
                            continue
                    
                    print(f"✅ {country_posts} new, {country_duplicates} dup")
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
            print(f"❌ Error: {str(e)[:50]}")
            failed += 1
    
    # Calculate statistics
    total_processed = total_posts + duplicate_posts
    duplicate_rate = round((duplicate_posts / total_processed * 100), 1) if total_processed > 0 else 0
    
    print("\n" + "="*60)
    print("✅ NEWS API COLLECTION COMPLETE!")
    print("="*60)
    
    print("\n📊 Posts by Sector:")
    for sector, count in sorted(sector_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            info = get_sector_info(sector)
            percentage = (count / total_posts * 100) if total_posts > 0 else 0
            print(f"   {info.get('icon', '🌐')} {info.get('name', sector):12s}: {count:3d} ({percentage:5.1f}%)")
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total Unique Posts:   {total_posts}")
    print(f"   Total Duplicates:     {duplicate_posts}")
    print(f"   Total Processed:      {total_processed}")
    print(f"   Duplicate Rate:       {duplicate_rate}%")
    print(f"   Successful Countries: {successful}/{len(COUNTRIES)}")
    print(f"   Failed Countries:     {failed}")
    print("="*60 + "\n")
    
    return {
        'unique_posts': total_posts,
        'duplicates': duplicate_posts,
        'total_processed': total_processed,
        'by_sector': sector_counts,
        'duplicate_rate': duplicate_rate,
        'successful_countries': successful,
        'failed_countries': failed
    }

# Test the collector
if __name__ == "__main__":
    print("🚀 Starting Multi-Sector News API Collector...")
    stats = collect_news_data()
    
    print("\n📊 Final Report:")
    print(f"   Total New Posts:      {stats['unique_posts']}")
    print(f"   Duplicates:           {stats['duplicates']}")
    print(f"   Duplicate Rate:       {stats['duplicate_rate']}%")
    print(f"   Successful Countries: {stats['successful_countries']}")
    print(f"   Failed Countries:     {stats['failed_countries']}")
    print("\n✅ Collection Complete!")