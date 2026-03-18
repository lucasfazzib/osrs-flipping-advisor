# 💰 OSRS Quant Market Intelligence Platform

> **A professional-grade Market Analytics Engine & Quantitative Flipping Platform for Old School RuneScape (OSRS).**

Built with the **Modern Data Stack**, this platform mimics high-frequency trading (HFT) environments used in Wall Street, but for the Grand Exchange. It uses a **Medallion Architecture** (Bronze, Silver, Gold) to process real-time market data into actionable trading signals.

---

## 🛠 The Tech Stack (The "Rockstar" Toolkit)

- **Language:** Python (Type-hinted, Staff Engineering standards)
- **Engine:** [Polars](https://pola.rs/) — A blazingly fast DataFrame library (Faster than Pandas).
- **Database:** [DuckDB](https://duckdb.org/) — The "SQLite for Analytics" (Zero-infrastructure OLAP).
- **Storage:** [Apache Parquet](https://parquet.apache.org/) — Columnar storage for efficient querying.
- **Logging:** [Loguru](https://github.com/Delgan/loguru) — Structured, production-ready logging.
- **Validation:** [Pydantic](https://docs.pydantic.dev/) & [YAML](https://yaml.org/) — Configuration management.

---

## 🏗 High-Level Architecture (Explained for a 10-Year-Old)

Imagine we are building a **Super-Spy Tool** to find the best deals in the RuneScape toy shop:

1.  **🥉 Bronze (The Messy Room):** We run into the shop, take a photo of every price tag, and throw the photos into a box. We don't change anything. If we ever argue about a price, we check the photo!
2.  **🥈 Silver (The Organizer):** We take the photos, write the names clearly on cards, and sort them by ID number. No more messy handwriting!
3.  **🥇 Gold (The Brain):** Our robot looks at the cards and calculates: *"If I buy this sword for 10 coins and sell it for 20, but the King takes 1 coin in tax... how much candy can I buy?"* This is where the magic happens.

---

## 🎨 Interactive Intelligence Dashboard (Streamlit)

The platform features a 2026-standard modern UI designed for both "Poor" and "Whale" players:

- **Budget Optimizer:** Automatically filters items based on your current GP. It won't suggest a 'Scythe of Vitur' if you only have 10,000 GP!
- **Liquidity Heatmaps:** Real-time Scatter plots showing the Risk (ROI) vs Reward (Liquidity).
- **Capital Allocation:** An "Intelligence" engine that tells you EXACTLY how much of your budget to spend on which items to maximize your hour-by-hour profit.

---

## 📊 Market Definitions & Financial Logic

As a **Staff Data Engineer**, the precision of your metrics matters. Here is how we define "Profit":

| Metric | Business Definition | Mathematical Formula |
| :--- | :--- | :--- |
| **Raw Spread** | The gap between the current highest "Buy" and "Sell" price. | $High - Low$ |
| **GE Tax** | The 1% fee taken by the Grand Exchange (introduced in 2021). | $\min(0.01 \times High, 5,000,000)$ |
| **Effective Spread** | The actual profit you keep after the taxman takes his share. | $High - Tax - Low$ |
| **ROI %** | Return on Investment. How much work your money is doing. | $(Effective Spread / Low) \times 100$ |
| **Limit Profit** | The max profit possible if you buy a full 4-hour limit. | $Effective Spread \times BuyLimit$ |

---

## 🚀 Getting Started

### 1. Setup Your Badge (User-Agent)
The OSRS Wiki API requires you to identify yourself. 
1. Open the [`.env`](.env) file.
2. Update `OSRS_USER_AGENT` to your contact info (e.g., `MyProject - @DiscordName`).

### 2. Install the Engine
```bash
pip install -r requirements.txt
```

### 3. Run the Pipeline
```bash
# Ingest raw data (Bronze)
python src/ingestion/extract_latest.py

# Clean and normalize (Silver)
python src/transformation/bronze_to_silver.py

# Calculate Market Opportunities (Gold)
python src/transformation/silver_to_gold.py
```

---


- **Idempotency:** Every ingestion is timestamped. We can "rewind" time and re-process any day in history.
- **Decoupling:** The API client doesn't care about the Database. The Database doesn't care about the API. We can swap DuckDB for Snowflake in 10 minutes.
- **Columnar Performance:** By using Parquet, we can scan 1 million rows of price data in the time it takes you to blink.
- **Error Resilience:** Real-world APIs fail. Our `WikiAPIClient` uses **Exponential Backoff** to retry requests if the server is busy.

---

*This is an open-source project designed for educational and quantitative analysis purposes. Happy flipping!*
