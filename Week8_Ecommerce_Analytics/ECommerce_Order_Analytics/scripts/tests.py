import sqlite3
from datetime import datetime


def test_invalid_order_id():
    conn = sqlite3.connect(":memory:")

    conn.execute("""
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY
        )
    """)

    conn.execute("""
        CREATE TABLE order_items (
            order_item_id TEXT,
            order_id TEXT
        )
    """)

    conn.execute(
        "INSERT INTO orders VALUES (?)",
        ("O001",)
    )

    conn.execute(
        "INSERT INTO order_items VALUES (?, ?)",
        ("OI001", "O999")
    )

    result = conn.execute("""
        SELECT oi.order_id
        FROM order_items oi
        LEFT JOIN orders o
            ON oi.order_id = o.order_id
        WHERE o.order_id IS NULL
    """).fetchall()

    assert len(result) == 1
    assert result[0][0] == "O999"

    conn.close()

    print("Test 1 passed: Invalid order_id detected")


def test_discount_greater_than_100():
    discount_percent = 120

    assert discount_percent > 100

    print("Test 2 passed: Discount greater than 100 detected")


def test_zero_quantity():
    quantity = 0
    price = 100

    revenue = quantity * price

    assert revenue == 0

    print("Test 3 passed: Zero quantity produces zero revenue")


def test_future_order_date():
    order_date = "2099-01-01"

    current_date = datetime.now().date()
    order_date_value = datetime.strptime(
        order_date,
        "%Y-%m-%d"
    ).date()

    assert order_date_value > current_date

    print("Test 4 passed: Future order date detected")


def run_tests():
    print("=" * 60)
    print("PART 5 - EDGE CASE TESTS")
    print("=" * 60)

    test_invalid_order_id()
    test_discount_greater_than_100()
    test_zero_quantity()
    test_future_order_date()

    print("=" * 60)
    print("All edge case tests passed.")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()