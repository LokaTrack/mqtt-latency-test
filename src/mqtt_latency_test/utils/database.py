import sqlite3


def create_connection(db_file: str = "database.db"):
    """Create a database connection to the SQLite database specified by db_file."""

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to database: {db_file}")
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")

    return conn


def close_connection(conn: sqlite3.Connection):
    """Close the database connection."""
    if conn:
        try:
            conn.close()
            print("Database connection closed.")
        except sqlite3.Error as e:
            print(f"Error closing database connection: {e}")
    else:
        print("No database connection to close.")
