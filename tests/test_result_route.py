from app import app


def test_result_page_renders_card_payment_result():
    app.config["TESTING"] = True

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["last_result"] = {
                "success": True,
                "message": "카드 결제가 승인되었습니다.",
                "items": [
                    {
                        "name": "생수",
                        "quantity": 1,
                        "subtotal": 900,
                    }
                ],
                "total_price": 900,
                "payment_type": "card",
                "order_id": 1,
                "inserted_cash": 0,
                "change_amount": 0,
                "change_result": {},
            }

        response = client.get("/result")

    assert response.status_code == 200
    assert "카드 결제가 승인되었습니다.".encode() in response.data


def test_result_page_renders_cash_payment_result():
    app.config["TESTING"] = True

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["last_result"] = {
                "success": True,
                "message": "현금 결제가 완료되었습니다.",
                "items": [
                    {
                        "name": "컵라면",
                        "quantity": 2,
                        "subtotal": 5000,
                    }
                ],
                "total_price": 5000,
                "payment_type": "cash",
                "order_id": 2,
                "inserted_cash": 10000,
                "change_amount": 5000,
                "change_result": {5000: 1},
            }

        response = client.get("/result")

    assert response.status_code == 200
    assert "현금 결제가 완료되었습니다.".encode() in response.data
    assert "거스름돈 구성".encode() in response.data
