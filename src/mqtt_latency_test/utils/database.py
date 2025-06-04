import sqlite3
import os
import logging
from dotenv import load_dotenv
from typing import Optional

logger = logging.getLogger("uvicorn.error")

load_dotenv()

# Get database file path from environment variable or use default
DATABASE_PATH = os.getenv("DATABASE_PATH", "database.db")


def create_connection(db_file: Optional[str] = None):
    """Create a database connection to the SQLite database specified by db_file."""

    if db_file is None:
        db_file = DATABASE_PATH

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        logger.debug(f"Connected to database: {db_file}")
    except sqlite3.Error as e:
        logger.debug(f"Error connecting to database: {e}")

    return conn


def close_connection(conn: sqlite3.Connection):
    """Close the database connection."""
    if conn:
        try:
            conn.close()
            logger.debug("Database connection closed.")
        except sqlite3.Error as e:
            logger.debug(f"Error closing database connection: {e}")
    else:
        logger.debug("No database connection to close.")


def create_first_case_table(conn: sqlite3.Connection):
    """Create the first_case table if it doesn't exist."""

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS first_case (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        iteration INTEGER,
        payload_timestamp_iso TEXT,
        payload_timestamp_epoch REAL,
        server_timestamp_iso TEXT,
        server_timestamp_epoch REAL,
        difference REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        logger.debug("Table 'first_case' created successfully.")
    except sqlite3.Error as e:
        logger.debug(f"Error creating table: {e}")


def create_second_case_table(conn: sqlite3.Connection):
    """Create the second_case table if it doesn't exist."""

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS second_case (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        iteration INTEGER,
        server_timestamp_iso TEXT,
        server_timestamp_epoch REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        logger.debug("Table 'second_case' created successfully.")
    except sqlite3.Error as e:
        logger.debug(f"Error creating table: {e}")


def insert_first_case_data(
    conn: sqlite3.Connection,
    iteration: Optional[int],
    payload_timestamp_iso: Optional[str],
    payload_timestamp_epoch: Optional[float],
    server_timestamp_iso: Optional[str],
    server_timestamp_epoch: Optional[float],
    difference: Optional[float],
) -> bool:
    """
    Insert data into the first_case table.

    Args:
        conn: Database connection
        iteration: Iteration number from the payload
        payload_timestamp_iso: ISO timestamp from payload
        payload_timestamp_epoch: Epoch timestamp from payload
        server_timestamp_iso: ISO timestamp from server
        server_timestamp_epoch: Epoch timestamp from server
        difference: Time difference between server and payload timestamps

    Returns:
        bool: True if successful, False otherwise
    """

    insert_sql = """
    INSERT INTO first_case (
        iteration, 
        payload_timestamp_iso, 
        payload_timestamp_epoch, 
        server_timestamp_iso, 
        server_timestamp_epoch, 
        difference
    ) VALUES (?, ?, ?, ?, ?, ?);
    """

    try:
        cursor = conn.cursor()
        cursor.execute(
            insert_sql,
            (
                iteration,
                payload_timestamp_iso,
                payload_timestamp_epoch,
                server_timestamp_iso,
                server_timestamp_epoch,
                difference,
            ),
        )
        conn.commit()
        logger.debug(f"Case 1 data inserted successfully. Row ID: {cursor.lastrowid}")
        return True
    except sqlite3.Error as e:
        logger.debug(f"Error inserting data: {e}")
        return False


def insert_second_case_data(
    conn: sqlite3.Connection,
    iteration: Optional[int],
    server_timestamp_iso: Optional[str],
    server_timestamp_epoch: Optional[float],
) -> bool:
    """
    Insert data into the second_case table.

    Args:
        conn: Database connection
        iteration: Iteration number from the payload
        server_timestamp_iso: ISO timestamp from server
        server_timestamp_epoch: Epoch timestamp from server

    Returns:
        bool: True if successful, False otherwise
    """

    insert_sql = """
    INSERT INTO second_case (
        iteration, 
        server_timestamp_iso, 
        server_timestamp_epoch
    ) VALUES (?, ?, ?);
    """

    try:
        cursor = conn.cursor()
        cursor.execute(
            insert_sql,
            (
                iteration,
                server_timestamp_iso,
                server_timestamp_epoch,
            ),
        )
        conn.commit()
        logger.debug(f"Case 2 data inserted successfully. Row ID: {cursor.lastrowid}")
        return True
    except sqlite3.Error as e:
        logger.debug(f"Error inserting data: {e}")
        return False


def initialize_database(db_file: Optional[str] = None):
    """Initialize the database and create necessary tables."""

    if db_file is None:
        db_file = DATABASE_PATH

    conn = create_connection(db_file)
    if conn:
        create_first_case_table(conn)
        create_second_case_table(conn)
        close_connection(conn)
        return True
    return False
