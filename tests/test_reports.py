
import csv

import pytest

from app.database import initialize_database, database_transaction
from app.services.reports_service import (
    get_inventory_report,
    get_low_stock_report,
    get_stock_movement_report,
    export_report_to_csv
)


@pytest.fixture
def report_db(tmp_path):

    db_path = tmp_path / "reports_test.db"

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
            ("Electronics", "Test category", "2026-01-01")
        )

        category_id = connection.execute(
            "SELECT id FROM categories WHERE name = ?",
            ("Electronics",)
        ).fetchone()["id"]

        connection.execute(
            """
            INSERT INTO products (
                name,
                sku,
                category_id,
                purchase_price_cents,
                selling_price_cents,
                quantity,
                minimum_stock,
                is_active,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "Keyboard",
                "KEY-001",
                category_id,
                500000,
                750000,
                3,
                5,
                1,
                "2026-01-01",
                "2026-01-01"
            )
        )

        connection.execute(
            """
            INSERT INTO products (
                name,
                sku,
                category_id,
                purchase_price_cents,
                selling_price_cents,
                quantity,
                minimum_stock,
                is_active,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "Mouse",
                "MOU-001",
                category_id,
                200000,
                300000,
                0,
                5,
                1,
                "2026-01-01",
                "2026-01-01"
            )
        )

        connection.execute(
            """
            INSERT INTO products (
                name,
                sku,
                category_id,
                purchase_price_cents,
                selling_price_cents,
                quantity,
                minimum_stock,
                is_active,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "Monitor",
                "MON-001",
                category_id,
                2000000,
                2500000,
                20,
                5,
                0,
                "2026-01-01",
                "2026-01-01"
            )
        )

        keyboard_id = connection.execute(
            "SELECT id FROM products WHERE sku = ?",
            ("KEY-001",)
        ).fetchone()["id"]

        connection.execute(
            """
            INSERT INTO stock_movements (
                product_id,
                movement_type,
                quantity,
                stock_after,
                reason,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                keyboard_id,
                "STOCK_IN",
                3,
                3,
                "Test stock entry",
                "2026-01-01T10:00:00"
            )
        )

    return db_path


def test_inventory_report(report_db):

    products = get_inventory_report(report_db)

    assert len(products) == 2

    keyboard = next(
        product for product in products
        if product["sku"] == "KEY-001"
    )

    assert keyboard["quantity"] == 3
    assert keyboard["inventory_value_cents"] == 1500000
    assert keyboard["status"] == "Low Stock"


def test_inventory_report_excludes_archived_products(report_db):

    products = get_inventory_report(report_db)

    skus = [product["sku"] for product in products]

    assert "MON-001" not in skus


def test_low_stock_report(report_db):

    products = get_low_stock_report(report_db)

    skus = [product["sku"] for product in products]

    assert "KEY-001" in skus
    assert "MOU-001" in skus
    assert "MON-001" not in skus


def test_low_stock_report_includes_zero_stock(report_db):

    products = get_low_stock_report(report_db)

    mouse = next(
        product for product in products
        if product["sku"] == "MOU-001"
    )

    assert mouse["quantity"] == 0


def test_stock_movement_report(report_db):

    movements = get_stock_movement_report(
        db_path=report_db
    )

    assert len(movements) == 1
    assert movements[0]["product_name"] == "Keyboard"
    assert movements[0]["movement_type"] == "STOCK_IN"


def test_stock_movement_report_limit(report_db):

    movements = get_stock_movement_report(
        limit=1,
        db_path=report_db
    )

    assert len(movements) == 1


@pytest.mark.parametrize(
    "limit",
    [0, -1, 1.5, True]
)
def test_invalid_movement_report_limit_rejected(
    report_db,
    limit
):

    with pytest.raises(ValueError):

        get_stock_movement_report(
            limit=limit,
            db_path=report_db
        )


def test_export_inventory_csv(tmp_path):

    rows = [
        {
            "name": "Keyboard",
            "sku": "KEY-001",
            "category_name": "Electronics",
            "purchase_price_cents": 500000,
            "selling_price_cents": 750000,
            "quantity": 3,
            "minimum_stock": 5,
            "inventory_value_cents": 1500000,
            "status": "Low Stock"
        }
    ]

    file_path = export_report_to_csv(
        "inventory",
        rows,
        tmp_path
    )

    assert file_path.exists()
    assert file_path.suffix == ".csv"

    with file_path.open(
        encoding="utf-8-sig",
        newline=""
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        data = list(reader)

    assert len(data) == 1
    assert data[0]["Product"] == "Keyboard"
    assert data[0]["SKU"] == "KEY-001"


def test_export_empty_report(tmp_path):

    file_path = export_report_to_csv(
        "inventory",
        [],
        tmp_path
    )

    assert file_path.exists()

    with file_path.open(
        encoding="utf-8-sig",
        newline=""
    ) as csv_file:

        reader = csv.reader(csv_file)

        headings = next(reader)

    assert "Product" in headings
    assert "SKU" in headings


def test_unsupported_report_export_rejected(tmp_path):

    with pytest.raises(ValueError):

        export_report_to_csv(
            "unknown_report",
            [],
            tmp_path
        )
