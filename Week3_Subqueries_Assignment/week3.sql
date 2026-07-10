CREATE DATABASE superstore;
USE superstore;
CREATE TABLE superstore_raw (
    row_id INT,
    order_id VARCHAR(30),
    order_date VARCHAR(20),
    ship_date VARCHAR(20),
    ship_mode VARCHAR(50),
    customer_id VARCHAR(30),
    customer_name VARCHAR(100),
    segment VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(50),
    product_id VARCHAR(50),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    product_name TEXT,
    sales DECIMAL(10,2),
    quantity INT,
    discount DECIMAL(5,2),
    profit DECIMAL(10,2)
);

LOAD DATA LOCAL INFILE 'C:/Users/HP/Downloads/archive/Sample - Superstore.csv'
INTO TABLE superstore_raw
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
row_id,
order_id,
order_date,
ship_date,
ship_mode,
customer_id,
customer_name,
segment,
country,
city,
state,
postal_code,
region,
product_id,
category,
sub_category,
product_name,
sales,
quantity,
discount,
profit
);


SELECT COUNT(*) FROM superstore_raw;

CREATE TABLE customers AS
SELECT DISTINCT
    customer_id,
    customer_name,
    segment,
    country,
    city,
    state,
    postal_code,
    region
FROM superstore_raw;

CREATE TABLE products AS
SELECT DISTINCT
    product_id,
    category,
    sub_category,
    product_name
FROM superstore_raw;

CREATE TABLE orders AS
SELECT DISTINCT
    order_id,
    order_date,
    ship_date,
    ship_mode,
    customer_id,
    product_id,
    sales,
    quantity,
    discount,
    profit
FROM superstore_raw;

 SELECT *
FROM orders
WHERE sales >
(
    SELECT AVG(sales)
    FROM orders
);

SELECT *
FROM orders o
WHERE sales =
(
    SELECT MAX(sales)
    FROM orders
    WHERE customer_id = o.customer_id
);

WITH customer_sales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT *
FROM customer_sales;

WITH customer_sales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)

SELECT *
FROM customer_sales
WHERE total_sales >
(
    SELECT AVG(total_sales)
    FROM customer_sales
);

WITH customer_sales AS
(
    SELECT
        customer_id,
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)

SELECT
customer_id,
total_sales,
RANK() OVER
(
ORDER BY total_sales DESC
) AS customer_rank
FROM customer_sales;


SELECT
customer_id,
order_id,
sales,

ROW_NUMBER() OVER
(
PARTITION BY customer_id
ORDER BY sales DESC
) AS row_number

FROM orders;

WITH customer_sales AS
(
SELECT
customer_id,
SUM(sales) total_sales
FROM orders
GROUP BY customer_id
)

SELECT *
FROM
(
SELECT
customer_id,
total_sales,
RANK() OVER(ORDER BY total_sales DESC) ranking
FROM customer_sales
)t
WHERE ranking<=3;


WITH customer_sales AS
(
SELECT
customer_id,
SUM(sales) total_sales
FROM orders
GROUP BY customer_id
)

SELECT

c.customer_name,

cs.total_sales,

RANK() OVER
(
ORDER BY cs.total_sales DESC
) customer_rank

FROM customer_sales cs

JOIN customers c

ON cs.customer_id=c.customer_id;

WITH customer_sales AS
(
SELECT
customer_id,
SUM(sales) total_sales
FROM orders
GROUP BY customer_id
)

SELECT

c.customer_name,
cs.total_sales

FROM customer_sales cs

JOIN customers c

ON cs.customer_id=c.customer_id

ORDER BY total_sales DESC

LIMIT 5;

WITH customer_sales AS
(
SELECT
customer_id,
SUM(sales) total_sales
FROM orders
GROUP BY customer_id
)

SELECT

c.customer_name,
cs.total_sales

FROM customer_sales cs

JOIN customers c

ON cs.customer_id=c.customer_id

ORDER BY total_sales ASC

LIMIT 5;

SELECT

c.customer_name,

COUNT(o.order_id) total_orders

FROM customers c

JOIN orders o

ON c.customer_id=o.customer_id

GROUP BY c.customer_name

HAVING COUNT(o.order_id)=1;

WITH customer_sales AS
(
SELECT
customer_id,
SUM(sales) total_sales
FROM orders
GROUP BY customer_id
)

SELECT

c.customer_name,

cs.total_sales

FROM customer_sales cs

JOIN customers c

ON cs.customer_id=c.customer_id

WHERE total_sales>
(
SELECT AVG(total_sales)
FROM customer_sales
);

SELECT

c.customer_name,

MAX(o.sales) highest_order

FROM customers c

JOIN orders o

ON c.customer_id=o.customer_id

GROUP BY c.customer_name

ORDER BY highest_order DESC;

SELECT COUNT(*) FROM superstore_raw;
