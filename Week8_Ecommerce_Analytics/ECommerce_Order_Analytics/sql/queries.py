import sqlite3

DB_PATH = "database/ecommerce.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")

queries = {
    "1. Revenue by Category": """
        SELECT
            p.category,
            ROUND(SUM(
                oi.quantity * oi.unit_price *
                (1 - oi.discount_percent / 100.0)
            ), 2) AS total_revenue
        FROM order_items oi
        JOIN products p
            ON oi.product_id = p.product_id
        GROUP BY p.category
        ORDER BY total_revenue DESC
    """,

    "2. Top 10 Customers": """
        SELECT
            c.customer_id,
            c.customer_name,
            ROUND(SUM(
                oi.quantity * oi.unit_price *
                (1 - oi.discount_percent / 100.0)
            ), 2) AS total_order_value
        FROM customers c
        JOIN orders o
            ON c.customer_id = o.customer_id
        JOIN order_items oi
            ON o.order_id = oi.order_id
        GROUP BY c.customer_id, c.customer_name
        ORDER BY total_order_value DESC
        LIMIT 10
    """,

    "3. Monthly Order Count": """
        SELECT
            strftime('%Y-%m', order_date) AS month,
            COUNT(DISTINCT order_id) AS order_count
        FROM orders
        WHERE date(order_date) >= date('now', '-12 months')
        GROUP BY month
        ORDER BY month
    """,

    "4. Customers Never Delivered": """
        SELECT DISTINCT
            c.customer_id,
            c.customer_name
        FROM customers c
        JOIN orders o
            ON c.customer_id = o.customer_id
        WHERE NOT EXISTS (
            SELECT 1
            FROM orders d
            WHERE d.customer_id = c.customer_id
              AND UPPER(d.status) = 'DELIVERED'
        )
    """,

    "5. More Returns Than Purchases": """
        SELECT
            p.product_id,
            p.product_name,
            SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS purchased,
            ABS(SUM(CASE WHEN oi.quantity < 0 THEN oi.quantity ELSE 0 END)) AS returned
        FROM products p
        JOIN order_items oi
            ON p.product_id = oi.product_id
        GROUP BY p.product_id, p.product_name
        HAVING returned > purchased
    """,

    "6. Return Rate by Category": """
        SELECT
            p.category,
            ABS(SUM(
                CASE WHEN oi.quantity < 0 THEN oi.quantity ELSE 0 END
            )) AS returned_items,
            SUM(ABS(oi.quantity)) AS total_items,
            ROUND(
                ABS(SUM(
                    CASE WHEN oi.quantity < 0 THEN oi.quantity ELSE 0 END
                )) * 100.0 /
                NULLIF(SUM(ABS(oi.quantity)), 0),
                2
            ) AS return_rate
        FROM products p
        JOIN order_items oi
            ON p.product_id = oi.product_id
        GROUP BY p.category
    """,

    "7. Running Revenue by Region": """
        WITH daily AS (
            SELECT
                o.region_code,
                date(o.order_date) AS order_date,
                SUM(
                    oi.quantity * oi.unit_price *
                    (1 - oi.discount_percent / 100.0)
                ) AS daily_revenue
            FROM orders o
            JOIN order_items oi
                ON o.order_id = oi.order_id
            GROUP BY o.region_code, date(o.order_date)
        )
        SELECT
            region_code,
            order_date,
            ROUND(daily_revenue, 2) AS daily_revenue,
            ROUND(
                SUM(daily_revenue) OVER (
                    PARTITION BY region_code
                    ORDER BY order_date
                ),
                2
            ) AS running_total
        FROM daily
        ORDER BY region_code, order_date
    """,

    "8. Dense Rank Products": """
        WITH product_revenue AS (
            SELECT
                p.category,
                p.product_id,
                p.product_name,
                SUM(
                    oi.quantity * oi.unit_price *
                    (1 - oi.discount_percent / 100.0)
                ) AS total_revenue
            FROM products p
            JOIN order_items oi
                ON p.product_id = oi.product_id
            GROUP BY p.category, p.product_id, p.product_name
        )
        SELECT
            category,
            product_name,
            ROUND(total_revenue, 2) AS total_revenue,
            DENSE_RANK() OVER (
                PARTITION BY category
                ORDER BY total_revenue DESC
            ) AS rank_in_category
        FROM product_revenue
        ORDER BY category, rank_in_category
    """,

    "9. Customer Order Gaps": """
        WITH customer_orders AS (
            SELECT
                customer_id,
                date(order_date) AS order_date,
                LAG(date(order_date)) OVER (
                    PARTITION BY customer_id
                    ORDER BY date(order_date)
                ) AS previous_order_date
            FROM orders
            WHERE customer_id IS NOT NULL
        ),
        gaps AS (
            SELECT
                customer_id,
                order_date,
                previous_order_date,
                CASE
                    WHEN previous_order_date IS NULL THEN NULL
                    ELSE julianday(order_date) -
                         julianday(previous_order_date)
                END AS days_gap
            FROM customer_orders
        ),
        avg_gaps AS (
            SELECT
                customer_id,
                AVG(days_gap) AS average_gap
            FROM gaps
            WHERE days_gap IS NOT NULL
            GROUP BY customer_id
        )
        SELECT
            g.customer_id,
            g.order_date,
            g.previous_order_date,
            ROUND(g.days_gap, 2) AS days_gap,
            CASE
                WHEN a.average_gap > 30 THEN 'At Risk'
                ELSE 'No'
            END AS risk_flag
        FROM gaps g
        LEFT JOIN avg_gaps a
            ON g.customer_id = a.customer_id
        ORDER BY g.customer_id, g.order_date
    """,

    "10. Monthly Customer Segments": """
        WITH monthly_revenue AS (
            SELECT
                o.customer_id,
                strftime('%Y-%m', o.order_date) AS month,
                SUM(
                    oi.quantity * oi.unit_price *
                    (1 - oi.discount_percent / 100.0)
                ) AS revenue
            FROM orders o
            JOIN order_items oi
                ON o.order_id = oi.order_id
            GROUP BY o.customer_id, month
        ),
        segments AS (
            SELECT
                customer_id,
                month,
                CASE
                    WHEN revenue > 10000 THEN 'High'
                    WHEN revenue >= 5000 THEN 'Medium'
                    ELSE 'Low'
                END AS segment
            FROM monthly_revenue
        )
        SELECT
            month,
            segment,
            COUNT(*) AS customer_count
        FROM segments
        GROUP BY month, segment
        ORDER BY month, segment
    """,

    "11. Lifetime Value Quartiles": """
        WITH customer_value AS (
            SELECT
                o.customer_id,
                SUM(
                    oi.quantity * oi.unit_price *
                    (1 - oi.discount_percent / 100.0)
                ) AS total_value
            FROM orders o
            JOIN order_items oi
                ON o.order_id = oi.order_id
            GROUP BY o.customer_id
        ),
        quartiles AS (
            SELECT
                customer_id,
                total_value,
                NTILE(4) OVER (
                    ORDER BY total_value DESC
                ) AS quartile
            FROM customer_value
        )
        SELECT
            customer_id,
            ROUND(total_value, 2) AS total_value,
            quartile,
            CASE quartile
                WHEN 1 THEN 'Platinum'
                WHEN 2 THEN 'Gold'
                WHEN 3 THEN 'Silver'
                WHEN 4 THEN 'Bronze'
            END AS quartile_label
        FROM quartiles
        ORDER BY quartile, total_value DESC
    """,

    "12. Year over Year": """
        WITH monthly AS (
            SELECT
                strftime('%Y', o.order_date) AS year,
                strftime('%m', o.order_date) AS month,
                SUM(
                    oi.quantity * oi.unit_price *
                    (1 - oi.discount_percent / 100.0)
                ) AS revenue
            FROM orders o
            JOIN order_items oi
                ON o.order_id = oi.order_id
            GROUP BY year, month
        ),
        comparison AS (
            SELECT
                year,
                month,
                revenue,
                LAG(revenue, 12) OVER (
                    ORDER BY year, month
                ) AS prev_year_revenue
            FROM monthly
        )
        SELECT
            year,
            month,
            ROUND(revenue, 2) AS revenue,
            ROUND(prev_year_revenue, 2) AS prev_year_revenue,
            CASE
                WHEN prev_year_revenue IS NULL
                     OR prev_year_revenue = 0
                THEN NULL
                ELSE ROUND(
                    (revenue - prev_year_revenue)
                    * 100.0 / prev_year_revenue,
                    2
                )
            END AS yoy_growth_percent
        FROM comparison
        ORDER BY year, month
    """,

    "13. First and Recent Category": """
        WITH ranked AS (
            SELECT
                o.customer_id,
                p.category,
                o.order_date,
                ROW_NUMBER() OVER (
                    PARTITION BY o.customer_id
                    ORDER BY o.order_date, o.order_id
                ) AS first_rank,
                ROW_NUMBER() OVER (
                    PARTITION BY o.customer_id
                    ORDER BY o.order_date DESC, o.order_id DESC
                ) AS last_rank
            FROM orders o
            JOIN order_items oi
                ON o.order_id = oi.order_id
            JOIN products p
                ON oi.product_id = p.product_id
            WHERE o.customer_id IS NOT NULL
        )
        SELECT
            customer_id,
            MAX(CASE WHEN first_rank = 1 THEN category END)
                AS first_category,
            MAX(CASE WHEN last_rank = 1 THEN category END)
                AS recent_category,
            CASE
                WHEN MAX(CASE WHEN first_rank = 1 THEN category END)
                   <>
                     MAX(CASE WHEN last_rank = 1 THEN category END)
                THEN 'Yes'
                ELSE 'No'
            END AS category_shift
        FROM ranked
        GROUP BY customer_id
        ORDER BY customer_id
    """,

    "14. Cumulative Customer Revenue": """
        WITH customer_revenue AS (
            SELECT
                o.customer_id,
                SUM(
                    oi.quantity * oi.unit_price *
                    (1 - oi.discount_percent / 100.0)
                ) AS revenue
            FROM orders o
            JOIN order_items oi
                ON o.order_id = oi.order_id
            WHERE o.customer_id IS NOT NULL
            GROUP BY o.customer_id
        )
        SELECT
            customer_id,
            ROUND(revenue, 2) AS revenue,
            ROUND(
                SUM(revenue) OVER (
                    ORDER BY revenue DESC
                ),
                2
            ) AS cumulative_revenue,
            ROUND(
                SUM(revenue) OVER (
                    ORDER BY revenue DESC
                ) * 100.0 /
                SUM(revenue) OVER (),
                2
            ) AS cumulative_percent
        FROM customer_revenue
        ORDER BY revenue DESC
    """,

    "15. Cohort Analysis": """
        WITH cohorts AS (
            SELECT
                customer_id,
                strftime('%Y-%m', registration_date) AS cohort_month
            FROM customers
        ),
        customer_orders AS (
            SELECT DISTINCT
                o.customer_id,
                strftime('%Y-%m', o.order_date) AS order_month
            FROM orders o
            WHERE o.customer_id IS NOT NULL
        ),
        cohort_activity AS (
            SELECT
                c.cohort_month,
                o.order_month,
                COUNT(DISTINCT o.customer_id) AS customers
            FROM cohorts c
            JOIN customer_orders o
                ON c.customer_id = o.customer_id
            GROUP BY c.cohort_month, o.order_month
        )
        SELECT
            cohort_month,
            order_month,
            customers
        FROM cohort_activity
        ORDER BY cohort_month, order_month
    """,

    "16. Products Bought Together": """
        SELECT
            p1.product_name AS product_a,
            p2.product_name AS product_b,
            COUNT(DISTINCT oi1.order_id) AS times_bought_together
        FROM order_items oi1
        JOIN order_items oi2
            ON oi1.order_id = oi2.order_id
           AND oi1.product_id < oi2.product_id
        JOIN products p1
            ON oi1.product_id = p1.product_id
        JOIN products p2
            ON oi2.product_id = p2.product_id
        GROUP BY p1.product_id, p2.product_id
        ORDER BY times_bought_together DESC
    """
}


def run_query(name, query):
    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    try:
        cursor = conn.execute(query)
        rows = cursor.fetchall()

        if not rows:
            print("No records found.")
            return

        print(" | ".join(column[0] for column in cursor.description))

        for row in rows[:100]:
            print(row)

        if len(rows) > 100:
            print(f"... {len(rows) - 100} more rows")

    except sqlite3.Error as e:
        print("SQL Error:", e)


for name, query in queries.items():
    run_query(name, query)

conn.close()