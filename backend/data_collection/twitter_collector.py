"""
twitter_collector.py
--------------------
Collects tweets with fallback strategy:
1. Try Twitter API (if you have key)
2. Fall back to sample data (for testing/demo)

Saves directly to database: text, country, source.

MVP Version - Simple & Reliable
Author: PulseNet Team
Date: October 2025
"""

import time
import re
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import db
from config import Config

# Try to import tweepy (Twitter API)
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False

# Emotion-based search queries
SEARCH_QUERIES = [
    'happy lang:en -is:retweet',
    'angry lang:en -is:retweet',
    'sad lang:en -is:retweet',
    'excited lang:en -is:retweet',
    'worried lang:en -is:retweet',
    'hope lang:en -is:retweet',
    'love lang:en -is:retweet',
    'frustrated lang:en -is:retweet',
    'peaceful lang:en -is:retweet',
    'anxious lang:en -is:retweet'
]

TWEETS_PER_QUERY = 30

# Country detection dictionary
COUNTRY_KEYWORDS = {
    'United States': ['usa', 'us', 'america', 'new york', 'los angeles', 'chicago', 'texas', 'california', 'florida', 'washington'],
    'United Kingdom': ['uk', 'britain', 'london', 'england', 'scotland', 'wales', 'manchester', 'birmingham'],
    'Canada': ['canada', 'toronto', 'vancouver', 'montreal', 'ontario', 'quebec'],
    'Australia': ['australia', 'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide'],
    'Germany': ['germany', 'berlin', 'munich', 'hamburg', 'frankfurt', 'cologne'],
    'France': ['france', 'paris', 'lyon', 'marseille', 'toulouse'],
    'Japan': ['japan', 'tokyo', 'osaka', 'kyoto', 'yokohama'],
    'India': ['india', 'mumbai', 'delhi', 'bangalore', 'chennai', 'kolkata'],
    'Brazil': ['brazil', 'brasil', 'sao paulo', 'rio de janeiro', 'brasilia'],
    'Mexico': ['mexico', 'mexico city', 'guadalajara', 'monterrey'],
    'Nigeria': ['nigeria', 'lagos', 'abuja', 'kano', 'ibadan'],
    'South Africa': ['south africa', 'johannesburg', 'cape town', 'durban', 'pretoria'],
    'Spain': ['spain', 'madrid', 'barcelona', 'valencia', 'sevilla'],
    'Italy': ['italy', 'rome', 'milan', 'naples', 'turin'],
    'Russia': ['russia', 'moscow', 'st petersburg', 'novosibirsk'],
    'China': ['china', 'beijing', 'shanghai', 'guangzhou', 'shenzhen'],
    'South Korea': ['korea', 'seoul', 'busan', 'incheon'],
    'Indonesia': ['indonesia', 'jakarta', 'bali', 'surabaya'],
    'Thailand': ['thailand', 'bangkok', 'phuket', 'chiang mai'],
    'Singapore': ['singapore'],
    'Philippines': ['philippines', 'manila', 'cebu'],
    'Argentina': ['argentina', 'buenos aires', 'cordoba'],
    'Colombia': ['colombia', 'bogota', 'medellin', 'cali'],
    'Egypt': ['egypt', 'cairo', 'alexandria', 'giza'],
    'Turkey': ['turkey', 'istanbul', 'ankara', 'izmir'],
    'Poland': ['poland', 'warsaw', 'krakow', 'gdansk'],
    'Netherlands': ['netherlands', 'amsterdam', 'rotterdam', 'the hague'],
    'Sweden': ['sweden', 'stockholm', 'gothenburg', 'malmo'],
    'Norway': ['norway', 'oslo', 'bergen', 'trondheim'],
    'Denmark': ['denmark', 'copenhagen', 'aarhus'],
    'Kenya': ['kenya', 'nairobi', 'mombasa', 'kisumu'],
}


def clean_text(text):
    """Clean tweet text - remove URLs, mentions, hashtags."""
    if not text:
        return ""
    
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = ' '.join(text.split())
    
    return text.strip()


def extract_country(text, user_location):
    """Extract country from tweet text or user location."""
    combined = f"{text} {user_location}".lower()
    
    for country, keywords in COUNTRY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in combined:
                return country
    
    return ""


def collect_from_twitter_api():
    """
    Collect tweets using Twitter API v2.
    Requires TWITTER_BEARER_TOKEN in .env file.
    """
    if not TWEEPY_AVAILABLE:
        return []
    
    bearer_token = getattr(Config, 'TWITTER_BEARER_TOKEN', None)
    
    if not bearer_token or bearer_token == '':
        return []
    
    try:
        client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
    except Exception as e:
        print(f"ERROR: Could not initialize Twitter API: {e}")
        return []
    
    all_tweets = []
    
    for query in SEARCH_QUERIES:
        try:
            response = client.search_recent_tweets(
                query=query,
                max_results=min(TWEETS_PER_QUERY, 100),
                tweet_fields=['created_at', 'author_id', 'text', 'geo'],
                user_fields=['location'],
                expansions=['author_id']
            )
            
            if response.data:
                users = {}
                if response.includes and 'users' in response.includes:
                    users = {u['id']: u for u in response.includes['users']}
                
                for tweet in response.data:
                    user = users.get(tweet.author_id, {})
                    
                    all_tweets.append({
                        'text': tweet.text,
                        'user_location': user.get('location', '') if user else ''
                    })
            
            time.sleep(1)
            
        except Exception as e:
            continue
    
    return all_tweets


def create_sample_data():
    """
    Generate sample Twitter data for testing.
    Used when no API access is available.
    """
    samples = [
        # Happy tweets
        {'text': 'Beautiful sunny day in London! So happy to be outside!', 'location': 'London, UK'},
        {'text': 'Just got promoted at work! Feeling blessed in New York', 'location': 'New York, USA'},
        {'text': 'Amazing concert tonight in Paris! Best night ever!', 'location': 'Paris, France'},
        
        # Angry tweets
        {'text': 'So angry about the traffic in Los Angeles right now!', 'location': 'Los Angeles, USA'},
        {'text': 'Frustrated with the delays in Mumbai today', 'location': 'Mumbai, India'},
        {'text': 'This is ridiculous! Berlin needs better public transport', 'location': 'Berlin, Germany'},
        
        # Sad tweets
        {'text': 'Feeling down today. Missing home in Toronto', 'location': 'Toronto, Canada'},
        {'text': 'Sad news from Tokyo. Sending prayers', 'location': 'Tokyo, Japan'},
        {'text': 'Heartbroken about what happened in Sydney', 'location': 'Sydney, Australia'},
        
        # Excited tweets
        {'text': 'So excited for the festival in Rio de Janeiro!', 'location': 'Rio de Janeiro, Brazil'},
        {'text': 'Cannot wait for tomorrow! Barcelona here I come!', 'location': 'Barcelona, Spain'},
        {'text': 'Thrilled to be visiting Singapore next week!', 'location': 'Singapore'},
        
        # Worried tweets
        {'text': 'Worried about the situation in Lagos right now', 'location': 'Lagos, Nigeria'},
        {'text': 'Anxious about the weather forecast for Miami', 'location': 'Miami, USA'},
        {'text': 'Concerned about the news from Cairo today', 'location': 'Cairo, Egypt'},
        
        # Hopeful tweets
        {'text': 'Hope things get better soon in Mexico City', 'location': 'Mexico City, Mexico'},
        {'text': 'Staying positive despite everything. Love from Seoul', 'location': 'Seoul, South Korea'},
        {'text': 'Better days are coming for Jakarta!', 'location': 'Jakarta, Indonesia'},
        
        # Love tweets
        {'text': 'Love this city! Rome is absolutely magical', 'location': 'Rome, Italy'},
        {'text': 'Fell in love with Amsterdam today', 'location': 'Amsterdam, Netherlands'},
        {'text': 'My heart belongs to Istanbul', 'location': 'Istanbul, Turkey'},
        
        # Peaceful tweets
        {'text': 'Peaceful morning walk in Stockholm. So calm', 'location': 'Stockholm, Sweden'},
        {'text': 'Finding peace in Oslo today', 'location': 'Oslo, Norway'},
        {'text': 'Zen vibes in Copenhagen', 'location': 'Copenhagen, Denmark'},
        
        # Frustrated tweets
        {'text': 'Frustrated with how things are going in Buenos Aires', 'location': 'Buenos Aires, Argentina'},
        {'text': 'This is annoying! Manila traffic is the worst', 'location': 'Manila, Philippines'},
        {'text': 'Getting tired of this situation in Warsaw', 'location': 'Warsaw, Poland'},
        
        # Anxious tweets
        {'text': 'Feeling anxious about the meeting tomorrow in Johannesburg', 'location': 'Johannesburg, South Africa'},
        {'text': 'Nervous about the exam results in Bangalore', 'location': 'Bangalore, India'},
        {'text': 'Anxious times in Chicago right now', 'location': 'Chicago, USA'},
    ]
    
    return samples


def collect_twitter_data():
    """
    Main collection function.
    Tries API first, falls back to sample data.
    """
    print(f"\n>>> Starting Twitter collection...\n")
    
    # Strategy 1: Try Twitter API
    tweets = []
    api_attempted = False
    
    if TWEEPY_AVAILABLE and hasattr(Config, 'TWITTER_BEARER_TOKEN'):
        print("Attempting Twitter API collection...")
        tweets = collect_from_twitter_api()
        api_attempted = True
    
    # Strategy 2: Use sample data
    if not tweets:
        if api_attempted:
            print("API collection failed or returned no data.")
        print("Using sample data (30 tweets for testing)...")
        tweets = create_sample_data()
    
    # Process and save tweets
    total_saved = 0
    
    for idx, tweet in enumerate(tweets, 1):
        print(f"[{idx}/{len(tweets)}] Processing tweet...", end=' ')
        
        # Clean text
        text = clean_text(tweet['text'])
        
        # Skip if too short
        if len(text) < 10:
            print("SKIPPED (too short)")
            continue
        
        # Extract country
        country = extract_country(tweet['text'], tweet.get('user_location', ''))
        
        # Save to database
        try:
            db.insert_raw_post(
                text=text,
                source='Twitter',
                country=country if country else None,
                emotion=None,  # ✅ NEW PARAMETER - will be analyzed later
                emotion_score=None  # ✅ NEW PARAMETER - will be analyzed later
            )
            total_saved += 1
            print(f"OK")
        except Exception as e:
            print(f"FAILED: {e}")
    
    print(f"\n{'='*60}")
    print(f">>> Twitter Collection Complete!")
    print(f"{'='*60}")
    print(f"Total processed: {len(tweets)}")
    print(f"Total saved to DB: {total_saved}")
    print(f"With country data: {sum(1 for t in tweets if extract_country(t['text'], t.get('user_location', '')))}")
    print(f"{'='*60}\n")
    
    return total_saved


# Test the collector
if __name__ == "__main__":
    print(">>> Starting Twitter Collector Test...")
    count = collect_twitter_data()
    print(f">>> Test Complete: {count} posts saved to database")