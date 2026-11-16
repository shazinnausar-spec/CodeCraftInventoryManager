# ==========================================
# CODECRAFT INVENTORY MANAGER
# PRODUCT SERVICE
# ==========================================

# Import SQLite.
import sqlite3

# Import database functions.
from app.config import DATABASE_PATH

from app.database import (
    database_transaction,
    get_connection,
    get_timestamp
)

def validate_product_data(
    name,
    sku,
    category_id,
    purchase_price_cents,
    selling_price_cents,
    quantity,
    minimum_stock
):
    """
    Validate product information before saving.
    """

    # Check product name.
    if not isinstance(name, str) or not name.strip():

        raise ValueError("Product name is required.")

    if len(name.strip()) > 150:

        raise ValueError("Product name cannot exceed 150 characters.")

    # Check SKU.
    if not isinstance(sku, str) or not sku.strip():

        raise ValueError("Product SKU is required.")

    if len(sku.strip()) > 50:

        raise ValueError("SKU cannot exceed 50 characters.")

    # Check category ID.
    if (
        isinstance(category_id, bool)
        or not isinstance(category_id, int)
        or category_id <= 0
    ):

        raise ValueError("Please select a valid category.")

    # Validate prices and quantities.
    numeric_fields = {

        "Purchase price": purchase_price_cents,
        "Selling price": selling_price_cents,
        "Quantity": quantity,
        "Minimum stock": minimum_stock

    }

    for field_name, value in numeric_fields.items():

        # Reject booleans and non-integer values.
        if isinstance(value, bool) or not isinstance(value, int):

            raise ValueError(
                f"{field_name} must be a whole number."
            )

        if value < 0:

            raise ValueError(
                f"{field_name} cannot be negative."
            )


def create_product(
    name,
    sku,
    category_id,
    purchase_price_cents,
    selling_price_cents,
    quantity,
    minimum_stock,
    db_path=DATABASE_PATH
):
    """
    Create a new product.

    If opening stock is provided, record an OPENING movement.

    Returns the new product ID.
    """

    # Validate all product information.
    validate_product_data(
        name,
        sku,
        category_id,
        purchase_price_cents,
        selling_price_cents,
        quantity,
        minimum_stock
    )

    # Clean user input.
    name = name.strip()
    sku = sku.strip().upper()

    # Get the current timestamp.
    timestamp = get_timestamp()

    try:

        # Begin a database transaction.
        with database_transaction(
            db_path=db_path
        ) as connection:

            # Insert the product.
            cursor = connection.execute(
                """
                INSERT INTO products (

                    name,
                    sku,
                    category_id,
                    purchase_price_cents,
                    selling_price_cents,
                    quantity,
                    minimum_stock,
                    created_at,
                    updated_at

                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    sku,
                    category_id,
                    purchase_price_cents,
                    selling_price_cents,
                    quantity,
                    minimum_stock,
                    timestamp,
                    timestamp
                )
            )

            # Get the newly generated product ID.
            product_id = cursor.lastrowid

            # Record opening stock if quantity is greater than zero.
            if quantity > 0:

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
                        "OPENING",
                        quantity,
                        quantity,
                        "Initial product stock",
                        timestamp
                    )
                )

            return product_id

    except sqlite3.IntegrityError as error:

        # Handle duplicate SKU.
        if "products.sku" in str(error):

            raise ValueError(
                "This SKU already exists. Please use a different SKU."
            ) from error

        # Handle invalid category.
        if "FOREIGN KEY" in str(error):

            raise ValueError(
                "The selected category does not exist."
            ) from error

        raise


def get_product(product_id, db_path=DATABASE_PATH):
    """
    Retrieve one product using its ID.
    """

    connection = get_connection(db_path or None) if db_path else get_connection()

    try:

        product = connection.execute(
            """
            SELECT
                products.*,
                categories.name AS category_name

            FROM products

            INNER JOIN categories
                ON products.category_id = categories.id

            WHERE products.id = ?
            """,
            (product_id,)
        ).fetchone()

        if product is None:

            return None

        return dict(product)

    finally:

        connection.close()


def get_all_products(
    search="",
    category_id=None,
    include_archived=False,
    db_path=DATABASE_PATH
):
    """
    Retrieve products with optional search and category filters.
    """

    connection = get_connection(db_path) if db_path else get_connection()

    try:

        # Base query.
        query = """
            SELECT
                products.*,
                categories.name AS category_name

            FROM products

            INNER JOIN categories
                ON products.category_id = categories.id

            WHERE 1 = 1
        """

        # Store SQL parameters.
        parameters = []

        # Hide archived products by default.
        if not include_archived:

            query += " AND products.is_active = 1"

        # Apply search filter.
        if search.strip():

            query += """
                AND (
                    products.name LIKE ?
                    OR products.sku LIKE ?
                )
            """

            search_value = f"%{search.strip()}%"

            parameters.extend([
                search_value,
                search_value
            ])

        # Apply category filter.
        if category_id is not None:

            query += " AND products.category_id = ?"

            parameters.append(category_id)

        # Sort alphabetically.
        query += " ORDER BY products.name COLLATE NOCASE"

        # Execute parameterized query.
        products = connection.execute(
            query,
            parameters
        ).fetchall()

        return [dict(product) for product in products]

    finally:

        connection.close()


def update_product(
    product_id,
    name,
    sku,
    category_id,
    purchase_price_cents,
    selling_price_cents,
    minimum_stock,
    db_path=DATABASE_PATH
):
    """
    Update product details.

    Quantity is intentionally excluded.
    """

    # Validate product information.
    validate_product_data(
        name,
        sku,
        category_id,
        purchase_price_cents,
        selling_price_cents,
        0,
        minimum_stock
    )

    timestamp = get_timestamp()

    try:

        with database_transaction(
            db_path=db_path
        ) as connection:

            cursor = connection.execute(
                """
                UPDATE products

                SET
                    name = ?,
                    sku = ?,
                    category_id = ?,
                    purchase_price_cents = ?,
                    selling_price_cents = ?,
                    minimum_stock = ?,
                    updated_at = ?

                WHERE id = ?
                AND is_active = 1
                """,
                (
                    name.strip(),
                    sku.strip().upper(),
                    category_id,
                    purchase_price_cents,
                    selling_price_cents,
                    minimum_stock,
                    timestamp,
                    product_id
                )
            )

            if cursor.rowcount == 0:

                raise ValueError(
                    "Product not found or already archived."
                )

    except sqlite3.IntegrityError as error:

        if "products.sku" in str(error):

            raise ValueError(
                "This SKU already exists."
            ) from error

        if "FOREIGN KEY" in str(error):

            raise ValueError(
                "The selected category does not exist."
            ) from error

        raise


def archive_product(product_id, db_path=DATABASE_PATH):
    """
    Archive a product instead of permanently deleting it.

    Products with remaining stock cannot be archived.
    """

    timestamp = get_timestamp()

    with database_transaction(
        db_path=db_path
    ) as connection:

        # Find the product.
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

            raise ValueError("Product is already archived.")

        if product["quantity"] > 0:

            raise ValueError(
                "Products with available stock cannot be archived. "
                "Please adjust the stock to zero first."
            )

        # Archive the product.
        connection.execute(
            """
            UPDATE products

            SET
                is_active = 0,
                updated_at = ?

            WHERE id = ?
            """,
            (
                timestamp,
                product_id
            )
        )