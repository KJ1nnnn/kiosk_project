from flask import Flask, flash, redirect, render_template, request, session, url_for

from database import init_db, get_db_connection
from services import change_service, order_service, payment_service, product_service


app = Flask(__name__)
app.secret_key = "campus-kiosk-dev-secret"
ADMIN_PASSWORD = "0000"

init_db()


@app.template_filter("won")
def format_won(value):
    return f"{int(value):,}원"


def parse_int(value, default=0):
    try:
        return int(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return default


def get_cart():
    return session.get("cart", {})


def save_cart(cart):
    session["cart"] = cart
    session.modified = True


def is_admin_authenticated():
    return session.get("admin_authenticated") is True


def get_safe_next_url():
    next_url = request.args.get("next")
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        return next_url
    return url_for("admin")


def build_cart_items(conn=None):
    cart = get_cart()
    cleaned_cart = {}
    items = []

    for product_id, quantity in cart.items():
        product = product_service.get_product_by_id(product_id, conn=conn)
        if product is None:
            continue

        quantity = max(1, int(quantity))
        cleaned_cart[str(product["id"])] = quantity
        stock = int(product["stock"])
        price = int(product["price"])
        subtotal = price * quantity

        items.append(
            {
                "product_id": int(product["id"]),
                "name": product["name"],
                "category": product["category"],
                "price": price,
                "quantity": quantity,
                "stock": stock,
                "subtotal": subtotal,
                "stock_warning": stock <= 0 or quantity > stock,
            }
        )

    if cleaned_cart != cart:
        save_cart(cleaned_cart)

    total_price = sum(item["subtotal"] for item in items)
    can_checkout = bool(items) and not any(item["stock_warning"] for item in items)
    return items, total_price, can_checkout


def create_paid_order(cart_items, payment_type, total_price, conn):
    order_id = order_service.create_order(
        cart_items, payment_type, total_price, conn=conn
    )

    for item in cart_items:
        success = product_service.decrease_stock(
            item["product_id"], item["quantity"], conn=conn
        )
        if not success:
            raise ValueError(f"{item['name']} 재고가 부족합니다.")

    return order_id


def save_result(
    success,
    message,
    items=None,
    total_price=0,
    payment_type="",
    order_id=None,
    inserted_cash=0,
    change_amount=0,
    change_result=None,
):
    session["last_result"] = {
        "success": success,
        "message": message,
        "items": items or [],
        "total_price": int(total_price),
        "payment_type": payment_type,
        "order_id": order_id,
        "inserted_cash": int(inserted_cash or 0),
        "change_amount": int(change_amount or 0),
        "change_result": change_result or {},
    }
    session.modified = True


def with_bar_percentages(stats, value_key):
    max_value = max((int(item[value_key]) for item in stats), default=0)

    for item in stats:
        value = int(item[value_key])
        item["bar_percent"] = 0 if max_value == 0 else max(8, round(value / max_value * 100))

    return stats


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/menu")
def menu():
    products = product_service.get_all_products()
    cart_count = sum(int(quantity) for quantity in get_cart().values())
    return render_template("menu.html", products=products, cart_count=cart_count)


@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    product_id = request.form.get("product_id")
    quantity = max(1, parse_int(request.form.get("quantity"), default=1))
    product = product_service.get_product_by_id(product_id)

    if product is None:
        flash("존재하지 않는 상품입니다.", "error")
        return redirect(url_for("menu"))

    stock = int(product["stock"])
    if stock <= 0:
        flash(f"{product['name']} 상품은 품절입니다.", "error")
        return redirect(url_for("menu"))

    cart = get_cart()
    current_quantity = int(cart.get(str(product_id), 0))
    new_quantity = current_quantity + quantity

    if new_quantity > stock:
        cart[str(product_id)] = stock
        flash(f"{product['name']} 재고는 {stock}개까지 담을 수 있습니다.", "warning")
    else:
        cart[str(product_id)] = new_quantity
        flash(f"{product['name']} 상품을 장바구니에 담았습니다.", "success")

    save_cart(cart)
    return redirect(url_for("menu"))


@app.route("/cart")
def cart():
    items, total_price, can_checkout = build_cart_items()
    return render_template(
        "cart.html",
        items=items,
        total_price=total_price,
        can_checkout=can_checkout,
    )


@app.route("/cart/update", methods=["POST"])
def update_cart():
    product_id = request.form.get("product_id")
    action = request.form.get("action", "update")
    cart = get_cart()

    if action == "remove":
        cart.pop(str(product_id), None)
        save_cart(cart)
        flash("상품을 장바구니에서 삭제했습니다.", "success")
        return redirect(url_for("cart"))

    product = product_service.get_product_by_id(product_id)
    if product is None:
        cart.pop(str(product_id), None)
        save_cart(cart)
        flash("존재하지 않는 상품을 장바구니에서 삭제했습니다.", "warning")
        return redirect(url_for("cart"))

    stock = int(product["stock"])
    if stock <= 0:
        cart.pop(str(product_id), None)
        save_cart(cart)
        flash(f"{product['name']} 상품은 품절되어 장바구니에서 삭제했습니다.", "warning")
        return redirect(url_for("cart"))

    quantity = max(1, parse_int(request.form.get("quantity"), default=1))
    if quantity > stock:
        quantity = stock
        flash(f"{product['name']} 재고는 {stock}개까지 선택할 수 있습니다.", "warning")
    else:
        flash("장바구니 수량을 수정했습니다.", "success")

    cart[str(product_id)] = quantity
    save_cart(cart)
    return redirect(url_for("cart"))


@app.route("/payment")
def payment():
    items, total_price, can_checkout = build_cart_items()
    if not items:
        flash("장바구니가 비어 있습니다.", "warning")
        return redirect(url_for("menu"))
    if not can_checkout:
        flash("재고를 확인한 뒤 결제할 수 있습니다.", "warning")
        return redirect(url_for("cart"))
    return render_template("payment.html", items=items, total_price=total_price)


@app.route("/payment/card", methods=["POST"])
def payment_card():
    conn = get_db_connection()
    try:
        items, total_price, _ = build_cart_items(conn=conn)
        valid_stock, stock_message = product_service.validate_cart_stock(
            items, conn=conn
        )
        if not items or not valid_stock:
            conn.rollback()
            flash(stock_message or "장바구니가 비어 있습니다.", "error")
            return redirect(url_for("cart"))

        payment_result = payment_service.process_card_payment(total_price)
        if not payment_result["success"]:
            conn.rollback()
            save_result(
                False,
                payment_result["message"],
                items=items,
                total_price=total_price,
                payment_type="card",
            )
            return redirect(url_for("result"))

        order_id = create_paid_order(items, "card", total_price, conn=conn)
        conn.commit()

        save_result(
            True,
            payment_result["message"],
            items=items,
            total_price=total_price,
            payment_type="card",
            order_id=order_id,
        )
        session.pop("cart", None)
        return redirect(url_for("result"))
    except Exception as error:
        conn.rollback()
        save_result(False, f"결제 처리 중 오류가 발생했습니다: {error}")
        return redirect(url_for("result"))
    finally:
        conn.close()


@app.route("/payment/cash", methods=["POST"])
def payment_cash():
    inserted_cash = parse_int(request.form.get("inserted_cash"), default=-1)
    if inserted_cash < 0:
        flash("투입 금액을 숫자로 입력하세요.", "error")
        return redirect(url_for("payment"))

    conn = get_db_connection()
    try:
        items, total_price, _ = build_cart_items(conn=conn)
        valid_stock, stock_message = product_service.validate_cart_stock(
            items, conn=conn
        )
        if not items or not valid_stock:
            conn.rollback()
            flash(stock_message or "장바구니가 비어 있습니다.", "error")
            return redirect(url_for("cart"))

        payment_result = payment_service.process_cash_payment(
            total_price, inserted_cash, conn=conn
        )
        if not payment_result["success"]:
            conn.rollback()
            save_result(
                False,
                payment_result["message"],
                items=items,
                total_price=total_price,
                payment_type="cash",
                inserted_cash=inserted_cash,
                change_amount=payment_result.get("change_amount", 0),
                change_result=payment_result.get("change_result", {}),
            )
            return redirect(url_for("result"))

        order_id = create_paid_order(items, "cash", total_price, conn=conn)
        conn.commit()

        save_result(
            True,
            payment_result["message"],
            items=items,
            total_price=total_price,
            payment_type="cash",
            order_id=order_id,
            inserted_cash=inserted_cash,
            change_amount=payment_result["change_amount"],
            change_result=payment_result["change_result"],
        )
        session.pop("cart", None)
        return redirect(url_for("result"))
    except Exception as error:
        conn.rollback()
        save_result(False, f"결제 처리 중 오류가 발생했습니다: {error}")
        return redirect(url_for("result"))
    finally:
        conn.close()


@app.route("/result")
def result():
    last_result = session.get("last_result")
    if last_result is None:
        return redirect(url_for("menu"))
    return render_template("result.html", result=last_result)


@app.route("/admin")
def admin():
    if not is_admin_authenticated():
        return redirect(url_for("admin_login", next=request.path))

    products = product_service.get_all_products()
    orders = order_service.get_all_orders()
    cash_box = change_service.get_cash_box()
    hourly_order_stats = with_bar_percentages(
        order_service.get_order_count_by_hour(), "order_count"
    )
    product_sales_stats = with_bar_percentages(
        order_service.get_product_sales_stats(limit=8), "sold_quantity"
    )
    return render_template(
        "admin.html",
        products=products,
        orders=orders,
        cash_box=cash_box,
        hourly_order_stats=hourly_order_stats,
        product_sales_stats=product_sales_stats,
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if is_admin_authenticated():
        return redirect(get_safe_next_url())

    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["admin_authenticated"] = True
            session.modified = True
            flash("관리자 인증이 완료되었습니다.", "success")
            return redirect(get_safe_next_url())

        flash("비밀번호가 올바르지 않습니다.", "error")

    return render_template("admin_login.html")


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("admin_authenticated", None)
    flash("관리자 로그아웃이 완료되었습니다.", "success")
    return redirect(url_for("menu"))


@app.route("/admin/product/update", methods=["POST"])
def admin_product_update():
    if not is_admin_authenticated():
        flash("관리자 비밀번호를 먼저 입력하세요.", "warning")
        return redirect(url_for("admin_login", next=url_for("admin")))

    product_id = request.form.get("product_id")
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    price = parse_int(request.form.get("price"), default=-1)
    stock = parse_int(request.form.get("stock"), default=-1)
    is_popular = request.form.get("is_popular") == "1"

    if not name or price < 0 or stock < 0:
        flash("상품명, 가격, 재고를 올바르게 입력하세요.", "error")
        return redirect(url_for("admin"))

    updated = product_service.update_product(
        product_id, name, category, price, stock, is_popular
    )
    if updated:
        flash("상품 정보를 수정했습니다.", "success")
    else:
        flash("상품 수정에 실패했습니다.", "error")

    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)
