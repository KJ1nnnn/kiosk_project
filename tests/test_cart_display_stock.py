from app import app
from services import product_service


def get_product_by_type(item_type):
    return next(
        item
        for item in product_service.get_all_products()
        if item["item_type"] == item_type
    )


def test_menu_stock_display_subtracts_cart_quantity_without_changing_database():
    app.config["TESTING"] = True
    product = get_product_by_type("rental")
    original_stock = int(product["stock"])
    cart_quantity = 2 if original_stock >= 2 else 1

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["cart"] = {str(product["id"]): cart_quantity}

        response = client.get("/menu")

    updated_product = product_service.get_product_by_id(product["id"])
    display_stock = max(0, original_stock - cart_quantity)

    assert response.status_code == 200
    assert f"재고 {display_stock}개".encode() in response.data
    assert f"장바구니 {cart_quantity}개 반영".encode() in response.data
    assert int(updated_product["stock"]) == original_stock


def test_menu_disables_add_button_when_cart_reserves_all_stock():
    app.config["TESTING"] = True
    product = get_product_by_type("rental")
    original_stock = int(product["stock"])

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["cart"] = {str(product["id"]): original_stock}

        response = client.get("/menu")

    assert response.status_code == 200
    assert "품절".encode() in response.data
    assert int(product_service.get_product_by_id(product["id"])["stock"]) == original_stock


def test_menu_defaults_to_rental_tab_and_filters_purchase_items():
    app.config["TESTING"] = True
    rental_product = get_product_by_type("rental")
    purchase_product = get_product_by_type("purchase")

    with app.test_client() as client:
        response = client.get("/menu")

    assert response.status_code == 200
    assert rental_product["name"].encode() in response.data
    assert purchase_product["name"].encode() not in response.data
    assert b'href="/menu?type=purchase"' in response.data


def test_cart_add_from_purchase_tab_returns_to_purchase_tab():
    app.config["TESTING"] = True
    product = get_product_by_type("purchase")
    original_stock = int(product["stock"])
    if original_stock <= 0:
        product_service.update_stock(product["id"], 1)

    try:
        with app.test_client() as client:
            response = client.post(
                "/cart/add",
                data={
                    "product_id": product["id"],
                    "quantity": 1,
                    "menu_type": "purchase",
                },
            )
    finally:
        product_service.update_stock(product["id"], original_stock)

    assert response.status_code == 302
    assert "/menu?type=purchase" in response.headers["Location"]
