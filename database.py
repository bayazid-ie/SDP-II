import sqlite3

# User Account Database Functions
def create_table():
    """Create the users table if it does not exist."""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_user(name, username, email, password):
    """Insert a new user into the database."""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
    if cursor.fetchone():
        conn.close()
        return False

    cursor.execute("INSERT INTO users (name, username, email, password) VALUES (?, ?, ?, ?)",
                   (name, username, email, password))
    conn.commit()
    conn.close()

    return True

def check_user_credentials(username, password):
    """Check if the user exists with the given credentials."""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None




# ===== Task Scheduler Database Functions =====
def create_task_table():
    """Create the tasks table if it does not exist in user.db"""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_task(title, category, date, time, description):
    """Insert a new task and return the task ID"""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (title, category, date, time, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, category, date, time, description))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

def get_all_tasks():
    """Get all tasks ordered by date and time"""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM tasks 
        ORDER BY date, time
    ''')
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def delete_task(task_id):
    """Delete a task by ID"""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()



# ===== Study Timer Database Functions =====

def create_study_timer_table():
    """Create the study timer table if it doesn't exist"""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            start_time TEXT NOT NULL,
            duration INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_study_task(subject, start_time, duration):
    """Insert a new study task into the database."""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO study_tasks (subject, start_time, duration) VALUES (?, ?, ?)",
        (subject, start_time, duration)
    )
    conn.commit()
    conn.close()

def get_all_study_tasks():
    """Retrieve all study tasks from the database."""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("SELECT subject, start_time, duration FROM study_tasks")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def delete_study_task(subject, start_time):
    """Delete a task from the database."""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM study_tasks WHERE subject = ? AND start_time = ?",
        (subject, start_time)
    )
    conn.commit()
    conn.close()

   
# ===== Notes Sharing Database Functions =====
import sqlite3
import os
from datetime import datetime

DB_FILE = "user.db"

def create_shared_notes_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shared_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uploader_id INTEGER,
            uploader_name TEXT,
            title TEXT,
            filename TEXT,
            upload_date TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_shared_note(uploader_id, uploader_name, title, filename):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO shared_notes (uploader_id, uploader_name, title, filename, upload_date)
        VALUES (?, ?, ?, ?, ?)
    """, (uploader_id, uploader_name, title, filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_shared_notes():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, uploader_name, title, filename FROM shared_notes")
    notes = cursor.fetchall()
    conn.close()
    return notes

def delete_shared_note(note_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM shared_notes WHERE id=?", (note_id,))
    result = cursor.fetchone()
    if result:
        file_path = os.path.join("shared_notes", result[0])
        if os.path.exists(file_path):
            os.remove(file_path)
    cursor.execute("DELETE FROM shared_notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()
