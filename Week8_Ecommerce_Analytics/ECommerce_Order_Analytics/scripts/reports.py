import sqlite3
from datetime import datetime, timedelta

DB_PATH = "database/ecommerce.db"


def get_date_range(report_type):
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")

    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    return start_date, end_date


def get_previous_period(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    days = (end - start).days + 1

    previous_end = start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=days - 1)

    return (
        previous_start.strftime("%Y-%m-%d"),
        previous_end.strftime("%Y-%m-%d")
    )


def get_summary(conn, start_date, end_date):
    query = """
        SELECT
            COUNT(DISTINCT o.order_id),
            COALESCE(SUM(
                oi.quantity *
                oi.unit_price *
                (1 - oi.discount_percent / 100.0)
            ), 0),
            COUNT(DISTINCT o.customer_id)
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        WHERE date(o.order_date)
        BETWEEN date(?) AND date(?)
    """

    return conn.execute(
        query,
        (start_date, end_date)
    ).fetchone()


def get_top_products(conn, start_date, end_date):
    query = """
        SELECT
            p.product_name,
            ROUND(
                SUM(
                    oi.quantity *
                    oi.unit_price *
                    (1 - oi.discount_percent / 100.0)
                ),
                2
            ) AS revenue
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        JOIN products p
            ON oi.product_id = p.product_id
        WHERE date(o.order_date)
        BETWEEN date(?) AND date(?)
        GROUP BY p.product_id, p.product_name
        ORDER BY revenue DESC
        LIMIT 3
    """

    return conn.execute(
        query,
        (start_date, end_date)
    ).fetchall()


def calculate_change(current, previous):
    if previous == 0:
        return None

    return ((current - previous) / previous) * 100


def main():
    print("=" * 50)
    print("E-COMMERCE SALES REPORT")
    print("=" * 50)

    report_type = input(
        "Enter report type (daily/weekly/monthly): "
    ).strip().lower()

    if report_type not in ["daily", "weekly", "monthly"]:
        print("Invalid report type.")
        return

    start_date, end_date = get_date_range(
        report_type
    )

    previous_start, previous_end = get_previous_period(
        start_date,
        end_date
    )

    conn = sqlite3.connect(DB_PATH)

    current = get_summary(
        conn,
        start_date,
        end_date
    )

    previous = get_summary(
        conn,
        previous_start,
        previous_end
    )

    top_products = get_top_products(
        conn,
        start_date,
        end_date
    )

    current_orders = current[0]
    current_revenue = current[1]
    current_customers = current[2]

    previous_orders = previous[0]
    previous_revenue = previous[1]
    previous_customers = previous[2]

    order_change = calculate_change(
        current_orders,
        previous_orders
    )

    revenue_change = calculate_change(
        current_revenue,
        previous_revenue
    )

    customer_change = calculate_change(
        current_customers,
        previous_customers
    )

    print()
    print("REPORT TYPE:", report_type.upper())
    print("CURRENT PERIOD:", start_date, "to", end_date)
    print(
        "PREVIOUS PERIOD:",
        previous_start,
        "to",
        previous_end
    )

    print()
    print("SUMMARY")
    print("-" * 50)

    print("Total orders:", current_orders)
    print("Total revenue:", round(current_revenue, 2))
    print("Unique customers:", current_customers)

    print()
    print("COMPARISON WITH PREVIOUS PERIOD")
    print("-" * 50)

    if order_change is not None:
        print(
            "Orders change:",
            round(order_change, 2),
            "%"
        )
    else:
        print("Orders change: N/A")

    if revenue_change is not None:
        print(
            "Revenue change:",
            round(revenue_change, 2),
            "%"
        )
    else:
        print("Revenue change: N/A")

    if customer_change is not None:
        print(
            "Customer change:",
            round(customer_change, 2),
            "%"
        )
    else:
        print("Customer change: N/A")

    print()
    print("TOP 3 PRODUCTS")
    print("-" * 50)

    if top_products:
        for index, product in enumerate(
            top_products,
            start=1
        ):
            print(
                f"{index}. {product[0]} - Revenue: {product[1]}"
            )
    else:
        print("No products found.")

    conn.close()

    print()
    print("Report generated successfully.")


if __name__ == "__main__":
    main()