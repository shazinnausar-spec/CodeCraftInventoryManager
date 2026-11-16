
import sqlite3

import pytest

from app.database import (
    initialize_database,
    database_transaction
)

from app.services.backup_service import (
    create_backup,
    validate_backup,
    restore_backup
)


@pytest.fixture
def backup_environment(tmp_path):

    db_path = tmp_path / "database" / "inventory.db"
    backup_dir = tmp_path / "backups"

    initialize_database(db_path)

    with database_transaction(db_path) as connection:

        connection.execute(
            """
            INSERT INTO categories (
                name,
                description,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (
                "Electronics",
                "Test category",
                "2026-01-01"
            )
        )

    return db_path, backup_dir


def test_create_backup(
    backup_environment
):

    db_path, backup_dir = backup_environment

    backup_path = create_backup(
        db_path,
        backup_dir
    )

    assert backup_path.exists()
    assert backup_path.suffix == ".db"
    assert backup_path.parent == backup_dir


def test_created_backup_is_valid(
    backup_environment
):

    db_path, backup_dir = backup_environment

    backup_path = create_backup(
        db_path,
        backup_dir
    )

    assert validate_backup(backup_path) is True


def test_backup_contains_database_data(
    backup_environment
):

    db_path, backup_dir = backup_environment

    backup_path = create_backup(
        db_path,
        backup_dir
    )

    connection = sqlite3.connect(
        str(backup_path)
    )

    try:

        category = connection.execute(
            "SELECT name FROM categories"
        ).fetchone()

        assert category[0] == "Electronics"

    finally:

        connection.close()


def test_create_backup_missing_database_rejected(
    tmp_path
):

    missing_db = tmp_path / "missing.db"

    with pytest.raises(FileNotFoundError):

        create_backup(
            missing_db,
            tmp_path / "backups"
        )



def test_restore_backup(
    backup_environment
):

    db_path, backup_dir = backup_environment

    # Create the original backup.
    backup_path = create_backup(
        db_path,
        backup_dir
    )

    # Change the active database.
    with database_transaction(db_path) as connection:

        connection.execute(
            "DELETE FROM categories"
        )

    # Confirm the active database changed.
    connection = sqlite3.connect(str(db_path))

    try:

        count = connection.execute(
            "SELECT COUNT(*) FROM categories"
        ).fetchone()[0]

        assert count == 0

    finally:

        connection.close()

    # Restore the original backup.
    safety_backup = restore_backup(
        backup_path,
        db_path,
        backup_dir
    )

    # Confirm the original data is restored.
    connection = sqlite3.connect(str(db_path))

    try:

        count = connection.execute(
            "SELECT COUNT(*) FROM categories"
        ).fetchone()[0]

        assert count == 1

    finally:

        connection.close()

    # Confirm a safety backup was created.
    assert safety_backup is not None
    assert safety_backup.exists()


def test_restore_invalid_backup_rejected(
    backup_environment,
    tmp_path
):

    db_path, backup_dir = backup_environment

    invalid_backup = tmp_path / "invalid.db"

    invalid_backup.write_text(
        "This is not a SQLite database."
    )

    with pytest.raises(ValueError):

        restore_backup(
            invalid_backup,
            db_path,
            backup_dir
        )

    # The original database must remain unchanged.
    with sqlite3.connect(str(db_path)) as connection:

        count = connection.execute(
            "SELECT COUNT(*) FROM categories"
        ).fetchone()[0]

        assert count == 1


def test_restore_missing_backup_rejected(
    backup_environment,
    tmp_path
):

    db_path, backup_dir = backup_environment

    with pytest.raises(FileNotFoundError):

        restore_backup(
            tmp_path / "missing.db",
            db_path,
            backup_dir
        )


def test_restore_database_onto_itself_rejected(
    backup_environment
):

    db_path, backup_dir = backup_environment

    with pytest.raises(ValueError):

        restore_backup(
            db_path,
            db_path,
            backup_dir
        )


def test_restore_backup_without_existing_database(
    tmp_path
):

    # Prepare a valid backup source.
    original_db = tmp_path / "original.db"

    initialize_database(original_db)

    backup_dir = tmp_path / "backups"

    backup_path = create_backup(
        original_db,
        backup_dir
    )

    # Restore into a new database location.
    new_db = tmp_path / "restored" / "inventory.db"

    safety_backup = restore_backup(
        backup_path,
        new_db,
        backup_dir
    )

    assert new_db.exists()
    assert safety_backup is None

    assert validate_backup(new_db) is True


def test_invalid_database_schema_rejected(
    tmp_path
):

    invalid_db = tmp_path / "wrong_schema.db"

    connection = sqlite3.connect(str(invalid_db))

    try:

        connection.execute(
            "CREATE TABLE example (id INTEGER)"
        )

        connection.commit()

    finally:

        connection.close()

    with pytest.raises(ValueError):

        validate_backup(invalid_db)
