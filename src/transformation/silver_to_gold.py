import polars as pl
import yaml
from pathlib import Path
from src.core.logger import logger

def calculate_flipping_metrics(df_latest: pl.DataFrame, df_mapping: pl.DataFrame, tax_rate: float, tax_cap: int) -> pl.DataFrame:
    """
    Gold Transformation:
    - Join mapping metadata with prices
    - Calculate Quant metrics:
        - raw_spread
        - ge_tax (1% capped at 5M)
        - effective_spread (high*(1-tax) - low)
        - roi_pct
        - potential_profit_per_limit (if we fill the buy limit)
    """
    # Join on ID
    df = df_latest.join(df_mapping, on="id")
    
    # Financial Logic
    # GE Tax: 1% but max 5M GP. Note: Only applies when SELLING (the high price).
    df = df.with_columns([
        ((pl.col("high") * tax_rate).floor().clip(upper_bound=tax_cap)).alias("ge_tax")
    ])
    
    df = df.with_columns([
        (pl.col("high") - pl.col("low")).alias("raw_spread"),
        (pl.col("high") - pl.col("ge_tax") - pl.col("low")).alias("effective_spread")
    ])
    
    df = df.with_columns([
        (pl.col("effective_spread") / pl.col("low") * 100).alias("roi_pct")
    ])
    
    # Potential Profit: (Effective Spread * Buy Limit)
    # This represents the 'Capital Efficiency' of the item.
    df = df.with_columns([
        (pl.col("effective_spread") * pl.col("limit")).alias("limit_profit")
    ])
    
    # Filter out garbage (nulls or negative spreads)
    return df.filter(
        (pl.col("high").is_not_null()) & 
        (pl.col("low").is_not_null()) &
        (pl.col("effective_spread") > 0)
    ).sort("limit_profit", descending=True)

def main():
    with open("configs/settings.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    silver_root = Path(config["storage"]["silver_path"])
    gold_root = Path(config["storage"]["gold_path"])
    gold_root.mkdir(parents=True, exist_ok=True)
    
    # Parameters from config
    tax_rate = config["quant"]["tax_rate"]
    tax_cap = config["quant"]["tax_cap"]
    
    try:
        # Load Silver
        logger.info("Loading Silver Parquet files")
        df_latest = pl.read_parquet(silver_root / "latest.parquet")
        df_mapping = pl.read_parquet(silver_root / "mapping.parquet")
        
        # Calculate Gold
        logger.info("Generating Gold Analytics (Flipping Metrics)")
        df_gold = calculate_flipping_metrics(df_latest, df_mapping, tax_rate, tax_cap)
        
        # Save Gold
        output_path = gold_root / "market_opportunities.parquet"
        df_gold.write_parquet(output_path)
        logger.success(f"Gold Opportunity Table ready: {df_gold.shape[0]} candidates")
        
        # Display top 10 for terminal confirmation
        print("\n--- TOP 10 FLIPPING OPPORTUNITIES (By Limit Profit) ---")
        print(df_gold.select([
            "name", "low", "high", "ge_tax", "effective_spread", "roi_pct", "limit_profit"
        ]).head(10))
        
    except Exception as e:
        logger.error(f"Gold transformation failed: {e}")

if __name__ == "__main__":
    main()
