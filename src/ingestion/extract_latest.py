import json
import os
import yaml
from pathlib import Path
from datetime import datetime
from src.core.api_client import WikiAPIClient
from src.core.logger import logger

def save_raw_json(data: dict, layer_path: str, endpoint: str):
    """
    Bronze Ingestion: Store raw API JSON with Partitioning Logic.
    Partition: /bronze/<endpoint>/YYYY/MM/DD/YYYY-MM-DD_HH-MM_raw.json
    """
    now = datetime.utcnow()
    partition_path = Path(layer_path) / endpoint / str(now.year) / f"{now.month:02}" / f"{now.day:02}"
    partition_path.mkdir(parents=True, exist_ok=True)
    
    filename = f"{now.strftime('%Y-%m-%dT%H-%M-%S')}_raw.json"
    full_path = partition_path / filename
    
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Bronze Snapshot Saved: {full_path}")
    return str(full_path)

def main():
    # Load config (Staff logic: Move this to a dedicated ConfigLoader later)
    with open("configs/settings.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    client = WikiAPIClient(config["api"]["base_url"])
    bronze_root = config["storage"]["bronze_path"]
    
    try:
        # 1. Fetch Mapping (Metadata: IDs to Names)
        logger.info("Extracting Item Mapping metadata")
        mapping_data = client.fetch(config["api"]["endpoints"]["mapping"])
        save_raw_json(mapping_data, bronze_root, "mapping")
        
        # 2. Fetch Latest Prices
        logger.info("Extracting Latest Market Prices snapshot")
        latest_data = client.fetch(config["api"]["endpoints"]["latest"])
        save_raw_json(latest_data, bronze_root, "latest")
        
        logger.success("Ingestion cycle complete: Bronze Layer ready.")
        
    finally:
        client.close()

if __name__ == "__main__":
    main()
