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
            (name, category, price, stock, image, item_type, is_popular, created_at)
        VALUES (?, ?, ?, ?, '', ?, ?, '2026-05-11T00:00:00')
        """,
        [
            ("무선 마우스", "대여", 5000, 20, "rental", 1),
            ("필기구 세트", "구매", 2500, 10, "purchase", 0),
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
    products = {
        product["name"]: product
        for product in product_service.get_all_products(conn=conn)
    }
    order_service.create_order(
        [
            {
                "product_id": products["무선 마우스"]["id"],
                "quantity": 1,
                "price": 5000,
            },
            {
                "product_id": products["필기구 세트"]["id"],
                "quantity": 3,
                "price": 2500,
            },
        ],
        "card",
        12500,
        conn=conn,
    )

    stats = order_service.get_product_sales_stats(conn=conn)

    assert stats[0]["name"] == "필기구 세트"
    assert stats[0]["sold_quantity"] == 3
    assert stats[1]["name"] == "무선 마우스"
    assert stats[1]["is_popular"] == 1
