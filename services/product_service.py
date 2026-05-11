from database import get_db_connection


def row_to_dict(row):
    return dict(row) if row is not None else None


def get_all_products(conn=None):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    rows = conn.execute(
        """
        SELECT id, name, category, price, stock, image, is_popular, created_at
        FROM products
        ORDER BY is_popular DESC, category, id
        """
    ).fetchall()
    products = [dict(row) for row in rows]

    if owns_connection:
        conn.close()

    return products


def get_product_by_id(product_id, conn=None):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    row = conn.execute(
        """
        SELECT id, name, category, price, stock, image, is_popular, created_at
        FROM products
        WHERE id = ?
        """,
        (int(product_id),),
    ).fetchone()
    product = row_to_dict(row)

    if owns_connection:
        conn.close()

    return product


def is_sold_out(product_id, conn=None):
    product = get_product_by_id(product_id, conn=conn)
    return product is None or int(product["stock"]) <= 0


def has_sufficient_stock(product_id, quantity, conn=None):
    product = get_product_by_id(product_id, conn=conn)
    return product is not None and int(product["stock"]) >= int(quantity)


def decrease_stock(product_id, quantity, conn=None):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    quantity = int(quantity)
    if quantity <= 0:
        if owns_connection:
            conn.close()
        return False

    row = conn.execute(
        "SELECT stock FROM products WHERE id = ?", (int(product_id),)
    ).fetchone()

    if row is None or int(row["stock"]) < quantity:
        if owns_connection:
            conn.close()
        return False

    conn.execute(
        "UPDATE products SET stock = stock - ? WHERE id = ?",
        (quantity, int(product_id)),
    )

    if owns_connection:
        conn.commit()
        conn.close()

    return True


def update_stock(product_id, new_stock, conn=None):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    new_stock = max(0, int(new_stock))
    cursor = conn.execute(
        "UPDATE products SET stock = ? WHERE id = ?",
        (new_stock, int(product_id)),
    )

    if owns_connection:
        conn.commit()
        conn.close()

    return cursor.rowcount > 0


def update_product(product_id, name, category, price, stock, is_popular=False, conn=None):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    cursor = conn.execute(
        """
        UPDATE products
        SET name = ?, category = ?, price = ?, stock = ?, is_popular = ?
        WHERE id = ?
        """,
        (
            name.strip(),
            category.strip(),
            max(0, int(price)),
            max(0, int(stock)),
            1 if is_popular else 0,
            int(product_id),
        ),
    )

    if owns_connection:
        conn.commit()
        conn.close()

    return cursor.rowcount > 0


def update_popular_status(product_id, is_popular, conn=None):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    cursor = conn.execute(
        "UPDATE products SET is_popular = ? WHERE id = ?",
        (1 if is_popular else 0, int(product_id)),
    )

    if owns_connection:
        conn.commit()
        conn.close()

    return cursor.rowcount > 0


def validate_cart_stock(cart_items, conn=None):
    for item in cart_items:
        product = get_product_by_id(item["product_id"], conn=conn)
        if product is None:
            return False, "장바구니에 존재하지 않는 상품이 있습니다."
        if int(product["stock"]) <= 0:
            return False, f"{product['name']} 상품은 품절입니다."
        if int(product["stock"]) < int(item["quantity"]):
            return (
                False,
                f"{product['name']} 재고가 부족합니다. 현재 재고: {product['stock']}개",
            )
    return True, ""
