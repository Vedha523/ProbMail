"""
statistics.py
-------------
Module: Descriptive Statistical Analysis and Visualizations for Email Datasets.

Calculates:
- Frequency counts (Spam vs Ham)
- Central tendencies: Mean, Median
- Dispersion: Standard Deviation, Variance, Min, Max
Across key dimensions:
- Character length
- Word count
- URL count
- Special characters count
- Capitalization ratio
- Numerical digit count

Also generates static publication-quality Matplotlib figures in static/img/.

Author: 2nd-Year B.Tech Computer Science Student Project
Academic Title: Spam Email Classification Engine Using Conditional Probability
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Headless backend for web server
import matplotlib.pyplot as plt

from feature_extraction import (
    count_urls,
    count_special_characters,
    count_digits,
    calculate_capitalization,
    tokenize
)
from preprocessing import combine_subject_and_body

def compute_metric_stats(values):
    """
    Computes mean, median, standard deviation, min, and max for a numeric list or array.
    """
    if values is None or len(values) == 0:
        return {"mean": 0.0, "median": 0.0, "std": 0.0, "min": 0, "max": 0}
    
    arr = np.array(values, dtype=float)
    return {
        "mean": round(float(np.mean(arr)), 2),
        "median": round(float(np.median(arr)), 2),
        "std": round(float(np.std(arr)), 2),
        "min": round(float(np.min(arr)), 2),
        "max": round(float(np.max(arr)), 2)
    }

def analyze_dataset_statistics(df):
    """
    Runs full descriptive statistical profiling on an email DataFrame
    with columns ['Subject', 'Message', 'Spam/Ham'].
    """
    # Normalize labels
    labels = df['Spam/Ham'].astype(str).str.lower().values
    is_spam = np.array([label == 'spam' for label in labels])
    is_ham = np.invert(is_spam)

    total_emails = len(df)
    spam_count = int(np.sum(is_spam))
    ham_count = int(np.sum(is_ham))

    spam_pct = round((spam_count / total_emails) * 100, 2) if total_emails > 0 else 0
    ham_pct = round((ham_count / total_emails) * 100, 2) if total_emails > 0 else 0

    # Extract email metrics
    combined_texts = [
        combine_subject_and_body(row.get('Subject', ''), row.get('Message', ''))
        for _, row in df.iterrows()
    ]

    char_lengths = [len(t) for t in combined_texts]
    word_counts = [len(tokenize(t)) for t in combined_texts]
    url_counts = [count_urls(t) for t in combined_texts]
    special_counts = [count_special_characters(t) for t in combined_texts]
    digit_counts = [count_digits(t) for t in combined_texts]
    cap_ratios = [calculate_capitalization(t)["uppercase_ratio"] for t in combined_texts]

    # Convert to numpy for boolean indexing
    cl_arr = np.array(char_lengths)
    wc_arr = np.array(word_counts)
    url_arr = np.array(url_counts)
    sc_arr = np.array(special_counts)
    dg_arr = np.array(digit_counts)
    cr_arr = np.array(cap_ratios)

    stats = {
        "summary": {
            "total_emails": total_emails,
            "spam_count": spam_count,
            "ham_count": ham_count,
            "spam_percentage": spam_pct,
            "ham_percentage": ham_pct
        },
        "overall": {
            "char_length": compute_metric_stats(char_lengths),
            "word_count": compute_metric_stats(word_counts),
            "url_count": compute_metric_stats(url_counts),
            "special_char_count": compute_metric_stats(special_counts),
            "digit_count": compute_metric_stats(digit_counts),
            "capitalization_ratio": compute_metric_stats(cap_ratios)
        },
        "by_class": {
            "spam": {
                "char_length": compute_metric_stats(cl_arr[is_spam]),
                "word_count": compute_metric_stats(wc_arr[is_spam]),
                "url_count": compute_metric_stats(url_arr[is_spam]),
                "special_char_count": compute_metric_stats(sc_arr[is_spam]),
                "digit_count": compute_metric_stats(dg_arr[is_spam]),
                "capitalization_ratio": compute_metric_stats(cr_arr[is_spam])
            },
            "ham": {
                "char_length": compute_metric_stats(cl_arr[is_ham]),
                "word_count": compute_metric_stats(wc_arr[is_ham]),
                "url_count": compute_metric_stats(url_arr[is_ham]),
                "special_char_count": compute_metric_stats(sc_arr[is_ham]),
                "digit_count": compute_metric_stats(dg_arr[is_ham]),
                "capitalization_ratio": compute_metric_stats(cr_arr[is_ham])
            }
        }
    }

    return stats

def generate_statistical_plots(stats, output_dir="static/img"):
    """
    Generates academic Matplotlib statistical charts saved to output_dir:
    1. class_distribution.png
    2. feature_comparison.png
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Class Distribution Plot
    fig, ax = plt.subplots(figsize=(6, 4))
    classes = ['Legitimate (Ham)', 'Spam']
    counts = [stats['summary']['ham_count'], stats['summary']['spam_count']]
    colors = ['#10B981', '#EF4444']
    
    bars = ax.bar(classes, counts, color=colors, width=0.5, edgecolor='#333', linewidth=1)
    ax.set_ylabel('Number of Emails', fontsize=11, fontweight='bold')
    ax.set_title('Dataset Class Distribution (Enron Corpus)', fontsize=12, fontweight='bold', pad=12)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Add data labels
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + (max(counts)*0.015),
                f'{int(h)} ({round(h/sum(counts)*100, 1)}%)',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    dist_path = os.path.join(output_dir, 'class_distribution.png')
    plt.savefig(dist_path, dpi=160)
    plt.close()

    # 2. Key Feature Means Comparison (Spam vs Ham)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    metrics = ['Avg URLs', 'Avg Special Chars', 'Avg Digits', 'Cap Ratio (x10)']
    
    spam_vals = [
        stats['by_class']['spam']['url_count']['mean'],
        stats['by_class']['spam']['special_char_count']['mean'],
        stats['by_class']['spam']['digit_count']['mean'],
        stats['by_class']['spam']['capitalization_ratio']['mean'] * 10
    ]
    ham_vals = [
        stats['by_class']['ham']['url_count']['mean'],
        stats['by_class']['ham']['special_char_count']['mean'],
        stats['by_class']['ham']['digit_count']['mean'],
        stats['by_class']['ham']['capitalization_ratio']['mean'] * 10
    ]

    x = np.arange(len(metrics))
    width = 0.35

    ax.bar(x - width/2, ham_vals, width, label='Ham (Enron)', color='#10B981', edgecolor='#333', alpha=0.9)
    ax.bar(x + width/2, spam_vals, width, label='Spam', color='#EF4444', edgecolor='#333', alpha=0.9)

    ax.set_ylabel('Mean Occurrence / Value', fontsize=11, fontweight='bold')
    ax.set_title('Comparative Mean Feature Values: Ham vs Spam', fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=10, fontweight='medium')
    ax.legend(frameon=True)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    feat_path = os.path.join(output_dir, 'feature_comparison.png')
    plt.savefig(feat_path, dpi=160)
    plt.close()

    return {
        "class_distribution_plot": "/static/img/class_distribution.png",
        "feature_comparison_plot": "/static/img/feature_comparison.png"
    }

if __name__ == "__main__":
    df_sample = pd.read_csv("data/enron_spam_data.csv")
    stats = analyze_dataset_statistics(df_sample)
    plots = generate_statistical_plots(stats)
    print("Dataset Statistical Summary:")
    print("  Total:", stats['summary']['total_emails'])
    print("  Spam:", stats['summary']['spam_count'])
    print("  Ham:", stats['summary']['ham_count'])
    print("  Plots saved:", plots)
