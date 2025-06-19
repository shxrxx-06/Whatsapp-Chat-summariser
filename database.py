import sqlite3
import json
from datetime import datetime

def init_database():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect('chat_summaries.db')
    cursor = conn.cursor()
    
    # Create table for storing chat summaries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            summary TEXT,
            tasks TEXT,
            keywords TEXT,
            raw_output TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_summary_to_db(filename, summary, tasks, keywords, raw_output):
    """Save chat summary results to the database."""
    conn = sqlite3.connect('chat_summaries.db')
    cursor = conn.cursor()
    
    # Convert tasks list to JSON string for storage
    tasks_json = json.dumps(tasks) if tasks else None
    
    cursor.execute('''
        INSERT INTO chat_summaries (filename, summary, tasks, keywords, raw_output)
        VALUES (?, ?, ?, ?, ?)
    ''', (filename, summary, tasks_json, keywords, raw_output))
    
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    
    return record_id

def get_all_summaries():
    """Retrieve all chat summaries from the database."""
    conn = sqlite3.connect('chat_summaries.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, filename, upload_timestamp, summary, tasks, keywords, raw_output
        FROM chat_summaries
        ORDER BY upload_timestamp DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    # Convert results to list of dictionaries
    summaries = []
    for row in results:
        summary = {
            'id': row[0],
            'filename': row[1],
            'upload_timestamp': row[2],
            'summary': row[3],
            'tasks': json.loads(row[4]) if row[4] else [],
            'keywords': row[5],
            'raw_output': row[6]
        }
        summaries.append(summary)
    
    return summaries

def get_summary_by_id(summary_id):
    """Retrieve a specific chat summary by ID."""
    conn = sqlite3.connect('chat_summaries.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, filename, upload_timestamp, summary, tasks, keywords, raw_output
        FROM chat_summaries
        WHERE id = ?
    ''', (summary_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'filename': result[1],
            'upload_timestamp': result[2],
            'summary': result[3],
            'tasks': json.loads(result[4]) if result[4] else [],
            'keywords': result[5],
            'raw_output': result[6]
        }
    return None

if __name__ == '__main__':
    # Initialize database
    init_database()
    print("Database initialized successfully!")
    
    # Test saving a summary
    test_tasks = [
        {"Task": "Test task", "Responsible": "John", "Deadline": "2025-06-20"}
    ]
    record_id = save_summary_to_db(
        "test_chat.txt",
        "Test summary",
        test_tasks,
        "test, keywords",
        "Raw test output"
    )
    print(f"Test record saved with ID: {record_id}")
    
    # Test retrieving summaries
    summaries = get_all_summaries()
    print(f"Retrieved {len(summaries)} summaries from database")

