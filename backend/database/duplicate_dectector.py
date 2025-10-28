"""
duplicate_detector.py
---------------------
Detects and prevents duplicate posts from being inserted into the database.
Uses multiple detection strategies for accuracy.
"""

import hashlib
import re
from typing import Optional, Tuple
from difflib import SequenceMatcher
import sqlite3


class DuplicateDetector:
    """
    Detects duplicate posts using multiple strategies:
    1. Exact text match
    2. Normalized text match (removes punctuation, lowercase)
    3. Hash-based detection (first 200 characters)
    4. Fuzzy matching (85%+ similarity)
    """
    
    def __init__(self, db_manager):
        """
        Initialize duplicate detector.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        self.similarity_threshold = 0.85  # 85% similarity = duplicate
        
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison by:
        - Converting to lowercase
        - Removing extra whitespace
        - Removing punctuation
        - Removing URLs
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove punctuation and special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def create_hash(self, text: str, length: int = 200) -> str:
        """
        Create hash from first N characters of normalized text.
        
        Args:
            text: Text to hash
            length: Number of characters to use (default: 200)
        
        Returns:
            MD5 hash string
        """
        normalized = self.normalize_text(text)
        truncated = normalized[:length]
        return hashlib.md5(truncated.encode()).hexdigest()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity ratio between two texts.
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        
        # Use SequenceMatcher for fuzzy comparison
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def is_duplicate_exact(self, text: str) -> Tuple[bool, Optional[int]]:
        """
        Check for exact text match in database.
        
        Returns:
            (is_duplicate, existing_post_id)
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM raw_posts 
            WHERE text = ? 
            LIMIT 1
        ''', (text,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return (True, result['id'])
        return (False, None)
    
    def is_duplicate_normalized(self, text: str) -> Tuple[bool, Optional[int]]:
        """
        Check for normalized text match (case-insensitive, no punctuation).
        
        Returns:
            (is_duplicate, existing_post_id)
        """
        normalized = self.normalize_text(text)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get all recent posts (last 7 days) for comparison
        cursor.execute('''
            SELECT id, text FROM raw_posts 
            WHERE timestamp > datetime('now', '-7 days')
        ''')
        
        posts = cursor.fetchall()
        conn.close()
        
        for post in posts:
            if self.normalize_text(post['text']) == normalized:
                return (True, post['id'])
        
        return (False, None)
    
    def is_duplicate_hash(self, text: str) -> Tuple[bool, Optional[int]]:
        """
        Check for duplicate using hash of first 200 characters.
        Fast method for large databases.
        
        Returns:
            (is_duplicate, existing_post_id)
        """
        text_hash = self.create_hash(text, length=200)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Check if we have this hash in recent posts
        cursor.execute('''
            SELECT id, text FROM raw_posts 
            WHERE timestamp > datetime('now', '-7 days')
        ''')
        
        posts = cursor.fetchall()
        conn.close()
        
        for post in posts:
            post_hash = self.create_hash(post['text'], length=200)
            if post_hash == text_hash:
                return (True, post['id'])
        
        return (False, None)
    
    def is_duplicate_fuzzy(self, text: str) -> Tuple[bool, Optional[int]]:
        """
        Check for duplicate using fuzzy matching (85%+ similarity).
        Catches near-duplicates with slight variations.
        
        Returns:
            (is_duplicate, existing_post_id)
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get recent posts from same day for comparison
        cursor.execute('''
            SELECT id, text FROM raw_posts 
            WHERE timestamp > datetime('now', '-1 day')
        ''')
        
        posts = cursor.fetchall()
        conn.close()
        
        for post in posts:
            similarity = self.calculate_similarity(text, post['text'])
            if similarity >= self.similarity_threshold:
                return (True, post['id'])
        
        return (False, None)
    
    def check_duplicate(self, text: str, use_fuzzy: bool = False) -> Tuple[bool, str, Optional[int]]:
        """
        Comprehensive duplicate check using multiple strategies.
        
        Args:
            text: Text to check
            use_fuzzy: Enable fuzzy matching (slower but more accurate)
        
        Returns:
            (is_duplicate, detection_method, existing_post_id)
        """
        if not text or len(text.strip()) < 10:
            return (False, "too_short", None)
        
        # Strategy 1: Exact match (fastest)
        is_dup, post_id = self.is_duplicate_exact(text)
        if is_dup:
            return (True, "exact_match", post_id)
        
        # Strategy 2: Hash-based (fast, reliable)
        is_dup, post_id = self.is_duplicate_hash(text)
        if is_dup:
            return (True, "hash_match", post_id)
        
        # Strategy 3: Normalized text (catches case variations)
        is_dup, post_id = self.is_duplicate_normalized(text)
        if is_dup:
            return (True, "normalized_match", post_id)
        
        # Strategy 4: Fuzzy matching (optional, slower)
        if use_fuzzy:
            is_dup, post_id = self.is_duplicate_fuzzy(text)
            if is_dup:
                return (True, "fuzzy_match", post_id)
        
        return (False, "unique", None)
    
    def get_duplicate_stats(self) -> dict:
        """
        Get statistics about duplicates in the database.
        
        Returns:
            Dictionary with duplicate statistics
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Total posts
        cursor.execute('SELECT COUNT(*) as total FROM raw_posts')
        total = cursor.fetchone()['total']
        
        # Posts from last 24 hours
        cursor.execute('''
            SELECT COUNT(*) as recent 
            FROM raw_posts 
            WHERE timestamp > datetime('now', '-1 day')
        ''')
        recent = cursor.fetchone()['recent']
        
        # Estimate duplicates by checking normalized text
        cursor.execute('''
            SELECT COUNT(*) as potential_duplicates
            FROM (
                SELECT LOWER(SUBSTR(text, 1, 200)) as normalized, COUNT(*) as cnt
                FROM raw_posts
                GROUP BY normalized
                HAVING cnt > 1
            )
        ''')
        duplicates = cursor.fetchone()['potential_duplicates']
        
        conn.close()
        
        return {
            'total_posts': total,
            'recent_posts_24h': recent,
            'potential_duplicate_groups': duplicates,
            'estimated_duplicate_rate': round((duplicates / total * 100), 1) if total > 0 else 0
        }
    
    def clean_duplicates(self, dry_run: bool = True) -> int:
        """
        Remove duplicate posts from database (keeps oldest).
        
        Args:
            dry_run: If True, only report what would be deleted
        
        Returns:
            Number of duplicates removed (or would be removed)
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Find duplicates based on normalized first 200 characters
        cursor.execute('''
            SELECT id, text, timestamp,
                   LOWER(SUBSTR(text, 1, 200)) as normalized
            FROM raw_posts
            ORDER BY timestamp ASC
        ''')
        
        posts = cursor.fetchall()
        seen_hashes = {}
        to_delete = []
        
        for post in posts:
            text_hash = self.create_hash(post['text'])
            
            if text_hash in seen_hashes:
                # This is a duplicate
                to_delete.append(post['id'])
            else:
                # First occurrence
                seen_hashes[text_hash] = post['id']
        
        if not dry_run and to_delete:
            # Actually delete duplicates
            cursor.executemany(
                'DELETE FROM raw_posts WHERE id = ?',
                [(pid,) for pid in to_delete]
            )
            conn.commit()
        
        conn.close()
        
        return len(to_delete)


# Helper function for easy integration
def is_duplicate(db_manager, text: str, use_fuzzy: bool = False) -> bool:
    """
    Quick helper function to check if text is duplicate.
    
    Args:
        db_manager: DatabaseManager instance
        text: Text to check
        use_fuzzy: Enable fuzzy matching
    
    Returns:
        True if duplicate, False if unique
    """
    detector = DuplicateDetector(db_manager)
    is_dup, method, post_id = detector.check_duplicate(text, use_fuzzy=use_fuzzy)
    return is_dup