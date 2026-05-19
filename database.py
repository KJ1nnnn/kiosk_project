from datetime import datetime
from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "kiosk.db"

MONEY_UNITS = [50000, 10000, 5000, 1000, 500, 100, 50, 10]

DEFAULT_CASH_BOX = {
    50000: 2,
    10000: 8,
    5000: 10,
    1000: 30,
    500: 40,
    100: 80,
    50: 50,
    10: 100,
}

DEFAULT_PRODUCTS = [
    {
        "name": "무선 마우스",
        "category": "대여",
        "price": 5000,
        "stock": 8,
        "item_type": "rental",
        "image": "",
    },
    {
        "name": "무선 키보드",
        "category": "대여",
        "price": 7000,
        "stock": 6,
        "item_type": "rental",
        "image": "",
    },
    {
        "name": "독서대",
        "category": "대여",
        "price": 3000,
        "stock": 10,
        "item_type": "rental",
        "image": "",
    },
    {
        "name": "담요",
        "category": "대여",
        "price": 4000,
        "stock": 12,
        "item_type": "rental",
        "image": "",
    },
    {
        "name": "일회용 칫솔 세트",
        "category": "구매",
        "price": 1200,
        "stock": 30,
        "item_type": "purchase",
        "image": "",
    },
    {
        "name": "필기구 세트",
        "category": "구매",
        "price": 2500,
        "stock": 25,
        "item_type": "purchase",
        "image": "",
    },
]


def get_db_connection(db_path=None):
    """SQLite 연결을 생성한다."""
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=None, conn=None, seed=True):
    """테이블을 만들고 필요하면 기본 물품과 현금 보유량을 넣는다."""
    owns_connection = conn is None
    conn = conn or get_db_connection(db_path)

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price INTEGER NOT NULL,
            stock INTEGER NOT NULL,
            image TEXT,
            item_type TEXT NOT NULL DEFAULT 'purchase',
            is_popular INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_price INTEGER NOT NULL,
            payment_type TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        );

        CREATE TABLE IF NOT EXISTS cash_box (
            money_unit INTEGER PRIMARY KEY,
            count INTEGER NOT NULL
        );
        """
    )
    ensure_schema_migrations(conn)

    if seed:
        seed_database(conn)

    conn.commit()

    if owns_connection:
        conn.close()


def ensure_schema_migrations(conn):
    product_columns = {
        row["name"] if isinstance(row, sqlite3.Row) else row[1]
        for row in conn.execute("PRAGMA table_info(products)").fetchall()
    }

    if "is_popular" not in product_columns:
        conn.execute(
            "ALTER TABLE products ADD COLUMN is_popular INTEGER NOT NULL DEFAULT 0"
        )
    if "item_type" not in product_columns:
        conn.execute(
            "ALTER TABLE products ADD COLUMN item_type TEXT NOT NULL DEFAULT 'purchase'"
        )
    if "is_active" not in product_columns:
        conn.execute(
            "ALTER TABLE products ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1"
        )


def seed_database(conn):
    now = datetime.now().isoformat(timespec="seconds")
    sync_default_products(conn, now)

    cash_count = conn.execute("SELECT COUNT(*) FROM cash_box").fetchone()[0]
    if cash_count == 0:
        conn.executemany(
            "INSERT INTO cash_box (money_unit, count) VALUES (?, ?)",
            DEFAULT_CASH_BOX.items(),
        )


def sync_default_products(conn, now):
    default_names = [product["name"] for product in DEFAULT_PRODUCTS]
    placeholders = ",".join("?" for _ in default_names)

    conn.execute(
        f"UPDATE products SET is_active = 0 WHERE name NOT IN ({placeholders})",
        default_names,
    )

    for product in DEFAULT_PRODUCTS:
        row = conn.execute(
            "SELECT id FROM products WHERE name = ?", (product["name"],)
        ).fetchone()
        if row is None:
            conn.execute(
                """
                INSERT INTO products
                    (name, category, price, stock, image, item_type, is_popular,
                     is_active, created_at)
                VALUES
                    (:name, :category, :price, :stock, :image, :item_type,
                     :is_popular, 1, :created_at)
                """,
                {**product, "is_popular": 0, "created_at": now},
            )
        else:
            conn.execute(
                """
                UPDATE products
                SET category = ?, price = ?, image = ?, item_type = ?, is_active = 1
                WHERE id = ?
                """,
                (
                    product["category"],
                    product["price"],
                    product["image"],
                    product["item_type"],
                    row["id"],
                ),
            )
