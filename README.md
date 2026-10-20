# Spam Email Classification Engine Using Conditional Probability

**An Academic Project for 2nd-Year B.Tech Computer Science and Engineering**

---

## 1. Project Title
**Spam Email Classification Engine Using Conditional Probability, Bayes' Theorem, and Chi-Square Feature Selection**

---

## 2. Problem Statement
Electronic mail remains one of the primary communication mediums worldwide. However, unsolicited commercial and malicious communications ("Spam") congest network bandwidth, waste user time, and expose organizations to phishing, identity theft, and financial fraud. 

Traditional heuristic filters rely on hardcoded keyword blacklists, which fail against evolving spam techniques. This project implements a mathematically transparent, statistically grounded machine learning engine based on **Conditional Probability**, **Bayes' Theorem**, **Laplace Smoothing**, and **Chi-Square ($\chi^2$) Feature Selection** to classify incoming emails as **HAM (Legitimate)** or **SPAM (Unsolicited/Malicious)** with high accuracy and explainability.

---

## 3. Main Objective
* Design and implement a full-stack, Python-based email platform.
* Apply statistical text preprocessing and feature extraction on the authentic **Enron Email Dataset**.
* Implement the mathematical formulation of **Conditional Probability** and **Bayes' Theorem** from first principles alongside Scikit-Learn's `MultinomialNB`.
* Perform **Chi-Square ($\chi^2$) Hypothesis Testing** to isolate statistically significant discriminative keywords ($p < 0.05$).
* Provide visual analytics, confusion matrix analysis, and an explainable inference dashboard suitable for academic demonstration and viva examinations.

---

## 4. Key Features
1. **User Authentication & Authorization**: Session-based login, registration with password confirmation, and secure password hashing via Werkzeug (`pbkdf2:sha256`).
2. **Dual-Mailbox Routing**: Incoming messages are evaluated in real time; Ham is routed to the **Inbox**, while Spam is quarantined in the **Spam Folder**.
3. **Interactive Email Composer**: Write custom emails or select pre-configured academic demonstration templates (Enron corporate memos vs. Lottery/Mortgage phishing lures).
4. **Bayesian Forensics Inspection**: Detailed email view displaying calculated **Spam Probability %**, **Ham Probability %**, structural indicators (URLs, shouting uppercase ratio, currency symbols), and key token conditional probabilities $P(\text{Spam} \mid \text{Token})$.
5. **Interactive Viva Bayes Calculator**: Test arbitrary single words dynamically to inspect priors, likelihoods, evidence, and posteriors.
6. **User Feedback & Continuous Audit**: Users can correct false positives or false negatives ("Mark as Spam" / "Not Spam"), updating mailbox routing and recording feedback logs.
7. **Comprehensive Statistical Dashboard**: Real-time Chart.js charts and static Matplotlib figures displaying class distributions, feature comparisons, and evaluation confusion matrices.

---

## 5. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| **Backend Framework** | Python 3.10+, Flask | Web server, routing, and session management |
| **Database** | SQLite3 | Relational database (`probmail.db`) |
| **Machine Learning** | Scikit-learn, NumPy, Pandas, SciPy | `MultinomialNB`, `TfidfVectorizer`, `chi2` |
| **Statistical Visualizations** | Matplotlib | Headless plot generation (`static/img/*.png`) |
| **Client-Side Charts** | Chart.js (CDN) | Interactive dashboard donut and bar graphs |
| **Frontend** | HTML5, Clean Vanilla CSS3, Vanilla JS | Student-friendly, modular presentation UI |
| **Dataset** | Enron Email Corpus | Realistic corporate communications and spam |

*(No React, Next.js, Django, PostgreSQL, Docker, or external heavy frameworks are used, adhering strictly to 2nd-year academic standards).*

---

## 6. System Architecture

```
[ Incoming / Composed Email (Subject + Body) ]
                       │
                       ▼
          [ Preprocessing Module ]
    • Lowercasing & whitespace normalization
    • Alphanumeric tokenization & noise filtering
                       │
                       ▼
         [ Feature Extraction Module ]
    • Structural features: Length, URLs, Special Chars, Shouting Ratio
    • Term Weights: TF-IDF Vectorizer (Unigrams + Bigrams)
                       │
                       ▼
      [ Chi-Square Feature Selection (χ²) ]
    • p-value thresholding (p < 0.05) to eliminate non-informative words
                       │
                       ▼
     [ Multinomial Naive Bayes & Bayes' Theorem ]
    • Likelihood computation with Laplace Smoothing (α=1.0)
    • Posterior probability calculation: P(Spam | X) vs P(Ham | X)
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
   P(Spam) ≥ 50%              P(Spam) < 50%
     [ SPAM ]                   [ HAM ]
          │                         │
          ▼                         ▼
   Quarantined in            Delivered to
   [ Spam Folder ]             [ Inbox ]
```

---

## 7. Folder Structure

```
ProbMail/
├── app.py                      # Flask web application routes and controller
├── database.py                 # SQLite database initialization & demo seeder
├── models.py                   # Data access models (User, Email, Feedback)
├── preprocessing.py            # Text cleaning, normalization, and tokenization
├── feature_extraction.py       # Structural email features & keyword indicators
├── bayes.py                    # Explicit Bayes' Theorem & Conditional Probability engine
├── chi_square.py               # Chi-Square (χ²) statistical feature selection module
├── statistics.py               # Descriptive statistics (Mean, Median, Std) & plots
├── evaluation.py               # Accuracy, Precision, Recall, F1, Confusion Matrix
├── train_model.py              # End-to-end model training and serialization pipeline
├── requirements.txt            # Python dependencies
├── README.md                   # Complete academic documentation & viva guide
│
├── data/
│   ├── enron_spam_data.csv     # 1,500 curated Enron ham & spam records
│   └── create_enron_dataset.py # Dataset generation/formatting script
│
├── models/
│   └── spam_model.pkl          # Serialized classifier, vectorizer, and metrics
│
├── templates/
│   ├── base.html               # Master layout with sidebar and navbar
│   ├── login.html              # Authentication sign-in page
│   ├── register.html           # User registration page
│   ├── dashboard.html          # Main metrics, charts, and Bayes word calculator
│   ├── inbox.html              # Legitimate Ham email list
│   ├── spam.html               # Isolated Spam email list
│   ├── compose.html            # Email composer with pre-fill demo templates
│   ├── email.html              # Detailed email forensics & probability breakdown
│   ├── history.html            # Classification audit log & feedback corrections
│   └── statistics.html         # In-depth statistical analysis & Chi-Square table
│
├── static/
│   ├── css/
│   │   └── style.css           # Clean vanilla CSS stylesheet
│   ├── js/
│   │   └── script.js           # Vanilla JS for live filtering and Chart.js
│   └── img/                    # Auto-generated Matplotlib evaluation graphs
│       ├── class_distribution.png
│       ├── feature_comparison.png
│       └── confusion_matrix.png
│
└── probmail.db                 # SQLite database file
```

---

## 8. Installation & Setup

### Prerequisites
* Python 3.8 or higher installed on your computer.
* VS Code or any standard code editor.

### Step 1: Open Terminal / Command Prompt
Navigate to the project root directory:
```bash
cd ProbMail
```

### Step 2: Create a Python Virtual Environment
**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 9. Model Training

To inspect the dataset, calculate Chi-Square scores, fit the Naive Bayes model, and generate the statistical plots:

```bash
python train_model.py
```

**Expected Terminal Output:**
* Records loaded: 1,500 (60% Ham, 40% Spam).
* TF-IDF features extracted: 1,772 unique n-grams.
* Chi-Square statistical analysis: ~1,015 significant features ($p < 0.05$).
* Model evaluation on test split: Accuracy, Precision, Recall, F1 > 98%.
* Artifact serialized to `models/spam_model.pkl`.

---

## 10. Running the Web Application

Start the Flask server:
```bash
python app.py
```

Then open your web browser and navigate to:
```
http://127.0.0.1:5000
```
*(In AI Studio preview environments, the server listens automatically on port 3000).*

### Demo Credentials for Viva Examination:
* **Student Account:**
  * **Email:** `student@probmail.ac.in`
  * **Password:** `student123`
* **Enron Executive Account:**
  * **Email:** `vince.kaminski@enron.org`
  * **Password:** `enron123`

---

## 11. Mathematical & Academic Concepts

### A. Conditional Probability
Conditional probability is the probability of an event $A$ occurring given that another event $B$ has already occurred, denoted as $P(A \mid B)$:

$$P(A \mid B) = \frac{P(A \cap B)}{P(B)}$$

In spam classification:
$$P(\text{Spam} \mid \text{"free"}) = \text{Probability that an email is Spam given that the word "free" appears}$$

### B. Bayes' Theorem
Bayes' Theorem provides a principled method to invert conditional probabilities:

$$P(\text{Spam} \mid X) = \frac{P(X \mid \text{Spam}) \cdot P(\text{Spam})}{P(X)}$$

Where:
* **Prior Probability $P(\text{Spam})$**: Base rate of spam emails in the corpus ($\frac{N_{\text{spam}}}{N_{\text{total}}}$).
* **Likelihood $P(X \mid \text{Spam})$**: Probability that the feature set $X$ occurs in spam emails.
* **Evidence / Marginal Likelihood $P(X)$**: Total probability of observing $X$:
  $$P(X) = P(X \mid \text{Spam})P(\text{Spam}) + P(X \mid \text{Ham})P(\text{Ham})$$
* **Posterior Probability $P(\text{Spam} \mid X)$**: The updated belief that the email is Spam after observing features $X$.

### C. Naive Bayes Conditional Independence Assumption
Assuming all words $w_1, w_2, \dots, w_n$ are conditionally independent given the class $C$:

$$P(w_1, w_2, \dots, w_n \mid C) = \prod_{i=1}^{n} P(w_i \mid C)$$

To prevent numerical underflow with small floating-point decimals, calculations are computed in log space:

$$\log P(C \mid w_1, \dots, w_n) \propto \log P(C) + \sum_{i=1}^{n} \log P(w_i \mid C)$$

### D. Laplace Additive Smoothing ($\alpha = 1.0$)
If a word never appeared in training for a class, its probability would be $0$, multiplying the whole product to zero. Laplace smoothing solves this:

$$P(w \mid C) = \frac{\text{Count}(w, C) + \alpha}{\sum_{w'} \text{Count}(w', C) + \alpha \cdot |V|}$$

Where $|V|$ is the total vocabulary size.

### E. Chi-Square ($\chi^2$) Feature Selection
Chi-Square tests the hypothesis that the occurrence of a word is independent of the class label:

$$\chi^2 = \sum \frac{(O - E)^2}{E}$$

Where $O$ is the Observed frequency and $E$ is the Expected frequency under the null hypothesis of independence. A significance level of $p < 0.05$ indicates strong correlation with Spam or Ham.

---

## 12. Model Evaluation Metrics

1. **Accuracy**: Overall fraction of correct predictions:
   $$\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}}$$
2. **Precision**: Out of all emails flagged as Spam, how many were truly Spam:
   $$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$$
   *(High precision prevents crucial legitimate emails from being lost in Spam).*
3. **Recall (Sensitivity)**: Fraction of actual spam emails caught:
   $$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$
4. **F1-Score**: Harmonic mean of Precision and Recall:
   $$F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

---

## 13. Viva Examination Preparation Guide

### Q1: Why did you choose Naive Bayes instead of Deep Learning / LLMs?
**Answer:** Naive Bayes is statistically transparent, highly efficient on high-dimensional text data, and provides direct conditional probability values for each word. It runs instantaneously without GPU requirements and avoids the black-box opacity of deep neural networks, making every classification explainable to users.

### Q2: What is the "Naive" assumption in Naive Bayes?
**Answer:** The assumption that all feature words are conditionally independent of each other given the class label. While words in natural language do have grammatical and semantic dependencies, empirical research shows that Naive Bayes works exceptionally well for text classification because the decision boundary remains optimal even when probability magnitudes are slightly shifted.

### Q3: Why is Laplace smoothing essential?
**Answer:** Without Laplace smoothing, if an incoming email contains a single word that never appeared in the spam training corpus, $P(\text{word} \mid \text{Spam}) = 0$. Since probabilities are multiplied, this would force the entire spam probability to zero regardless of how many other obvious spam words are present. Adding $\alpha=1$ prevents this zero-frequency issue.

### Q4: What does Chi-square feature selection do for this model?
**Answer:** Chi-square evaluates whether the difference between observed word counts and expected word counts across classes is statistically significant. Features with $p \ge 0.05$ appear randomly across both classes and add noise, while features with $p < 0.05$ (like "http", "free", "lottery", "pipeline") provide genuine discriminative signal.

### Q5: In email classification, is Type I error (FP) or Type II error (FN) worse?
**Answer:** Type I error (False Positive) is significantly worse. If a spam email lands in the inbox (Type II), the user is merely annoyed. But if an important business contract, job offer, or university alert is incorrectly marked as spam (Type I), the user could suffer severe consequences. Therefore, email classifiers prioritize high Precision.

---

## 14. License
Academic Open Source Project &mdash; Developed for B.Tech Computer Science Coursework.
