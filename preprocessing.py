"""
preprocessing.py
----------------
Module: Text Preprocessing for Email Spam Classification.

This module handles:
1. Handling missing values (null / empty strings).
2. Combining email Subject and Body.
3. Lowercasing text.
4. Cleaning whitespace and noise while preserving spam indicators ($ ! %).
5. Tokenization (splitting into meaningful words).

Author: 2nd-Year B.Tech Computer Science Student Project
Academic Title: Spam Email Classification Engine Using Conditional Probability
"""

import re
import string

def clean_missing_values(subject, body):
    """
    Ensures subject and body are valid strings, replacing None with empty string.
    """
    clean_subj = str(subject) if subject is not None else ""
    clean_bod = str(body) if body is not None else ""
    # Treat 'nan' strings from pandas as empty
    if clean_subj.strip().lower() == "nan":
        clean_subj = ""
    if clean_bod.strip().lower() == "nan":
        clean_bod = ""
    return clean_subj.strip(), clean_bod.strip()

def combine_subject_and_body(subject, body):
    """
    Combines email subject and email body into a single coherent text block.
    Subject often carries strong spam indicators (e.g., URGENT, FREE, WON).
    """
    clean_subj, clean_bod = clean_missing_values(subject, body)
    if clean_subj and clean_bod:
        return f"{clean_subj} {clean_bod}"
    return clean_subj or clean_bod or ""

def normalize_text(text):
    """
    Normalizes text by:
    1. Converting to lowercase.
    2. Normalizing multiple spaces, tabs, and newlines.
    3. Retaining basic alphanumeric characters and high-signal spam punctuation.
    """
    if not text:
        return ""
    
    # 1. Lowercase
    text = text.lower()
    
    # 2. Replace multiple whitespaces/newlines with single space
    text = re.sub(r'\s+', ' ', text)
    
    # 3. Strip leading and trailing whitespace
    return text.strip()

def tokenize(text):
    """
    Tokenizes text into a list of word tokens.
    Extracts words containing letters and numbers (at least 2 chars).
    """
    if not text:
        return []
    
    # Regex to extract words/tokens
    tokens = re.findall(r'\b[a-zA-Z0-9_\$]{2,}\b', text.lower())
    return tokens

def preprocess_email(subject, body):
    """
    Complete preprocessing pipeline for an incoming email:
    Combines -> Cleans missing values -> Normalizes -> Returns cleaned text and tokens.
    """
    combined = combine_subject_and_body(subject, body)
    normalized = normalize_text(combined)
    tokens = tokenize(normalized)
    return {
        "combined_text": combined,
        "normalized_text": normalized,
        "tokens": tokens,
        "token_count": len(tokens)
    }

if __name__ == "__main__":
    # Self-test for beginner verification
    test_subject = "URGENT: Claim your $1,000,000 lottery prize NOW!"
    test_body = "Congratulations winner! Visit http://claim-prize.com to claim. Call 1800-555!"
    result = preprocess_email(test_subject, test_body)
    print("Preprocessing Test:")
    print("Normalized Text:", result["normalized_text"])
    print("Tokens Found:", result["tokens"][:8], "...")
    print("Total Tokens:", result["token_count"])
