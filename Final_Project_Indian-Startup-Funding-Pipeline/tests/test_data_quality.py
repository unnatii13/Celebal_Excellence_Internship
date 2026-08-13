"""
Basic Silver-layer data quality checks.

Adapt the DELTA_PATH for your local/Databricks environment.
"""

import os

from pyspark.sql import SparkSession, functions as F


DELTA_PATH = os.getenv(
    "SILVER_PATH",
    "data/sample/silver",
)


def get_spark():
    return (
        SparkSession.builder
        .master("local[2]")
        .appName("IndianStartupFunding-DQ")
        .getOrCreate()
    )


def test_required_columns():
    spark = get_spark()
    df = spark.read.format("delta").load(DELTA_PATH)

    required = {
        "funding_date",
        "startup_name",
        "industry_vertical",
        "city",
        "amount_usd",
        "funding_year",
        "investment_stage",
        "record_hash",
    }

    assert required.issubset(set(df.columns))
    spark.stop()


def test_startup_name_not_blank():
    spark = get_spark()
    df = spark.read.format("delta").load(DELTA_PATH)

    invalid = df.filter(
        F.col("startup_name").isNull()
        | (F.trim("startup_name") == "")
    ).count()

    assert invalid == 0
    spark.stop()


def test_no_duplicate_record_hash():
    spark = get_spark()
    df = spark.read.format("delta").load(DELTA_PATH)

    duplicates = (
        df.groupBy("record_hash")
        .count()
        .filter(F.col("count") > 1)
        .count()
    )

    assert duplicates == 0
    spark.stop()


def test_no_negative_amounts():
    spark = get_spark()
    df = spark.read.format("delta").load(DELTA_PATH)

    invalid = df.filter(
        F.col("amount_usd").isNotNull()
        & (F.col("amount_usd") < 0)
    ).count()

    assert invalid == 0
    spark.stop()
