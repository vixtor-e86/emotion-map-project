"""
location_extractor.py
---------------------
Extracts city and continent from post text using NER.
Does NOT use Geopy (too slow) - uses continent mapping dictionary.

Usage:
    python backend/processing/location_extractor.py
"""

import sys
import os
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from transformers import pipeline
    from database.db_manager import db
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Install with: pip install transformers torch")
    sys.exit(1)

# Initialize NER pipeline (loads once)
print("🔄 Loading NER model (dslim/bert-base-NER)...")
try:
    ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)
    print("✅ Model loaded successfully!\n")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    sys.exit(1)

# Continent mapping (country → continent)
CONTINENT_MAP = {
    # Africa
    'Nigeria': 'Africa', 'South Africa': 'Africa', 'Egypt': 'Africa',
    'Kenya': 'Africa', 'Ghana': 'Africa', 'Ethiopia': 'Africa',
    'Morocco': 'Africa', 'Algeria': 'Africa', 'Tunisia': 'Africa',
    'Tanzania': 'Africa', 'Uganda': 'Africa', 'Zimbabwe': 'Africa',
    
    # Asia
    'China': 'Asia', 'India': 'Asia', 'Japan': 'Asia',
    'South Korea': 'Asia', 'Indonesia': 'Asia', 'Thailand': 'Asia',
    'Vietnam': 'Asia', 'Philippines': 'Asia', 'Pakistan': 'Asia',
    'Bangladesh': 'Asia', 'Malaysia': 'Asia', 'Singapore': 'Asia',
    'Israel': 'Asia', 'Saudi Arabia': 'Asia', 'UAE': 'Asia',
    'Turkey': 'Asia', 'Iran': 'Asia', 'Iraq': 'Asia',
    
    # Europe
    'United Kingdom': 'Europe', 'UK': 'Europe', 'France': 'Europe',
    'Germany': 'Europe', 'Italy': 'Europe', 'Spain': 'Europe',
    'Netherlands': 'Europe', 'Belgium': 'Europe', 'Switzerland': 'Europe',
    'Sweden': 'Europe', 'Norway': 'Europe', 'Denmark': 'Europe',
    'Poland': 'Europe', 'Austria': 'Europe', 'Greece': 'Europe',
    'Portugal': 'Europe', 'Finland': 'Europe', 'Ireland': 'Europe',
    'Russia': 'Europe', 'Ukraine': 'Europe', 'Czech Republic': 'Europe',
    
    # North America
    'United States': 'North America', 'USA': 'North America',
    'Canada': 'North America', 'Mexico': 'North America',
    'Cuba': 'North America', 'Jamaica': 'North America',
    'Haiti': 'North America', 'Dominican Republic': 'North America',
    
    # South America
    'Brazil': 'South America', 'Argentina': 'South America',
    'Colombia': 'South America', 'Chile': 'South America',
    'Peru': 'South America', 'Venezuela': 'South America',
    'Ecuador': 'South America', 'Bolivia': 'South America',
    
    # Oceania
    'Australia': 'Oceania', 'New Zealand': 'Oceania',
    'Fiji': 'Oceania', 'Papua New Guinea': 'Oceania',
}

def extract_cities_from_text(text: str) -> list:
    """
    Extract city/location names from text using NER.
    
    Args:
        text: Text to analyze
    
    Returns:
        list: List of city names found (empty if none)
    """
    if not text or len(text.strip()) < 10:
        return []
    
    try:
        results = ner_pipeline(text)
        
        cities = []
        for entity in results:
            # Look for LOC (Location) or GPE (Geo-Political Entity)
            if entity.get('entity_group') in ['LOC', 'GPE']:
                city_name = entity['word'].strip()
                
                # Filter out countries (we already have those)
                if city_name not in CONTINENT_MAP:
                    cities.append(city_name)
        
        return cities if cities else []
        
    except Exception as e:
        return []

def get_continent(country: str) -> str:
    """
    Get continent for a country.
    
    Args:
        country: Country name
    
    Returns:
        str: Continent name or None
    """
    if not country:
        return None
    
    # Direct lookup
    continent = CONTINENT_MAP.get(country)
    if continent:
        return continent
    
    # Try case-insensitive match
    for country_key, cont in CONTINENT_MAP.items():
        if country.lower() == country_key.lower():
            return cont
    
    return None

def process_posts(silent: bool = False):
    """
    Process all posts without location data.
    
    Args:
        silent: If True, minimal output (for background tasks)
    """
    
    if not silent:
        print("\n" + "="*60)
        print("LOCATION EXTRACTOR")
        print("="*60)
    
    # Get posts without city/continent
    posts = db.get_posts_without_location()
    
    if not posts:
        if not silent:
            print("No posts needing location extraction")
        return 0
    
    total = len(posts)
    if not silent:
        print(f"Processing {total} posts...")
    
    # Progress tracking
    processed = 0
    cities_found = 0
    continents_added = 0
    start_time = datetime.now()
    
    for i, post in enumerate(posts, 1):
        try:
            # Extract cities from text
            cities = extract_cities_from_text(post['text'])
            city = cities[0] if cities else None
            
            # Get continent from country (already in DB)
            country = post.get('country')
            continent = get_continent(country) if country else None
            
            # Update database
            if city or continent:
                db.update_post_location(post['id'], city, country, continent)
                processed += 1
                if city:
                    cities_found += 1
                if continent:
                    continents_added += 1
            
            # Progress indicator (every 200 posts)
            if not silent and (i % 200 == 0 or i == total):
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = i / elapsed if elapsed > 0 else 0
                print(f"  [{i}/{total}] Rate: {rate:.1f}/s")
        
        except Exception as e:
            if not silent:
                print(f"  Error on post {post['id']}: {e}")
            continue
    
    # Final statistics
    elapsed = (datetime.now() - start_time).total_seconds()
    if not silent:
        print(f"\nProcessed {processed} posts in {elapsed:.1f}s")
        print(f"Cities: {cities_found}, Continents: {continents_added}")
        print("="*60)
    
    return processed

if __name__ == '__main__':
    try:
        process_posts()
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()