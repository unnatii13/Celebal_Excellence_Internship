import sqlite3

conn = sqlite3.connect("database/ecommerce.db")

tables = [
    "customers",
    "orders",
    "products",
    "order_items"
]

for table in tables:
    print("\n" + table.upper())
    print("-" * 30)

    columns = conn.execute(
        f"PRAGMA table_info({table})"
    ).fetchall()

    for column in columns:
        print(column[1], "-", column[2])

conn.close()