# Databricks notebook source
# Gold: Silver Delta -> business-ready analytical Delta datasets

from pyspark.sql import functions as F
from pyspark.sql.window import Window

dbutils.widgets.text(
    "silver_path",
    "abfss://raw@<storage-account>.dfs.core.windows.net/silver",
)
dbutils.widgets.text(
    "gold_path",
    "abfss://raw@<storage-account>.dfs.core.windows.net/gold",
)

SILVER_PATH = dbutils.widgets.get("silver_path")
GOLD_PATH = dbutils.widgets.get("gold_path")

silver = spark.read.format("delta").load(SILVER_PATH)


def save_gold(df, name):
    path = f"{GOLD_PATH}/{name}"
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .save(path)
    )
    print(f"{name}: {df.count()} rows -> {path}")


# 1. Top funded sectors
top_funded_sectors = (
    silver
    .filter(
        F.col("industry_vertical").isNotNull()
        & (F.trim("industry_vertical") != "")
    )
    .groupBy("industry_vertical")
    .agg(
        F.sum("amount_usd").alias("total_funding_usd"),
        F.count("*").alias("deal_count"),
        F.countDistinct("startup_name").alias("startup_count"),
    )
    .orderBy(F.desc("total_funding_usd"))
)

save_gold(top_funded_sectors, "top_funded_sectors")


# 2. City funding ranking
city_totals = (
    silver
    .filter(F.col("city").isNotNull() & (F.trim("city") != ""))
    .groupBy("city")
    .agg(
        F.sum("amount_usd").alias("total_funding_usd"),
        F.count("*").alias("deal_count"),
    )
)

city_funding_rank = (
    city_totals
    .withColumn(
        "funding_rank",
        F.rank().over(
            Window.orderBy(F.desc("total_funding_usd"))
        ),
    )
    .orderBy("funding_rank")
)

save_gold(city_funding_rank, "city_funding_rank")


# 3. Sector YoY snapshot
yearly_sector = (
    silver
    .filter(
        F.col("funding_year").isNotNull()
        & F.col("industry_vertical").isNotNull()
    )
    .groupBy("industry_vertical", "funding_year")
    .agg(
        F.sum("amount_usd").alias("total_funding_usd"),
        F.count("*").alias("deal_count"),
    )
)

sector_window = Window.partitionBy(
    "industry_vertical"
).orderBy("funding_year")

sector_yoy_snapshot = (
    yearly_sector
    .withColumn(
        "previous_year_funding_usd",
        F.lag("total_funding_usd").over(sector_window),
    )
    .withColumn(
        "yoy_change_pct",
        F.when(
            F.col("previous_year_funding_usd").isNotNull()
            & (F.col("previous_year_funding_usd") != 0),
            (
                (
                    F.col("total_funding_usd")
                    - F.col("previous_year_funding_usd")
                )
                / F.col("previous_year_funding_usd")
                * 100
            ),
        ),
    )
)

save_gold(sector_yoy_snapshot, "sector_yoy_snapshot")


# 4. Investor activity
investor_activity = (
    silver
    .withColumn(
        "investor",
        F.explode(
            F.split(
                F.regexp_replace(
                    F.coalesce("investor_names", F.lit("")),
                    r"\s*;\s*",
                    ";",
                ),
                ";",
            )
        ),
    )
    .withColumn("investor", F.trim("investor"))
    .filter(F.col("investor") != "")
    .groupBy("investor")
    .agg(
        F.count("*").alias("deal_count"),
        F.countDistinct("startup_name").alias("startup_count"),
        F.sum("amount_usd").alias("total_funding_usd"),
    )
    .orderBy(
        F.desc("deal_count"),
        F.desc("total_funding_usd"),
    )
)

save_gold(investor_activity, "investor_deal_count")


# 5. Average deal size by stage
avg_deal_by_stage = (
    silver
    .groupBy("investment_stage")
    .agg(
        F.avg("amount_usd").alias("avg_deal_usd"),
        F.count("*").alias("deal_count"),
    )
    .orderBy(F.desc("avg_deal_usd"))
)

save_gold(avg_deal_by_stage, "avg_deal_by_stage")
