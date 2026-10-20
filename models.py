"""
models.py
---------
Module: Data Access Layer and Database Entity Models for ProbMail.

Contains:
1. User model: Registration, lookup, password authentication via Werkzeug.
2. Email model: Email dispatch, folder filtering (inbox, spam, sent, trash),
   persistent classification history, system stats, read status, searching, and deletion.
3. Feedback model: Record user corrections (Mark as Spam / Not Spam) for continuous evaluation.

Author: 2nd-Year B.Tech Computer Science Student Project
Academic Title: Spam Email Classification Engine Using Conditional Probability
"""

import json
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

class UserModel:
    @staticmethod
    def create(name, email, password):
        """Creates a new user with hashed password."""
        conn = get_db()
        cursor = conn.cursor()
        hashed = generate_password_hash(password)
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name.strip(), email.strip().lower(), hashed)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return UserModel.get_by_id(user_id)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id):
        """Finds user by primary key ID."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_email(email):
        """Finds user by email address."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email.strip().lower(),))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def verify_password(stored_hash, candidate_password):
        """Verifies candidate password against stored Werkzeug hash."""
        return check_password_hash(stored_hash, candidate_password)

    @staticmethod
    def get_all_users():
        """Returns list of all registered users (for easy recipient selection)."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]


class EmailModel:
    @staticmethod
    def create(sender_id, receiver_id, sender_email, receiver_email,
               subject, body, prediction, spam_prob, ham_prob, folder,
               indicators=None, top_words=None):
        """Creates a new classified email in the database."""
        conn = get_db()
        cursor = conn.cursor()
        ind_json = json.dumps(indicators or [])
        words_json = json.dumps(top_words or [])
        
        cursor.execute("""
        INSERT INTO emails (
            sender_id, receiver_id, sender_email, receiver_email,
            subject, body, prediction, spam_probability, ham_probability,
            folder, is_read, indicators_json, top_words_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
        """, (
            sender_id, receiver_id, sender_email, receiver_email,
            subject, body, prediction, spam_prob, ham_prob,
            folder, ind_json, words_json
        ))
        conn.commit()
        email_id = cursor.lastrowid
        conn.close()
        return EmailModel.get_by_id(email_id)

    @staticmethod
    def get_by_id(email_id):
        """Retrieves a single email by ID, deserializing JSON fields."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        
        data = dict(row)
        try:
            data['indicators'] = json.loads(data.get('indicators_json') or '[]')
        except:
            data['indicators'] = []
        try:
            data['top_words'] = json.loads(data.get('top_words_json') or '[]')
        except:
            data['top_words'] = []
        return data

    @staticmethod
    def get_emails_for_user(user_id, folder="inbox", search_query=None):
        """
        Retrieves emails for a user in a specific folder, with optional text search.
        - folder='sent': displays messages submitted by user_id
        - folder='inbox': displays legitimate (HAM) messages routed to user_id
        - folder='spam': displays spam messages quarantined for user_id
        """
        conn = get_db()
        cursor = conn.cursor()

        if folder == "sent":
            # Sent emails are authored/submitted by user_id
            sql = "SELECT * FROM emails WHERE sender_id = ?"
            params = [user_id]
        else:
            # Inbox or Spam: includes emails addressed to user_id OR submitted/analyzed by user_id
            sql = "SELECT * FROM emails WHERE (receiver_id = ? OR sender_id = ?) AND folder = ?"
            params = [user_id, user_id, folder]

        if search_query and search_query.strip():
            q = f"%{search_query.strip()}%"
            sql += " AND (subject LIKE ? OR body LIKE ? OR sender_email LIKE ? OR receiver_email LIKE ?)"
            params.extend([q, q, q, q])

        sql += " ORDER BY created_at DESC, id DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            d = dict(r)
            try:
                d['indicators'] = json.loads(d.get('indicators_json') or '[]')
            except:
                d['indicators'] = []
            try:
                d['top_words'] = json.loads(d.get('top_words_json') or '[]')
            except:
                d['top_words'] = []
            results.append(d)
        return results

    @staticmethod
    def get_all_classifications(search_query=None, prediction_filter=None):
        """
        Retrieves all persistent email classification records across the database
        for the Classification History log and operational dashboard.
        Guarantees that classification history shows actual persistent records.
        """
        conn = get_db()
        cursor = conn.cursor()
        sql = "SELECT * FROM emails WHERE 1=1"
        params = []

        if prediction_filter and prediction_filter.upper() in ["HAM", "SPAM"]:
            sql += " AND UPPER(prediction) = ?"
            params.append(prediction_filter.upper())

        if search_query and search_query.strip():
            q = f"%{search_query.strip()}%"
            sql += " AND (subject LIKE ? OR body LIKE ? OR sender_email LIKE ? OR receiver_email LIKE ?)"
            params.extend([q, q, q, q])

        sql += " ORDER BY created_at DESC, id DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            d = dict(r)
            try:
                d['indicators'] = json.loads(d.get('indicators_json') or '[]')
            except:
                d['indicators'] = []
            try:
                d['top_words'] = json.loads(d.get('top_words_json') or '[]')
            except:
                d['top_words'] = []
            results.append(d)
        return results

    @staticmethod
    def get_system_stats():
        """
        Returns real persistent database metrics for operational overview KPI cards:
        - Total emails processed (guaranteed = ham_count + spam_count)
        - Legitimate emails (HAM)
        - Spam emails detected
        - Spam detection rate (%)
        """
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM emails WHERE UPPER(prediction) = 'HAM'")
        ham_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emails WHERE UPPER(prediction) = 'SPAM'")
        spam_count = cursor.fetchone()[0]

        conn.close()

        total_processed = ham_count + spam_count
        spam_rate = round((spam_count / total_processed) * 100, 1) if total_processed > 0 else 0.0

        return {
            "total_processed": total_processed,
            "ham_count": ham_count,
            "spam_count": spam_count,
            "spam_rate": spam_rate
        }

    @staticmethod
    def mark_as_read(email_id):
        """Sets is_read = 1."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE emails SET is_read = 1 WHERE id = ?", (email_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def update_folder(email_id, new_folder):
        """Moves an email to another folder ('inbox', 'spam', 'trash')."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE emails SET folder = ? WHERE id = ?", (new_folder, email_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_permanently(email_id):
        """Permanently deletes an email."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM emails WHERE id = ?", (email_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_folder_counts(user_id):
        """Returns email counts for dashboard sidebar badges."""
        conn = get_db()
        cursor = conn.cursor()

        # Inbox unread & total
        cursor.execute("SELECT COUNT(*) FROM emails WHERE (receiver_id = ? OR sender_id = ?) AND folder = 'inbox'", (user_id, user_id))
        inbox_total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emails WHERE (receiver_id = ? OR sender_id = ?) AND folder = 'inbox' AND is_read = 0", (user_id, user_id))
        inbox_unread = cursor.fetchone()[0]

        # Spam total & unread
        cursor.execute("SELECT COUNT(*) FROM emails WHERE (receiver_id = ? OR sender_id = ?) AND folder = 'spam'", (user_id, user_id))
        spam_total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emails WHERE (receiver_id = ? OR sender_id = ?) AND folder = 'spam' AND is_read = 0", (user_id, user_id))
        spam_unread = cursor.fetchone()[0]

        # Sent total
        cursor.execute("SELECT COUNT(*) FROM emails WHERE sender_id = ?", (user_id,))
        sent_total = cursor.fetchone()[0]

        conn.close()
        return {
            "inbox_total": inbox_total,
            "inbox_unread": inbox_unread,
            "spam_total": spam_total,
            "spam_unread": spam_unread,
            "sent_total": sent_total
        }


class FeedbackModel:
    @staticmethod
    def record_feedback(email_id, user_id, original_prediction, corrected_label):
        """
        Stores user correction when a user marks an email as 'Mark as Spam' or 'Not Spam'.
        Also moves email to the corresponding folder.
        """
        conn = get_db()
        cursor = conn.cursor()

        # Insert feedback log
        cursor.execute("""
        INSERT INTO feedback (email_id, user_id, original_prediction, corrected_label)
        VALUES (?, ?, ?, ?)
        """, (email_id, user_id, original_prediction, corrected_label))

        # Update email folder & prediction
        new_folder = "spam" if corrected_label.upper() == "SPAM" else "inbox"
        cursor.execute("""
        UPDATE emails
        SET folder = ?, prediction = ?
        WHERE id = ?
        """, (new_folder, corrected_label.upper(), email_id))

        conn.commit()
        conn.close()

    @staticmethod
    def get_all_feedback():
        """Retrieves list of all feedback corrections for model auditing."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT f.*, e.subject, u.name as user_name
        FROM feedback f
        JOIN emails e ON f.email_id = e.id
        JOIN users u ON f.user_id = u.id
        ORDER BY f.created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
