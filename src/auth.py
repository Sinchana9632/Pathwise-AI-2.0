import hashlib
import sqlite3
from src.database import get_db_connection

def hash_password(password: str) -> str:
    """Hashes a password using SHA-256 for secure database storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name: str, email: str, password: str) -> bool:
    """
    Registers a new user into the SQLite database.
    Returns True if successful, False if the email already exists.
    """
    hashed_pwd = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email.lower().strip(), hashed_pwd)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # This error fires if the email is already registered (due to the UNIQUE constraint)
        return False
    finally:
        conn.close()

def login_user(email: str, password: str):
    """
    Verifies user credentials against the database records.
    Returns the user row data if valid, or None if authentication fails.
    """
    hashed_pwd = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email.lower().strip(), hashed_pwd)
    )
    user = cursor.fetchone()
    conn.close()
    
    return user  # Returns dictionary-like row if found, otherwise None
def save_resume_analysis(user_id: int, score: int):
    """Saves the initial and current match score to the resume_analyses table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if the user already has an analysis record
    cursor.execute("SELECT analysis_id FROM resume_analyses WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()
    
    if existing:
        # Update the current score
        cursor.execute(
            "UPDATE resume_analyses SET current_score = ?, analyzed_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (score, user_id)
        )
    else:
        # Insert a fresh record (initial and current score are the same at the start)
        cursor.execute(
            "INSERT INTO resume_analyses (user_id, initial_score, current_score) VALUES (?, ?, ?)",
            (user_id, score, score)
        )
    conn.commit()
    conn.close()

def save_skill_gaps(user_id: int, skills_list: list):
    """Inserts missing skills into the skill_gaps table if they don't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for skill in skills_list:
        skill_clean = skill.strip().title()
        if not skill_clean:
            continue
        # Check to avoid duplicate skills for the same user
        cursor.execute(
            "SELECT gap_id FROM skill_gaps WHERE user_id = ? AND skill_name = ?",
            (user_id, skill_clean)
        )
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO skill_gaps (user_id, skill_name, status) VALUES (?, ?, 'Missing')",
                (user_id, skill_clean)
            )
            
    conn.commit()
    conn.close()
def get_user_metrics(user_id: int):
    """Retrieves the initial and current score metrics for a specific user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT initial_score, current_score FROM resume_analyses WHERE user_id = ?", 
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row  # Will return a dictionary-like row or None

def get_user_skills(user_id: int):
    """Retrieves all tracking skills and their statuses for a specific user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT gap_id, skill_name, status FROM skill_gaps WHERE user_id = ?", 
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows  # Returns a list of rows
def save_chat_message(user_id: int, sender: str, message: str):
    """Saves a single chat message thread to the history table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_id, sender, message) VALUES (?, ?, ?)",
        (user_id, sender, message)
    )
    conn.commit()
    conn.close()

def get_chat_history(user_id: int):
    """Fetches all past chat messages for a specific user ordered by time."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT sender, message FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows