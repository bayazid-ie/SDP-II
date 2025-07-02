import sqlite3

def create_table():
    """Create or update the users table with all required columns"""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    
    # First create the basic table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    # Add new columns if they don't exist
    new_columns = [
        ('university', 'TEXT DEFAULT ""'),
        ('department', 'TEXT DEFAULT ""'),
        ('address', 'TEXT DEFAULT ""'),
        ('phone', 'TEXT DEFAULT ""'),
        ('bio', 'TEXT DEFAULT ""')
    ]
    
    for column_name, column_type in new_columns:
        try:
            cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type}')
        except sqlite3.OperationalError:
            pass  # Column already exists
    
    conn.commit()
    conn.close()

def insert_user(name, username, email, password):
    """Insert a new user into the database"""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (name, username, email, password)
            VALUES (?, ?, ?, ?)
        ''', (name, username, email, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username or email already exists
    finally:
        conn.close()

def check_user_credentials(username, password):
    """Check if username and password match"""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_user_info(username):
    """Get complete user information by username"""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name, username, email, university, department, address, phone, bio
        FROM users WHERE username = ?
    ''', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'name': user[0],
            'username': user[1],
            'email': user[2],
            'university': user[3],
            'department': user[4],
            'address': user[5],
            'phone': user[6],
            'bio': user[7]
        }
    return None

def update_user_profile(username, **kwargs):
    """Update user profile information"""
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [username]
    
    cursor.execute(f'''
        UPDATE users 
        SET {set_clause}
        WHERE username = ?
    ''', values)
    
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

# [Keep all your existing task, study timer, and notes sharing functions below]



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

    


STUDY_ROOM_DB = 'study_room.db'

def create_study_room_tables():
    conn = sqlite3.connect(STUDY_ROOM_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shared_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            size TEXT NOT NULL,
            path TEXT NOT NULL,
            uploaded_by TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_message(sender, message):
    conn = sqlite3.connect(STUDY_ROOM_DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (sender, message) VALUES (?, ?)
    ''', (sender, message))
    conn.commit()
    conn.close()

def get_all_messages():
    conn = sqlite3.connect(STUDY_ROOM_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT sender, message, timestamp FROM messages ORDER BY timestamp')
    messages = cursor.fetchall()
    conn.close()
    return messages

def insert_shared_file(name, size, path, uploaded_by):
    conn = sqlite3.connect(STUDY_ROOM_DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO shared_files (name, size, path, uploaded_by) VALUES (?, ?, ?, ?)
    ''', (name, size, path, uploaded_by))
    conn.commit()
    conn.close()

def get_all_shared_files():
    conn = sqlite3.connect(STUDY_ROOM_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT name, size, path FROM shared_files ORDER BY timestamp')
    files = cursor.fetchall()
    conn.close()
    # Return as list of dicts for convenience
    return [{"name": row[0], "size": row[1], "path": row[2]} for row in files]
