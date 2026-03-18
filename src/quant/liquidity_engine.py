import polars as pl
import yaml
from pathlib import Path
from src.core.logger import logger
import os
import os

def calculate_volume_velocity(df_5m: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate Volume Velocity (Liquidity Score).
    This measures how active an item is. High spread + Zero volume = 'Pipe Dream'.
    """
    df = df_5m.with_columns([
        (pl.col("highPriceVolume") + pl.col("lowPriceVolume")).alias("total_volume"),
        ((pl.col("avgHighPrice") * pl.col("highPriceVolume")) + 
         (pl.col("avgLowPrice") * pl.col("lowPriceVolume"))).alias("volume_gp_flow")
    ])
    
    # Staff Logic: Group by ID to get a single liquidity profile per item
    return df.group_by("id").agg([
        pl.col("total_volume").sum().alias("last_5m_volume"),
        pl.col("volume_gp_flow").sum().alias("last_5m_gp_flow"),
        pl.col("avgHighPrice").mean().alias("avg_5m_price")
    ])

def apply_liquidity_filter(df_gold: pl.DataFrame, df_liquidity: pl.DataFrame, min_gp_flow: int) -> pl.DataFrame:
    """
    Filter the Gold Opportunity Table by real-world liquidity.
    - min_gp_flow: Minimum GP traded in the last 5 minutes to consider an item 'Flippable'.
    """
    df = df_gold.join(df_liquidity, on="id", how="left")
    
    # Fill nulls for items with zero volume in the snapshot
    df = df.with_columns([
        pl.col("last_5m_volume").fill_null(0),
        pl.col("last_5m_gp_flow").fill_null(0)
    ])
    
    # Calculate Liquidity Score (0 to 1 scale for ranking)
    max_flow = df.select(pl.col("last_5m_gp_flow").max()).to_series()[0] or 1
    df = df.with_columns([
        (pl.col("last_5m_gp_flow") / max_flow).alias("liquidity_score")
    ])
    
    return df.filter(pl.col("last_5m_gp_flow") >= min_gp_flow)

def main():
    with open("configs/settings.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Paths
    bronze_root = config["storage"]["bronze_path"]
    silver_root = Path(config["storage"]["silver_path"])
    gold_root = Path(config["storage"]["gold_path"])
    
    # Ingestion Client (We need the 5m data)
    from src.core.api_client import WikiAPIClient
    client = WikiAPIClient(config["api"]["base_url"])
    
    try:
        # 1. Fetch 5m Volume Data (Real-time Liquidity)
        logger.info("Fetching 5m Volume Data for Liquidity Analysis")
        raw_5m = client.fetch(config["api"]["endpoints"]["timeseries"])
        
        # 2. Transform 5m to Silver-ish Polars DF
        data_5m = [{"id": int(k), **v} for k, v in raw_5m.get("data", {}).items()]
        df_5m = pl.DataFrame(data_5m)
        
        # 3. Calculate Liquidity Metrics
        logger.info("Calculating Volume Velocity and GP Flow")
        df_liquidity = calculate_volume_velocity(df_5m)
        
        # 4. Load existing Gold Opportunities
        df_gold = pl.read_parquet(gold_root / "market_opportunities.parquet")
        
        # 5. Apply Quant Filters (Min 1M GP flow by default)
        min_gp_flow = config["quant"].get("min_liquidity", 1000000)
        logger.info(f"Filtering by Liquidity (Min Flow: {min_gp_flow:,} GP/5m)")
        
        df_liquid_gold = apply_liquidity_filter(df_gold, df_liquidity, min_gp_flow)
        
        # 6. Save Ranked Opportunities Locally
        ranked_path = gold_root / "ranked_opportunities.parquet"
        ranked_df = df_liquid_gold.sort("liquidity_score", descending=True)
        ranked_df.write_parquet(ranked_path)

        # 7. Sync to Cloud Data Warehouse (Supabase) if configured
        import os
        supabase_url = os.environ.get("SUPABASE_URL")
        from dotenv import load_dotenv
        load_dotenv()
        supabase_url = os.getenv("SUPABASE_URL") or supabase_url

        if supabase_url:
            logger.info("Synchronizing data to Supabase (PostgreSQL)...")
            try:
                # Need sqlalchemy format for some drivers, but adbc usually expects postgresql://
                # Clean URL just in case
                conn_str = supabase_url
                ranked_df.write_database(
                    table_name="gold_margins",
                    connection=conn_str.replace("postgresql://", "postgresql+psycopg2://"),
                    if_table_exists="replace"
                )
                logger.success("Supabase Data Warehouse Sink Complete!")
            except Exception as db_e:
                logger.error(f"Failed to sync to Supabase: {db_e}")

        
        logger.success(f"Strategy Engine Complete: {df_liquid_gold.shape[0]} Liquid Opportunities Found.")
        
        # Top 5 Liquid High-Margin Items
        print("\n--- TOP 5 LIQUID OPPORTUNITIES (Ranked by Liquidity Score) ---")
        print(df_liquid_gold.select([
            "name", "roi_pct", "last_5m_gp_flow", "liquidity_score", "limit_profit"
        ]).sort("liquidity_score", descending=True).head(5))
        
    except Exception as e:
        logger.error(f"Strategy Engine failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
