-- City funding ranking
WITH city_totals AS (
    SELECT
        city,
        SUM(amount_usd) AS total_funding_usd,
        COUNT(*) AS deal_count
    FROM silver_startup_funding
    WHERE city IS NOT NULL
      AND TRIM(city) <> ''
    GROUP BY city
)
SELECT
    city,
    ROUND(total_funding_usd, 2) AS total_funding_usd,
    deal_count,
    RANK() OVER (
        ORDER BY total_funding_usd DESC
    ) AS funding_rank
FROM city_totals
ORDER BY funding_rank;
