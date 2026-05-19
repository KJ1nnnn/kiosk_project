import sqlite3

import pytest

from database import init_db
from services import product_service


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    init_db(conn=connection, seed=False)
    connection.execute(
        """
        INSERT INTO products (name, category, price, stock, image, created_at)
        VALUES ('테스트 물품', '테스트', 1000, 10, '', '2026-05-11T00:00:00')
        """
    )
    connection.commit()
    yield connection
    connection.close()


def test_decrease_stock_when_stock_is_enough(conn):
    product = product_service.get_all_products(conn=conn)[0]

    success = product_service.decrease_stock(product["id"], 3, conn=conn)
    updated = product_service.get_product_by_id(product["id"], conn=conn)

    assert success is True
    assert updated["stock"] == 7


def test_decrease_stock_fails_when_quantity_is_too_large(conn):
    product = product_service.get_all_products(conn=conn)[0]

    success = product_service.decrease_stock(product["id"], 11, conn=conn)
    updated = product_service.get_product_by_id(product["id"], conn=conn)

    assert success is False
    assert updated["stock"] == 10


def test_is_sold_out_when_stock_is_zero(conn):
    product = product_service.get_all_products(conn=conn)[0]

    product_service.update_stock(product["id"], 0, conn=conn)

    assert product_service.is_sold_out(product["id"], conn=conn) is True


def test_update_product_can_mark_popular_item(conn):
    product = product_service.get_all_products(conn=conn)[0]

    success = product_service.update_product(
        product["id"], "테스트 물품", "테스트", 1000, 10, is_popular=True, conn=conn
    )
    updated = product_service.get_product_by_id(product["id"], conn=conn)

    assert success is True
    assert updated["is_popular"] == 1
