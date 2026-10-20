"""
bayes.py
--------
Module: Mathematical Implementation of Conditional Probability and Bayes' Theorem.

Academic Concepts Demonstrated:
1. Conditional Probability:
   P(Spam | Feature) and P(Ham | Feature)
   "The probability that an email is Spam given that a specific word/feature appears."

2. Bayes' Theorem:
   P(Spam | X) = [ P(X | Spam) * P(Spam) ] / P(X)
   Where:
   - P(Spam)          = Prior Probability of Spam
   - P(X | Spam)      = Likelihood of observing feature X in Spam
   - P(X)             = Marginal Probability / Evidence
   - P(Spam | X)      = Posterior Probability

3. Naive Bayes Assumption:
   Features are conditionally independent given the class.
   P(W1, W2, ... Wn | Spam) = Product of P(Wi | Spam) for all i

4. Laplace Smoothing (Additive Smoothing):
   Prevents zero-probability problems when a word never appeared in training:
   P(Wi | Class) = (Count(Wi, Class) + alpha) / (TotalWordsInClass + alpha * VocabularySize)

Author: 2nd-Year B.Tech Computer Science Student Project
Academic Title: Spam Email Classification Engine Using Conditional Probability
"""

import math
from preprocessing import tokenize

class ConditionalProbabilityEngine:
    """
    Academically explicit Bayesian inference engine.
    Calculates exact priors, word likelihoods with Laplace smoothing,
    and step-by-step posterior probabilities.
    """
    def __init__(self, alpha=1.0):
        self.alpha = alpha  # Laplace smoothing parameter
        self.total_emails = 0
        self.spam_count = 0
        self.ham_count = 0
        self.prior_spam = 0.5
        self.prior_ham = 0.5
        
        # Word counts per class
        self.spam_word_counts = {}
        self.ham_word_counts = {}
        self.total_spam_words = 0
        self.total_ham_words = 0
        self.vocabulary = set()

    def train_on_corpus(self, tokenized_emails, labels):
        """
        Calculates frequencies, prior probabilities, and word likelihoods
        from a training corpus.
        tokenized_emails: list of lists of word tokens
        labels: list of 'spam' or 'ham'
        """
        self.total_emails = len(labels)
        self.spam_count = sum(1 for label in labels if label.lower() == 'spam')
        self.ham_count = self.total_emails - self.spam_count

        # Prior probabilities: P(Spam) and P(Ham)
        self.prior_spam = self.spam_count / self.total_emails if self.total_emails > 0 else 0.5
        self.prior_ham = self.ham_count / self.total_emails if self.total_emails > 0 else 0.5

        self.spam_word_counts = {}
        self.ham_word_counts = {}
        self.total_spam_words = 0
        self.total_ham_words = 0
        self.vocabulary = set()

        for tokens, label in zip(tokenized_emails, labels):
            is_spam = (label.lower() == 'spam')
            for token in tokens:
                self.vocabulary.add(token)
                if is_spam:
                    self.spam_word_counts[token] = self.spam_word_counts.get(token, 0) + 1
                    self.total_spam_words += 1
                else:
                    self.ham_word_counts[token] = self.ham_word_counts.get(token, 0) + 1
                    self.total_ham_words += 1

    def calculate_word_likelihood(self, word, class_label):
        """
        Calculates P(Word | Class) using Laplace Smoothing:
        P(w | C) = (count(w in C) + alpha) / (total_words_in_C + alpha * |V|)
        """
        vocab_size = len(self.vocabulary)
        if vocab_size == 0:
            vocab_size = 1

        if class_label.lower() == 'spam':
            count = self.spam_word_counts.get(word, 0)
            total = self.total_spam_words
        else:
            count = self.ham_word_counts.get(word, 0)
            total = self.total_ham_words

        likelihood = (count + self.alpha) / (total + (self.alpha * vocab_size))
        return likelihood

    def calculate_single_word_conditional_probability(self, word):
        """
        Calculates P(Spam | Word) and P(Ham | Word) via Bayes' Theorem:
        P(Spam | Word) = [ P(Word | Spam) * P(Spam) ] / P(Word)
        where P(Word) = P(Word | Spam)*P(Spam) + P(Word | Ham)*P(Ham)
        """
        p_word_given_spam = self.calculate_word_likelihood(word, 'spam')
        p_word_given_ham = self.calculate_word_likelihood(word, 'ham')

        # Marginal probability / Evidence: P(Word)
        evidence = (p_word_given_spam * self.prior_spam) + (p_word_given_ham * self.prior_ham)
        if evidence == 0:
            return {"word": word, "p_spam_given_word": 0.5, "p_ham_given_word": 0.5}

        # Bayes' rule application
        p_spam_given_word = (p_word_given_spam * self.prior_spam) / evidence
        p_ham_given_word = (p_word_given_ham * self.prior_ham) / evidence

        return {
            "word": word,
            "p_word_given_spam": round(p_word_given_spam, 6),
            "p_word_given_ham": round(p_word_given_ham, 6),
            "evidence_p_word": round(evidence, 6),
            "p_spam_given_word": round(p_spam_given_word, 4),
            "p_ham_given_word": round(p_ham_given_word, 4),
            "spam_count_in_train": self.spam_word_counts.get(word, 0),
            "ham_count_in_train": self.ham_word_counts.get(word, 0)
        }

    def explain_classification(self, text, top_n=10):
        """
        Generates an academically rigorous, step-by-step conditional probability breakdown
        suitable for student presentation and viva examination.
        """
        tokens = tokenize(text)
        if not tokens:
            return {
                "tokens": [],
                "prior_spam": round(self.prior_spam, 4),
                "prior_ham": round(self.prior_ham, 4),
                "word_breakdowns": [],
                "log_spam_score": 0.0,
                "log_ham_score": 0.0,
                "spam_probability": 0.5,
                "ham_probability": 0.5,
                "prediction": "HAM"
            }

        # Use log space to prevent floating-point underflow:
        # log P(C | w1..wn) proportional to log P(C) + sum(log P(wi | C))
        log_prob_spam = math.log(max(self.prior_spam, 1e-12))
        log_prob_ham = math.log(max(self.prior_ham, 1e-12))

        word_breakdowns = []
        for word in tokens:
            w_given_spam = self.calculate_word_likelihood(word, 'spam')
            w_given_ham = self.calculate_word_likelihood(word, 'ham')
            
            log_prob_spam += math.log(w_given_spam)
            log_prob_ham += math.log(w_given_ham)

            single_bayes = self.calculate_single_word_conditional_probability(word)
            word_breakdowns.append({
                "word": word,
                "p_word_given_spam": w_given_spam,
                "p_word_given_ham": w_given_ham,
                "p_spam_given_word": single_bayes["p_spam_given_word"],
                "p_ham_given_word": single_bayes["p_ham_given_word"],
                "spam_count": single_bayes["spam_count_in_train"],
                "ham_count": single_bayes["ham_count_in_train"]
            })

        # Convert log likelihoods back to normalized posterior probabilities
        # Softmax / log-sum-exp trick for numerical stability
        max_log = max(log_prob_spam, log_prob_ham)
        exp_spam = math.exp(log_prob_spam - max_log)
        exp_ham = math.exp(log_prob_ham - max_log)
        total_exp = exp_spam + exp_ham

        posterior_spam = round(exp_spam / total_exp, 4)
        posterior_ham = round(exp_ham / total_exp, 4)

        # Sort words by strongest discriminative power (highest deviation from 0.5)
        sorted_breakdowns = sorted(
            word_breakdowns,
            key=lambda x: abs(x["p_spam_given_word"] - 0.5),
            reverse=True
        )

        return {
            "tokens_analyzed": len(tokens),
            "prior_spam": round(self.prior_spam, 4),
            "prior_ham": round(self.prior_ham, 4),
            "log_spam_score": round(log_prob_spam, 2),
            "log_ham_score": round(log_prob_ham, 2),
            "spam_probability": posterior_spam,
            "ham_probability": posterior_ham,
            "prediction": "SPAM" if posterior_spam >= 0.5 else "HAM",
            "top_words": sorted_breakdowns[:top_n]
        }

if __name__ == "__main__":
    # Viva Demonstration Mock
    sample_corpus = [
        (["meeting", "schedule", "pipeline", "gas"], "ham"),
        (["quarterly", "report", "conference", "call"], "ham"),
        (["free", "lottery", "urgent", "prize", "cash"], "spam"),
        (["guaranteed", "viagra", "cheap", "winner"], "spam")
    ]
    engine = ConditionalProbabilityEngine()
    engine.train_on_corpus([item[0] for item in sample_corpus], [item[1] for item in sample_corpus])
    
    # Calculate P(Spam | 'free')
    result = engine.calculate_single_word_conditional_probability("free")
    print("Viva Test - Bayes' Theorem on single word 'free':")
    print(f"  P(Spam) = {engine.prior_spam}")
    print(f"  P('free' | Spam) = {result['p_word_given_spam']}")
    print(f"  P('free' | Ham)  = {result['p_word_given_ham']}")
    print(f"  P(Spam | 'free') = {result['p_spam_given_word'] * 100}%")
