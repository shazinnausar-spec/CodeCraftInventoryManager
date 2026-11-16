
import csv
from datetime import datetime
from pathlib import Path

from app.config import DATABASE_PATH, EXPORT_DIR
from app.database import get_connection


# --------------------------------------------------
# INVENTORY REPORT
# --------------------------------------------------

def get_inventory_report(db_path=DATABASE_PATH):
    """
    Retrieve all active products with their inventory values.

    Inventory value is calculated using purchase prices.
    """

    connection = get_connection(db_path)

    try:
        products = connection.execute(
            """
            SELECT
                products.id,
                products.name,
                products.sku,
                categories.name AS category_name,
                products.purchase_price_cents,
                products.selling_price_cents,
                products.quantity,
                products.minimum_stock,
                (
                    products.purchase_price_cents
                    * products.quantity
                ) AS inventory_value_cents
            FROM products
            INNER JOIN categories
                ON products.category_id = categories.id
            WHERE products.is_active = 1
            ORDER BY products.name COLLATE NOCASE
            """
        ).fetchall()

        report = []

        for product in products:

            product = dict(product)

            if product["quantity"] == 0:
                status = "Out of Stock"

            elif product["quantity"] <= product["minimum_stock"]:
                status = "Low Stock"

            else:
                status = "In Stock"

            product["status"] = status

            report.append(product)

        return report

    finally:
        connection.close()


# --------------------------------------------------
# LOW STOCK REPORT
# --------------------------------------------------

def get_low_stock_report(db_path=DATABASE_PATH):
    """
    Retrieve active products at or below their minimum
    stock level, including products with zero stock.
    """

    connection = get_connection(db_path)

    try:
        products = connection.execute(
            """
            SELECT
                products.id,
                products.name,
                products.sku,
                categories.name AS category_name,
                products.quantity,
                products.minimum_stock,
                products.purchase_price_cents,
                products.selling_price_cents
            FROM products
            INNER JOIN categories
                ON products.category_id = categories.id
            WHERE products.is_active = 1
                AND products.quantity <= products.minimum_stock
            ORDER BY
                products.quantity ASC,
                products.name COLLATE NOCASE
            """
        ).fetchall()

        return [dict(product) for product in products]

    finally:
        connection.close()


# --------------------------------------------------
# STOCK MOVEMENT REPORT
# --------------------------------------------------

def get_stock_movement_report(
    limit=10000,
    db_path=DATABASE_PATH
):
    """
    Retrieve stock movement records with product details.
    """

    if (
        isinstance(limit, bool)
        or not isinstance(limit, int)
        or limit <= 0
    ):
        raise ValueError(
            "Limit must be a positive whole number."
        )

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
            ORDER BY stock_movements.id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        return [dict(movement) for movement in movements]

    finally:
        connection.close()


# --------------------------------------------------
# CSV EXPORT
# --------------------------------------------------

REPORT_COLUMNS = {

    "inventory": [
        ("Product", "name"),
        ("SKU", "sku"),
        ("Category", "category_name"),
        ("Purchase Price (Cents)", "purchase_price_cents"),
        ("Selling Price (Cents)", "selling_price_cents"),
        ("Quantity", "quantity"),
        ("Minimum Stock", "minimum_stock"),
        ("Inventory Value (Cents)", "inventory_value_cents"),
        ("Status", "status"),
    ],

    "low_stock": [
        ("Product", "name"),
        ("SKU", "sku"),
        ("Category", "category_name"),
        ("Current Stock", "quantity"),
        ("Minimum Stock", "minimum_stock"),
        ("Purchase Price (Cents)", "purchase_price_cents"),
        ("Selling Price (Cents)", "selling_price_cents"),
    ],

    "stock_movements": [
        ("Date", "created_at"),
        ("Product", "product_name"),
        ("SKU", "product_sku"),
        ("Movement Type", "movement_type"),
        ("Quantity", "quantity"),
        ("Stock After", "stock_after"),
        ("Reason", "reason"),
    ],

}


def export_report_to_csv(
    report_type,
    rows,
    export_dir=EXPORT_DIR
):
    """
    Export a supported report to a CSV file.

    The file uses UTF-8 with BOM for better compatibility
    with Microsoft Excel.
    """

    if report_type not in REPORT_COLUMNS:
        raise ValueError("Unsupported report type.")

    if not isinstance(rows, (list, tuple)):
        raise ValueError("Report rows must be a list or tuple.")

    export_path = Path(export_dir)

    export_path.mkdir(
        parents=True,
        exist_ok=True
    )

    # Generate a unique filename.
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    filename = f"{report_type}_{timestamp}.csv"

    file_path = export_path / filename

    columns = REPORT_COLUMNS[report_type]

    # Create the CSV file.
    with file_path.open(
        mode="w",
        newline="",
        encoding="utf-8-sig"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                header for header, key in columns
            ],
            extrasaction="ignore"
        )

        # Write column headings.
        writer.writeheader()

        # Write report records.
        for row in rows:

            writer.writerow({
                header: row.get(key, "")
                for header, key in columns
            })

    return file_path
