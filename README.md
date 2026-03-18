# OSRS Flipping & Quantitative Engine ⚔️

A fully automated, end-to-end Data Engineering and Quantitative Analysis pipeline for *Old School RuneScape*. This toolkit extracts real-time Grand Exchange pricing telemetry, applies financial liquidity filters to find profitable arbitrage opportunities ("Flipping"), and serves them via a modern Web Dashboard.

##  Cloud-Native Architecture

This project is designed to run 24/7 autonomously using a Modern Data Stack:
1. **GitHub Actions (Cron Orchestrator):** Runs the ETL pipeline (`full_run.py`) every 5 minutes.
2. **OSRS Wiki API (Data Lake Source):** Extracts thousands of mapping data and 5-minute timeseries volumes.
3. **Polars & Python (Quant Engine):** Calculates effective spreads, subtracts the GE 1% Tax algorithmically, and generates Liquidity Scores.
4. **Supabase / PostgreSQL (Data Warehouse):** Live syncs the filtered subset of highly liquid, profitable gold margins using `psycopg2`.
5. **Streamlit Community Cloud (Frontend):** Renders the visual terminal, fetching data straight from the Supabase warehouse with 60-second TTL caching.

##  Live Demo
Access the live intelligence terminal here: **[https://osrs-flipping-advisor.streamlit.app/]**

---

##  Local Developer Setup

If you want to fork this project, run the pipeline locally, or hook it to your own Supabase instance, follow these steps.

### 1. Prerequisites
- Python 3.10+
- A free Supabase account (or any local PostgreSQL instance)

### 2. Installation
Clone the repo and configure your virtual environment:
```bash
git clone https://github.com/lucasfazzib/osrs-flipping-advisor.git
cd osrs-flipping-advisor

python -m venv .venv
source .venv/Scripts/activate  # On Unix use: source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create a file named `.env` in the root folder and add the following keys. The User-Agent is mandatory per the OSRS Wiki API guidelines.
```env
OSRS_USER_AGENT=OSRS Quant Platform - @YourDiscordOrGithubHandle
LOG_LEVEL=INFO
PYTHONPATH=./src

# Supabase (or any PostgreSQL instance) Connection String
SUPABASE_URL=postgresql://postgres.your_project_id:your_password@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
```

### 4. Running the Pipeline (Backend)
To manually execute the ingestion and algorithmic processes, run the full pipeline loop. This will fetch API data, calculate metrics, and push the final `gold_margins` to your database.
```bash
python full_run.py
```

### 5. Running the Terminal (Frontend)
To see the results in your local browser, fire up Streamlit:
```bash
streamlit run app_streamlit.py
```
This will open `localhost:8501` featuring your localized data matrix.

---

## ⚙️ Modifying Trading Parameters
You can adjust the boundaries of what the engine considers "profitable" or "liquid" by modifying `configs/settings.yaml`.
```yaml
quant:
  tax_rate: 0.01          # Standard Grand Exchange Tax (1%)
  tax_cap: 5000000        # GE Tax cap rules
  min_liquidity: 1000000  # Minimum 1,000,000 GP moved in the last 5 minutes to be listed
  min_spread_pct: 0.01    # Minimum required clean profit margin (1%)
```

## ⚠️ Disclaimer
This tool executes read-only operations. It does NOT interact with the local Runescape client, does not bot, and does not break Jagex ToS. 
Trading on the Grand Exchange involves risk, and this tool merely highlights mathematical arbitrage opportunities based on historical cache snapshots.

