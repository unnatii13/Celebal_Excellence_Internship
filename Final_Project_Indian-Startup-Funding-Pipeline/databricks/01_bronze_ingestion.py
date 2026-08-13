# Databricks notebook source
# COMMAND ----------
# Bronze: raw CSV -> append-only Delta
#
# Set these parameters in the notebook/job:
#   source_csv
#   bronze_path

from pyspark.sql import functions as F

dbutils.widgets.text(
    "source_csv",
    "abfss://raw@<storage-account>.dfs.core.windows.net/startup-funding/Indian_Startup_Funding.csv",
)
dbutils.widgets.text(
    "bronze_path",
    "abfss://raw@<storage-account>.dfs.core.windows.net/bronze",
)

SOURCE_CSV = dbutils.widgets.get("source_csv")
BRONZE_PATH = dbutils.widgets.get("bronze_path")

if "<storage-account>" in SOURCE_CSV or "<storage-account>" in BRONZE_PATH:
    raise ValueError(
        "Replace <storage-account> in the widget values with your actual ADLS Gen2 storage account."
    )

raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", False)
    .csv(SOURCE_CSV)
)

bronze_df = (
    raw_df
    .withColumn("_ingested_at", F.current_timestamp())
    .withColumn("_source_file", F.input_file_name())
)

(
    bronze_df.write
    .format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .save(BRONZE_PATH)
)

print(f"Bronze row count: {bronze_df.count()}")
print(f"Bronze Delta path: {BRONZE_PATH}")

display(bronze_df.limit(20))
