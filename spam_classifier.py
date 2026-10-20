"""
spam_classifier.py
------------------
Module: Email Spam Classification Inference Engine.

Integrates:
1. Trained Scikit-Learn MultinomialNB model
2. TfidfVectorizer feature extractor
3. ConditionalProbabilityEngine for granular Bayes Theorem breakdowns
4. Structural feature extraction (URLs, capitalization, special characters)

Author: 2nd-Year B.Tech Computer Science Student Project
Academic Title: Spam Email Classification Engine Using Conditional Probability
"""

import os
import joblib
from preprocessing import combine_subject_and_body, normalize_text
from feature_extraction import extract_email_features

MODEL_PATH = "models/spam_model.pkl"

class SpamClassifier:
    """
    Singleton-style classifier loader and inference provider.
    """
    _instance = None
    _model_data = None

    def __init__(self, model_path=MODEL_PATH):
        self.model_path = model_path
        self.load_model()

    def load_model(self):
        if not os.path.exists(self.model_path):
            print(f"[Warning] Model file not found at {self.model_path}. Triggering training...")
            try:
                import train_model
                train_model.train()
            except Exception as e:
                print(f"[Error] Automatic training failed: {e}")
                self._model_data = None
                return

        try:
            self._model_data = joblib.load(self.model_path)
            print("[SpamClassifier] Successfully loaded spam classification model bundle.")
        except Exception as e:
            print(f"[Error] Failed to load model bundle: {e}")
            self._model_data = None

    @property
    def is_ready(self):
        return self._model_data is not None

    def get_metadata(self):
        """Returns trained model performance metrics, dataset stats, and Chi-square results."""
        if not self.is_ready:
            return {}
        return {
            "eval_metrics": self._model_data.get("eval_metrics", {}),
            "chi2_results": self._model_data.get("chi2_results", {}),
            "dataset_stats": self._model_data.get("dataset_stats", {}),
            "vocabulary_size": self._model_data.get("vocabulary_size", 0),
            "training_samples": self._model_data.get("training_samples", 0),
            "testing_samples": self._model_data.get("testing_samples", 0)
        }

    def classify(self, subject, body):
        """
        Classifies an email and returns detailed Bayesian reasoning.
        """
        if not self.is_ready:
            # Fallback heuristic if model not loaded
            return {
                "prediction": "HAM",
                "folder": "inbox",
                "is_spam": False,
                "spam_probability": 10.0,
                "ham_probability": 90.0,
                "indicators": ["Model not loaded; default Ham fallback applied."],
                "word_breakdowns": [],
                "structural_features": {}
            }

        classifier = self._model_data["classifier"]
        vectorizer = self._model_data["vectorizer"]
        prob_engine = self._model_data.get("prob_engine")

        # 1. Preprocess & extract structural features
        structural_feats = extract_email_features(subject, body)
        combined = combine_subject_and_body(subject, body)
        normalized = normalize_text(combined)

        # 2. Vectorize text with TF-IDF
        X_vec = vectorizer.transform([normalized])

        # 3. MultinomialNB probabilities
        probs = classifier.predict_proba(X_vec)[0]  # [P(Ham), P(Spam)]
        ham_prob = round(float(probs[0]) * 100, 2)
        spam_prob = round(float(probs[1]) * 100, 2)

        # Ensure probabilities sum to 100
        if round(ham_prob + spam_prob, 2) != 100.0:
            spam_prob = round(100.0 - ham_prob, 2)

        prediction = "SPAM" if spam_prob >= 50.0 else "HAM"
        folder = "spam" if prediction == "SPAM" else "inbox"

        # 4. Bayesian Step-by-step reasoning via ConditionalProbabilityEngine
        bayes_explanation = {}
        if prob_engine:
            bayes_explanation = prob_engine.explain_classification(normalized, top_n=6)

        # 5. Compile academic explanation indicators
        indicators = list(structural_feats.get("indicators", []))
        
        # Add word probability indicators from Bayes engine
        top_words = bayes_explanation.get("top_words", [])
        if top_words:
            spammy_words = [w for w in top_words if w["p_spam_given_word"] > 0.6]
            hammy_words = [w for w in top_words if w["p_ham_given_word"] > 0.6]
            if spammy_words:
                top_s = spammy_words[0]
                indicators.append(
                    f"Strong spam token: '{top_s['word']}' has P(Spam|'{top_s['word']}') = {round(top_s['p_spam_given_word']*100, 1)}%"
                )
            elif hammy_words:
                top_h = hammy_words[0]
                indicators.append(
                    f"Workplace token: '{top_h['word']}' has P(Ham|'{top_h['word']}') = {round(top_h['p_ham_given_word']*100, 1)}%"
                )

        return {
            "prediction": prediction,
            "folder": folder,
            "is_spam": (prediction == "SPAM"),
            "spam_probability": spam_prob,
            "ham_probability": ham_prob,
            "indicators": indicators,
            "structural_features": structural_feats,
            "bayes_explanation": bayes_explanation,
            "top_words": top_words,
            "priors": {
                "P(Spam)": round(getattr(prob_engine, "prior_spam", 0.4), 4),
                "P(Ham)": round(getattr(prob_engine, "prior_ham", 0.6), 4)
            }
        }

# Global singleton helper
_classifier_instance = None

def get_classifier():
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = SpamClassifier()
    return _classifier_instance

def classify_email(subject, body):
    """Convenience functional wrapper for classification."""
    return get_classifier().classify(subject, body)

if __name__ == "__main__":
    clf = get_classifier()
    res1 = clf.classify(
        "URGENT LOTTERY WINNER!",
        "Congratulations! You have won $1,000,000 cash. Click http://claim.com now to collect."
    )
    print("Test Spam Classification:")
    print("  Prediction:", res1["prediction"])
    print(f"  Spam Prob: {res1['spam_probability']}% | Ham Prob: {res1['ham_probability']}%")
    print("  Indicators:", res1["indicators"])

    res2 = clf.classify(
        "Quarterly pipeline maintenance schedule",
        "Please review the attached spreadsheet for our Houston meeting regarding energy contracts."
    )
    print("\nTest Ham Classification:")
    print("  Prediction:", res2["prediction"])
    print(f"  Spam Prob: {res2['spam_probability']}% | Ham Prob: {res2['ham_probability']}%")
    print("  Indicators:", res2["indicators"])
