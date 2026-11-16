
import sqlite3

from app.config import DATABASE_PATH
from app.database import (
    database_transaction,
    get_connection,
    get_timestamp
)


def validate_stock_quantity(quantity):
    """
    Check that the stock quantity is a positive whole number.
    """

    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValueError("Quantity must be a whole number.")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")


def validate_stock_reason(reason):
    """
    Check the optional reason entered for a stock movement.
    """

    if not isinstance(reason, str):
        raise ValueError("Reason must be text.")

    if len(reason.strip()) > 500:
        raise ValueError("Reason cannot exceed 500 characters.")


def stock_in(product_id, quantity, reason="", db_path=DATABASE_PATH):
    """
    Add stock to an existing active product.

    The product quantity and movement history are updated
    together in one database transaction.
    """

    validate_stock_quantity(quantity)
    validate_stock_reason(reason)

    timestamp = get_timestamp()

    with database_transaction(db_path=db_path) as connection:

        # Find the product and its current stock.
        product = connection.execute(
            """
            SELECT id, quantity, is_active
            FROM products
            WHERE id = ?
            """,
            (product_id,)
        ).fetchone()

        if product is None:
            raise ValueError("Product not found.")

        if not product["is_active"]:
            raise ValueError("Cannot update stock of an archived product.")

        # Calculate the new stock quantity.
        new_quantity = product["quantity"] + quantity

        # Update the product's stock.
        connection.execute(
            """
            UPDATE products
            SET quantity = ?, updated_at = ?
            WHERE id = ?
            """,
            (new_quantity, timestamp, product_id)
        )

        # Record the stock movement.
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
                product_id,
                "STOCK_IN",
                quantity,
                new_quantity,
                reason.strip(),
                timestamp
            )
        )

        return new_quantity


def stock_out(product_id, quantity, reason="", db_path=DATABASE_PATH):
    """
    Remove stock from an existing active product.

    Stock cannot become negative.
    """

    validate_stock_quantity(quantity)
    validate_stock_reason(reason)

    timestamp = get_timestamp()

    with database_transaction(db_path=db_path) as connection:

        # Find the product and its current stock.
        product = connection.execute(
            """
            SELECT id, quantity, is_active
            FROM products
            WHERE id = ?
            """,
            (product_id,)
        ).fetchone()

        if product is None:
            raise ValueError("Product not found.")

        if not product["is_active"]:
            raise ValueError("Cannot update stock of an archived product.")

        # Check whether enough stock is available.
        if quantity > product["quantity"]:
            raise ValueError(
                f"Insufficient stock. Available quantity: "
                f"{product['quantity']}."
            )

        # Calculate the remaining stock.
        new_quantity = product["quantity"] - quantity

        # Update the product's stock.
        connection.execute(
            """
            UPDATE products
            SET quantity = ?, updated_at = ?
            WHERE id = ?
            """,
            (new_quantity, timestamp, product_id)
        )

        # Record the stock movement.
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
                product_id,
                "STOCK_OUT",
                quantity,
                new_quantity,
                reason.strip(),
                timestamp
            )
        )

        return new_quantity


def get_stock_movements(
    product_id=None,
    movement_type=None,
    limit=100,
    db_path=DATABASE_PATH
):
    """
    Retrieve stock movement history.

    Optional filters:
    - product_id: Show movements for one product.
    - movement_type: STOCK_IN, STOCK_OUT or OPENING.
    - limit: Maximum number of records.
    """

    if (
        isinstance(limit, bool)
        or not isinstance(limit, int)
        or limit <= 0
    ):
        raise ValueError("Limit must be a positive whole number.")

    if movement_type is not None:
        if movement_type not in ("OPENING", "STOCK_IN", "STOCK_OUT"):
            raise ValueError("Invalid stock movement type.")

    connection = get_connection(db_path)

    try:
        query = """
            SELECT
                stock_movements.*,
                products.name AS product_name,
                products.sku AS product_sku
            FROM stock_movements
            INNER JOIN products
                ON stock_movements.product_id = products.id
            WHERE 1 = 1
        """

        parameters = []

        if product_id is not None:
            query += " AND stock_movements.product_id = ?"
            parameters.append(product_id)

        if movement_type is not None:
            query += " AND stock_movements.movement_type = ?"
            parameters.append(movement_type)

        query += """
            ORDER BY stock_movements.id DESC
            LIMIT ?
        """

        parameters.append(limit)

        movements = connection.execute(
            query,
            parameters
        ).fetchall()

        return [dict(movement) for movement in movements]

    finally:
        connection.close()
