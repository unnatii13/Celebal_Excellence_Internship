# Databricks notebook source
# Silver: Bronze Delta -> cleansed/standardized Delta
#
# Set:
#   bronze_path
#   silver_path
#   inr_to_usd
#
# The reference document identifies an INR/USD mix but does not prescribe
# a conversion methodology, so the rate remains configurable.

from pyspark.sql import functions as F

dbutils.widgets.text(
    "bronze_path",
    "abfss://raw@<storage-account>.dfs.core.windows.net/bronze",
)
dbutils.widgets.text(
    "silver_path",
    "abfss://raw@<storage-account>.dfs.core.windows.net/silver",
)
dbutils.widgets.text("inr_to_usd", "0.012")

BRONZE_PATH = dbutils.widgets.get("bronze_path")
SILVER_PATH = dbutils.widgets.get("silver_path")
INR_TO_USD = float(dbutils.widgets.get("inr_to_usd"))

df = spark.read.format("delta").load(BRONZE_PATH)

rename_map = {
    "Date": "funding_date",
    "Startup Name": "startup_name",
    "Industry Vertical": "industry_vertical",
    "Sub-Vertical": "sub_vertical",
    "City": "city",
    "Investor Names": "investor_names",
    "Investment Type": "investment_type",
    "Amount (USD)": "amount_raw",
}

for source, target in rename_map.items():
    if source in df.columns:
        df = df.withColumnRenamed(source, target)

required = [
    "funding_date",
    "startup_name",
    "industry_vertical",
    "sub_vertical",
    "city",
    "investor_names",
    "investment_type",
    "amount_raw",
]

missing = [column for column in required if column not in df.columns]
if missing:
    raise ValueError(f"Missing expected source columns: {missing}")


def clean_text(column):
    return F.trim(
        F.regexp_replace(
            F.regexp_replace(
                F.coalesce(F.col(column), F.lit("")),
                r"[\r\n\t]+",
                " ",
            ),
            r"\s+",
            " ",
        )
    )


city_clean = F.lower(clean_text("city"))

city_normalized = (
    F.when(city_clean.isin("bangalore", "bengaluru"), "Bengaluru")
    .when(city_clean.isin("delhi", "new delhi"), "Delhi")
    .when(city_clean.isin("gurgaon", "gurugram"), "Gurugram")
    .when(city_clean.isin("mumbai", "bombay"), "Mumbai")
    .otherwise(F.initcap(city_clean))
)

raw_amount = F.upper(F.trim(F.coalesce(F.col("amount_raw"), F.lit(""))))
numeric_amount = F.regexp_replace(
    raw_amount, r"[^0-9.\-]", ""
).cast("double")

amount_usd = (
    F.when(
        raw_amount.contains("₹") | raw_amount.contains("INR"),
        numeric_amount * F.lit(INR_TO_USD),
    )
    .when(
        raw_amount.contains("$") | raw_amount.contains("USD"),
        numeric_amount,
    )
    .otherwise(numeric_amount)
)

silver_df = (
    df
    .withColumn("funding_date", F.to_date("funding_date"))
    .withColumn("startup_name", clean_text("startup_name"))
    .withColumn("industry_vertical", clean_text("industry_vertical"))
    .withColumn("sub_vertical", clean_text("sub_vertical"))
    .withColumn("city", city_normalized)
    .withColumn("investor_names", clean_text("investor_names"))
    .withColumn("investment_type", clean_text("investment_type"))
    .withColumn("amount_usd", amount_usd)
    .withColumn("funding_year", F.year("funding_date"))
    .withColumn(
        "investment_stage",
        F.when(F.lower("investment_type").contains("seed"), "Seed")
        .when(F.lower("investment_type").contains("series a"), "Series A")
        .when(F.lower("investment_type").contains("series b"), "Series B")
        .when(F.lower("investment_type").contains("series c"), "Series C")
        .when(F.lower("investment_type").contains("series d"), "Series D")
        .otherwise("Other"),
    )
    .withColumn(
        "record_hash",
        F.sha2(
            F.concat_ws(
                "||",
                *[
                    F.coalesce(F.col(column).cast("string"), F.lit(""))
                    for column in required
                ],
            ),
            256,
        ),
    )
    .filter(F.col("startup_name") != "")
    .dropDuplicates(["record_hash"])
)

(
    silver_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(SILVER_PATH)
)

print(f"Silver row count: {silver_df.count()}")
print(f"Silver Delta path: {SILVER_PATH}")

display(silver_df.limit(20))
