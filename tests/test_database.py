# Import SQLite for database error testing.
import sqlite3

# Import the database functions.
from app.database import (
    initialize_database,
    get_connection,
    database_transaction,
    check_database_connection,
    get_database_info
)


def test_database_initialization(tmp_path):

    # Create a temporary test database.
    db_path = tmp_path / "test_inventory.db"

    # Initialize the database.
    initialize_database(db_path)

    # Check that the database connection works.
    assert check_database_connection(db_path) is True

    # Get database information.
    info = get_database_info(db_path)

    # Expected application tables.
    expected_tables = {
        "categories",
        "products",
        "stock_movements",
        "app_settings"
    }

    # Check that all expected tables exist.
    assert set(info["tables"]) == expected_tables


def test_database_initialization_is_repeatable(tmp_path):

    db_path = tmp_path / "test_inventory.db"

    # Initialize the database twice.
    initialize_database(db_path)
    initialize_database(db_path)

    # Check that the database still works.
    assert check_database_connection(db_path) is True


def test_database_foreign_keys(tmp_path):

    db_path = tmp_path / "test_inventory.db"

    initialize_database(db_path)

    # Try creating a product without a valid category.
    with database_transaction(db_path) as connection:

        try:

            connection.execute(
                """
                INSERT INTO products (
                    name,
                    sku,
                    category_id,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "Test Product",
                    "TEST-001",
                    999,
                    "2026-11-16T00:00:00+00:00",
                    "2026-11-16T00:00:00+00:00"
                )
            )

            assert False, "Invalid category should be rejected."

        except sqlite3.IntegrityError:
            pass


def test_database_transaction_rollback(tmp_path):

    db_path = tmp_path / "test_inventory.db"

    initialize_database(db_path)

    # Try inserting a category and then force an error.
    try:

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
                    "Rollback Test",
                    "Temporary category",
                    "2026-11-16T00:00:00+00:00"
                )
            )

            # Simulate an error.
            raise ValueError("Testing transaction rollback")

    except ValueError:
        pass

    # Check that the category was not saved.
    connection = get_connection(db_path)

    try:

        result = connection.execute(
            """
            SELECT *
            FROM categories
            WHERE name = ?
            """,
            ("Rollback Test",)
        ).fetchone()

        assert result is None

    finally:

        connection.close()