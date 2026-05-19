from datetime import datetime

from database import get_db_connection


def create_order(cart_items, payment_type, total_price, conn=None, status="paid"):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    now = datetime.now().isoformat(timespec="seconds")
    cursor = conn.execute(
        """
        INSERT INTO orders (total_price, payment_type, status, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (int(total_price), payment_type, status, now),
    )
    order_id = cursor.lastrowid

    for item in cart_items:
        conn.execute(
            """
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
            """,
            (
                order_id,
                int(item["product_id"]),
                int(item["quantity"]),
                int(item["price"]),
            ),
        )

    if owns_connection:
        conn.commit()
        conn.close()

    return order_id


def get_all_orders(conn=None):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    rows = conn.execute(
        """
        SELECT
            o.id,
            o.total_price,
            o.payment_type,
            o.status,
            o.created_at,
            COALESCE(SUM(oi.quantity), 0) AS item_count,
            COALESCE(
                GROUP_CONCAT(p.name || ' x' || oi.quantity, ', '),
                ''
            ) AS item_summary
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN products p ON oi.product_id = p.id
        GROUP BY o.id
        ORDER BY o.id DESC
        """
    ).fetchall()
    orders = [dict(row) for row in rows]

    if owns_connection:
        conn.close()

    return orders


def get_order_items(order_id, conn=None):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    rows = conn.execute(
        """
        SELECT
            oi.id,
            oi.order_id,
            oi.product_id,
            p.name AS product_name,
            oi.quantity,
            oi.price,
            oi.quantity * oi.price AS subtotal
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
        ORDER BY oi.id
        """,
        (int(order_id),),
    ).fetchall()
    items = [dict(row) for row in rows]

    if owns_connection:
        conn.close()

    return items


def get_order_count_by_hour(conn=None):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    rows = conn.execute(
        """
        SELECT
            substr(created_at, 12, 2) AS hour,
            COUNT(*) AS order_count
        FROM orders
        WHERE status = 'paid'
        GROUP BY hour
        ORDER BY hour
        """
    ).fetchall()
    stats = [dict(row) for row in rows]

    if owns_connection:
        conn.close()

    return stats


def get_product_sales_stats(conn=None, limit=8):
    owns_connection = conn is None
    conn = conn or get_db_connection()

    rows = conn.execute(
        """
        SELECT
            p.id AS product_id,
            p.name,
            p.category,
            p.is_popular,
            COALESCE(SUM(oi.quantity), 0) AS sold_quantity,
            COALESCE(SUM(oi.quantity * oi.price), 0) AS sales_amount
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN products p ON oi.product_id = p.id
        WHERE o.status = 'paid' AND p.is_active = 1
        GROUP BY p.id
        ORDER BY sold_quantity DESC, sales_amount DESC, p.id
        LIMIT ?
        """,
        (int(limit),),
    ).fetchall()
    stats = [dict(row) for row in rows]

    if owns_connection:
        conn.close()

    return stats
