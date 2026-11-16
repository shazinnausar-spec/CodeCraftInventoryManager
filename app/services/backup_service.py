
import os
import sqlite3

from datetime import datetime
from pathlib import Path

from app.config import DATABASE_PATH, BACKUP_DIR


# Required tables for a valid application backup.
REQUIRED_TABLES = {
    "categories",
    "products",
    "stock_movements",
    "app_settings",
}


# --------------------------------------------------
# DATABASE COPY HELPER
# --------------------------------------------------

def copy_database(source_path, destination_path):
    """
    Copy a SQLite database safely using SQLite's
    built-in backup API.
    """

    source_path = Path(source_path)
    destination_path = Path(destination_path)

    if not source_path.exists():
        raise FileNotFoundError(
            "The source database does not exist."
        )

    destination_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    source_connection = sqlite3.connect(str(source_path))
    destination_connection = sqlite3.connect(
        str(destination_path)
    )

    try:

        source_connection.backup(destination_connection)

    finally:

        destination_connection.close()
        source_connection.close()


# --------------------------------------------------
# CREATE BACKUP
# --------------------------------------------------

def create_backup(
    db_path=DATABASE_PATH,
    backup_dir=BACKUP_DIR
):
    """
    Create a timestamped database backup.

    Returns the path of the created backup.
    """

    db_path = Path(db_path)
    backup_dir = Path(backup_dir)

    if not db_path.exists():
        raise FileNotFoundError(
            "The application database does not exist."
        )

    if db_path.resolve() == backup_dir.resolve():
        raise ValueError(
            "The backup folder cannot be the database file."
        )

    backup_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    backup_path = (
        backup_dir
        / f"inventory_backup_{timestamp}.db"
    )

    copy_database(
        db_path,
        backup_path
    )

    return backup_path


# --------------------------------------------------
# VALIDATE BACKUP
# --------------------------------------------------

def validate_backup(backup_path):
    """
    Check that a backup is a valid application database.
    """

    backup_path = Path(backup_path)

    if not backup_path.exists():
        raise FileNotFoundError(
            "The selected backup file does not exist."
        )

    if not backup_path.is_file():
        raise ValueError(
            "The selected backup path is not a file."
        )

    connection = None

    try:

        connection = sqlite3.connect(
            str(backup_path)
        )

        # Check database integrity.
        integrity = connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()

        if not integrity or integrity[0] != "ok":
            raise ValueError(
                "The backup database is corrupted."
            )

        # Check required application tables.
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
                AND name NOT LIKE 'sqlite_%'
            """
        ).fetchall()

        existing_tables = {
            row[0] for row in tables
        }

        missing_tables = (
            REQUIRED_TABLES - existing_tables
        )

        if missing_tables:
            raise ValueError(
                "Invalid application backup. "
                f"Missing tables: {', '.join(sorted(missing_tables))}"
            )

        return True

    except sqlite3.DatabaseError as error:

        raise ValueError(
            "The selected file is not a valid SQLite backup."
        ) from error

    finally:

        if connection is not None:
            connection.close()


# --------------------------------------------------
# RESTORE BACKUP
# --------------------------------------------------

def restore_backup(
    backup_path,
    db_path=DATABASE_PATH,
    backup_dir=BACKUP_DIR
):
    """
    Restore a validated backup.

    Before replacing the current database, create
    a safety backup of the existing database.

    Returns the safety backup path.
    """

    backup_path = Path(backup_path)
    db_path = Path(db_path)
    backup_dir = Path(backup_dir)

    if not backup_path.exists():
        raise FileNotFoundError(
            "The selected backup file does not exist."
        )

    if not backup_path.is_file():
        raise ValueError(
            "The selected backup path is not a file."
        )

    # Prevent restoring the database onto itself.
    if backup_path.resolve() == db_path.resolve():
        raise ValueError(
            "The selected backup is already the active database."
        )

    # Validate before changing anything.
    validate_backup(backup_path)

    # Ensure the database folder exists.
    db_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Create a temporary database in the same folder.
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    temporary_path = db_path.with_name(
        f"{db_path.stem}_restore_{timestamp}.tmp"
    )

    try:

        # Copy the selected backup into a temporary file.
        copy_database(
            backup_path,
            temporary_path
        )

        # Validate the temporary restored database.
        validate_backup(temporary_path)

        # Protect the current database before replacement.
        safety_backup = None

        if db_path.exists():

            safety_backup = create_backup(
                db_path,
                backup_dir
            )

        # Replace the active database.
        os.replace(
            temporary_path,
            db_path
        )

        return safety_backup

    finally:

        # Remove temporary files if they still exist.
        if temporary_path.exists():

            temporary_path.unlink()
