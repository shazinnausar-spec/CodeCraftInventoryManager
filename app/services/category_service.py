import sqlite3

from app.config import DATABASE_PATH
from app.database import (
    database_transaction,
    get_connection,
    get_timestamp
)


def create_category(name, description="", db_path=DATABASE_PATH):
    """
    Create a new product category.

    Category names must be unique.
    """

    # Validate the category name.
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Category name is required.")

    if len(name.strip()) > 100:
        raise ValueError("Category name cannot exceed 100 characters.")

    # Validate the description.
    if not isinstance(description, str):
        raise ValueError("Category description must be text.")

    if len(description.strip()) > 500:
        raise ValueError("Description cannot exceed 500 characters.")

    try:
        with database_transaction(db_path=db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO categories (name, description, created_at)
                VALUES (?, ?, ?)
                """,
                (
                    name.strip(),
                    description.strip(),
                    get_timestamp()
                )
            )

            return cursor.lastrowid

    except sqlite3.IntegrityError as error:
        if "categories.name" in str(error):
            raise ValueError(
                "This category already exists."
            ) from error

        raise


def get_category(category_id, db_path=DATABASE_PATH):
    """Retrieve one category using its ID."""

    connection = get_connection(db_path)

    try:
        category = connection.execute(
            """
            SELECT id, name, description, created_at
            FROM categories
            WHERE id = ?
            """,
            (category_id,)
        ).fetchone()

        return dict(category) if category is not None else None

    finally:
        connection.close()


def get_all_categories(db_path=DATABASE_PATH):
    """Retrieve all categories in alphabetical order."""

    connection = get_connection(db_path)

    try:
        categories = connection.execute(
            """
            SELECT id, name, description, created_at
            FROM categories
            ORDER BY name COLLATE NOCASE
            """
        ).fetchall()

        return [dict(category) for category in categories]

    finally:
        connection.close()