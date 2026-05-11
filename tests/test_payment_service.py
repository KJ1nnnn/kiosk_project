import sqlite3

import pytest

from database import MONEY_UNITS, init_db
from services import payment_service
from services.change_service import get_cash_box


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    init_db(conn=connection, seed=False)
    for money in MONEY_UNITS:
        connection.execute(
            "INSERT INTO cash_box (money_unit, count) VALUES (?, ?)", (money, 0)
        )
    connection.commit()
    yield connection
    connection.close()


def set_cash_box(conn, cash_box):
    for money, count in cash_box.items():
        conn.execute(
            "UPDATE cash_box SET count = ? WHERE money_unit = ?", (count, money)
        )
    conn.commit()


def test_card_payment_success():
    result = payment_service.process_card_payment(6300)

    assert result["success"] is True
    assert result["payment_type"] == "card"


def test_cash_payment_success_updates_cash_box(conn):
    set_cash_box(conn, {1000: 5, 500: 2, 100: 10})

    result = payment_service.process_cash_payment(6300, 10000, conn=conn)
    cash_box = get_cash_box(conn=conn)

    assert result["success"] is True
    assert result["change_amount"] == 3700
    assert result["change_result"] == {1000: 3, 500: 1, 100: 2}
    assert cash_box[10000] == 1
    assert cash_box[1000] == 2
    assert cash_box[500] == 1
    assert cash_box[100] == 8


def test_cash_payment_fails_when_inserted_cash_is_not_enough(conn):
    set_cash_box(conn, {1000: 5, 500: 2, 100: 10})

    result = payment_service.process_cash_payment(6300, 5000, conn=conn)
    cash_box = get_cash_box(conn=conn)

    assert result["success"] is False
    assert result["message"] == "투입 금액이 부족합니다."
    assert cash_box[5000] == 0


def test_cash_payment_fails_when_change_is_not_available(conn):
    set_cash_box(conn, {1000: 1, 500: 0, 100: 1, 50: 0, 10: 0})

    result = payment_service.process_cash_payment(6300, 10000, conn=conn)
    cash_box = get_cash_box(conn=conn)

    assert result["success"] is False
    assert result["message"] == "키오스크에 거스름돈이 부족합니다."
    assert cash_box[10000] == 0
