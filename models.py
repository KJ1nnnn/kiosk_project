from dataclasses import dataclass


@dataclass
class Product:
    id: int
    name: str
    category: str
    price: int
    stock: int
    image: str = ""


@dataclass
class Order:
    id: int
    total_price: int
    payment_type: str
    status: str
    created_at: str


@dataclass
class OrderItem:
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: int
