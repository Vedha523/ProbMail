"""
evaluation.py
-------------
Module: Model Performance Evaluation and Confusion Matrix Generation.

Academic Metrics Computed:
1. Accuracy: Overall proportion of correct predictions.
   Formula: (TP + TN) / (TP + TN + FP + FN)
2. Precision: Out of all emails predicted as SPAM, how many were actually SPAM.
   Formula: TP / (TP + FP)
   (Critical in email filtering: High precision prevents legitimate Ham emails from being lost in Spam)
3. Recall (Sensitivity): Out of all actual SPAM emails, how many were detected.
   Formula: TP / (TP + FN)
4. F1-Score: Harmonic mean of Precision and Recall.
   Formula: 2 * (Precision * Recall) / (Precision + Recall)
5. Confusion Matrix:
   - TP (True Positive): Actual Spam correctly predicted as Spam
   - TN (True Negative): Actual Ham correctly predicted as Ham
   - FP (False Positive): Actual Ham incorrectly predicted as Spam (Type I Error)
   - FN (False Negative): Actual Spam incorrectly predicted as Ham (Type II Error)

Author: 2nd-Year B.Tech Computer Science Student Project
Academic Title: Spam Email Classification Engine Using Conditional Probability
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

def evaluate_model(y_true, y_pred, output_dir="static/img"):
    """
    Evaluates binary classification predictions.
    y_true, y_pred: Arrays/lists of 1 (Spam) and 0 (Ham), or 'spam' and 'ham'.
    """
    # Normalize labels to integers (1: Spam, 0: Ham)
    y_true_bin = [1 if str(y).lower() == 'spam' or y == 1 else 0 for y in y_true]
    y_pred_bin = [1 if str(y).lower() == 'spam' or y == 1 else 0 for y in y_pred]

    acc = accuracy_score(y_true_bin, y_pred_bin)
    prec = precision_score(y_true_bin, y_pred_bin, zero_division=0)
    rec = recall_score(y_true_bin, y_pred_bin, zero_division=0)
    f1 = f1_score(y_true_bin, y_pred_bin, zero_division=0)

    # Compute confusion matrix: [[TN, FP], [FN, TP]]
    cm = confusion_matrix(y_true_bin, y_pred_bin, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    # Generate Confusion Matrix Visualization
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Draw heatmap
    cax = ax.matshow(cm, cmap=plt.cm.Blues, alpha=0.85)
    fig.colorbar(cax)

    # Labels and titles
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Pred Ham (0)', 'Pred Spam (1)'], fontsize=11, fontweight='bold')
    ax.set_yticklabels(['Actual Ham (0)', 'Actual Spam (1)'], fontsize=11, fontweight='bold')
    ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('True Label', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Evaluation Confusion Matrix', fontsize=13, fontweight='bold', pad=20)

    # Cell annotations
    cell_descriptions = [
        [f"True Negative (TN)\n{tn}", f"False Positive (FP)\n{fp}"],
        [f"False Negative (FN)\n{fn}", f"True Positive (TP)\n{tp}"]
    ]
    
    for i in range(2):
        for j in range(2):
            color = "white" if cm[i, j] > (cm.max() / 2) else "black"
            ax.text(j, i, cell_descriptions[i][j],
                    ha="center", va="center", color=color,
                    fontsize=11, fontweight="bold")

    plt.tight_layout()
    cm_path = os.path.join(output_dir, 'confusion_matrix.png')
    plt.savefig(cm_path, dpi=160)
    plt.close()

    metrics = {
        "accuracy": round(float(acc), 4),
        "accuracy_pct": round(float(acc) * 100, 2),
        "precision": round(float(prec), 4),
        "precision_pct": round(float(prec) * 100, 2),
        "recall": round(float(rec), 4),
        "recall_pct": round(float(rec) * 100, 2),
        "f1_score": round(float(f1), 4),
        "f1_score_pct": round(float(f1) * 100, 2),
        "confusion_matrix": {
            "true_positive": int(tp),
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "total_tested": int(tp + tn + fp + fn)
        },
        "confusion_matrix_plot": "/static/img/confusion_matrix.png",
        "explanations": {
            "accuracy": "Proportion of all emails (Spam & Ham) correctly classified.",
            "precision": "Reliability of spam detection. High precision ensures non-spam is not marked spam.",
            "recall": "Sensitivity. Percentage of all actual spam emails successfully caught.",
            "f1_score": "Harmonic balance between precision and recall.",
            "type_1_error": f"False Positives: {fp} legitimate email(s) incorrectly flagged as spam.",
            "type_2_error": f"False Negatives: {fn} spam email(s) missed and landed in inbox."
        }
    }

    return metrics

if __name__ == "__main__":
    # Test evaluation
    y_test = [0, 0, 0, 1, 1, 1, 0, 1]
    y_pred = [0, 0, 1, 1, 1, 0, 0, 1]
    m = evaluate_model(y_test, y_pred)
    print("Model Evaluation Test:")
    print(f"  Accuracy: {m['accuracy_pct']}%")
    print(f"  Precision: {m['precision_pct']}%")
    print(f"  Recall: {m['recall_pct']}%")
    print(f"  F1 Score: {m['f1_score_pct']}%")
    print("  Confusion Matrix:", m["confusion_matrix"])
