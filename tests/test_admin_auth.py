from app import app, sort_admin_products
from database import MONEY_UNITS


def test_admin_page_redirects_to_login_without_password():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/admin")

    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_admin_login_rejects_wrong_password():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.post(
            "/admin/login",
            data={"password": "1234"},
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert "비밀번호가 올바르지 않습니다.".encode() in response.data


def test_admin_login_accepts_password_0000():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.post(
            "/admin/login?next=/admin",
            data={"password": "0000"},
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert "학습 도구 재고와 이용 내역".encode() in response.data


def test_admin_product_update_requires_password():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.post("/admin/product/update")

    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_admin_cash_update_requires_password():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.post("/admin/cash/update")

    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_admin_cash_update_passes_cash_counts_to_service(monkeypatch):
    app.config["TESTING"] = True
    captured_counts = {}

    def fake_update_cash_box_counts(cash_counts):
        captured_counts.update(cash_counts)
        return True

    monkeypatch.setattr(
        "app.change_service.update_cash_box_counts", fake_update_cash_box_counts
    )
    data = {f"cash_{money}": "2" for money in MONEY_UNITS}

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["admin_authenticated"] = True

        response = client.post(
            "/admin/cash/update",
            data=data,
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert captured_counts == {money: 2 for money in MONEY_UNITS}
    assert "키오스크 보유 현금 수량을 수정했습니다.".encode() in response.data


def test_admin_product_order_places_purchase_above_rental():
    products = [
        {"name": "인기 대여 물품", "item_type": "rental", "is_popular": 1},
        {"name": "구매 물품", "item_type": "purchase", "is_popular": 0},
        {"name": "일반 대여 물품", "item_type": "rental", "is_popular": 0},
    ]

    sorted_products = sort_admin_products(products)

    assert [product["name"] for product in sorted_products] == [
        "구매 물품",
        "인기 대여 물품",
        "일반 대여 물품",
    ]
