import sqlite3
import os

DB_NAME = "pathwise.db"

def get_db_connection():
    """Establishes a connection to the local SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name like a dictionary
    return conn

def init_db():
    """Initializes the database and creates the necessary tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            groq_api_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Create Resume Analyses Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_analyses (
            analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            initial_score INTEGER,
            current_score INTEGER,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )
    ''')
    
    # 3. Create Skill Gaps Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skill_gaps (
            gap_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            skill_name TEXT NOT NULL,
            status TEXT DEFAULT 'Missing', -- Can switch to 'Completed' via the chatbot
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )
    ''')
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sender TEXT NOT NULL, -- 'user' or 'assistant'
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✓ PathWise AI 2.0 Database initialized successfully.")

if __name__ == "__main__":
    init_db()