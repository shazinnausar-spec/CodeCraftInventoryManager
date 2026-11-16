
import pytest

from app.database import initialize_database
from app.services.category_service import create_category
from app.services.product_service import (
    create_product,
    get_product,
    archive_product
)
from app.services.stock_service import (
    stock_in,
    stock_out,
    get_stock_movements
)


@pytest.fixture
def stock_database(tmp_path):
    """
    Create a separate temporary database for each test.
    """

    db_path = tmp_path / "stock_test.db"

    initialize_database(db_path)

    category_id = create_category(
        "Electronics",
        db_path=db_path
    )

    product_id = create_product(
        name="Keyboard",
        sku="KEY-001",
        category_id=category_id,
        purchase_price_cents=100000,
        selling_price_cents=150000,
        quantity=10,
        minimum_stock=2,
        db_path=db_path
    )

    return db_path, product_id


def test_stock_in_increases_quantity(stock_database):
    db_path, product_id = stock_database

    new_quantity = stock_in(
        product_id,
        5,
        "New shipment",
        db_path
    )

    product = get_product(product_id, db_path)

    assert new_quantity == 15
    assert product["quantity"] == 15


def test_stock_in_records_movement(stock_database):
    db_path, product_id = stock_database

    stock_in(product_id, 5, "New shipment", db_path)

    movements = get_stock_movements(
        product_id=product_id,
        movement_type="STOCK_IN",
        db_path=db_path
    )

    assert len(movements) == 1
    assert movements[0]["quantity"] == 5
    assert movements[0]["stock_after"] == 15
    assert movements[0]["reason"] == "New shipment"


def test_stock_out_decreases_quantity(stock_database):
    db_path, product_id = stock_database

    new_quantity = stock_out(
        product_id,
        4,
        "Damaged items",
        db_path
    )

    product = get_product(product_id, db_path)

    assert new_quantity == 6
    assert product["quantity"] == 6


def test_stock_out_records_movement(stock_database):
    db_path, product_id = stock_database

    stock_out(product_id, 4, "Damaged items", db_path)

    movements = get_stock_movements(
        product_id=product_id,
        movement_type="STOCK_OUT",
        db_path=db_path
    )

    assert len(movements) == 1
    assert movements[0]["quantity"] == 4
    assert movements[0]["stock_after"] == 6


def test_stock_out_cannot_make_quantity_negative(stock_database):
    db_path, product_id = stock_database

    with pytest.raises(ValueError, match="Insufficient stock"):
        stock_out(product_id, 20, "Too many items", db_path)

    product = get_product(product_id, db_path)

    assert product["quantity"] == 10

    movements = get_stock_movements(
        product_id=product_id,
        movement_type="STOCK_OUT",
        db_path=db_path
    )

    assert len(movements) == 0


@pytest.mark.parametrize("quantity", [0, -1, 1.5, True, "5"])
def test_invalid_stock_quantity_rejected(stock_database, quantity):
    db_path, product_id = stock_database

    with pytest.raises(ValueError):
        stock_in(product_id, quantity, db_path=db_path)


def test_archived_product_stock_cannot_be_changed(stock_database):
    db_path = stock_database[0]

    category_id = create_category(
        "Accessories",
        db_path=db_path
    )

    product_id = create_product(
        "Mouse",
        "MOU-001",
        category_id,
        50000,
        75000,
        0,
        2,
        db_path
    )

    archive_product(product_id, db_path)

    with pytest.raises(ValueError, match="archived"):
        stock_in(product_id, 5, db_path=db_path)


def test_stock_history_returns_latest_movements_first(stock_database):
    db_path, product_id = stock_database

    stock_in(product_id, 5, "First shipment", db_path)
    stock_out(product_id, 2, "First sale", db_path)

    movements = get_stock_movements(
        product_id=product_id,
        db_path=db_path
    )

    assert movements[0]["movement_type"] == "STOCK_OUT"
    assert movements[1]["movement_type"] == "STOCK_IN"
    assert movements[2]["movement_type"] == "OPENING"


def test_stock_history_limit(stock_database):
    db_path, product_id = stock_database

    stock_in(product_id, 5, "First shipment", db_path)
    stock_out(product_id, 2, "First sale", db_path)

    movements = get_stock_movements(
        product_id=product_id,
        limit=2,
        db_path=db_path
    )

    assert len(movements) == 2
