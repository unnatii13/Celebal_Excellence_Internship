# Delta Lake MERGE Implementation — Incremental Data Processing

Incremental customer-dimension processing using Delta Lake's `MERGE` operation, implemented with [`deltalake`](https://github.com/delta-io/delta-rs) (delta-rs) — a real, pure-Python/Rust Delta Lake engine. No Spark cluster or JVM required.

## Objective

Load a base customer dataset into a Delta table, clean it, apply an incoming incremental feed via `MERGE`, and implement both common dimension-update strategies:

- **SCD Type 1** — overwrite in place, no history kept
- **SCD Type 2** — preserve full history with `is_current` / `effective_date` / `end_date`

## Files

| File | Description |
|---|---|
| `delta_lake_merge_assignment.ipynb` | Main notebook — fully executed, all steps and outputs included |
| `customer_master.csv` | Base/existing customer records (bronze source) |
| `customer_incremental.csv` | Incoming feed: mix of updates to existing customers and brand-new customers |

## Notebook Steps

1. **Load** `customer_master.csv` into a Delta table (bronze layer)
2. **Clean** — remove exact duplicate rows, remove duplicate `customer_id`s (keep latest), fill nulls in `segment` and `postal_code`
3. **Inspect the incremental feed** — classify each row as `NEW` or `UPDATE`
4. **Apply MERGE**
   - **4a. SCD Type 1** — one `MERGE`: `WHEN MATCHED THEN UPDATE`, `WHEN NOT MATCHED THEN INSERT`
   - **4b. SCD Type 2** — two-pass `MERGE`: close out the old current row (`is_current=False`, stamp `end_date`), then insert the new version as current
5. **Validate** — row-count checks, duplicate checks, completeness checks (all assertions pass)
6. **Display results** — final tables, sample history for updated customers, Delta transaction log (`history()`)

## Requirements

```bash
pip install deltalake pandas pyarrow ipykernel nbclient nbformat
```

## Running

Open `delta_lake_merge_assignment.ipynb` in Jupyter and run all cells, or re-execute headlessly:

```bash
jupyter nbconvert --to notebook --execute delta_lake_merge_assignment.ipynb
```

The notebook is idempotent — it wipes and recreates its Delta tables (`./delta/`) at the top of the run, so it can be re-run freely.

## Results (this run)

| Metric | Value |
|---|---|
| Cleaned master rows | 150 |
| Incremental — new customers | 8 |
| Incremental — updates | 20 |
| SCD1 final row count | 158 (one row per customer) |
| SCD2 final row count | 178 (includes historical versions) |
| Validation checks | All passed ✅ |

## Notes on the engine

`deltalake` (delta-rs) implements the real Delta Lake protocol — transaction log, versioning, `MERGE` semantics — in Rust with Python bindings. It's functionally equivalent to `DeltaTable.forPath(spark, path).merge(...)` in PySpark for everything used here, but doesn't need a Spark cluster, so it's well suited to local development, testing, and small-to-medium datasets.
