import pytest

from app import app
from services import product_service


@pytest.fixture
def rental_product():
    product = next(
        item
        for item in product_service.get_all_products()
        if item["item_type"] == "rental"
    )
    original_stock = int(product["stock"])
    if original_stock <= 0:
        product_service.update_stock(product["id"], 1)

    try:
        yield product_service.get_product_by_id(product["id"])
    finally:
        product_service.update_stock(product["id"], original_stock)


def put_product_in_cart(client, product):
    with client.session_transaction() as session:
        session["cart"] = {str(product["id"]): 1}


def test_rental_checkout_requires_student_id_tag(rental_product):
    app.config["TESTING"] = True

    with app.test_client() as client:
        put_product_in_cart(client, rental_product)
        response = client.get("/payment")

    assert response.status_code == 302
    assert "/rental/student-id" in response.headers["Location"]


def test_rental_student_id_tag_unlocks_payment_page(rental_product):
    app.config["TESTING"] = True

    with app.test_client() as client:
        put_product_in_cart(client, rental_product)
        response = client.post("/rental/student-id")
        payment_page = client.get("/payment")

    assert response.status_code == 302
    assert "/payment" in response.headers["Location"]
    assert payment_page.status_code == 200
    assert "결제 방식을 선택하세요".encode() in payment_page.data


def test_direct_rental_card_payment_requires_student_id_tag(rental_product):
    app.config["TESTING"] = True

    with app.test_client() as client:
        put_product_in_cart(client, rental_product)
        response = client.post("/payment/card")

    assert response.status_code == 302
    assert "/rental/student-id" in response.headers["Location"]


def test_return_flow_shows_completion_page():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.post("/return/student-id", follow_redirects=True)

    assert response.status_code == 200
    assert "학습 도구 반납이 완료되었습니다".encode() in response.data
