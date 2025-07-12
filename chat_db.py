import sqlite3

def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    # Add session_id column to the chats table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL, -- New column for session ID
            user TEXT NOT NULL,
            bot TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Modify save_chat to accept session_id
def save_chat(session_id, user_msg, bot_msg):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('INSERT INTO chats (session_id, user, bot) VALUES (?, ?, ?)', (session_id, user_msg, bot_msg))
    conn.commit()
    conn.close()

# This function will now get the latest message for each unique session
def get_all_sessions_latest_chats():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    # Select the last chat (based on max id) for each unique session_id
    c.execute('''
        SELECT c.id, c.session_id, c.user, c.bot, c.timestamp
        FROM chats c
        INNER JOIN (
            SELECT session_id, MAX(id) as max_id
            FROM chats
            GROUP BY session_id
        ) AS latest_chats ON c.session_id = latest_chats.session_id AND c.id = latest_chats.max_id
        ORDER BY c.id DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

# This function will get all chats for a specific session_id
def get_session_chats(session_id):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('SELECT user, bot, timestamp FROM chats WHERE session_id = ? ORDER BY id ASC', (session_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# Function to clear all chat history from the database
def clear_all_chats():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('DELETE FROM chats')
    conn.commit()
    conn.close()

# Function to delete a specific chat session (all messages within that session)
def delete_chat_by_id(chat_id):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    # First, get the session_id associated with this chat_id
    c.execute('SELECT session_id FROM chats WHERE id = ?', (chat_id,))
    session_id_to_delete = c.fetchone()

    if session_id_to_delete:
        session_id_to_delete = session_id_to_delete[0]
        # Then, delete all chats for that session_id
        c.execute('DELETE FROM chats WHERE session_id = ?', (session_id_to_delete,))
    conn.commit()
    conn.close()