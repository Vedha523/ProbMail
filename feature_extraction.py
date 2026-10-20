"""
feature_extraction.py
---------------------
Module: Feature Extraction for Email Spam Classification.

Extracts both:
1. Text Features:
   - Word token frequencies
   - TF-IDF representations (via vectorizer)
   - Suspicious keyword matching
2. Email Structural Features:
   - Total character length
   - Total word count
   - URL / link count (http, https, www)
   - Special character count (!, $, %, ?, *, #)
   - Numerical digit count
   - Uppercase character count & uppercase ratio (shouting indicator)

Author: 2nd-Year B.Tech Computer Science Student Project
Academic Title: Spam Email Classification Engine Using Conditional Probability
"""

import re
import string
from collections import Counter
from preprocessing import combine_subject_and_body, tokenize

# Prominent spam trigger keywords commonly identified in academic email forensics
SPAM_TRIGGER_KEYWORDS = [
    "free", "guaranteed", "prize", "winner", "urgent", "refinance",
    "viagra", "cialis", "lottery", "congratulations", "cash", "bonus",
    "discount", "click", "million", "pre-approved", "credit", "debt",
    "crypto", "bitcoin", "investment", "unclaimed", "claim", "limited time",
    "exclusive", "act now", "100%", "risk-free", "miracle", "overnight"
]

# Prominent Enron corporate / legitimate ham keywords
HAM_TRIGGER_KEYWORDS = [
    "meeting", "conference", "attached", "schedule", "pipeline",
    "agreement", "contract", "review", "houston", "trading", "ferc",
    "compliance", "regards", "committee", "operations", "quarterly",
    "risk", "tariffs", "energy", "memo", "forecast", "intranet"
]

def count_urls(text):
    """Counts occurrences of web URLs (http://, https://, www.)."""
    if not text:
        return 0
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(?:com|org|net|biz|info)/[^\s]*)'
    matches = re.findall(url_pattern, text, re.IGNORECASE)
    return len(matches)

def count_special_characters(text):
    """Counts high-signal spam special characters: !, $, %, *, ?, #."""
    if not text:
        return 0
    special_chars = set("!$%*?#")
    return sum(1 for char in text if char in special_chars)

def count_exclamation_marks(text):
    """Counts exclamation marks, often used in spam for false urgency."""
    if not text:
        return 0
    return text.count("!")

def count_currency_symbols(text):
    """Counts currency symbols ($, €, £, ¥)."""
    if not text:
        return 0
    currency_chars = set("$€£¥")
    return sum(1 for char in text if char in currency_chars)

def count_digits(text):
    """Counts numerical digits (0-9)."""
    if not text:
        return 0
    return sum(1 for char in text if char.isdigit())

def calculate_capitalization(text):
    """
    Calculates:
    - total uppercase character count
    - ratio of uppercase letters to total alphabet characters
    High uppercase ratio is an indicator of 'shouting' in spam.
    """
    if not text:
        return {"uppercase_count": 0, "uppercase_ratio": 0.0}
    
    alpha_chars = [c for c in text if c.isalpha()]
    if not alpha_chars:
        return {"uppercase_count": 0, "uppercase_ratio": 0.0}
    
    upper_chars = [c for c in alpha_chars if c.isupper()]
    count = len(upper_chars)
    ratio = round(count / len(alpha_chars), 4)
    return {"uppercase_count": count, "uppercase_ratio": ratio}

def find_suspicious_words(text):
    """
    Finds and counts occurrences of known spam trigger keywords in the text.
    """
    if not text:
        return {"found_keywords": [], "keyword_count": 0}
    
    lower_text = text.lower()
    found = []
    for kw in SPAM_TRIGGER_KEYWORDS:
        # Check whole word match or phrase match
        pattern = r'\b' + re.escape(kw) + r'\b'
        matches = re.findall(pattern, lower_text)
        if matches:
            found.append({"keyword": kw, "count": len(matches)})
    
    total_found = sum(item["count"] for item in found)
    return {
        "found_keywords": found,
        "keyword_count": total_found
    }

def find_ham_indicators(text):
    """
    Finds and counts occurrences of legitimate corporate / ham keywords.
    """
    if not text:
        return {"found_keywords": [], "keyword_count": 0}
    
    lower_text = text.lower()
    found = []
    for kw in HAM_TRIGGER_KEYWORDS:
        pattern = r'\b' + re.escape(kw) + r'\b'
        matches = re.findall(pattern, lower_text)
        if matches:
            found.append({"keyword": kw, "count": len(matches)})
    
    total_found = sum(item["count"] for item in found)
    return {
        "found_keywords": found,
        "keyword_count": total_found
    }

def extract_email_features(subject, body):
    """
    Comprehensive feature extraction function for a single email.
    Combines text analysis and structural statistical features.
    """
    raw_combined = combine_subject_and_body(subject, body)
    tokens = tokenize(raw_combined)
    cap_info = calculate_capitalization(raw_combined)
    suspicious = find_suspicious_words(raw_combined)
    ham_ind = find_ham_indicators(raw_combined)
    
    features = {
        "char_length": len(raw_combined),
        "word_count": len(tokens),
        "url_count": count_urls(raw_combined),
        "special_char_count": count_special_characters(raw_combined),
        "exclamation_count": count_exclamation_marks(raw_combined),
        "currency_count": count_currency_symbols(raw_combined),
        "digit_count": count_digits(raw_combined),
        "uppercase_count": cap_info["uppercase_count"],
        "uppercase_ratio": cap_info["uppercase_ratio"],
        "suspicious_keyword_count": suspicious["keyword_count"],
        "suspicious_keywords_found": [k["keyword"] for k in suspicious["found_keywords"]],
        "ham_keyword_count": ham_ind["keyword_count"],
        "ham_keywords_found": [k["keyword"] for k in ham_ind["found_keywords"]],
    }
    
    # Generate human-readable explanation flags
    indicators = []
    if features["url_count"] > 0:
        indicators.append(f"Contains {features['url_count']} external URL link(s)")
    if features["uppercase_ratio"] > 0.25:
        indicators.append(f"High uppercase ratio ({int(features['uppercase_ratio']*100)}% capital letters)")
    if features["exclamation_count"] >= 2:
        indicators.append(f"Multiple exclamation marks ({features['exclamation_count']} '!')")
    if features["currency_count"] > 0:
        indicators.append(f"Currency symbols detected ({features['currency_count']})")
    if features["suspicious_keyword_count"] > 0:
        kws = ", ".join(features["suspicious_keywords_found"][:4])
        indicators.append(f"Promotional spam keywords: {kws}")
    if features["ham_keyword_count"] > 0 and features["suspicious_keyword_count"] == 0:
        kws = ", ".join(features["ham_keywords_found"][:3])
        indicators.append(f"Legitimate workplace keywords: {kws}")
    
    features["indicators"] = indicators
    return features

if __name__ == "__main__":
    sample_subj = "URGENT WINNER: Claim $10,000 Cash Prize NOW!"
    sample_body = "Congratulations! Click http://prize-claim.com/win immediately. Free entry, 100% guaranteed payout!"
    feats = extract_email_features(sample_subj, sample_body)
    print("Feature Extraction Demonstration:")
    for k, v in feats.items():
        print(f"  {k}: {v}")
