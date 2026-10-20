"""
chi_square.py
-------------
Module: Chi-Square (χ²) Statistical Feature Selection.

Academic Definition:
The Chi-Square test tests the null hypothesis (H0) that the occurrence of
a specific word is independent of the email class (Spam or Ham).

Formula:
χ² = Σ [ (Observed - Expected)² / Expected ]

- High χ² Score: The word appears disproportionately more often in one class
  (Spam or Ham) than expected by random chance.
- p-value < 0.05: The association is statistically significant at the 95%
  confidence level, meaning we reject the null hypothesis of independence.

Author: 2nd-Year B.Tech Computer Science Student Project
Academic Title: Spam Email Classification Engine Using Conditional Probability
"""

import numpy as np
import pandas as pd
from sklearn.feature_selection import chi2

def compute_chi_square_features(X_features, y_labels, feature_names, top_n=20, p_threshold=0.05):
    """
    Performs Chi-Square statistical test on feature matrix X against class labels y.
    
    Parameters:
    - X_features: Sparse or dense term-frequency matrix (from CountVectorizer / TF-IDF)
    - y_labels: Array of binary class labels (1 for spam, 0 for ham)
    - feature_names: List of vocabulary words corresponding to columns in X_features
    - top_n: Number of top statistically significant words to return
    - p_threshold: Significance alpha level (standard: 0.05)
    
    Returns:
    - List of dicts with word, chi2_score, p_value, is_significant, and associated_class
    """
    # Compute chi2 statistics and p-values using scikit-learn
    chi2_scores, p_values = chi2(X_features, y_labels)
    
    # Calculate class-specific means to determine which class the word favors
    # y_labels: 1 is spam, 0 is ham
    y_arr = np.array(y_labels)
    spam_mask = (y_arr == 1)
    ham_mask = (y_arr == 0)
    
    # Mean frequency or tf-idf per class
    # Convert sparse matrix slice to array if sparse
    if hasattr(X_features, "toarray"):
        spam_mean = np.array(X_features[spam_mask].mean(axis=0)).flatten()
        ham_mean = np.array(X_features[ham_mask].mean(axis=0)).flatten()
    else:
        spam_mean = np.mean(X_features[spam_mask], axis=0)
        ham_mean = np.mean(X_features[ham_mask], axis=0)

    feature_stats = []
    for i, word in enumerate(feature_names):
        c2 = float(chi2_scores[i])
        pv = float(p_values[i])
        
        # Skip NaNs
        if np.isnan(c2) or np.isnan(pv):
            continue

        associated_class = "SPAM" if spam_mean[i] >= ham_mean[i] else "HAM"
        is_significant = bool(pv < p_threshold)

        feature_stats.append({
            "word": word,
            "chi2_score": round(c2, 4),
            "p_value": round(pv, 6),
            "p_value_sci": f"{pv:.2e}" if pv < 0.0001 else f"{round(pv, 5)}",
            "is_significant": is_significant,
            "associated_class": associated_class,
            "spam_avg": round(float(spam_mean[i]), 4),
            "ham_avg": round(float(ham_mean[i]), 4)
        })

    # Sort descending by Chi-Square score (highest discriminative power first)
    feature_stats.sort(key=lambda x: x["chi2_score"], reverse=True)
    
    significant_count = sum(1 for f in feature_stats if f["is_significant"])
    
    return {
        "total_vocabulary_evaluated": len(feature_names),
        "significant_features_count": significant_count,
        "alpha_threshold": p_threshold,
        "top_features": feature_stats[:top_n],
        "top_spam_features": [f for f in feature_stats if f["associated_class"] == "SPAM"][:top_n // 2],
        "top_ham_features": [f for f in feature_stats if f["associated_class"] == "HAM"][:top_n // 2]
    }

if __name__ == "__main__":
    from sklearn.feature_extraction.text import CountVectorizer
    
    # Quick sanity test
    test_texts = [
        "pipeline gas contract trading meeting",
        "conference schedule pipeline houston",
        "win free cash prize lottery now",
        "urgent discount viagra free bonus money"
    ]
    test_labels = [0, 0, 1, 1]  # 0: Ham, 1: Spam
    
    vec = CountVectorizer()
    X = vec.fit_transform(test_texts)
    names = vec.get_feature_names_out()
    
    results = compute_chi_square_features(X, test_labels, names, top_n=5)
    print("Chi-Square Test Successful:")
    print("Top feature:", results["top_features"][0])
