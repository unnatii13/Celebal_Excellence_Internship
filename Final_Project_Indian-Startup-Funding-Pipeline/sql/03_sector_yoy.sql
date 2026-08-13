-- Sector year-over-year funding
WITH yearly AS (
    SELECT
        industry_vertical AS sector,
        funding_year,
        SUM(amount_usd) AS funding_usd
    FROM silver_startup_funding
    WHERE industry_vertical IS NOT NULL
      AND funding_year IS NOT NULL
    GROUP BY industry_vertical, funding_year
),
with_previous AS (
    SELECT
        sector,
        funding_year,
        funding_usd,
        LAG(funding_usd) OVER (
            PARTITION BY sector
            ORDER BY funding_year
        ) AS previous_year_funding_usd
    FROM yearly
)
SELECT
    sector,
    funding_year,
    ROUND(funding_usd, 2) AS funding_usd,
    ROUND(previous_year_funding_usd, 2)
        AS previous_year_funding_usd,
    ROUND(
        CASE
            WHEN previous_year_funding_usd IS NULL
              OR previous_year_funding_usd = 0
            THEN NULL
            ELSE
                (
                    (funding_usd - previous_year_funding_usd)
                    / previous_year_funding_usd
                ) * 100
        END,
        2
    ) AS yoy_change_pct
FROM with_previous
ORDER BY sector, funding_year;
