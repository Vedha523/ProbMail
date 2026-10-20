"""
train_model.py
--------------
Main Training Pipeline for:
"Spam Email Classification Engine Using Conditional Probability"

Executes:
1. Load dataset (data/enron_spam_data.csv)
2. Inspect dataset dimensions & class balance
3. Clean missing values & preprocess text
4. Train/Test split (80% Train, 20% Test)
5. Extract TF-IDF / Bag-of-Words text features
6. Compute Chi-Square (χ²) statistical feature selection
7. Train Scikit-Learn MultinomialNB (Naive Bayes) classifier
8. Train Custom ConditionalProbabilityEngine for granular viva explainability
9. Evaluate on unseen test data (Accuracy, Precision, Recall, F1, Confusion Matrix)
10. Generate statistical & evaluation graphs in static/img/
11. Serialize model artifact to models/spam_model.pkl

Author: 2nd-Year B.Tech Computer Science Student Project
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from preprocessing import combine_subject_and_body, normalize_text, tokenize
from bayes import ConditionalProbabilityEngine
from chi_square import compute_chi_square_features
from statistics import analyze_dataset_statistics, generate_statistical_plots
from evaluation import evaluate_model

DATASET_PATH = "data/enron_spam_data.csv"
MODEL_SAVE_PATH = "models/spam_model.pkl"

def train():
    print("=" * 65)
    print(" SPAM EMAIL CLASSIFICATION ENGINE USING CONDITIONAL PROBABILITY")
    print(" Training & Statistical Feature Selection Pipeline")
    print("=" * 65)

    # 1. Load dataset
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}. Please generate or provide it.")
    
    print(f"\n[Step 1] Loading dataset from: {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)
    print(f"         Total records loaded: {len(df)}")
    print(f"         Columns detected: {list(df.columns)}")

    # 2. Inspect & Clean missing values
    print("\n[Step 2] Cleaning missing values and inspecting class balance...")
    df['Subject'] = df['Subject'].fillna('')
    df['Message'] = df['Message'].fillna('')
    df['Spam/Ham'] = df['Spam/Ham'].astype(str).str.lower().str.strip()

    # Binary target: 1 = Spam, 0 = Ham
    df['target'] = df['Spam/Ham'].apply(lambda x: 1 if x == 'spam' else 0)

    spam_cnt = int(df['target'].sum())
    ham_cnt = len(df) - spam_cnt
    print(f"         Legitimate (Ham) emails: {ham_cnt} ({round(ham_cnt/len(df)*100, 1)}%)")
    print(f"         Spam emails:             {spam_cnt} ({round(spam_cnt/len(df)*100, 1)}%)")

    # 3. Descriptive Statistics & Graph Generation
    print("\n[Step 3] Computing descriptive statistics and generating graphs...")
    stats = analyze_dataset_statistics(df)
    stat_plots = generate_statistical_plots(stats, output_dir="static/img")
    print(f"         Statistical charts generated: {list(stat_plots.keys())}")

    # 4. Text Preprocessing
    print("\n[Step 4] Preprocessing email content (Subject + Body concatenation)...")
    cleaned_texts = [
        normalize_text(combine_subject_and_body(row['Subject'], row['Message']))
        for _, row in df.iterrows()
    ]
    df['cleaned_text'] = cleaned_texts

    # 5. Train / Test Split
    print("\n[Step 5] Splitting data into 80% Training and 20% Testing sets...")
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        df['cleaned_text'],
        df['target'],
        test_size=0.20,
        random_state=42,
        stratify=df['target']
    )
    print(f"         Training samples: {len(X_train_raw)}")
    print(f"         Testing samples:  {len(X_test_raw)}")

    # 6. Feature Extraction (TF-IDF Vectorizer)
    print("\n[Step 6] Extracting TF-IDF text features (Vocabulary & Term Weights)...")
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True
    )
    X_train_tfidf = vectorizer.fit_transform(X_train_raw)
    X_test_tfidf = vectorizer.transform(X_test_raw)
    feature_names = vectorizer.get_feature_names_out()
    print(f"         Vocabulary dimension: {len(feature_names)} unique features/n-grams")

    # 7. Chi-Square (χ²) Statistical Feature Selection
    print("\n[Step 7] Performing Chi-Square (χ²) Statistical Analysis...")
    chi2_results = compute_chi_square_features(
        X_train_tfidf,
        y_train,
        feature_names,
        top_n=30,
        p_threshold=0.05
    )
    print(f"         Statistically significant features (p < 0.05): {chi2_results['significant_features_count']}")
    print("         Top 5 Most Significant Spam Indicators:")
    for f in chi2_results['top_spam_features'][:5]:
        print(f"           • '{f['word']}': χ² = {f['chi2_score']}, p = {f['p_value_sci']}")
    print("         Top 5 Most Significant Ham Indicators:")
    for f in chi2_results['top_ham_features'][:5]:
        print(f"           • '{f['word']}': χ² = {f['chi2_score']}, p = {f['p_value_sci']}")

    # 8. Train Multinomial Naive Bayes Classifier
    print("\n[Step 8] Training Multinomial Naive Bayes (MultinomialNB) model...")
    # alpha=1.0 applies Laplace smoothing
    nb_classifier = MultinomialNB(alpha=1.0)
    nb_classifier.fit(X_train_tfidf, y_train)
    print("         Model successfully fitted with Laplace smoothing (alpha=1.0).")

    # 9. Train Academic Conditional Probability Engine (For granular explainability)
    print("\n[Step 9] Calibrating explicit Conditional Probability Engine...")
    train_tokens = [tokenize(t) for t in X_train_raw]
    train_str_labels = ['spam' if y == 1 else 'ham' for y in y_train]
    prob_engine = ConditionalProbabilityEngine(alpha=1.0)
    prob_engine.train_on_corpus(train_tokens, train_str_labels)
    print(f"         Calculated Priors: P(Spam)={round(prob_engine.prior_spam, 4)}, P(Ham)={round(prob_engine.prior_ham, 4)}")

    # 10. Model Evaluation on Unseen Test Data
    print("\n[Step 10] Evaluating classifier on unseen test set...")
    y_pred = nb_classifier.predict(X_test_tfidf)
    y_prob = nb_classifier.predict_proba(X_test_tfidf)

    eval_metrics = evaluate_model(y_test, y_pred, output_dir="static/img")
    print(f"         Accuracy:  {eval_metrics['accuracy_pct']}%")
    print(f"         Precision: {eval_metrics['precision_pct']}%")
    print(f"         Recall:    {eval_metrics['recall_pct']}%")
    print(f"         F1-Score:  {eval_metrics['f1_score_pct']}%")
    print(f"         Confusion Matrix: {eval_metrics['confusion_matrix']}")

    # 11. Save artifacts
    print("\n[Step 11] Saving model package to disk...")
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    
    model_bundle = {
        "classifier": nb_classifier,
        "vectorizer": vectorizer,
        "prob_engine": prob_engine,
        "chi2_results": chi2_results,
        "eval_metrics": eval_metrics,
        "dataset_stats": stats,
        "vocabulary_size": len(feature_names),
        "classes": ["ham", "spam"],
        "training_samples": len(X_train_raw),
        "testing_samples": len(X_test_raw)
    }

    joblib.dump(model_bundle, MODEL_SAVE_PATH)
    print(f"         Artifact saved to: {MODEL_SAVE_PATH}")
    print("=" * 65)
    print(" TRAINING COMPLETE! The model is ready for the web application.")
    print("=" * 65)

    return model_bundle

if __name__ == "__main__":
    train()
