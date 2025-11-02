# finance_config.py
"""
Finance-specific configuration for FinancePulse.
Add this file to backend/processing/
"""

# ===== FINANCE KEYWORDS =====
FINANCE_KEYWORDS = [
    # Markets & Exchanges
    'stock', 'stocks', 'share', 'shares', 'equity', 'equities',
    'market', 'markets', 'trading', 'trader', 'NYSE', 'NASDAQ', 
    'dow jones', 'S&P 500', 'russell', 'index', 'indices',
    
    # Crypto
    'crypto', 'cryptocurrency', 'bitcoin', 'BTC', 'ethereum', 'ETH',
    'blockchain', 'DeFi', 'altcoin', 'token', 'NFT', 'Web3',
    'dogecoin', 'DOGE', 'ripple', 'XRP', 'cardano', 'ADA',
    
    # Trading Actions
    'buy', 'sell', 'trade', 'invest', 'investment', 'investor',
    'portfolio', 'position', 'long', 'short', 'call', 'put',
    'option', 'options', 'futures', 'derivatives', 'hedge',
    
    # Financial Metrics
    'earnings', 'revenue', 'profit', 'loss', 'dividend', 'yield',
    'IPO', 'acquisition', 'merger', 'valuation', 'PE ratio',
    'market cap', 'capitalization', 'quarterly', 'annual report',
    
    # Sentiment Indicators
    'bull', 'bullish', 'bear', 'bearish', 'rally', 'crash',
    'surge', 'plunge', 'soar', 'tank', 'moon', 'dump',
    'breakout', 'correction', 'volatility', 'momentum',
    
    # Top 50 Companies (Tickers)
    'AAPL', 'Apple', 'MSFT', 'Microsoft', 'GOOGL', 'Google', 'Alphabet',
    'AMZN', 'Amazon', 'TSLA', 'Tesla', 'META', 'Meta', 'Facebook',
    'NVDA', 'NVIDIA', 'JPM', 'JPMorgan', 'V', 'Visa',
    'WMT', 'Walmart', 'JNJ', 'Johnson', 'PG', 'Procter',
    'MA', 'Mastercard', 'HD', 'Home Depot', 'DIS', 'Disney',
    'BAC', 'Bank of America', 'NFLX', 'Netflix', 'ADBE', 'Adobe',
    'CSCO', 'Cisco', 'PFE', 'Pfizer', 'INTC', 'Intel',
    'AMD', 'ORCL', 'Oracle', 'COIN', 'Coinbase',
    
    # Economy & Policy
    'inflation', 'interest rate', 'Fed', 'Federal Reserve', 'ECB',
    'recession', 'GDP', 'unemployment', 'economic growth',
    'central bank', 'monetary policy', 'fiscal policy',
    'stimulus', 'quantitative easing', 'rate hike', 'rate cut',
    
    # Banking & Finance
    'bank', 'banking', 'loan', 'credit', 'debt', 'bond',
    'treasury', 'mortgage', 'fintech', 'payment', 'forex',
    'currency', 'dollar', 'euro', 'commodity', 'gold', 'oil',
    
    # Investor Slang (WSB Style)
    'tendies', 'diamond hands', 'paper hands', 'HODL', 'YOLO',
    'to the moon', 'ape', 'retard', 'stonk', 'DD', 'FOMO'
]

# ===== FINANCE SUBREDDITS =====
FINANCE_SUBREDDITS = [
    # Main Trading
    "wallstreetbets", "stocks", "investing", "StockMarket",
    "Daytrading", "swingtrading", "options", "thetagang",
    
    # Crypto
    "CryptoCurrency", "Bitcoin", "ethereum", "CryptoMarkets",
    "ethtrader", "dogecoin", "SatoshiStreetBets",
    
    # Specific Strategies
    "pennystocks", "ValueInvesting", "dividends", "FIRE",
    "Bogleheads", "SecurityAnalysis",
    
    # Personal Finance
    "personalfinance", "FinancialPlanning", "povertyfinance",
    
    # Economy & News
    "Economics", "economy", "business", "Finance",
    
    # International
    "CanadianInvestor", "UKInvesting", "EuropeFIRE",
    "IndiaInvestments", "ASX_Bets"  # Australia
]

# ===== FINANCE RSS FEEDS =====
FINANCE_RSS_FEEDS = {
    # Major Financial News
    "Bloomberg Markets": "https://feeds.bloomberg.com/markets/news.rss",
    "MarketWatch": "https://www.marketwatch.com/rss/",
    "CNBC Markets": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "WSJ Markets": "https://feeds.finance.yahoo.com/rss/2.0/headline",
    
    # Crypto-Specific
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "CryptoSlate": "https://cryptoslate.com/feed/",
    
    # Business & Economy
    "Financial Times": "https://www.ft.com/rss/home",
    "Forbes Money": "https://www.forbes.com/money/feed/",
    "Investor's Business Daily": "https://www.investors.com/feed/",
    
    # Analysis & Opinion
    "Seeking Alpha": "https://seekingalpha.com/feed.xml",
    "The Motley Fool": "https://www.fool.com/feeds/index.aspx",
    "Benzinga": "https://www.benzinga.com/feed"
}

# ===== EMOTION → MARKET SENTIMENT MAPPING =====
EMOTION_TO_SENTIMENT = {
    'joy': {
        'sentiment': 'bullish',
        'score': 85,
        'color': '#10b981',  # Green
        'label': '🟢 Bullish',
        'description': 'Strong positive sentiment - buying pressure expected'
    },
    'hope': {
        'sentiment': 'bullish',
        'score': 75,
        'color': '#34d399',  # Light green
        'label': '🟢 Optimistic',
        'description': 'Positive outlook - recovery or growth anticipated'
    },
    'calmness': {
        'sentiment': 'neutral',
        'score': 50,
        'color': '#94a3b8',  # Gray
        'label': '⚪ Neutral',
        'description': 'Stable sentiment - low volatility expected'
    },
    'sadness': {
        'sentiment': 'bearish',
        'score': 35,
        'color': '#f87171',  # Light red
        'label': '🔴 Cautious',
        'description': 'Negative sentiment - selling pressure possible'
    },
    'anger': {
        'sentiment': 'bearish',
        'score': 25,
        'color': '#ef4444',  # Red
        'label': '🔴 Bearish',
        'description': 'Strong negative sentiment - high volatility expected'
    }
}

# ===== TICKER REGEX PATTERNS =====
import re

TICKER_PATTERN = re.compile(r'\$([A-Z]{1,5})\b')  # Matches $AAPL, $TSLA, etc.
CRYPTO_PATTERN = re.compile(r'\b(BTC|ETH|DOGE|XRP|ADA|SOL|MATIC|AVAX|DOT|LINK)\b', re.IGNORECASE)

def is_finance_related(text: str) -> bool:
    """
    Check if text is finance-related.
    
    Args:
        text: Text to analyze
        
    Returns:
        bool: True if finance-related
    """
    if not text or not isinstance(text, str):
        return False
    
    text_lower = text.lower()
    
    # Check for any finance keyword
    return any(keyword.lower() in text_lower for keyword in FINANCE_KEYWORDS)

def extract_tickers(text: str) -> list:
    """
    Extract stock tickers from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        list: List of unique tickers found
    """
    if not text:
        return []
    
    # Find $ tickers (e.g., $AAPL)
    tickers = TICKER_PATTERN.findall(text)
    
    # Find crypto symbols
    crypto = CRYPTO_PATTERN.findall(text)
    
    # Combine and deduplicate
    all_tickers = list(set(tickers + crypto))
    
    return [t.upper() for t in all_tickers]

def get_market_sentiment(emotion: str) -> dict:
    """
    Convert emotion to market sentiment.
    
    Args:
        emotion: One of 5 emotions
        
    Returns:
        dict: Sentiment data
    """
    return EMOTION_TO_SENTIMENT.get(emotion, EMOTION_TO_SENTIMENT['calmness'])

def calculate_market_score(emotion_counts: dict) -> int:
    """
    Calculate overall market sentiment score (0-100).
    
    Args:
        emotion_counts: Dict with emotion counts
        
    Returns:
        int: Market score (0=Very Bearish, 50=Neutral, 100=Very Bullish)
    """
    total = sum(emotion_counts.values())
    if total == 0:
        return 50  # Neutral
    
    # Weighted average
    score = 0
    for emotion, count in emotion_counts.items():
        sentiment_data = EMOTION_TO_SENTIMENT.get(emotion, {'score': 50})
        score += sentiment_data['score'] * count
    
    return round(score / total)