# Data Processing Part (Snowflake)

### Ingesting Data from MinIO to Snowflake

Due to Snowflake's inability to connect directly to a locally hosted MinIO instance as an external stage, we must manually download the data from MinIO to a local directory and then use the SnowSQL CLI to upload the files to the appropriate Snowflake stage.

#### Steps:

1. **Download data locally** from MinIO to your filesystem.
2. **Use SnowSQL CLI** to upload the files to the correct Snowflake stage.

Example command using SnowSQL:

```bash
~/.snowsql/1.3.3/snowsql -a HEURITECH-AWS_EUW1 -u PAULHAPPY
```

Then use the `PUT` command to upload the files:

```bash
PUT file:///home/yald/Documents/Test/local_storage/metadata/bronze/crawler/metadata/user_post/1745962981.927765/reddit/Dr_Alzamon/*.json \
  @BACKEND_DEV_DE_2025_STAGE_PAULHAPPY/datalake/bronze/crawler/metadata/user_post/1745962981.927765/reddit/Dr_Alzamon;
```

## Snowflake Data Pipeline Overview

This project implements a full data ingestion and transformation pipeline in **Snowflake** using **Snowpark Python**. It follows a classic **medallion architecture** (Bronze → Silver → Gold) to process raw social media data.

---

### Stage Layout

The raw data is ingested from a Snowflake **external stage** (e.g. MinIO, S3-compatible storage), under the following path structure:

```
@TECHTEST.BACKEND_DEV_DE_2025_PAULHAPPY.BACKEND_DEV_DE_2025_STAGE_PAULHAPPY/datalake/bronze/crawler/metadata/user_post/{ingestion_ts}/{platform}/{author}/{file}.json.gz
```

Each file represents a social media post, and its file path encodes important metadata:

| Segment          | Meaning                                                        |
| ---------------- | -------------------------------------------------------------- |
| `{ingestion_ts}` | The ingestion timestamp directory (used for incremental loads) |
| `{platform}`     | e.g., `reddit`, `linkedin`                                     |
| `{author}`       | Unique identifier of the post author                           |
| `{file}`         | Post content in `.json.gz` format                              |

This structure enables efficient filtering and partitioning during ingestion.

---

### Meta-table: `PROCESSING_DATE`

The pipeline maintains a metadata table `PROCESSING_DATE`, which tracks the **last successfully processed ingestion timestamp** per source table (e.g. `bronze_crawler_data`).

This allows the Bronze layer to:

- **Ingest only new files**
- **Avoid reprocessing already-loaded data**
- **Support incremental processing**

---

### Bronze Layer – Raw Data Ingestion

- **Target Table:** `bronze_crawler_data`
- **Operation Mode:** Append-only
- **Source:** JSON files in the staged path above
- **Schema:** Dynamically inferred from JSON files, with additional metadata columns:
  - `ingestion_date_timestamp` (from path)
  - `platform` (from path)
  - `author` (from path)
- Media URLs, post text, likes, comments, etc., are preserved in raw form.

---

### Silver Layer – Cleaned Data

- **Target Table:** `silver_crawler_data`
- **Operation Mode:** Overwrite (for now)
- **Transformations:**
  - Timestamps converted to `TIMESTAMP_LTZ`
  - Lists and arrays preserved
  - Duplicates removed

This layer serves as the **trusted, normalized representation** of the original data.

---

### Gold Layer – Aggregated KPIs

- **Target Table:** `gold.crawler_data`
- **Operation Mode:** Rebuilt each run (via SQL)
- **KPIs captured:**
  - **Top post per author** (by total interactions)
  - **Top post per author per week**

Each row in `gold.crawler_data` represents an author-week pair with both global and weekly best-performing content, plus author ranking and metadata.

---

### Pipeline Execution

The pipeline is executed from the `main()` function:

```python
def main(session: snowpark.Session):
    ...
```

It runs the 3-layer process in order:

1. **BronzeIngestor** – loads new JSON files from stage
2. **SilverTransformer** – cleans and casts raw data
3. **GoldAggregator** – computes summary metrics

---

### 🚀 Execution Output

At the end of each run, Snowflake tables are updated:

| Layer  | Table                 |
| ------ | --------------------- |
| Bronze | `bronze_crawler_data` |
| Silver | `silver_crawler_data` |
| Gold   | `gold_crawler_data`   |

And metadata in `PROCESSING_DATE` is updated accordingly.
