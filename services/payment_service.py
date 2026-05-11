from database import get_db_connection
from services.change_service import (
    add_cash_to_box,
    break_down_cash_amount,
    calculate_change,
    get_cash_box,
    record_inserted_cash,
    update_cash_box_after_change,
)


def process_card_payment(total_price):
    total_price = int(total_price)

    if total_price <= 0:
        return {
            "success": False,
            "payment_type": "card",
            "message": "결제할 금액이 없습니다.",
        }

    return {
        "success": True,
        "payment_type": "card",
        "message": "카드 결제가 승인되었습니다.",
        "change_amount": 0,
        "change_result": {},
    }


def process_cash_payment(total_price, inserted_cash, conn=None):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    try:
        total_price = int(total_price)
        inserted_cash = int(inserted_cash)

        if total_price <= 0:
            return {
                "success": False,
                "payment_type": "cash",
                "message": "결제할 금액이 없습니다.",
            }

        if inserted_cash < total_price:
            return {
                "success": False,
                "payment_type": "cash",
                "message": "투입 금액이 부족합니다.",
                "inserted_cash": inserted_cash,
                "change_amount": 0,
                "change_result": {},
            }

        inserted_units = break_down_cash_amount(inserted_cash)
        if inserted_units is None:
            return {
                "success": False,
                "payment_type": "cash",
                "message": "현금은 10원 단위로 입력해야 합니다.",
                "inserted_cash": inserted_cash,
                "change_amount": 0,
                "change_result": {},
            }

        change_amount = inserted_cash - total_price
        cash_box = get_cash_box(conn=conn)
        cash_box_after_insert = add_cash_to_box(cash_box, inserted_units)
        change_result = calculate_change(change_amount, cash_box_after_insert)

        if change_result is None:
            return {
                "success": False,
                "payment_type": "cash",
                "message": "키오스크에 거스름돈이 부족합니다.",
                "inserted_cash": inserted_cash,
                "change_amount": change_amount,
                "change_result": {},
            }

        record_inserted_cash(inserted_units, conn=conn)
        update_cash_box_after_change(change_result, conn=conn)

        if owns_connection:
            conn.commit()

        return {
            "success": True,
            "payment_type": "cash",
            "message": "현금 결제가 완료되었습니다.",
            "inserted_cash": inserted_cash,
            "change_amount": change_amount,
            "change_result": change_result,
        }
    except Exception:
        if owns_connection:
            conn.rollback()
        raise
    finally:
        if owns_connection:
            conn.close()
