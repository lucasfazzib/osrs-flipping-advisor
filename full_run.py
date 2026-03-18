import sys, os
import runpy

sys.path.append(os.getcwd())

print("--- 1. INGESTION ---")
runpy.run_module('src.ingestion.extract_latest', run_name='__main__')

print("\n--- 2. BRONZE TO SILVER ---")
runpy.run_module('src.transformation.bronze_to_silver', run_name='__main__')

print("\n--- 3. SILVER TO GOLD ---")
runpy.run_module('src.transformation.silver_to_gold', run_name='__main__')

print("\n--- 4. QUANT & DB SYNC ---")
runpy.run_module('src.quant.liquidity_engine', run_name='__main__')
