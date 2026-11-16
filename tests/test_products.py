# Import pytest.
import pytest

# Import database functions.
from app.database import (
    initialize_database,
    database_transaction,
    get_connection
)

# Import product functions.
from app.services.product_service import (
    create_product,
    get_product,
    get_all_products,
    update_product,
    archive_product
)


@pytest.fixture
def test_db(tmp_path):

    # Create an isolated test database.
    db_path = tmp_path / "test_products.db"

    # Initialize database tables.
    initialize_database(db_path)

    # Create a test category.
    with database_transaction(db_path) as connection:

        cursor = connection.execute(
            """
            INSERT INTO categories (
                name,
                description,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (
                "Accessories",
                "Computer accessories",
                "2026-11-16T00:00:00+00:00"
            )
        )

        category_id = cursor.lastrowid

    return db_path, category_id


def test_create_product(test_db):

    db_path, category_id = test_db

    product_id = create_product(
        name="Wireless Keyboard",
        sku="KEY-001",
        category_id=category_id,
        purchase_price_cents=250000,
        selling_price_cents=350000,
        quantity=25,
        minimum_stock=5,
        db_path=db_path
    )

    product = get_product(product_id, db_path)

    assert product["name"] == "Wireless Keyboard"
    assert product["sku"] == "KEY-001"
    assert product["quantity"] == 25
    assert product["purchase_price_cents"] == 250000


def test_create_product_records_opening_stock(test_db):

    db_path, category_id = test_db

    product_id = create_product(
        "Mouse",
        "MOU-001",
        category_id,
        100000,
        150000,
        10,
        3,
        db_path=db_path
    )

    connection = get_connection(db_path)

    try:

        movement = connection.execute(
            """
            SELECT *

            FROM stock_movements

            WHERE product_id = ?
            """,
            (product_id,)
        ).fetchone()

        assert movement["movement_type"] == "OPENING"
        assert movement["quantity"] == 10
        assert movement["stock_after"] == 10

    finally:

        connection.close()


def test_duplicate_sku_rejected(test_db):

    db_path, category_id = test_db

    create_product(
        "Keyboard",
        "KEY-001",
        category_id,
        100000,
        150000,
        10,
        2,
        db_path=db_path
    )

    with pytest.raises(ValueError, match="SKU already exists"):

        create_product(
            "Another Keyboard",
            "KEY-001",
            category_id,
            100000,
            150000,
            5,
            2,
            db_path=db_path
        )


def test_negative_price_rejected(test_db):

    db_path, category_id = test_db

    with pytest.raises(ValueError):

        create_product(
            "Keyboard",
            "KEY-002",
            category_id,
            -100,
            150000,
            10,
            2,
            db_path=db_path
        )


def test_product_search(test_db):

    db_path, category_id = test_db

    create_product(
        "Wireless Keyboard",
        "KEY-001",
        category_id,
        100000,
        150000,
        10,
        2,
        db_path=db_path
    )

    create_product(
        "Wireless Mouse",
        "MOU-001",
        category_id,
        50000,
        80000,
        20,
        5,
        db_path=db_path
    )

    results = get_all_products(
        search="Keyboard",
        db_path=db_path
    )

    assert len(results) == 1
    assert results[0]["name"] == "Wireless Keyboard"


def test_update_product(test_db):

    db_path, category_id = test_db

    product_id = create_product(
        "Keyboard",
        "KEY-001",
        category_id,
        100000,
        150000,
        10,
        2,
        db_path=db_path
    )

    update_product(
        product_id,
        "Mechanical Keyboard",
        "KEY-001",
        category_id,
        120000,
        180000,
        3,
        db_path=db_path
    )

    product = get_product(product_id, db_path)

    assert product["name"] == "Mechanical Keyboard"
    assert product["purchase_price_cents"] == 120000

    # Editing product details must not change stock.
    assert product["quantity"] == 10


def test_archive_product(test_db):

    db_path, category_id = test_db

    product_id = create_product(
        "Keyboard",
        "KEY-001",
        category_id,
        100000,
        150000,
        0,
        2,
        db_path=db_path
    )

    archive_product(
        product_id,
        db_path=db_path
    )

    # Archived products are excluded by default.
    assert get_all_products(db_path=db_path) == []

    # Historical product information remains available.
    product = get_product(product_id, db_path)

    assert product["is_active"] == 0


def test_archive_product_with_stock_rejected(test_db):

    db_path, category_id = test_db

    product_id = create_product(
        "Keyboard",
        "KEY-001",
        category_id,
        100000,
        150000,
        10,
        2,
        db_path=db_path
    )

    with pytest.raises(ValueError, match="stock cannot be archived"):

        archive_product(
            product_id,
            db_path=db_path
        )