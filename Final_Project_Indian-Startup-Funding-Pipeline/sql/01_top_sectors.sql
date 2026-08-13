-- Top funded sectors
SELECT
    industry_vertical AS sector,
    ROUND(SUM(amount_usd), 2) AS total_funding_usd,
    COUNT(*) AS deal_count,
    COUNT(DISTINCT startup_name) AS startup_count
FROM silver_startup_funding
WHERE industry_vertical IS NOT NULL
  AND TRIM(industry_vertical) <> ''
GROUP BY industry_vertical
ORDER BY total_funding_usd DESC;
