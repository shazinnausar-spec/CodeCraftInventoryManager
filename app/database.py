# Import SQLite.
import sqlite3

# Import the contextmanager decorator.
from contextlib import contextmanager

# Import datetime for timestamps.
from datetime import datetime, timezone

# Import Path for safe file handling.
from pathlib import Path

# Import our database configuration.
from app.config import DATABASE_PATH, create_app_directories

# Import the database schema.
from app.models.database_schema import SCHEMA


def get_timestamp():
    """
    Return the current UTC timestamp.

    We use UTC so timestamps remain consistent
    across different computer time zones.
    """

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_connection(db_path=DATABASE_PATH):
    """
    Create and return a SQLite database connection.
    """

    # Convert the database path into a Path object.
    db_path = Path(db_path)

    # Ensure the parent directory exists.
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Connect to the SQLite database.
    connection = sqlite3.connect(
        str(db_path),
        timeout=10
    )

    # Return rows as dictionary-like objects.
    connection.row_factory = sqlite3.Row

    # Enable foreign key enforcement.
    connection.execute("PRAGMA foreign_keys = ON")

    # Set a busy timeout to handle temporary database locks.
    connection.execute("PRAGMA busy_timeout = 10000")

    return connection


@contextmanager
def database_transaction(db_path=DATABASE_PATH):
    """
    Manage a database transaction safely.

    Automatically commits when successful.
    Automatically rolls back if an error occurs.
    Always closes the connection.
    """

    # Open a database connection.
    connection = get_connection(db_path)

    try:

        # Give the connection to the calling function.
        yield connection

        # Save database changes.
        connection.commit()

    except Exception:

        # Undo incomplete database changes.
        connection.rollback()

        # Pass the original error to the caller.
        raise

    finally:

        # Always close the connection.
        connection.close()


def initialize_database(db_path=DATABASE_PATH):
    """
    Create all required database tables and indexes.
    """

    # Create the application's data directories
    # when initializing the default application database.
    if Path(db_path) == Path(DATABASE_PATH):
        create_app_directories()

    # Open a database connection.
    connection = get_connection(db_path)

    try:

        # Execute the complete database schema.
        connection.executescript(SCHEMA)

        # Save database initialization changes.
        connection.commit()

    finally:

        # Close the database connection.
        connection.close()


def check_database_connection(db_path=DATABASE_PATH):
    """
    Check whether the database can be accessed.
    """

    connection = get_connection(db_path)

    try:

        # Execute a simple database test query.
        result = connection.execute(
            "SELECT 1"
        ).fetchone()

        return result[0] == 1

    finally:

        connection.close()


def get_database_info(db_path=DATABASE_PATH):
    """
    Return basic database information.
    """

    connection = get_connection(db_path)

    try:

        # Get the SQLite version.
        version = connection.execute(
            "SELECT sqlite_version()"
        ).fetchone()[0]

        # Get the names of all application tables.
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()

        return {
            "sqlite_version": version,
            "tables": [row["name"] for row in tables]
        }

    finally:

        connection.close()