import pandas as pd
import random
import os
from datetime import datetime, timedelta

random.seed(42)

os.makedirs("data/raw", exist_ok=True)

customer_count = 500
product_count = 500
order_count = 1000
item_count = 2000

customer_types = ["Regular", "Premium", "VIP"]
categories = ["Electronics", "Clothing", "Home", "Books", "Sports"]
subcategories = {
    "Electronics": ["Laptop", "Phone", "Headphones", "Tablet"],
    "Clothing": ["Shirts", "Jeans", "Shoes", "Jackets"],
    "Home": ["Furniture", "Kitchen", "Decor", "Appliances"],
    "Books": ["Fiction", "Science", "History", "Technology"],
    "Sports": ["Fitness", "Cricket", "Football", "Tennis"]
}
regions = ["NORTH", "SOUTH", "EAST", "WEST"]

first_names = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Rahul",
    "Vivek", "Rohan", "Karan", "Priya", "Neha",
    "Kavya", "Simran", "Ananya", "Pooja", "Sneha"
]

last_names = [
    "Sharma", "Verma", "Gupta", "Singh", "Patel",
    "Kumar", "Joshi", "Agarwal", "Mehta", "Kaur"
]

customers = []

start_registration = datetime.now() - timedelta(days=900)

for i in range(1, customer_count + 1):
    name = random.choice(first_names) + " " + random.choice(last_names)
    email = name.lower().replace(" ", ".") + str(i) + "@example.com"

    if i % 47 == 0:
        email = "invalid-email"

    registration_date = start_registration + timedelta(
        days=random.randint(0, 850)
    )

    customers.append({
        "customer_id": f"C{i:04d}",
        "customer_name": name,
        "email": email,
        "registration_date": registration_date.strftime("%Y-%m-%d"),
        "customer_type": random.choice(customer_types)
    })

customers_df = pd.DataFrame(customers)

products = []

for i in range(1, product_count + 1):
    category = random.choice(categories)
    subcategory = random.choice(subcategories[category])
    name = f"{subcategory} Product {i}"

    if i % 20 == 0:
        name = "  " + name.upper() + "  "

    products.append({
        "product_id": f"P{i:04d}",
        "product_name": name,
        "category": category,
        "subcategory": subcategory,
        "cost_price": round(random.uniform(100, 5000), 2)
    })

products_df = pd.DataFrame(products)

orders = []

start_date = datetime.now() - timedelta(days=730)

for i in range(1, order_count + 1):
    customer_id = f"C{random.randint(1, customer_count):04d}"

    if i % 20 == 0:
        customer_id = None

    order_date = start_date + timedelta(
        days=random.randint(0, 729),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

    status = random.choices(
        ["Delivered", "Pending", "Cancelled", "Returned"],
        weights=[60, 20, 10, 10]
    )[0]

    orders.append({
        "order_id": f"O{i:05d}",
        "customer_id": customer_id,
        "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "region_code": random.choice(regions)
    })

orders_df = pd.DataFrame(orders)

order_items = []

for i in range(1, item_count + 1):
    order_id = f"O{random.randint(1, order_count):05d}"
    product_id = f"P{random.randint(1, product_count):04d}"

    quantity = random.randint(1, 5)

    if i % 33 == 0:
        quantity = -random.randint(1, 3)

    if i % 100 == 0:
        quantity = 0

    unit_price = round(random.uniform(100, 8000), 2)
    discount = random.choice([0, 5, 10, 15, 20])

    order_items.append({
        "item_id": f"I{i:06d}",
        "order_id": order_id,
        "product_id": product_id,
        "quantity": quantity,
        "unit_price": unit_price,
        "discount_percent": discount
    })

order_items_df = pd.DataFrame(order_items)

orders_df.loc[
    orders_df.index[:20],
    "order_date"
] = orders_df.loc[
    orders_df.index[:20],
    "order_date"
].apply(
    lambda x: datetime.strptime(
        x,
        "%Y-%m-%d %H:%M:%S"
    ).strftime("%d-%m-%Y")
)

customers_df.to_csv(
    "data/raw/customers.csv",
    index=False
)

orders_df.to_csv(
    "data/raw/orders.csv",
    index=False
)

products_df.to_csv(
    "data/raw/products.csv",
    index=False
)

order_items_df.to_csv(
    "data/raw/order_items.csv",
    index=False
)

print("Data generation completed.")
print("Customers:", len(customers_df))
print("Orders:", len(orders_df))
print("Products:", len(products_df))
print("Order Items:", len(order_items_df))