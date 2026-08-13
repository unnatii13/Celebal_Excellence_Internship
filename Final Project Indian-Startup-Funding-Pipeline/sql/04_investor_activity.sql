-- Investor activity
WITH investors AS (
    SELECT
        TRIM(investor) AS investor,
        startup_name,
        amount_usd
    FROM silver_startup_funding
    LATERAL VIEW EXPLODE(
        SPLIT(investor_names, ';')
    ) e AS investor
)
SELECT
    investor,
    COUNT(*) AS deal_count,
    COUNT(DISTINCT startup_name) AS startup_count,
    ROUND(SUM(amount_usd), 2) AS total_funding_usd
FROM investors
WHERE investor <> ''
GROUP BY investor
ORDER BY deal_count DESC, total_funding_usd DESC;
