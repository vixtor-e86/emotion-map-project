"""
sector_config.py
----------------
Configuration for all 4 sectors: Finance, Health, Technology, Sports
Includes keywords, emotion mappings, and data sources for each sector.
"""

import re

# ============================================
# SECTOR DEFINITIONS
# ============================================

SECTORS = {
    'finance': {
        'name': 'Finance',
        'icon': '💰',
        'color': '#10b981',
        'description': 'Market Sentiment & Economic Trends'
    },
    'health': {
        'name': 'Health',
        'icon': '🏥',
        'color': '#3b82f6',
        'description': 'Healthcare & Wellness Insights'
    },
    'technology': {
        'name': 'Technology',
        'icon': '💻',
        'color': '#8b5cf6',
        'description': 'Tech Innovation & Digital Trends'
    },
    'sports': {
        'name': 'Sports',
        'icon': '⚽',
        'color': '#f59e0b',
        'description': 'Sports News & Fan Sentiment'
    }
}

# ============================================
# EMOTION LABELS PER SECTOR
# ============================================

EMOTION_LABELS = {
    'finance': {
        'joy': {'emoji': '🟢', 'label': 'Strong Bullish', 'score': 85},
        'hope': {'emoji': '📈', 'label': 'Optimistic', 'score': 75},
        'calmness': {'emoji': '⚪', 'label': 'Neutral', 'score': 50},
        'sadness': {'emoji': '📉', 'label': 'Cautious', 'score': 35},
        'anger': {'emoji': '🔴', 'label': 'Strong Bearish', 'score': 25}
    },
    'health': {
        'joy': {'emoji': '💚', 'label': 'Healthy', 'score': 85},
        'hope': {'emoji': '🌱', 'label': 'Recovering', 'score': 75},
        'calmness': {'emoji': '😌', 'label': 'Stable', 'score': 50},
        'sadness': {'emoji': '😟', 'label': 'Concerned', 'score': 35},
        'anger': {'emoji': '😤', 'label': 'Critical', 'score': 25}
    },
    'technology': {
        'joy': {'emoji': '🚀', 'label': 'Innovative', 'score': 85},
        'hope': {'emoji': '💡', 'label': 'Optimistic', 'score': 75},
        'calmness': {'emoji': '🧘', 'label': 'Stable', 'score': 50},
        'sadness': {'emoji': '😔', 'label': 'Disappointed', 'score': 35},
        'anger': {'emoji': '🐛', 'label': 'Frustrated', 'score': 25}
    },
    'sports': {
        'joy': {'emoji': '🎉', 'label': 'Excited', 'score': 85},
        'hope': {'emoji': '🔥', 'label': 'Hopeful', 'score': 75},
        'calmness': {'emoji': '😐', 'label': 'Neutral', 'score': 50},
        'sadness': {'emoji': '😢', 'label': 'Disappointed', 'score': 35},
        'anger': {'emoji': '😡', 'label': 'Frustrated', 'score': 25}
    }
}

# ============================================
# KEYWORDS PER SECTOR
# ============================================

SECTOR_KEYWORDS = {
    'finance': [
        # Markets & Trading
        'stock', 'stocks', 'share', 'shares', 'market', 'markets',
        'trading', 'trader', 'NYSE', 'NASDAQ', 'dow jones', 'S&P 500',
        'cryptocurrency', 'bitcoin', 'ethereum', 'crypto', 'blockchain',
        
        # Actions
        'buy', 'sell', 'invest', 'investment', 'portfolio', 'dividend',
        'earnings', 'revenue', 'profit', 'IPO', 'merger', 'acquisition',
        
        # Sentiment
        'bull', 'bullish', 'bear', 'bearish', 'rally', 'crash',
        'surge', 'plunge', 'moon', 'dump', 'breakout', 'correction',
        
        # Economy
        'inflation', 'interest rate', 'Fed', 'recession', 'GDP',
        'unemployment', 'economic', 'fiscal', 'monetary',
        
        # Tickers
        'AAPL', 'TSLA', 'AMZN', 'MSFT', 'GOOGL', 'META', 'NVDA'
    ],
    
    'health': [
        # General Health
        'health', 'healthcare', 'medical', 'medicine', 'doctor',
        'hospital', 'clinic', 'patient', 'treatment', 'therapy',
        
        # Conditions
        'disease', 'illness', 'symptom', 'diagnosis', 'cure',
        'infection', 'virus', 'bacteria', 'pandemic', 'epidemic',
        
        # Wellness
        'fitness', 'exercise', 'workout', 'nutrition', 'diet',
        'wellness', 'mental health', 'stress', 'anxiety', 'depression',
        
        # Medical Terms
        'vaccine', 'vaccination', 'immunization', 'prescription',
        'surgery', 'operation', 'recovery', 'rehabilitation',
        
        # Lifestyle
        'sleep', 'meditation', 'yoga', 'vitamins', 'supplements',
        'healthy eating', 'weight loss', 'obesity', 'diabetes'
    ],
    
    'technology': [
        # General Tech
        'technology', 'tech', 'software', 'hardware', 'computer',
        'laptop', 'smartphone', 'device', 'gadget', 'digital',
        
        # AI & ML
        'AI', 'artificial intelligence', 'machine learning', 'ML',
        'neural network', 'deep learning', 'ChatGPT', 'GPT',
        
        # Internet & Web
        'internet', 'website', 'app', 'application', 'platform',
        'cloud', 'server', 'database', 'API', 'programming',
        
        # Companies
        'Apple', 'Google', 'Microsoft', 'Amazon', 'Meta', 'Tesla',
        'OpenAI', 'NVIDIA', 'Intel', 'Samsung', 'Huawei',
        
        # Innovation
        'innovation', 'startup', 'breakthrough', 'launch', 'release',
        'update', 'upgrade', 'feature', 'bug', 'patch', 'beta',
        
        # Emerging Tech
        'blockchain', 'metaverse', 'VR', 'AR', 'quantum', '5G',
        'IoT', 'cybersecurity', 'data privacy', 'encryption'
    ],
    
    'sports': [
        # General Sports
        'sports', 'game', 'match', 'tournament', 'championship',
        'league', 'season', 'playoff', 'final', 'cup',
        
        # Football/Soccer
        'football', 'soccer', 'goal', 'penalty', 'midfielder',
        'striker', 'goalkeeper', 'FIFA', 'World Cup', 'Premier League',
        'La Liga', 'Champions League', 'Messi', 'Ronaldo',
        
        # Basketball
        'basketball', 'NBA', 'dunk', 'three-pointer', 'Lakers',
        'Warriors', 'LeBron', 'playoffs', 'championship',
        
        # Cricket
        'cricket', 'wicket', 'century', 'innings', 'bowler',
        'batsman', 'IPL', 'T20', 'test match', 'Virat Kohli',
        
        # Other Sports
        'tennis', 'rugby', 'baseball', 'golf', 'racing',
        'Olympics', 'athlete', 'player', 'team', 'coach',
        
        # Actions
        'win', 'won', 'victory', 'defeat', 'loss', 'draw',
        'score', 'scored', 'winning', 'losing', 'champion'
    ]
}

# ============================================
# RSS FEEDS PER SECTOR
# ============================================

RSS_FEEDS = {
    'finance': {
        "Bloomberg Markets": "https://feeds.bloomberg.com/markets/news.rss",
        "MarketWatch": "https://www.marketwatch.com/rss/",
        "CNBC Markets": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
        "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "Forbes Money": "https://www.forbes.com/money/feed/",
    },
    
    'health': {
        "WHO News": "https://www.who.int/rss-feeds/news-english.xml",
        "CDC": "https://tools.cdc.gov/api/v2/resources/media/132608.rss",
        "WebMD": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC",
        "Health News": "https://www.medicalnewstoday.com/rss/news.xml",
        "Healthline": "https://www.healthline.com/rss",
    },
    
    'technology': {
        "TechCrunch": "https://techcrunch.com/feed/",
        "The Verge": "https://www.theverge.com/rss/index.xml",
        "Wired": "https://www.wired.com/feed/rss",
        "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
        "Engadget": "https://www.engadget.com/rss.xml",
        "MIT Tech Review": "https://www.technologyreview.com/feed/",
    },
    
    'sports': {
        "ESPN": "https://www.espn.com/espn/rss/news",
        "BBC Sport": "http://feeds.bbci.co.uk/sport/rss.xml",
        "Sky Sports": "https://www.skysports.com/rss/12040",
        "Goal.com": "https://www.goal.com/feeds/en/news",
        "Sports Illustrated": "https://www.si.com/rss/si_topstories.rss",
    }
}

# ============================================
# SUBREDDITS PER SECTOR
# ============================================

SUBREDDITS = {
    'finance': [
        "wallstreetbets", "stocks", "investing", "StockMarket",
        "CryptoCurrency", "Bitcoin", "ethereum", "options",
        "Daytrading", "swingtrading", "pennystocks", "dividends",
        "personalfinance", "Economics", "economy"
    ],
    
    'health': [
        "Health", "fitness", "nutrition", "loseit", "HealthAnxiety",
        "mentalhealth", "depression", "Anxiety", "medical",
        "medicine", "AskDocs", "EatCheapAndHealthy", "HealthyFood",
        "yoga", "Meditation", "sleep"
    ],
    
    'technology': [
        "technology", "tech", "gadgets", "Android", "apple",
        "programming", "coding", "MachineLearning", "artificial",
        "singularity", "Futurology", "cybersecurity", "privacy",
        "linux", "hardware", "software"
    ],
    
    'sports': [
        "sports", "soccer", "football", "nba", "nfl",
        "baseball", "hockey", "tennis", "golf", "cricket",
        "sports", "worldcup", "PremierLeague", "MMA", "boxing"
    ]
}

# ============================================
# UTILITY FUNCTIONS
# ============================================

def detect_sector(text: str) -> str:
    """
    Detect which sector a text belongs to.
    
    Args:
        text: Text to analyze
    
    Returns:
        str: Sector name ('finance', 'health', 'technology', 'sports', 'general')
    """
    if not text or not isinstance(text, str):
        return 'general'
    
    text_lower = text.lower()
    
    # Count keyword matches for each sector
    scores = {}
    for sector, keywords in SECTOR_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        scores[sector] = score
    
    # Get sector with highest score
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    
    return 'general'

def get_emotion_config(sector: str, emotion: str) -> dict:
    """
    Get emotion configuration for a specific sector.
    
    Args:
        sector: Sector name
        emotion: Emotion name
    
    Returns:
        dict: Emotion config with emoji, label, score
    """
    if sector not in EMOTION_LABELS:
        sector = 'finance'  # Default
    
    return EMOTION_LABELS[sector].get(emotion, {
        'emoji': '⚪',
        'label': 'Unknown',
        'score': 50
    })

def get_sector_info(sector: str) -> dict:
    """
    Get sector information.
    
    Args:
        sector: Sector name
    
    Returns:
        dict: Sector info
    """
    return SECTORS.get(sector, {
        'name': 'General',
        'icon': '🌐',
        'color': '#6b7280',
        'description': 'General Topics'
    })

# Extract tickers (finance-specific)
TICKER_PATTERN = re.compile(r'\$([A-Z]{1,5})\b')
CRYPTO_PATTERN = re.compile(r'\b(BTC|ETH|DOGE|XRP|ADA|SOL|MATIC)\b', re.IGNORECASE)

def extract_tickers(text: str) -> list:
    """Extract stock/crypto tickers from text"""
    if not text:
        return []
    
    tickers = TICKER_PATTERN.findall(text)
    crypto = CRYPTO_PATTERN.findall(text)
    all_tickers = list(set(tickers + crypto))
    
    return [t.upper() for t in all_tickers]