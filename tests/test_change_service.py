from services.change_service import calculate_change, can_give_change


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
