
from app.config import DATABASE_PATH
from app.database import get_connection


def get_dashboard_statistics(db_path=DATABASE_PATH):
    """
    Retrieve the main inventory statistics.

    Inventory value is calculated using purchase prices,
    not selling prices.
    """

    connection = get_connection(db_path)

    try:
        statistics = connection.execute(
            """
            SELECT
                COUNT(*) AS total_products,
                COALESCE(SUM(quantity), 0) AS total_stock,
                COALESCE(
                    SUM(purchase_price_cents * quantity),
                    0
                ) AS inventory_value,
                COALESCE(
                    SUM(
                        CASE
                            WHEN quantity > 0
                            AND quantity <= minimum_stock
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS low_stock_products,
                COALESCE(
                    SUM(
                        CASE
                            WHEN quantity = 0
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS out_of_stock_products
            FROM products
            WHERE is_active = 1
            """
        ).fetchone()

        return dict(statistics)

    finally:
        connection.close()


def get_low_stock_products(limit=10, db_path=DATABASE_PATH):
    """
    Retrieve active products that have reached
    or fallen below their minimum stock level.

    Products with zero stock are excluded because
    they are counted separately as out of stock.
    """

    if (
        isinstance(limit, bool)
        or not isinstance(limit, int)
        or limit <= 0
    ):
        raise ValueError("Limit must be a positive whole number.")

    connection = get_connection(db_path)

    try:
        products = connection.execute(
            """
            SELECT
                products.id,
                products.name,
                products.sku,
                products.quantity,
                products.minimum_stock,
                categories.name AS category_name
            FROM products
            INNER JOIN categories
                ON products.category_id = categories.id
            WHERE products.is_active = 1
                AND products.quantity > 0
                AND products.quantity <= products.minimum_stock
            ORDER BY products.quantity ASC, products.name COLLATE NOCASE
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        return [dict(product) for product in products]

    finally:
        connection.close()


def get_recent_stock_movements(limit=10, db_path=DATABASE_PATH):
    """
    Retrieve the latest stock movements
    for active products.
    """

    if (
        isinstance(limit, bool)
        or not isinstance(limit, int)
        or limit <= 0
    ):
        raise ValueError("Limit must be a positive whole number.")

    connection = get_connection(db_path)

    try:
        movements = connection.execute(
            """
            SELECT
                stock_movements.id,
                stock_movements.movement_type,
                stock_movements.quantity,
                stock_movements.stock_after,
                stock_movements.reason,
                stock_movements.created_at,
                products.name AS product_name,
                products.sku AS product_sku
            FROM stock_movements
            INNER JOIN products
                ON stock_movements.product_id = products.id
            WHERE products.is_active = 1
            ORDER BY stock_movements.id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        return [dict(movement) for movement in movements]

    finally:
        connection.close()
