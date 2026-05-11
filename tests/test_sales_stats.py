import sqlite3

import pytest

from database import init_db
from services import order_service, product_service


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    init_db(conn=connection, seed=False)
    connection.executemany(
        """
        INSERT INTO products
            (name, category, price, stock, image, is_popular, created_at)
        VALUES (?, ?, ?, ?, '', ?, '2026-05-11T00:00:00')
        """,
        [
            ("생수", "음료", 900, 20, 1),
            ("컵라면", "식사", 2500, 10, 0),
        ],
    )
    connection.commit()
    yield connection
    connection.close()


def test_order_count_by_hour(conn):
    products = product_service.get_all_products(conn=conn)
    order_service.create_order(
        [{"product_id": products[0]["id"], "quantity": 1, "price": 900}],
        "card",
        900,
        conn=conn,
    )
    conn.execute(
        "UPDATE orders SET created_at = '2026-05-11T09:15:00' WHERE id = 1"
    )
    order_service.create_order(
        [{"product_id": products[1]["id"], "quantity": 1, "price": 2500}],
        "cash",
        2500,
        conn=conn,
    )
    conn.execute(
        "UPDATE orders SET created_at = '2026-05-11T09:30:00' WHERE id = 2"
    )
    conn.commit()

    stats = order_service.get_order_count_by_hour(conn=conn)

    assert stats == [{"hour": "09", "order_count": 2}]


def test_product_sales_stats_orders_by_quantity(conn):
    products = product_service.get_all_products(conn=conn)
    order_service.create_order(
        [
            {"product_id": products[0]["id"], "quantity": 1, "price": 900},
            {"product_id": products[1]["id"], "quantity": 3, "price": 2500},
        ],
        "card",
        8400,
        conn=conn,
    )

    stats = order_service.get_product_sales_stats(conn=conn)

    assert stats[0]["name"] == "컵라면"
    assert stats[0]["sold_quantity"] == 3
    assert stats[1]["name"] == "생수"
    assert stats[1]["is_popular"] == 1
