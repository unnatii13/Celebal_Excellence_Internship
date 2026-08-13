# Databricks notebook source
# SCD Type 2: maintain historical versions of sector/year metrics.
#
# Requires Delta Lake / Databricks Runtime.

from delta.tables import DeltaTable
from pyspark.sql import functions as F

dbutils.widgets.text(
    "gold_path",
    "abfss://raw@<storage-account>.dfs.core.windows.net/gold",
)

GOLD_PATH = dbutils.widgets.get("gold_path")

source_path = f"{GOLD_PATH}/sector_yoy_snapshot"
history_path = f"{GOLD_PATH}/sector_yoy_history"

source_df = (
    spark.read.format("delta").load(source_path)
    .select(
        F.col("industry_vertical").alias("sector"),
        "funding_year",
        "total_funding_usd",
        "deal_count",
        "yoy_change_pct",
    )
    .withColumn("effective_from", F.current_date())
    .withColumn(
        "effective_to",
        F.lit(None).cast("date"),
    )
    .withColumn("is_current", F.lit(True))
    .withColumn(
        "record_hash",
        F.sha2(
            F.concat_ws(
                "||",
                F.coalesce(F.col("sector"), F.lit("")),
                F.col("funding_year").cast("string"),
                F.col("total_funding_usd").cast("string"),
                F.col("deal_count").cast("string"),
                F.coalesce(
                    F.col("yoy_change_pct").cast("string"),
                    F.lit(""),
                ),
            ),
            256,
        ),
    )
)

if not DeltaTable.isDeltaTable(spark, history_path):
    (
        source_df.write
        .format("delta")
        .mode("overwrite")
        .save(history_path)
    )
    print("Created initial SCD2 history table.")
else:
    history = DeltaTable.forPath(spark, history_path)

    # Close the active version when its metric values change.
    (
        history.alias("target")
        .merge(
            source_df.alias("source"),
            """
            target.sector = source.sector
            AND target.funding_year = source.funding_year
            AND target.is_current = true
            """,
        )
        .whenMatchedUpdate(
            condition="target.record_hash <> source.record_hash",
            set={
                "effective_to": "current_date()",
                "is_current": "false",
            },
        )
        .execute()
    )

    # Insert new records and changed versions.
    (
        history.alias("target")
        .merge(
            source_df.alias("source"),
            """
            target.sector = source.sector
            AND target.funding_year = source.funding_year
            AND target.record_hash = source.record_hash
            AND target.is_current = true
            """,
        )
        .whenNotMatchedInsert(
            values={
                "sector": "source.sector",
                "funding_year": "source.funding_year",
                "total_funding_usd": "source.total_funding_usd",
                "deal_count": "source.deal_count",
                "yoy_change_pct": "source.yoy_change_pct",
                "effective_from": "source.effective_from",
                "effective_to": "source.effective_to",
                "is_current": "source.is_current",
                "record_hash": "source.record_hash",
            }
        )
        .execute()
    )

print("SCD Type 2 history updated.")
display(spark.read.format("delta").load(history_path))
