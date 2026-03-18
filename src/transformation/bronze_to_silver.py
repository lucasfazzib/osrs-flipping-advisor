import polars as pl
import json
import yaml
from pathlib import Path
from src.core.logger import logger

def load_latest_bronze(bronze_dir: str, endpoint: str) -> dict:
    """
    Find the most recent JSON file in the partitioned Bronze directory.
    """
    path = Path(bronze_dir) / endpoint
    all_files = sorted(path.rglob("*.json"), reverse=True)
    if not all_files:
        raise FileNotFoundError(f"No Bronze data found for {endpoint}")
    
    logger.info(f"Loading Bronze file: {all_files[0]}")
    with open(all_files[0], "r", encoding="utf-8") as f:
        return json.load(f)

def transform_mapping(raw_data: list) -> pl.DataFrame:
    """
    Silver Transformation for Mapping:
    - Enforce types
    - Select relevant metadata
    """
    return pl.DataFrame(raw_data).select([
        pl.col("id").cast(pl.Int32),
        pl.col("name").cast(pl.Utf8),
        pl.col("limit").cast(pl.Int32).fill_null(0),
        pl.col("value").cast(pl.Int32),
        pl.col("highalch").cast(pl.Int32).fill_null(0),
        pl.col("lowalch").cast(pl.Int32).fill_null(0),
        pl.col("members").cast(pl.Boolean).fill_null(False),
    ])

def transform_latest(raw_data: dict) -> pl.DataFrame:
    """
    Silver Transformation for Latest Prices:
    - Flatten nested dict {id: {high, low...}}
    - Convert Unix timestamps to Datetime
    - Handle null prices
    """
    data = raw_data.get("data", {})
    records = []
    for item_id, prices in data.items():
        records.append({
            "id": int(item_id),
            "high": prices.get("high"),
            "highTime": prices.get("highTime"),
            "low": prices.get("low"),
            "lowTime": prices.get("lowTime")
        })
    
    df = pl.DataFrame(records)
    
    # Convert timestamps to Datetime and clean
    return df.with_columns([
        pl.from_epoch(pl.col("highTime"), time_unit="s").alias("high_time"),
        pl.from_epoch(pl.col("lowTime"), time_unit="s").alias("low_time"),
        pl.col("high").cast(pl.Int64),
        pl.col("low").cast(pl.Int64)
    ]).drop(["highTime", "lowTime"])

def main():
    with open("configs/settings.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    bronze_root = config["storage"]["bronze_path"]
    silver_root = Path(config["storage"]["silver_path"])
    silver_root.mkdir(parents=True, exist_ok=True)
    
    # 1. Transform Mapping
    logger.info("Transforming Mapping: Bronze -> Silver")
    raw_mapping = load_latest_bronze(bronze_root, "mapping")
    df_mapping = transform_mapping(raw_mapping)
    df_mapping.write_parquet(silver_root / "mapping.parquet")
    logger.success(f"Silver Mapping ready: {df_mapping.shape[0]} items")
    
    # 2. Transform Latest
    logger.info("Transforming Latest Prices: Bronze -> Silver")
    raw_latest = load_latest_bronze(bronze_root, "latest")
    df_latest = transform_latest(raw_latest)
    df_latest.write_parquet(silver_root / "latest.parquet")
    logger.success(f"Silver Latest ready: {df_latest.shape[0]} items")

if __name__ == "__main__":
    main()
