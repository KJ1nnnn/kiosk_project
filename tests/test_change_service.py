import sqlite3

import pytest

from database import MONEY_UNITS, init_db
from services.change_service import (
    calculate_change,
    can_give_change,
    get_cash_box,
    update_cash_box_counts,
)


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


def test_calculate_change_with_enough_cash():
    cash_box = {
        1000: 5,
        500: 2,
        100: 10,
    }

    result = calculate_change(3700, cash_box)

    assert result == {1000: 3, 500: 1, 100: 2}


def test_calculate_change_returns_none_when_cash_is_not_enough():
    cash_box = {
        1000: 1,
        500: 0,
        100: 1,
    }

    result = calculate_change(3700, cash_box)

    assert result is None
    assert can_give_change(3700, cash_box) is False


def test_calculate_change_exact_unit():
    cash_box = {
        5000: 1,
        1000: 3,
    }

    result = calculate_change(5000, cash_box)

    assert result == {5000: 1}


def test_calculate_zero_change():
    assert calculate_change(0, {}) == {}


def test_update_cash_box_counts_replaces_cash_box_counts(conn):
    result = update_cash_box_counts({50000: 1, 10000: 3, 500: 8}, conn=conn)
    cash_box = get_cash_box(conn=conn)

    assert result is True
    assert cash_box[50000] == 1
    assert cash_box[10000] == 3
    assert cash_box[500] == 8
    assert cash_box[1000] == 0


def test_update_cash_box_counts_rejects_negative_count(conn):
    result = update_cash_box_counts({1000: -1}, conn=conn)
    cash_box = get_cash_box(conn=conn)

    assert result is False
    assert cash_box[1000] == 0
