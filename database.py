"""
database.py
-----------
Module: SQLite Database Management for ProbMail.

Academic Requirements:
- Uses SQLite and standard python `sqlite3` module.
- Proper schema with foreign keys, indexing, and timestamps.
- Passwords securely hashed with Werkzeug generate_password_hash.
- Auto-seeds default demo users and emails for easy demonstration during vivas.

Author: 2nd-Year B.Tech Computer Science Student Project
Academic Title: Spam Email Classification Engine Using Conditional Probability
"""

import sqlite3
import os
import json
from werkzeug.security import generate_password_hash

DB_PATH = "probmail.db"

def get_db():
    """
    Returns an open SQLite database connection with row_factory configured
    so columns can be accessed by name like dictionaries.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """
    Initializes database tables and seeds demo users and emails.
    """
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Emails Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        sender_email TEXT NOT NULL,
        receiver_email TEXT NOT NULL,
        subject TEXT NOT NULL,
        body TEXT NOT NULL,
        prediction TEXT NOT NULL,
        spam_probability REAL NOT NULL,
        ham_probability REAL NOT NULL,
        folder TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        indicators_json TEXT DEFAULT '[]',
        top_words_json TEXT DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 3. User Feedback Table (for model correction & continuous learning)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        original_prediction TEXT NOT NULL,
        corrected_label TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (email_id) REFERENCES emails (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    conn.commit()

    # Seed demo accounts if table is empty
    cursor.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()["count"] == 0:
        print("[Database] Seeding initial academic demo accounts and sample emails...")
        
        # User 1: Student
        hashed_pw1 = generate_password_hash("student123")
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ("Arjun Sharma (Student)", "student@probmail.ac.in", hashed_pw1)
        )
        student_id = cursor.lastrowid

        # User 2: Enron Executive
        hashed_pw2 = generate_password_hash("enron123")
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ("Dr. Vince Kaminski (Research)", "vince.kaminski@enron.org", hashed_pw2)
        )
        vince_id = cursor.lastrowid

        # User 3: External Vendor
        hashed_pw3 = generate_password_hash("vendor123")
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ("Promotional Dispatcher", "offers@global-prizes-promo.com", hashed_pw3)
        )
        promo_id = cursor.lastrowid

        # Seed sample legitimate (Ham) emails
        ham_samples = [
            (
                vince_id, student_id,
                "vince.kaminski@enron.org", "student@probmail.ac.in",
                "Enron Research: Natural Gas Price Modeling & Pipeline Tariff Review",
                "Dear Arjun,\n\nPlease find attached our latest econometric models for Henry Hub forward pricing. We have incorporated the volatility skew from the California deregulation index.\n\nLet us review these projections during our Thursday 2 PM conference call.\n\nBest regards,\nVince Kaminski\nManaging Director, Quantitative Research, Enron",
                "HAM", 0.04, 99.96, "inbox", 0,
                json.dumps(["Legitimate workplace keywords: research, attached, conference", "Workplace token: 'enron' has P(Ham|'enron') = 99.9%"]),
                json.dumps([{"word": "research", "p_ham_given_word": 0.98}, {"word": "attached", "p_ham_given_word": 0.97}])
            ),
            (
                vince_id, student_id,
                "vince.kaminski@enron.org", "student@probmail.ac.in",
                "Schedule for Thursday Strategy Committee Meeting",
                "Good morning team,\n\nThe agenda for tomorrow's executive review is as follows:\n1. Pipeline maintenance status update\n2. Q3 natural gas transmission targets\n3. Regulatory compliance with FERC guidelines\n\nMeeting will be held in Conference Room 3201.\n\nRegards,\nVince",
                "HAM", 0.08, 99.92, "inbox", 1,
                json.dumps(["Legitimate workplace keywords: meeting, schedule, pipeline", "Workplace token: 'conference' has P(Ham|'conference') = 99.8%"]),
                json.dumps([{"word": "meeting", "p_ham_given_word": 0.96}, {"word": "pipeline", "p_ham_given_word": 0.99}])
            )
        ]

        # Seed sample spam emails
        spam_samples = [
            (
                promo_id, student_id,
                "offers@global-prizes-promo.com", "student@probmail.ac.in",
                "URGENT: YOU HAVE WON $1,500,000 CASH IN THE GLOBAL LOTTERY!",
                "CONGRATULATIONS WINNER!\n\nYour email address was randomly selected to receive a grand cash award of $1,500,000 USD. To claim your prize immediately without delay, click here: http://claim-prize-cash99.com/verify and submit your account info.\n\n100% Guaranteed payout! Call 1-800-555-4921 now!",
                "SPAM", 99.94, 0.06, "spam", 0,
                json.dumps(["Contains 1 external URL link(s)", "High uppercase ratio (32% capital letters)", "Multiple exclamation marks (3 '!')", "Currency symbols detected (2)", "Promotional spam keywords: winner, prize, urgent, cash, claim", "Strong spam token: 'http' has P(Spam|'http') = 99.8%"]),
                json.dumps([{"word": "winner", "p_spam_given_word": 0.99}, {"word": "http", "p_spam_given_word": 0.998}, {"word": "urgent", "p_spam_given_word": 0.98}])
            ),
            (
                promo_id, student_id,
                "offers@global-prizes-promo.com", "student@probmail.ac.in",
                "Refinance Your Mortgage Now at 1.99% Guaranteed Rate!",
                "Are you tired of paying high monthly interest? Refinance today! No credit checks, zero upfront fees, instant online pre-approval.\n\nVisit http://fast-mortgage-relief.net/apply and eliminate your debt today!",
                "SPAM", 98.75, 1.25, "spam", 0,
                json.dumps(["Contains 1 external URL link(s)", "Promotional spam keywords: refinance, guaranteed, debt", "Strong spam token: 'refinance' has P(Spam|'refinance') = 98.5%"]),
                json.dumps([{"word": "refinance", "p_spam_given_word": 0.98}, {"word": "guaranteed", "p_spam_given_word": 0.97}])
            )
        ]

        for s in ham_samples + spam_samples:
            cursor.execute("""
            INSERT INTO emails (
                sender_id, receiver_id, sender_email, receiver_email,
                subject, body, prediction, spam_probability, ham_probability,
                folder, is_read, indicators_json, top_words_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, s)

        conn.commit()
        print("[Database] Demo accounts and sample emails seeded successfully.")

    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialization completed successfully.")
