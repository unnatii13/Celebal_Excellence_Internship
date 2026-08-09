import pandas as pd
import os


def clean_orders(orders):
    missing_customer_ids = (
        orders["customer_id"].isna() |
        orders["customer_id"].astype(str).str.strip().isin(
            ["", "NULL", "null", "nan", "NaN"]
        )
    ).sum()

    orders["customer_id"] = orders["customer_id"].replace(
        ["", "NULL", "null", "NaN", "nan"],
        pd.NA
    )

    original_dates = orders["order_date"].copy()

    orders["order_date"] = pd.to_datetime(
        orders["order_date"],
        dayfirst=True,
        errors="coerce"
    )

    invalid_dates = orders["order_date"].isna().sum()

    orders["order_date"] = orders["order_date"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return orders, missing_customer_ids, invalid_dates


def clean_products(products):
    original_names = products["product_name"].astype(str)

    products["product_name"] = (
        products["product_name"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    changed_names = (
        original_names != products["product_name"]
    ).sum()

    return products, changed_names


def validate_emails(customers):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    valid_emails = customers["email"].astype(str).str.match(
        pattern,
        na=False
    )

    invalid_customers = customers.loc[
        ~valid_emails,
        "customer_id"
    ].tolist()

    return invalid_customers


def check_referential_integrity(orders, order_items):
    valid_order_ids = set(
        orders["order_id"].dropna()
    )

    invalid_items = order_items[
        ~order_items["order_id"].isin(valid_order_ids)
    ]

    return invalid_items


def main():
    os.makedirs("data/cleaned", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    orders = pd.read_csv("data/raw/orders.csv")
    order_items = pd.read_csv("data/raw/order_items.csv")
    products = pd.read_csv("data/raw/products.csv")
    customers = pd.read_csv("data/raw/customers.csv")

    orders, missing_customer_ids, invalid_dates = clean_orders(
        orders
    )

    products, changed_names = clean_products(
        products
    )

    invalid_customer_ids = validate_emails(
        customers
    )

    invalid_order_items = check_referential_integrity(
        orders,
        order_items
    )

    orders.to_csv(
        "data/cleaned/orders_cleaned.csv",
        index=False
    )

    order_items.to_csv(
        "data/cleaned/order_items_cleaned.csv",
        index=False
    )

    products.to_csv(
        "data/cleaned/products_cleaned.csv",
        index=False
    )

    customers.to_csv(
        "data/cleaned/customers_cleaned.csv",
        index=False
    )

    report = f"""
E-COMMERCE DATA QUALITY REPORT

ORDERS
Total orders: {len(orders)}
Missing customer IDs: {missing_customer_ids}
Invalid dates: {invalid_dates}

PRODUCTS
Total products: {len(products)}
Product names normalized: {changed_names}

CUSTOMERS
Total customers: {len(customers)}
Invalid emails: {len(invalid_customer_ids)}

ORDER ITEMS
Total order items: {len(order_items)}
Invalid order references: {len(invalid_order_items)}
"""

    if len(invalid_order_items) > 0:
        report += "\nInvalid order IDs:\n"

        for order_id in invalid_order_items[
            "order_id"
        ].unique():
            report += f"{order_id}\n"

    with open(
        "reports/data_quality_report.txt",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(report)

    print("Data cleaning completed.")
    print("Cleaned files saved in data/cleaned/")
    print("Report saved in reports/")


if __name__ == "__main__":
    main()