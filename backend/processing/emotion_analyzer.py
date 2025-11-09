"""
emotion_analyzer.py (MULTI-SECTOR EDITION)
-------------------------------------------
Analyzes emotions with SECTOR-SPECIFIC context for:
- Finance, Health, Technology, Sports

Each sector has custom emotion boosting keywords.
"""

import sys
import os
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from transformers import pipeline
    from database.db_manager import db
    from processing.sector_config import extract_tickers, get_emotion_config
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

# Emotion mapping: Model (7) → Our system (5)
EMOTION_MAPPING = {
    'joy': 'joy',
    'anger': 'anger',
    'sadness': 'sadness',
    'fear': 'sadness',
    'surprise': 'joy',
    'disgust': 'anger',
    'neutral': 'calmness'
}

# ============================================
# SECTOR-SPECIFIC EMOTION KEYWORDS
# ============================================

SECTOR_EMOTION_KEYWORDS = {
    'finance': {
        'joy': ['moon', 'rocket', 'lambo', 'tendies', 'bull run', 'breakout', 'rally', 'surge'],
        'anger': ['crash', 'tank', 'dump', 'scam', 'rugpull', 'rekt', 'bloodbath', 'liquidated'],
        'hope': ['bullish', 'buy the dip', 'hodl', 'accumulate', 'undervalued', 'recovery'],
    },
    
    'health': {
        'joy': ['healthy', 'recovered', 'cured', 'wellness', 'improvement', 'better', 'healed'],
        'anger': ['sick', 'pain', 'disease', 'outbreak', 'epidemic', 'critical', 'emergency'],
        'hope': ['recovery', 'treatment', 'vaccine', 'cure', 'promising', 'breakthrough'],
    },
    
    'technology': {
        'joy': ['launch', 'breakthrough', 'innovation', 'revolutionary', 'amazing', 'incredible'],
        'anger': ['bug', 'crash', 'failure', 'vulnerability', 'hack', 'breach', 'outage'],
        'hope': ['beta', 'update', 'upgrade', 'coming soon', 'next generation', 'future'],
    },
    
    'sports': {
        'joy': ['win', 'victory', 'champion', 'goal', 'score', 'winning', 'triumph', 'celebrate'],
        'anger': ['loss', 'defeat', 'injured', 'foul', 'penalty', 'controversial', 'robbed'],
        'hope': ['comeback', 'potential', 'training', 'improving', 'next season', 'recovery'],
    }
}

def detect_sector_emotion_boost(text: str, sector: str):
    """
    Detect sector-specific emotional signals.
    
    Args:
        text: Text to analyze
        sector: Sector name
    
    Returns:
        tuple: (emotion, confidence) or (None, 0)
    """
    if sector not in SECTOR_EMOTION_KEYWORDS:
        return (None, 0)
    
    text_lower = text.lower()
    sector_keywords = SECTOR_EMOTION_KEYWORDS[sector]
    
    # Check each emotion's keywords
    emotion_scores = {}
    for emotion, keywords in sector_keywords.items():
        score = sum(2 for kw in keywords if kw in text_lower)  # Weight: 2 per keyword
        if score > 0:
            emotion_scores[emotion] = score
    
    # Return strongest emotion
    if emotion_scores:
        best_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = min(0.75 + (emotion_scores[best_emotion] * 0.05), 0.95)
        return (best_emotion, confidence)
    
    return (None, 0)

def classify_emotion(text: str, sector='general', confidence_threshold: float = 0.4):
    """
    Classify emotion with SECTOR-SPECIFIC context.
    
    Priority:
    1. Sector-specific emotion signals
    2. AI model prediction
    
    Args:
        text: Text to analyze
        sector: Sector name
        confidence_threshold: Minimum confidence
    
    Returns:
        tuple: (emotion_name, confidence_score)
    """
    if not text or not isinstance(text, str) or len(text.strip()) < 3:
        return "calmness", 0.3
    
    # PRIORITY 1: Check sector-specific emotional signals
    sector_emotion, sector_confidence = detect_sector_emotion_boost(text, sector)
    if sector_emotion:
        return sector_emotion, sector_confidence
    
    # PRIORITY 2: Use AI model
    try:
        predictions = emotion_classifier(text)[0]
        top_prediction = predictions[0]
        
        model_emotion = top_prediction['label']
        score = top_prediction['score']
        
        mapped_emotion = EMOTION_MAPPING.get(model_emotion, 'calmness')
        
        if score >= confidence_threshold:
            return mapped_emotion, score
        else:
            return "calmness", score
            
    except Exception as e:
        print(f"⚠️  Error analyzing text: {e}")
        return "calmness", 0.0

def process_posts_by_sector(sector=None, batch_size: int = 100, silent: bool = False):
    """
    Process posts for a specific sector or all sectors.
    
    Args:
        sector: Sector name (None = all sectors)
        batch_size: Batch size
        silent: Minimal output
    
    Returns:
        int: Number of posts processed
    """
    if not silent:
        print("\n" + "="*60)
        if sector:
            print(f"EMOTION ANALYZER - {sector.upper()}")
        else:
            print("MULTI-SECTOR EMOTION ANALYZER")
        print("="*60)
    
    # Get posts without emotion
    posts = db.get_posts_without_emotion(sector=sector)
    
    if not posts:
        if not silent:
            print(f"No unprocessed posts found" + (f" for {sector}" if sector else ""))
        return 0
    
    total = len(posts)
    if not silent:
        print(f"Processing {total} posts" + (f" from {sector}" if sector else ""))
    
    # Track stats
    processed = 0
    emotion_counts = {'joy': 0, 'anger': 0, 'sadness': 0, 'hope': 0, 'calmness': 0}
    sector_counts = {}
    tickers_found = []
    start_time = datetime.now()
    
    for i, post in enumerate(posts, 1):
        try:
            post_sector = post.get('sector', 'general')
            
            # Analyze emotion with sector context
            emotion, score = classify_emotion(post['text'], sector=post_sector)
            
            # Extract tickers for finance
            if post_sector == 'finance':
                try:
                    tickers = extract_tickers(post['text'])
                    if tickers:
                        tickers_found.extend(tickers)
                except:
                    pass
            
            # Update database
            db.update_post_emotion(post['id'], emotion, score)
            
            # Track stats
            emotion_counts[emotion] += 1
            sector_counts[post_sector] = sector_counts.get(post_sector, 0) + 1
            processed += 1
            
            # Progress
            if not silent and (i % 100 == 0 or i == total):
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = processed / elapsed if elapsed > 0 else 0
                print(f"  [{i}/{total}] Rate: {rate:.1f} posts/sec")
        
        except Exception as e:
            if not silent:
                print(f"  Error on post {post['id']}: {e}")
            continue
    
    # Final stats
    elapsed = (datetime.now() - start_time).total_seconds()
    
    if not silent:
        print(f"\n✅ Processed {processed} posts in {elapsed:.1f}s ({processed/elapsed:.1f} posts/sec)")
        
        # By sector
        if len(sector_counts) > 1:
            print("\n📊 Posts by Sector:")
            from processing.sector_config import get_sector_info
            for s, count in sorted(sector_counts.items(), key=lambda x: x[1], reverse=True):
                info = get_sector_info(s)
                print(f"   {info['icon']} {info['name']:12s}: {count:4d} posts")
        
        # Emotion breakdown
        print("\n📈 Emotion Breakdown:")
        for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / processed * 100) if processed > 0 else 0
            print(f"   {emotion.capitalize():10s}: {count:4d} ({percentage:5.1f}%)")
        
        # Tickers (finance only)
        if tickers_found and not sector or sector == 'finance':
            unique_tickers = set(tickers_found)
            print(f"\n💰 Finance Tickers: {len(unique_tickers)} unique")
            from collections import Counter
            top_tickers = Counter(tickers_found).most_common(10)
            print("   Top 10:", ', '.join([f"{t[0]}({t[1]})" for t in top_tickers]))
        
        print("="*60)
    
    return processed

def process_all_sectors(silent=False):
    """Process all sectors one by one."""
    print("\n" + "="*60)
    print("🌐 PROCESSING ALL SECTORS")
    print("="*60)
    
    total_processed = 0
    
    for sector in ['finance', 'health', 'technology', 'sports']:
        from processing.sector_config import get_sector_info
        info = get_sector_info(sector)
        
        print(f"\n{info['icon']} Processing {info['name']}...")
        count = process_posts_by_sector(sector=sector, silent=True)
        total_processed += count
        print(f"   ✅ {count} posts analyzed")
    
    print(f"\n✅ Total: {total_processed} posts processed across all sectors")
    print("="*60 + "\n")
    
    return total_processed

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-Sector Emotion Analyzer')
    parser.add_argument('--sector', type=str, choices=['finance', 'health', 'technology', 'sports', 'all'],
                       default='all', help='Sector to process')
    
    args = parser.parse_args()
    
    try:
        if args.sector == 'all':
            process_all_sectors()
        else:
            process_posts_by_sector(sector=args.sector)
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()