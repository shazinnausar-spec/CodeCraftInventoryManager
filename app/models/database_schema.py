# SQL commands used to create our application database.

SCHEMA = """

-- ==========================================
-- TABLE 1: CATEGORIES
-- ==========================================

CREATE TABLE IF NOT EXISTS categories (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL COLLATE NOCASE UNIQUE,

    description TEXT DEFAULT '',

    created_at TEXT NOT NULL

);


-- ==========================================
-- TABLE 2: PRODUCTS
-- ==========================================

CREATE TABLE IF NOT EXISTS products (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    sku TEXT NOT NULL COLLATE NOCASE UNIQUE,

    category_id INTEGER NOT NULL,

    purchase_price_cents INTEGER NOT NULL DEFAULT 0
        CHECK (purchase_price_cents >= 0),

    selling_price_cents INTEGER NOT NULL DEFAULT 0
        CHECK (selling_price_cents >= 0),

    quantity INTEGER NOT NULL DEFAULT 0
        CHECK (quantity >= 0),

    minimum_stock INTEGER NOT NULL DEFAULT 0
        CHECK (minimum_stock >= 0),

    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),

    created_at TEXT NOT NULL,

    updated_at TEXT NOT NULL,

    FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE RESTRICT

);


-- ==========================================
-- TABLE 3: STOCK MOVEMENTS
-- ==========================================

CREATE TABLE IF NOT EXISTS stock_movements (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    product_id INTEGER NOT NULL,

    movement_type TEXT NOT NULL
        CHECK (
            movement_type IN (
                'OPENING',
                'STOCK_IN',
                'STOCK_OUT'
            )
        ),

    quantity INTEGER NOT NULL
        CHECK (quantity > 0),

    stock_after INTEGER NOT NULL
        CHECK (stock_after >= 0),

    reason TEXT DEFAULT '',

    created_at TEXT NOT NULL,

    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE RESTRICT

);


-- ==========================================
-- TABLE 4: APPLICATION SETTINGS
-- ==========================================

CREATE TABLE IF NOT EXISTS app_settings (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    setting_key TEXT NOT NULL UNIQUE,

    setting_value TEXT NOT NULL DEFAULT ''

);


-- ==========================================
-- DATABASE INDEXES
-- ==========================================

CREATE INDEX IF NOT EXISTS idx_products_name
ON products(name COLLATE NOCASE);

CREATE INDEX IF NOT EXISTS idx_products_category
ON products(category_id);

CREATE INDEX IF NOT EXISTS idx_products_active
ON products(is_active);

CREATE INDEX IF NOT EXISTS idx_stock_product
ON stock_movements(product_id);

CREATE INDEX IF NOT EXISTS idx_stock_created
ON stock_movements(created_at);

"""