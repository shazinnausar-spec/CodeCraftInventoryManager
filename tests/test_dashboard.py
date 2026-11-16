
import pytest

from app.database import initialize_database
from app.services.category_service import create_category
from app.services.product_service import (
    create_product,
    archive_product
)
from app.services.stock_service import stock_in, stock_out
from app.services.dashboard_service import (
    get_dashboard_statistics,
    get_low_stock_products,
    get_recent_stock_movements
)


@pytest.fixture
def dashboard_database(tmp_path):

    db_path = tmp_path / "dashboard_test.db"

    initialize_database(db_path)

    category_id = create_category(
        "Electronics",
        db_path=db_path
    )

    return db_path, category_id


def test_dashboard_statistics(dashboard_database):

    db_path, category_id = dashboard_database

    create_product(
        "Keyboard", "KEY-001", category_id,
        10000, 15000, 10, 2,
        db_path
    )

    create_product(
        "Mouse", "MOU-001", category_id,
        5000, 8000, 2, 5,
        db_path
    )

    create_product(
        "Monitor", "MON-001", category_id,
        50000, 65000, 0, 3,
        db_path
    )

    statistics = get_dashboard_statistics(db_path)

    assert statistics["total_products"] == 3
    assert statistics["total_stock"] == 12
    assert statistics["low_stock_products"] == 1
    assert statistics["out_of_stock_products"] == 1

    # (10000 * 10) + (5000 * 2) = 110000 cents.
    assert statistics["inventory_value"] == 110000


def test_archived_products_excluded_from_statistics(
    dashboard_database
):

    db_path, category_id = dashboard_database

    product_id = create_product(
        "Keyboard", "KEY-001", category_id,
        10000, 15000, 0, 2,
        db_path
    )

    archive_product(product_id, db_path)

    statistics = get_dashboard_statistics(db_path)

    assert statistics["total_products"] == 0
    assert statistics["total_stock"] == 0
    assert statistics["inventory_value"] == 0


def test_low_stock_products(dashboard_database):

    db_path, category_id = dashboard_database

    create_product(
        "Keyboard", "KEY-001", category_id,
        10000, 15000, 2, 5,
        db_path
    )

    create_product(
        "Mouse", "MOU-001", category_id,
        5000, 8000, 10, 2,
        db_path
    )

    create_product(
        "Monitor", "MON-001", category_id,
        50000, 65000, 0, 3,
        db_path
    )

    products = get_low_stock_products(db_path=db_path)

    assert len(products) == 1
    assert products[0]["name"] == "Keyboard"


def test_recent_stock_movements(dashboard_database):

    db_path, category_id = dashboard_database

    product_id = create_product(
        "Keyboard", "KEY-001", category_id,
        10000, 15000, 10, 2,
        db_path
    )

    stock_in(product_id, 5, "New shipment", db_path)
    stock_out(product_id, 2, "Damaged items", db_path)

    movements = get_recent_stock_movements(db_path=db_path)

    assert len(movements) == 3
    assert movements[0]["movement_type"] == "STOCK_OUT"
    assert movements[1]["movement_type"] == "STOCK_IN"
    assert movements[2]["movement_type"] == "OPENING"


@pytest.mark.parametrize("limit", [0, -1, 1.5, True])
def test_invalid_dashboard_limits_rejected(
    dashboard_database,
    limit
):

    db_path, category_id = dashboard_database

    with pytest.raises(ValueError):
        get_low_stock_products(limit, db_path)

    with pytest.raises(ValueError):
        get_recent_stock_movements(limit, db_path)
