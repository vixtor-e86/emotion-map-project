"""
emotion_analyzer.py (FINANCE EDITION)
--------------------------------------
Analyzes emotions in raw posts using Hugging Face transformer model.
NOW WITH FINANCE-SPECIFIC EMOTION DETECTION!

Maps 7 model emotions to our 5-emotion system:
- joy (stays joy) → BULLISH
- anger (stays anger) → BEARISH
- sadness (stays sadness) → CAUTIOUS
- fear → sadness → CAUTIOUS
- surprise → joy → BULLISH
- disgust → anger → BEARISH
- neutral → calmness → NEUTRAL

Usage:
    python backend/processing/emotion_analyzer.py
"""

import sys
import os
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from transformers import pipeline
    from database.db_manager import db
    from processing.finance_config import extract_tickers, FINANCE_KEYWORDS
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Install with: pip install transformers torch")
    sys.exit(1)

# Initialize emotion classifier (loads once)
print("📄 Loading emotion model (j-hartmann/emotion-english-distilroberta-base)...")
try:
    emotion_classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=None
    )
    print("✅ Model loaded successfully!\n")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    sys.exit(1)

# Emotion mapping: Model (7) → Our system (5) → Market Sentiment
EMOTION_MAPPING = {
    'joy': 'joy',           # Bullish
    'anger': 'anger',       # Bearish
    'sadness': 'sadness',   # Cautious
    'fear': 'sadness',      # Fear = Cautious (bearish)
    'surprise': 'joy',      # Surprise often positive (bullish)
    'disgust': 'anger',     # Disgust = Bearish
    'neutral': 'calmness'   # Neutral = Stable
}

# Keywords for detecting "hope" (not in base model)
HOPE_KEYWORDS = [
    # General hope
    'hope', 'hopeful', 'hoping', 'optimistic', 'optimism',
    'better tomorrow', 'bright future', 'looking forward',
    'things will improve', 'positive outlook', 'promising',
    'recovery', 'rebuilding', 'progress', 'breakthrough',
    
    # Finance-specific hope (BULLISH signals)
    'rally', 'bullish', 'bull market', 'bull run', 'surge', 'growth',
    'gains', 'profit', 'moon', 'breakout', 'all time high', 'ATH',
    'buying opportunity', 'undervalued', 'strong buy', 'long position',
    'accumulation phase', 'bottom is in', 'reversal', 'support level'
]

def detect_finance_emotion_boost(text: str):
    """
    Detect finance-specific emotional language that might intensify sentiment.
    This helps catch market-specific emotions the general model might miss.
    
    Args:
        text: Text to analyze
    
    Returns:
        tuple: (boost_emotion, confidence) or (None, 0)
    """
    text_lower = text.lower()
    
    # Strong BEARISH signals (map to anger)
    bearish_signals = [
        'crash', 'crashed', 'crashing', 'tank', 'tanked', 'tanking',
        'plunge', 'plunged', 'plunging', 'collapse', 'collapsed',
        'dump', 'dumped', 'dumping', 'disaster', 'catastrophe',
        'bankruptcy', 'bankrupt', 'liquidation', 'liquidated',
        'loss', 'losses', 'losing', 'bloodbath', 'massacre',
        'correction', 'bear market', 'sell off', 'selloff',
        'panic selling', 'panic sell', 'bag holder', 'rekt',
        'rugpull', 'rug pull', 'scam', 'ponzi', 'fraud',
        'fud', 'fear uncertainty doubt', 'capitulation'
    ]
    
    # Strong BULLISH signals (map to joy)
    bullish_signals = [
        'moon', 'mooning', 'to the moon', 'rocket', '🚀',
        'lambo', 'lamborghini', 'tendies', 'diamond hands', '💎',
        'buy the dip', 'btfd', 'hodl', 'hold', 'accumulate',
        'bull run', 'parabolic', 'exponential', 'skyrocket',
        'all time high', 'ath', 'breakout', 'rally', 'pump',
        'surge', 'soar', 'explode', 'rip', 'let\'s go',
        'bullish af', 'mega bullish', 'extremely bullish',
        'going up', 'moon mission', 'wen lambo'
    ]
    
    # Check for bearish (higher priority - fear drives markets)
    bearish_count = sum(1 for signal in bearish_signals if signal in text_lower)
    if bearish_count >= 2:
        return ('anger', 0.95)  # Very confident bearish
    elif bearish_count == 1:
        return ('anger', 0.85)  # Confident bearish
    
    # Check for bullish
    bullish_count = sum(1 for signal in bullish_signals if signal in text_lower)
    if bullish_count >= 2:
        return ('joy', 0.95)  # Very confident bullish
    elif bullish_count == 1:
        return ('joy', 0.85)  # Confident bullish
    
    return (None, 0)

def classify_emotion(text: str, confidence_threshold: float = 0.4):
    """
    Classify emotion in text with FINANCE-SPECIFIC boosting.
    
    Priority:
    1. Finance-specific emotion signals (crash, moon, etc.)
    2. Hope keywords (rally, bullish, etc.)
    3. AI model prediction
    
    Args:
        text: Text to analyze
        confidence_threshold: Minimum confidence (0.0 to 1.0)
    
    Returns:
        tuple: (emotion_name, confidence_score)
    """
    if not text or not isinstance(text, str) or len(text.strip()) < 3:
        return "calmness", 0.3  # Default for empty/short text
    
    # PRIORITY 1: Check for finance-specific emotional language FIRST
    finance_emotion, finance_confidence = detect_finance_emotion_boost(text)
    if finance_emotion:
        return finance_emotion, finance_confidence
    
    # PRIORITY 2: Check for hope keywords (model doesn't detect this well)
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in HOPE_KEYWORDS):
        return "hope", 0.85
    
    # PRIORITY 3: Use AI model for general emotion detection
    try:
        # Get predictions from model
        predictions = emotion_classifier(text)[0]
        top_prediction = predictions[0]
        
        # Map model emotion to our 5-emotion system
        model_emotion = top_prediction['label']
        score = top_prediction['score']
        
        mapped_emotion = EMOTION_MAPPING.get(model_emotion, 'calmness')
        
        # Apply confidence threshold
        if score >= confidence_threshold:
            return mapped_emotion, score
        else:
            return "calmness", score  # Low confidence = neutral/calm
            
    except Exception as e:
        print(f"⚠️  Error analyzing text: {e}")
        return "calmness", 0.0

def process_posts(batch_size: int = 100, silent: bool = False):
    """
    Process all posts without emotion data.
    NOW WITH TICKER EXTRACTION!
    
    Args:
        batch_size: Number of posts to process before committing
        silent: If True, minimal output (for background tasks)
    """
    if not silent:
        print("\n" + "="*60)
        print("FINANCE EMOTION ANALYZER")
        print("="*60)
    
    # Get posts without emotion
    posts = db.get_posts_without_emotion()
    
    if not posts:
        if not silent:
            print("No unprocessed posts found")
        return 0
    
    total = len(posts)
    if not silent:
        print(f"Processing {total} finance posts...")
    
    # Progress tracking
    processed = 0
    emotion_counts = {'joy': 0, 'anger': 0, 'sadness': 0, 'hope': 0, 'calmness': 0}
    tickers_found = []
    start_time = datetime.now()
    
    for i, post in enumerate(posts, 1):
        try:
            # Analyze emotion (FINANCE-AWARE!)
            emotion, score = classify_emotion(post['text'])
            
            # Extract tickers if available (for finance posts)
            try:
                tickers = extract_tickers(post['text'])
                if tickers:
                    tickers_found.extend(tickers)
                    if not silent and i % 50 == 0:  # Log every 50 posts
                        print(f"  Found tickers: {', '.join(set(tickers_found[-10:]))}")
            except Exception as e:
                pass  # Tickers are optional, don't fail on this
            
            # Update database
            db.update_post_emotion(post['id'], emotion, score)
            
            # Track statistics
            emotion_counts[emotion] += 1
            processed += 1
            
            # Progress indicator (every 100 posts or last)
            if not silent and (i % 100 == 0 or i == total):
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = processed / elapsed if elapsed > 0 else 0
                print(f"  [{i}/{total}] Rate: {rate:.1f} posts/sec")
        
        except Exception as e:
            if not silent:
                print(f"  Error on post {post['id']}: {e}")
            continue
    
    # Final statistics
    elapsed = (datetime.now() - start_time).total_seconds()
    
    if not silent:
        print(f"\n✅ Processed {processed} posts in {elapsed:.1f}s ({processed/elapsed:.1f} posts/sec)")
        
        # Market sentiment breakdown
        print("\n📊 Market Sentiment Breakdown:")
        bullish = emotion_counts['joy'] + emotion_counts['hope']
        bearish = emotion_counts['anger'] + emotion_counts['sadness']
        neutral = emotion_counts['calmness']
        
        total_emotions = sum(emotion_counts.values())
        if total_emotions > 0:
            bullish_pct = (bullish / total_emotions) * 100
            bearish_pct = (bearish / total_emotions) * 100
            neutral_pct = (neutral / total_emotions) * 100
            
            print(f"  🟢 BULLISH:  {bullish:4d} ({bullish_pct:5.1f}%) - Joy + Hope")
            print(f"  🔴 BEARISH:  {bearish:4d} ({bearish_pct:5.1f}%) - Anger + Sadness")
            print(f"  ⚪ NEUTRAL:  {neutral:4d} ({neutral_pct:5.1f}%) - Calmness")
        
        print("\n📈 Detailed Emotion Breakdown:")
        for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / processed * 100) if processed > 0 else 0
            sentiment_label = {
                'joy': '🟢 Strong Bullish',
                'hope': '📈 Optimistic',
                'calmness': '⚪ Neutral',
                'sadness': '📉 Cautious',
                'anger': '🔴 Strong Bearish'
            }
            print(f"  {sentiment_label.get(emotion, emotion):20s}: {count:4d} ({percentage:5.1f}%)")
        
        # Tickers summary
        if tickers_found:
            unique_tickers = set(tickers_found)
            print(f"\n💰 Tickers Found: {len(unique_tickers)} unique")
            from collections import Counter
            top_tickers = Counter(tickers_found).most_common(10)
            print("   Top 10:", ', '.join([f"{t[0]}({t[1]})" for t in top_tickers]))
        
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