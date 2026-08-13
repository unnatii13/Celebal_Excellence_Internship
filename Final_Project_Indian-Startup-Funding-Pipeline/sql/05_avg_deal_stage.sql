-- Average deal size by investment stage
SELECT
    investment_stage,
    ROUND(AVG(amount_usd), 2) AS avg_deal_usd,
    COUNT(*) AS deal_count
FROM silver_startup_funding
GROUP BY investment_stage
ORDER BY avg_deal_usd DESC;
