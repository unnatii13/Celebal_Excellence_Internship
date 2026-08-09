import pandas as pd
import sqlite3
import os


os.makedirs("database", exist_ok=True)

db_path = "database/ecommerce.db"

if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)

customers = pd.read_csv(
    "data/cleaned/customers_cleaned.csv"
)

orders = pd.read_csv(
    "data/cleaned/orders_cleaned.csv"
)

products = pd.read_csv(
    "data/cleaned/products_cleaned.csv"
)

order_items = pd.read_csv(
    "data/cleaned/order_items_cleaned.csv"
)

customers.to_sql(
    "customers",
    conn,
    if_exists="replace",
    index=False
)

orders.to_sql(
    "orders",
    conn,
    if_exists="replace",
    index=False
)

products.to_sql(
    "products",
    conn,
    if_exists="replace",
    index=False
)

order_items.to_sql(
    "order_items",
    conn,
    if_exists="replace",
    index=False
)

print("Customers:", len(customers))
print("Orders:", len(orders))
print("Products:", len(products))
print("Order Items:", len(order_items))

print("Database created successfully.")

conn.close()