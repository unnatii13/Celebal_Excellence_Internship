# Indian Startup Funding Pipeline

## 1. Project Overview

An end-to-end Data Engineering pipeline that converts raw Indian startup funding CSV data into trusted and analytical datasets using the **Medallion Architecture**:

```text
Raw CSV
   |
   v
ADLS Gen2
   |
   v
Bronze Delta
   |
   v
Silver Delta
   |
   v
Gold Delta
   |
   v
Databricks SQL
```

The supplied technical use-case defines the project around three analytical gaps:

- sector-wise funding velocity and year-over-year change
- city-level startup-hub analysis
- investor activity and funding-stage patterns

## 2. Repository Structure

```text
Indian-Startup-Funding-Pipeline/
|
├── data/
│   ├── raw/
│   └── sample/
│
├── ingestion/
│   └── upload_to_adls.py
│
├── databricks/
│   ├── 01_bronze_ingestion.py
│   ├── 02_silver_transformation.py
│   ├── 03_gold_analytics.py
│   └── 04_scd2_history.py
│
├── sql/
│   ├── 01_top_sectors.sql
│   ├── 02_city_ranking.sql
│   ├── 03_sector_yoy.sql
│   ├── 04_investor_activity.sql
│   └── 05_avg_deal_stage.sql
│
├── tests/
│   └── test_data_quality.py
│
├── screenshots/
│
└── README.md
```

## 3. Source Dataset

Expected source fields:

- Date
- Startup Name
- Industry Vertical
- Sub-Vertical
- City
- Investor Names
- Investment Type
- Amount (USD)

Place the real CSV in:

```text
data/raw/Indian_Startup_Funding.csv
```

## 4. Architecture

```text
                    +----------------------+
                    |   Startup CSV        |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | ADLS Gen2 Landing    |
                    | raw/startup-funding/ |
                    +----------+-----------+
                               |
                         Azure Data Factory
                               |
                               v
                    +----------------------+
                    | 01 Bronze            |
                    | Raw Delta             |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | 02 Silver            |
                    | Clean + Standardize  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | 03 Gold              |
                    | Analytics            |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | 04 SCD Type 2        |
                    | History              |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Databricks SQL       |
                    +----------------------+
```

## 5. Bronze

`01_bronze_ingestion.py`

Responsibilities:

- read raw CSV
- preserve source values
- append ingestion metadata
- write Delta
- no business cleaning

## 6. Silver

`02_silver_transformation.py`

Responsibilities:

- rename columns to stable names
- trim and clean text
- parse dates
- normalize cities
- standardize amount into USD
- derive funding year
- derive investment stage
- create a record hash
- remove duplicates

### Amount conversion

The source documentation identifies an INR/USD mix but does not prescribe an exchange-rate methodology. The notebook therefore exposes `inr_to_usd` as a parameter.

## 7. Gold

`03_gold_analytics.py`

Creates:

```text
top_funded_sectors
city_funding_rank
sector_yoy_snapshot
investor_deal_count
avg_deal_by_stage
```

## 8. SCD Type 2

`04_scd2_history.py`

Maintains historical sector/year versions with:

```text
effective_from
effective_to
is_current
record_hash
```

Delta `MERGE` closes changed active records and inserts new versions.

## 9. SQL Analytics

### Top sectors

`sql/01_top_sectors.sql`

Uses:

```text
GROUP BY
SUM
ORDER BY
```

### City ranking

`sql/02_city_ranking.sql`

Uses:

```text
RANK() OVER
```

### Sector YoY

`sql/03_sector_yoy.sql`

Uses:

```text
CTE
LAG()
```

### Investor activity

`sql/04_investor_activity.sql`

Uses:

```text
EXPLODE
GROUP BY
COUNT
```

### Average deal size

`sql/05_avg_deal_stage.sql`

Uses:

```text
AVG()
GROUP BY
```

## 10. Execution Order

Run the pipeline in this order:

```text
1. ingestion/upload_to_adls.py
          |
          v
2. 01_bronze_ingestion.py
          |
          v
3. 02_silver_transformation.py
          |
          v
4. 03_gold_analytics.py
          |
          v
5. 04_scd2_history.py
          |
          v
6. SQL analytics
          |
          v
7. Data-quality tests
```

## 11. Azure Components

```text
Azure Data Lake Storage Gen2
        |
        v
Azure Data Factory
        |
        v
Azure Databricks
        |
        v
Delta Lake
        |
        v
Databricks SQL
```

Use identity-based authentication for Azure-to-Databricks/ADLS access. Do not commit secrets to GitHub.

## 12. Screenshots

Recommended evidence:

```text
screenshots/
├── 01_adls_raw.png
├── 02_bronze_delta.png
├── 03_silver_cleaned.png
├── 04_gold_tables.png
├── 05_top_sectors_sql.png
├── 06_city_ranking_sql.png
├── 07_investor_activity_sql.png
└── 08_scd2_history.png
```

## 13. GitHub

Before pushing:

```bash
git add .
git commit -m "Build Indian startup funding pipeline"
git push
```

Never commit:

```text
.env
client secrets
storage keys
passwords
API keys
connection strings
```
