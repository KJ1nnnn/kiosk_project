from database import MONEY_UNITS, get_db_connection


def calculate_change(change_amount, cash_box):
    """보유 현금을 고려해서 거스름돈 구성을 계산한다.

    반환값:
    - 성공: {화폐단위: 개수}
    - 실패: None
    """
    change_amount = int(change_amount)

    if change_amount < 0:
        return None
    if change_amount == 0:
        return {}
    if change_amount % 10 != 0:
        return None

    remaining = change_amount
    result = {}

    for money in MONEY_UNITS:
        available_count = int(cash_box.get(money, cash_box.get(str(money), 0)) or 0)
        needed_count = remaining // money
        use_count = min(available_count, needed_count)

        if use_count > 0:
            result[money] = use_count
            remaining -= money * use_count

    if remaining != 0:
        return None

    return result


def can_give_change(change_amount, cash_box):
    return calculate_change(change_amount, cash_box) is not None


def break_down_cash_amount(amount):
    """사용자가 넣은 현금 총액을 큰 단위부터 분해해 시뮬레이션한다."""
    amount = int(amount)

    if amount < 0 or amount % 10 != 0:
        return None

    remaining = amount
    result = {}

    for money in MONEY_UNITS:
        count = remaining // money
        if count > 0:
            result[money] = count
            remaining -= money * count

    return result if remaining == 0 else None


def add_cash_to_box(cash_box, cash_units):
    updated = {money: int(cash_box.get(money, 0)) for money in MONEY_UNITS}
    for money, count in cash_units.items():
        updated[int(money)] = updated.get(int(money), 0) + int(count)
    return updated


def get_cash_box(conn=None):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    rows = conn.execute("SELECT money_unit, count FROM cash_box").fetchall()
    cash_box = {money: 0 for money in MONEY_UNITS}
    for row in rows:
        cash_box[int(row["money_unit"])] = int(row["count"])

    if owns_connection:
        conn.close()

    return cash_box


def update_cash_box_counts(cash_counts, conn=None):
    owns_connection = conn is None
    conn = conn or get_db_connection()
    normalized_counts = {}

    try:
        for money in MONEY_UNITS:
            count = int(cash_counts.get(money, cash_counts.get(str(money), 0)))
            if count < 0:
                if owns_connection:
                    conn.close()
                return False
            normalized_counts[money] = count
    except (TypeError, ValueError):
        if owns_connection:
            conn.close()
        return False

    for money, count in normalized_counts.items():
        current = conn.execute(
            "SELECT count FROM cash_box WHERE money_unit = ?", (int(money),)
        ).fetchone()
        if current is None:
            conn.execute(
                "INSERT INTO cash_box (money_unit, count) VALUES (?, ?)",
                (int(money), int(count)),
            )
        else:
            conn.execute(
                "UPDATE cash_box SET count = ? WHERE money_unit = ?",
                (int(count), int(money)),
            )

    if owns_connection:
        conn.commit()
        conn.close()

    return True


def record_inserted_cash(inserted_cash_units, conn=None):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    for money, count in inserted_cash_units.items():
        current = conn.execute(
            "SELECT count FROM cash_box WHERE money_unit = ?", (int(money),)
        ).fetchone()
        if current is None:
            conn.execute(
                "INSERT INTO cash_box (money_unit, count) VALUES (?, ?)",
                (int(money), int(count)),
            )
        else:
            conn.execute(
                "UPDATE cash_box SET count = count + ? WHERE money_unit = ?",
                (int(count), int(money)),
            )

    if owns_connection:
        conn.commit()
        conn.close()


def update_cash_box_after_change(change_result, conn=None):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    for money, count in change_result.items():
        cursor = conn.execute(
            """
            UPDATE cash_box
            SET count = count - ?
            WHERE money_unit = ? AND count >= ?
            """,
            (int(count), int(money), int(count)),
        )
        if cursor.rowcount == 0:
            if owns_connection:
                conn.rollback()
                conn.close()
            raise ValueError(f"{money}원권/동전 수량이 부족합니다.")

    if owns_connection:
        conn.commit()
        conn.close()
