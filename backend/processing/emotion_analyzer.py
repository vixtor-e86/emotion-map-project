"""
emotion_analyzer.py
-------------------
Analyzes emotions in raw posts using Hugging Face transformer model.
Maps 7 model emotions to our 5-emotion system:
- joy (stays joy)
- anger (stays anger) 
- sadness (stays sadness)
- fear → sadness
- surprise → joy
- disgust → anger
- neutral → calmness

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
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Install with: pip install transformers torch")
    sys.exit(1)

# Initialize emotion classifier (loads once)
print("🔄 Loading emotion model (j-hartmann/emotion-english-distilroberta-base)...")
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
    'fear': 'sadness',      # Fear is a form of sadness
    'surprise': 'joy',       # Surprise often positive
    'disgust': 'anger',      # Disgust similar to anger
    'neutral': 'calmness'    # Neutral = calm
}

# Keywords for detecting "hope" (not in base model)
HOPE_KEYWORDS = [
    'hope', 'hopeful', 'hoping', 'optimistic', 'optimism',
    'better tomorrow', 'bright future', 'looking forward',
    'things will improve', 'positive outlook', 'promising',
    'recovery', 'rebuilding', 'progress', 'breakthrough'
]

def classify_emotion(text: str, confidence_threshold: float = 0.4):
    """
    Classify emotion in text.
    
    Args:
        text: Text to analyze
        confidence_threshold: Minimum confidence (0.0 to 1.0)
    
    Returns:
        tuple: (emotion_name, confidence_score)
    """
    if not text or not isinstance(text, str) or len(text.strip()) < 3:
        return "calmness", 0.3  # Default for empty/short text
    
    # Check for hope keywords first (model doesn't detect this)
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in HOPE_KEYWORDS):
        return "hope", 0.85
    
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
    
    Args:
        batch_size: Number of posts to process before committing
        silent: If True, minimal output (for background tasks)
    """
    if not silent:
        print("\n" + "="*60)
        print("EMOTION ANALYZER")
        print("="*60)
    
    # Get posts without emotion
    posts = db.get_posts_without_emotion()
    
    if not posts:
        if not silent:
            print("No unprocessed posts found")
        return 0
    
    total = len(posts)
    if not silent:
        print(f"Processing {total} posts...")
    
    # Progress tracking
    processed = 0
    emotion_counts = {'joy': 0, 'anger': 0, 'sadness': 0, 'hope': 0, 'calmness': 0}
    start_time = datetime.now()
    
    for i, post in enumerate(posts, 1):
        try:
            # Analyze emotion
            emotion, score = classify_emotion(post['text'])
            
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
        print(f"\nProcessed {processed} posts in {elapsed:.1f}s ({processed/elapsed:.1f} posts/sec)")
        print("\nEmotion breakdown:")
        for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / processed * 100) if processed > 0 else 0
            print(f"  {emotion.capitalize():10s}: {count:4d} ({percentage:5.1f}%)")
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