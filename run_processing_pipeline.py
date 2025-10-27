"""
run_processing_pipeline.py
---------------------------
Simplified processing pipeline - runs the 3 core steps only.
No dependency checks, no schema updates (already done).

Usage:
    python run_processing_pipeline.py
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_processing():
    """Run the 3-step processing pipeline."""
    
    start_time = datetime.now()
    
    print("\n" + "="*60)
    print("PULSENET PROCESSING PIPELINE")
    print("="*60 + "\n")
    
    try:
        # STEP 1: Emotion Analysis
        print("Step 1/3: Analyzing emotions...")
        from backend.processing.emotion_analyzer import process_posts as analyze_emotions
        analyze_emotions()
        print("✓ Emotion analysis complete\n")
        
        # STEP 2: Location Extraction
        print("Step 2/3: Extracting locations...")
        from backend.processing.location_extractor import process_posts as extract_locations
        extract_locations()
        print("✓ Location extraction complete\n")
        
        # STEP 3: Data Aggregation
        print("Step 3/3: Aggregating data...")
        from backend.processing.aggregator import process_all_zoom_levels as aggregate_data
        aggregate_data()
        print("✓ Data aggregation complete\n")
        
        # Done
        elapsed = (datetime.now() - start_time).total_seconds()
        print("="*60)
        print(f"✓ Pipeline complete in {elapsed/60:.1f} minutes")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    run_processing()