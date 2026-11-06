
import sqlite3
import os

from contextlib import contextmanager
from datetime import datetime, timezone


# Database configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STORAGE_DIR = os.path.join(BASE_DIR, "storage")

os.makedirs(STORAGE_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(STORAGE_DIR, "agentx.db")


# Database connection
@contextmanager
def get_connection():

    conn = sqlite3.connect(DATABASE_PATH)

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")

    try:
        with conn:
            yield conn
    finally:
        conn.close()


# Initialize database tables
def initialize_database():

    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,

                FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
                ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation
            ON messages(conversation_id)
        """)


# Create or update a conversation and save a message
def save_message(thread_id, role, content):

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:

        # Create conversation if it doesn't exist
        conn.execute("""
            INSERT OR IGNORE INTO conversations
            (id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (
            thread_id,
            "New Chat",
            now,
            now
        ))

        # Automatically generate title from first user message
        if role == "user":

            conversation = conn.execute("""
                SELECT title FROM conversations
                WHERE id = ?
            """, (thread_id,)).fetchone()

            if conversation["title"] == "New Chat":

                title = content.strip().replace("\n", " ")

                if len(title) > 45:
                    title = title[:45].rsplit(" ", 1)[0] + "..."

                conn.execute("""
                    UPDATE conversations
                    SET title = ?
                    WHERE id = ?
                """, (title or "New Chat", thread_id))

        # Save message
        conn.execute("""
            INSERT INTO messages
            (conversation_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            thread_id,
            role,
            content,
            now
        ))

        # Update conversation timestamp
        conn.execute("""
            UPDATE conversations
            SET updated_at = ?
            WHERE id = ?
        """, (now, thread_id))


# Retrieve all conversations
def get_all_conversations():

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT *
            FROM conversations
            ORDER BY updated_at DESC
        """).fetchall()

        return [dict(row) for row in rows]


# Retrieve messages of a particular conversation
def get_conversation_messages(thread_id):

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
        """, (thread_id,)).fetchall()

        return [dict(row) for row in rows]


# Retrieve a conversation
def get_conversation(thread_id):

    with get_connection() as conn:

        row = conn.execute("""
            SELECT *
            FROM conversations
            WHERE id = ?
        """, (thread_id,)).fetchone()

        return dict(row) if row else None


# Delete a conversation
def delete_conversation(thread_id):

    with get_connection() as conn:

        cursor = conn.execute("""
            DELETE FROM conversations
            WHERE id = ?
        """, (thread_id,))

        return cursor.rowcount > 0
