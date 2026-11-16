import pytest

from app.database import initialize_database
from app.services.category_service import (
    create_category,
    get_category,
    get_all_categories
)


@pytest.fixture
def test_db(tmp_path):
    """Create a separate temporary database for each test."""

    db_path = tmp_path / "test_categories.db"
    initialize_database(db_path)

    return db_path


def test_create_category(test_db):
    category_id = create_category(
        "Electronics",
        "Electronic products",
        db_path=test_db
    )

    category = get_category(category_id, test_db)

    assert category["name"] == "Electronics"
    assert category["description"] == "Electronic products"


def test_duplicate_category_rejected(test_db):
    create_category("Accessories", db_path=test_db)

    with pytest.raises(ValueError, match="already exists"):
        create_category("Accessories", db_path=test_db)


def test_category_names_are_case_insensitive(test_db):
    create_category("Electronics", db_path=test_db)

    with pytest.raises(ValueError, match="already exists"):
        create_category("electronics", db_path=test_db)


def test_get_all_categories(test_db):
    create_category("Accessories", db_path=test_db)
    create_category("Electronics", db_path=test_db)
    create_category("Furniture", db_path=test_db)

    categories = get_all_categories(test_db)

    assert len(categories) == 3
    assert categories[0]["name"] == "Accessories"
    assert categories[1]["name"] == "Electronics"
    assert categories[2]["name"] == "Furniture"


def test_empty_category_name_rejected(test_db):
    with pytest.raises(ValueError, match="required"):
        create_category("   ", db_path=test_db)