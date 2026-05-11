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
        "name": "아이스 아메리카노",
        "category": "음료",
        "price": 1800,
        "stock": 12,
        "image": "",
    },
    {
        "name": "딸기 우유",
        "category": "음료",
        "price": 1500,
        "stock": 10,
        "image": "",
    },
    {
        "name": "생수",
        "category": "음료",
        "price": 900,
        "stock": 20,
        "image": "",
    },
    {
        "name": "삼각김밥",
        "category": "간식",
        "price": 1700,
        "stock": 8,
        "image": "",
    },
    {
        "name": "햄치즈 샌드위치",
        "category": "식사",
        "price": 3200,
        "stock": 6,
        "image": "",
    },
    {
        "name": "컵라면",
        "category": "식사",
        "price": 2500,
        "stock": 9,
        "image": "",
    },
    {
        "name": "초코바",
        "category": "간식",
        "price": 1200,
        "stock": 15,
        "image": "",
    },
    {
        "name": "핫도그",
        "category": "간식",
        "price": 2800,
        "stock": 5,
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
    """테이블을 만들고 필요하면 기본 상품과 현금 보유량을 넣는다."""
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
            is_popular INTEGER NOT NULL DEFAULT 0,
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


def seed_database(conn):
    product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    now = datetime.now().isoformat(timespec="seconds")

    if product_count == 0:
        conn.executemany(
            """
            INSERT INTO products
                (name, category, price, stock, image, is_popular, created_at)
            VALUES
                (:name, :category, :price, :stock, :image, :is_popular, :created_at)
            """,
            [
                {**product, "is_popular": 0, "created_at": now}
                for product in DEFAULT_PRODUCTS
            ],
        )

    cash_count = conn.execute("SELECT COUNT(*) FROM cash_box").fetchone()[0]
    if cash_count == 0:
        conn.executemany(
            "INSERT INTO cash_box (money_unit, count) VALUES (?, ?)",
            DEFAULT_CASH_BOX.items(),
        )
