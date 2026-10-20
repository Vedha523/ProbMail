"""
app.py
------
Main Flask Web Application for:
"Spam Email Classification Engine Using Conditional Probability"

Technology Stack:
- Backend: Python 3.x, Flask
- Database: SQLite (sqlite3)
- Machine Learning: Scikit-learn (MultinomialNB), TF-IDF, Chi-Square (χ²)
- Frontend: HTML5, CSS3, Vanilla JavaScript, Chart.js, Matplotlib

Author: 2nd-Year B.Tech Computer Science Student Project
Academic Title: Spam Email Classification Engine Using Conditional Probability
"""

import os
from functools import wraps
from itsdangerous import URLSafeSerializer
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
    abort,
    make_response,
    send_file
)

from database import init_db
from models import UserModel, EmailModel, FeedbackModel
from spam_classifier import get_classifier, classify_email

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "probmail-academic-project-secret-key-2026")

# Configure session cookies for local HTTP and browser compatibility
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 86400 * 7

# Token serializer for reliable iframe & cross-site authentication fallback
AUTH_SERIALIZER = URLSafeSerializer(app.secret_key, salt="probmail-auth-token-salt")

def generate_auth_token(user_id):
    """Generates a secure signed authentication token for the user."""
    return AUTH_SERIALIZER.dumps({"user_id": user_id})

def verify_auth_token(token):
    """Verifies a signed token and returns the user ID or None."""
    if not token:
        return None
    try:
        data = AUTH_SERIALIZER.loads(token)
        return data.get("user_id")
    except Exception:
        return None

# Ensure database tables and initial demo seed exist
init_db()

# Ensure ML model is loaded / trained
classifier = get_classifier()

@app.before_request
def check_token_auth():
    """Restores session from query parameter token or cookie if session is missing."""
    token = request.args.get("token") or request.cookies.get("probmail_token") or request.headers.get("X-Auth-Token")
    if token:
        uid = verify_auth_token(token)
        if uid:
            user = UserModel.get_by_id(uid)
            if user:
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                session["user_email"] = user["email"]
                session["auth_token"] = token
                session.permanent = True

def login_required(f):
    """Decorator ensuring that routes are only accessible to authenticated users."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            # Check token again in case before_request didn't catch it
            token = request.args.get("token") or request.cookies.get("probmail_token")
            if token:
                uid = verify_auth_token(token)
                if uid:
                    user = UserModel.get_by_id(uid)
                    if user:
                        session["user_id"] = user["id"]
                        session["user_name"] = user["name"]
                        session["user_email"] = user["email"]
                        session["auth_token"] = token
                        session.permanent = True
                        return f(*args, **kwargs)
            flash("Please sign in to access your mailbox.", "info")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_global_data():
    """Injects folder counts, user information, and auth token into all Jinja2 templates."""
    if "user_id" in session:
        user_id = session["user_id"]
        counts = EmailModel.get_folder_counts(user_id)
        token = session.get("auth_token") or generate_auth_token(user_id)
        return {
            "folder_counts": counts,
            "current_user_id": user_id,
            "current_user_name": session.get("user_name", "Student"),
            "current_user_email": session.get("user_email", ""),
            "auth_token": token
        }
    return {"folder_counts": None, "auth_token": ""}

# --------------------------------------------------------------------------
# Authentication Routes
# --------------------------------------------------------------------------

@app.route("/")
def index():
    """Root entry point: routes to dashboard if logged in, else to login."""
    if "user_id" in session:
        token = session.get("auth_token") or generate_auth_token(session["user_id"])
        return redirect(url_for("dashboard", token=token))
    
    # Check for token in URL or cookie
    token = request.args.get("token") or request.cookies.get("probmail_token")
    if token and verify_auth_token(token):
        return redirect(url_for("dashboard", token=token))

    return redirect(url_for("login"))

@app.route("/quick-login")
def quick_login():
    """Instant one-click sign in for demo accounts to prevent any iframe cookie issues."""
    role = request.args.get("role", "student").lower()
    email = "student@probmail.ac.in" if role == "student" else "vince.kaminski@enron.org"
    user = UserModel.get_by_email(email)
    if user:
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]
        session.permanent = True
        token = generate_auth_token(user["id"])
        session["auth_token"] = token
        flash(f"Signed in as {user['name']}!", "success")
        resp = redirect(url_for("dashboard", token=token))
        resp.set_cookie(
            "probmail_token",
            token,
            max_age=86400 * 7,
            samesite="Lax",
            secure=False,
            httponly=False
        )
        return resp
    flash("Demo user not found.", "error")
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles student / user login."""
    if "user_id" in session:
        token = session.get("auth_token") or generate_auth_token(session["user_id"])
        return redirect(url_for("dashboard", token=token))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "error")
            return render_template("login.html")

        user = UserModel.get_by_email(email)
        if user and UserModel.verify_password(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session.permanent = True
            token = generate_auth_token(user["id"])
            session["auth_token"] = token
            flash(f"Welcome back, {user['name']}!", "success")
            resp = redirect(url_for("dashboard", token=token))
            resp.set_cookie(
                "probmail_token",
                token,
                max_age=86400 * 7,
                samesite="Lax",
                secure=False,
                httponly=False
            )
            return resp
        else:
            flash("Invalid email or password. Please verify your credentials.", "error")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles new user registration."""
    if "user_id" in session:
        token = session.get("auth_token") or generate_auth_token(session["user_id"])
        return redirect(url_for("dashboard", token=token))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        existing = UserModel.get_by_email(email)
        if existing:
            flash("An account with that email already exists. Please sign in.", "error")
            return render_template("register.html")

        try:
            user = UserModel.create(name, email, password)
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session.permanent = True
            token = generate_auth_token(user["id"])
            session["auth_token"] = token
            flash("Account registered successfully! Welcome to ProbMail.", "success")
            resp = redirect(url_for("dashboard", token=token))
            resp.set_cookie(
                "probmail_token",
                token,
                max_age=86400 * 7,
                samesite="Lax",
                secure=False,
                httponly=False
            )
            return resp
        except Exception as e:
            flash(f"Registration failed: {str(e)}", "error")

    return render_template("register.html")

@app.route("/logout")
def logout():
    """Logs the user out and clears the session and cookie."""
    session.clear()
    flash("You have been signed out safely.", "info")
    resp = redirect(url_for("login"))
    resp.delete_cookie("probmail_token", samesite="Lax")
    return resp

# --------------------------------------------------------------------------
# Dashboard & Mailbox Routes
# --------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    """
    Clean Operational Overview Dashboard:
    - 4 compact KPI cards using actual database values:
      1. Total emails processed
      2. Legitimate emails (HAM)
      3. Spam emails detected
      4. Spam detection rate (%)
    - Readable classification distribution visualization
    - Recent classifications table from persistent database
    """
    system_stats = EmailModel.get_system_stats()
    recent_emails = EmailModel.get_all_classifications()[:6]
    metadata = classifier.get_metadata()

    return render_template(
        "dashboard.html",
        active_page="dashboard",
        system_stats=system_stats,
        recent_emails=recent_emails,
        dataset_stats=metadata.get("dataset_stats", {})
    )

@app.route("/inbox")
@login_required
def inbox():
    """Displays verified legitimate (Ham) emails."""
    user_id = session["user_id"]
    query = request.args.get("q", "")
    emails = EmailModel.get_emails_for_user(user_id, folder="inbox", search_query=query)
    return render_template("inbox.html", active_page="inbox", emails=emails, search_query=query)

@app.route("/spam")
@login_required
def spam_folder():
    """Displays automatically isolated Spam emails."""
    user_id = session["user_id"]
    query = request.args.get("q", "")
    emails = EmailModel.get_emails_for_user(user_id, folder="spam", search_query=query)
    return render_template("spam.html", active_page="spam", emails=emails, search_query=query)

@app.route("/sent")
@login_required
def sent_folder():
    """Displays emails submitted/sent by the logged-in user."""
    user_id = session["user_id"]
    query = request.args.get("q", "")
    emails = EmailModel.get_emails_for_user(user_id, folder="sent", search_query=query)
    return render_template("sent.html", active_page="sent", emails=emails, search_query=query)

# --------------------------------------------------------------------------
# Email Composition & Spam Classification Pipeline
# --------------------------------------------------------------------------

@app.route("/compose", methods=["GET", "POST"])
@login_required
def compose_email():
    """
    Primary Workflow: Compose and Classify Email.
    - Validates required subject & body.
    - Evaluates conditional probabilities with Bayesian inference.
    - Saves the message to local database:
      * Ham -> legitimate mailbox (Inbox)
      * Spam -> spam folder quarantine
      * Both -> recorded in Sent Messages
    - Returns JSON for interactive AJAX or renders compose.html with result panel.
    """
    sender_id = session["user_id"]
    sender_email = session["user_email"]

    if request.method == "POST":
        is_ajax = request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        if request.is_json:
            data = request.get_json() or {}
            receiver_email = data.get("receiver_email", "").strip().lower()
            subject = data.get("subject", "").strip()
            body = data.get("body", "").strip()
        else:
            receiver_email = request.form.get("receiver_email", "").strip().lower()
            subject = request.form.get("subject", "").strip()
            body = request.form.get("body", "").strip()

        if not subject or not body:
            error_msg = "Both Email Subject and Message Body are required to classify an email."
            if is_ajax:
                return jsonify({"success": False, "error": error_msg}), 400
            flash(error_msg, "error")
            users = UserModel.get_all_users()
            return render_template("compose.html", active_page="compose", users=users)

        if not receiver_email:
            receiver_email = "recipient@probmail.ac.in"

        # ------------------------------------------------------------------
        # CLASSIFICATION ENGINE EXECUTION (Bayes' Theorem & Conditional Prob)
        # ------------------------------------------------------------------
        result = classify_email(subject, body)
        prediction = result["prediction"]
        spam_prob = result["spam_probability"]
        ham_prob = result["ham_probability"]
        folder = result["folder"]
        indicators = result["indicators"]
        top_words = result["top_words"]

        # Local mailbox delivery:
        # Saved with sender_id = user_id and receiver_id = user_id
        # Guarantees the email appears in the user's Inbox/Spam and Sent Messages
        saved_email = EmailModel.create(
            sender_id=sender_id,
            receiver_id=sender_id,
            sender_email=sender_email,
            receiver_email=receiver_email,
            subject=subject,
            body=body,
            prediction=prediction,
            spam_prob=spam_prob,
            ham_prob=ham_prob,
            folder=folder,
            indicators=indicators,
            top_words=top_words
        )

        dest_mailbox = "Legitimate Mailbox (Inbox)" if prediction == "HAM" else "Spam Folder (Quarantine)"

        if is_ajax:
            return jsonify({
                "success": True,
                "email_id": saved_email["id"],
                "subject": saved_email["subject"],
                "prediction": prediction,
                "spam_probability": spam_prob,
                "ham_probability": ham_prob,
                "folder": folder,
                "destination_label": dest_mailbox,
                "indicators": indicators,
                "top_words": top_words[:5],
                "view_url": url_for("view_email", email_id=saved_email["id"])
            })

        flash(
            f"Email classified as {prediction} ({spam_prob}% Spam / {ham_prob}% Ham) and saved to {dest_mailbox}.",
            "error" if prediction == "SPAM" else "success"
        )
        users = UserModel.get_all_users()
        return render_template(
            "compose.html",
            active_page="compose",
            users=users,
            result={
                "id": saved_email["id"],
                "prediction": prediction,
                "spam_probability": spam_prob,
                "ham_probability": ham_prob,
                "folder": folder,
                "destination_label": dest_mailbox,
                "indicators": indicators,
                "top_words": top_words[:5]
            },
            submitted_subject=subject,
            submitted_body=body,
            submitted_receiver=receiver_email
        )

    users = UserModel.get_all_users()
    return render_template("compose.html", active_page="compose", users=users)

@app.route("/email/<int:email_id>")
@login_required
def view_email(email_id):
    """Displays a single email with full Bayesian reasoning breakdown."""
    email = EmailModel.get_by_id(email_id)
    if not email:
        flash("Email not found.", "error")
        return redirect(url_for("inbox"))

    # Mark as read
    EmailModel.mark_as_read(email_id)
    return render_template("email.html", active_page=email["folder"], email=email)

@app.route("/email/<int:email_id>/feedback", methods=["POST"])
@login_required
def submit_feedback(email_id):
    """
    Records user feedback: 'Mark as Spam' or 'Not Spam'.
    Moves the email to the appropriate mailbox and logs the correction.
    """
    user_id = session["user_id"]
    email = EmailModel.get_by_id(email_id)
    if not email:
        flash("Email not found.", "error")
        return redirect(url_for("inbox"))

    correction = request.form.get("correction", "HAM").upper()
    FeedbackModel.record_feedback(
        email_id=email_id,
        user_id=user_id,
        original_prediction=email["prediction"],
        corrected_label=correction
    )

    if correction == "SPAM":
        flash("Feedback recorded. Email marked as SPAM and moved to Spam folder.", "error")
        return redirect(url_for("spam_folder"))
    else:
        flash("Feedback recorded. Email marked as NOT SPAM and moved to Inbox.", "success")
        return redirect(url_for("inbox"))

@app.route("/email/<int:email_id>/delete", methods=["POST"])
@login_required
def delete_email_route(email_id):
    """Permanently deletes an email from SQLite database."""
    EmailModel.delete_permanently(email_id)
    flash("Email permanently deleted.", "info")
    return redirect(url_for("inbox"))

# --------------------------------------------------------------------------
# Academic History & Statistics Routes
# --------------------------------------------------------------------------

@app.route("/history")
@login_required
def classification_history():
    """
    Displays the complete persistent classification audit trail and user feedback logs.
    Supports live text search and class filter (All, HAM, SPAM).
    """
    query = request.args.get("q", "")
    pred_filter = request.args.get("filter", "")
    emails = EmailModel.get_all_classifications(search_query=query, prediction_filter=pred_filter)
    feedback_list = FeedbackModel.get_all_feedback()

    return render_template(
        "history.html",
        active_page="history",
        emails=emails,
        feedback_list=feedback_list,
        search_query=query,
        current_filter=pred_filter
    )

@app.route("/statistics")
@login_required
def statistics_page():
    """
    Organized Academic Statistics Page:
    - Section A: Model Evaluation (Accuracy, Precision, Recall, F1 on Enron test split)
    - Section B: Chi-Square (χ²) Feature Analysis Table (p < 0.05)
    - Section C: Descriptive Statistics Comparison (Ham vs Spam)
    - Max 2 charts: Class distribution and Confusion matrix
    """
    metadata = classifier.get_metadata()
    system_stats = EmailModel.get_system_stats()
    return render_template(
        "statistics.html",
        active_page="statistics",
        eval_metrics=metadata.get("eval_metrics", {}),
        chi2_results=metadata.get("chi2_results", {}),
        dataset_stats=metadata.get("dataset_stats", {}),
        system_stats=system_stats,
        training_samples=metadata.get("training_samples", 1200),
        testing_samples=metadata.get("testing_samples", 300)
    )

# --------------------------------------------------------------------------
# Dashboard Live Updates & Analytics API
# --------------------------------------------------------------------------

@app.route("/api/dashboard-stats")
@login_required
def api_dashboard_stats():
    """
    Lightweight authenticated JSON endpoint returning live dashboard metrics:
    - total_processed
    - ham_count
    - spam_count
    - spam_rate
    - recent_classifications (latest 6 records)
    - folder_counts
    - timestamp
    """
    from datetime import datetime
    user_id = session["user_id"]
    system_stats = EmailModel.get_system_stats()
    recent_records = EmailModel.get_all_classifications()[:6]
    folder_counts = EmailModel.get_folder_counts(user_id)

    recent_list = []
    for em in recent_records:
        recent_list.append({
            "id": em["id"],
            "sender_email": em.get("sender_email", ""),
            "receiver_email": em.get("receiver_email", ""),
            "subject": em.get("subject", ""),
            "body_snippet": (em.get("body") or "")[:65],
            "prediction": em.get("prediction", "HAM"),
            "spam_probability": em.get("spam_probability", 0.0),
            "ham_probability": em.get("ham_probability", 0.0),
            "is_read": em.get("is_read", 0),
            "created_date": em["created_at"][:10] if em.get("created_at") else "",
            "view_url": url_for("view_email", email_id=em["id"])
        })

    return jsonify({
        "success": True,
        "total_processed": system_stats["total_processed"],
        "ham_count": system_stats["ham_count"],
        "spam_count": system_stats["spam_count"],
        "spam_rate": system_stats["spam_rate"],
        "recent_classifications": recent_list,
        "folder_counts": folder_counts,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

# --------------------------------------------------------------------------
# Dynamic API Endpoint for Interactive Bayes Calculator
# --------------------------------------------------------------------------

@app.route("/api/bayes-word-probability")
def api_bayes_word_probability():
    """
    Calculates P(Spam | word) and P(Ham | word) using Bayes' Theorem
    for any user-provided word from the browser.
    """
    word = request.args.get("word", "").strip().lower()
    if not word:
        return jsonify({"error": "Word parameter is required"}), 400

    if not classifier.is_ready or not classifier._model_data:
        return jsonify({"error": "Bayesian probability engine not ready."}), 500

    prob_engine = classifier._model_data.get("prob_engine")
    if not prob_engine:
        return jsonify({"error": "Bayesian probability engine not found in model bundle."}), 500

    result = prob_engine.calculate_single_word_conditional_probability(word)
    return jsonify(result)

@app.route("/download-dataset")
def download_dataset():
    """Allows downloading the raw Enron Spam/Ham CSV dataset."""
    dataset_path = "data/enron_spam_data.csv"
    if os.path.exists(dataset_path):
        return send_file(
            dataset_path,
            as_attachment=True,
            download_name="enron_spam_data.csv",
            mimetype="text/csv"
        )
    flash("Dataset file not found.", "error")
    return redirect(url_for("dashboard"))

# --------------------------------------------------------------------------
# Error Handlers
# --------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("base.html", page_title="Page Not Found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("base.html", page_title="Server Error"), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"\n=================================================================")
    print(f" ProbMail Spam Classification Engine running on http://127.0.0.1:{port}")
    print(f"=================================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
