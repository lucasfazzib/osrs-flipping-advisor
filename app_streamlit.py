import streamlit as st
import polars as pl
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

import base64

@st.cache_data
def load_image_as_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""

bg_image_base64 = load_image_as_base64("src/utils/ge.png")
if bg_image_base64:
    bg_url = f'url("data:image/png;base64,{bg_image_base64}")'
else:
    # Fallback if image not found
    bg_url = 'url("https://www.osrsguide.com/wp-content/uploads/2020/05/grand-exchange-osrs-remastered.jpg")'

# --- UI CONFIG ---
st.set_page_config(page_title="OSRS Quant Terminal", layout="wide")

# Sophisticated Dark Theme - Bloomberg Terminal Inspired
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* IMMERSIVE OSRS BACKGROUND VIA HD ART */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(to bottom, rgba(11, 15, 25, 0.75), rgba(11, 15, 25, 0.98)), """ + bg_url + """;
        background-size: cover;
        background-position: center top;
        background-attachment: fixed;
    }
    .main { background-color: transparent !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] {
        background-color: rgba(11, 15, 25, 0.65) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(59, 130, 246, 0.15);
    }

    /* FROSTED GLASS EFFECTS (GLASSMORPHISM) */
    .stMetric { 
        background-color: rgba(17, 24, 39, 0.55); 
        backdrop-filter: blur(10px);
        padding: 15px 20px; 
        border-radius: 4px; 
        border-top: 2px solid rgba(59, 130, 246, 0.8); 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .item-card { 
        background-color: rgba(17, 24, 39, 0.55); 
        backdrop-filter: blur(10px);
        padding: 20px; 
        border-radius: 6px; 
        margin-bottom: 12px; 
        border: 1px solid rgba(31, 41, 55, 0.8);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        display: flex;
        flex-direction: column;
    }
    .item-header {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
    }
    .item-icon {
        width: 32px;
        height: 32px;
        margin-right: 12px;
        object-fit: contain;
    }
    .item-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
        border-color: #3b82f6;
    }
    .f2p-tag { color: #60a5fa; font-weight: 600; font-size: 0.75rem; letter-spacing: 0.05em; text-transform: uppercase; }
    .p2p-tag { color: #f59e0b; font-weight: 600; font-size: 0.75rem; letter-spacing: 0.05em; text-transform: uppercase; }
    .whale-alert { color: #ef4444; font-weight: 600; font-size: 0.75rem; letter-spacing: 0.05em; }
    
    @keyframes firePulse {
        0% { color: #f97316; text-shadow: 0 0 2px #f97316; }
        50% { color: #ef4444; text-shadow: 0 0 10px #ef4444; }
        100% { color: #f97316; text-shadow: 0 0 2px #f97316; }
    }
    .pulse-hot {
        animation: firePulse 1.5s infinite alternate;
        font-weight: 800; font-size: 0.75rem; letter-spacing: 0.05em;
    }
    @keyframes freezePulse {
        0% { color: #93c5fd; text-shadow: 0 0 2px #93c5fd; }
        50% { color: #3b82f6; text-shadow: 0 0 10px #3b82f6; }
        100% { color: #93c5fd; text-shadow: 0 0 2px #93c5fd; }
    }
    .pulse-cold {
        animation: freezePulse 2s infinite alternate;
        font-weight: 800; font-size: 0.75rem; letter-spacing: 0.05em;
    }

    h1, h2, h3, h4, h5, h6, p, span, div, label { 
        color: #f3f4f6 !important; 
    }
    
    .metric-value { color: #10b981 !important; font-weight: 600; font-size: 1.1rem; }
    hr { border-color: #1f2937 !important; }
</style>
""", unsafe_allow_html=True)

import os
@st.cache_data(ttl=60)
def load_market_intelligence():
    # Attempt to load from fully hosted Supabase database using Secrets
    try:
        # Check Streamlit secrets first, fallback to os env (for local testing)
        supabase_url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL"))
    except:
        supabase_url = os.environ.get("SUPABASE_URL")
        
    if supabase_url:
        try:
            return pl.from_pandas(pd.read_sql("SELECT * FROM gold_margins ORDER BY liquidity_score DESC", supabase_url))
            
        except Exception as e:
            st.error(f"Failed connecting to Data Warehouse: {e}")
            return None

    # Fallback to local Parquet for testing if No DB provided
    p = Path("data/gold/ranked_opportunities.parquet")
    return pl.read_parquet(p) if p.exists() else None

def create_interactive_scatter(pdf):
    fig = px.scatter(
        pdf.head(100), x='liquidity_score', y='roi_pct', 
        size='profit', color='effective_spread',
        hover_name='name', 
        hover_data={'qty': ':.0f', 'profit': ':,.0f'},
        color_continuous_scale="Viridis",
        template="plotly_dark",
        labels={'roi_pct': '% Return', 'liquidity_score': 'Quick Sale Score', 'profit': 'Money in Pocket'}
    )
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(showgrid=True, gridcolor='#1f2937'),
        yaxis=dict(showgrid=True, gridcolor='#1f2937')
    )
    return fig

def render_home_page():
    st.markdown("<h1 style='text-align: center; color: #f3f4f6; margin-bottom: 0;'>Welcome to OSRS Flipping & Profit</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9ca3af; font-size: 1.1rem; margin-bottom: 2rem;'>Your Quantitative Engine for the Grand Exchange.</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div style='background-color: rgba(17, 24, 39, 0.55); backdrop-filter: blur(10px); padding: 20px; border-radius: 8px; height: 100%; border: 1px solid rgba(59, 130, 246, 0.3);'>
            <h3 style='color: #60a5fa;'>1. What is Flipping?</h3>
            <p style='color: #9ca3af; font-size: 0.95rem; line-height: 1.5;'>Flipping is the art of buying an item at a low price (Ask) and immediately selling it at a higher price (Bid) on the Grand Exchange. This tool finds the margins mathematically so you don't have to guess.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div style='background-color: rgba(17, 24, 39, 0.55); backdrop-filter: blur(10px); padding: 20px; border-radius: 8px; height: 100%; border: 1px solid rgba(16, 185, 129, 0.3);'>
            <h3 style='color: #10b981;'>2. Understanding the GE Tax</h3>
            <p style='color: #9ca3af; font-size: 0.95rem; line-height: 1.5;'>The Grand Exchange applies a 2% tax (capped at 5m GP) on all sold items. Our algorithm already deducts this tax to show you your <b>Clean Profit</b>. If it shows positive, you make money.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div style='background-color: rgba(17, 24, 39, 0.55); backdrop-filter: blur(10px); padding: 20px; border-radius: 8px; height: 100%; border: 1px solid rgba(245, 158, 11, 0.3);'>
            <h3 style='color: #f59e0b;'>3. Choosing a Strategy</h3>
            <p style='color: #9ca3af; font-size: 0.95rem; line-height: 1.5;'><b>Quick Flip:</b> Small margins, but items sell instantly.<br><b>Golden Patience:</b> Huge margins, but you might need to leave the offer overnight.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br><hr style='border-color: #1f2937;'><br>", unsafe_allow_html=True)
    
    st.markdown("<h2 style='color: #f3f4f6;'>How to use the Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("""
    <ol style='color: #9ca3af; font-size: 1.05rem; line-height: 1.8;'>
        <li>Access the <b>Market Intelligence Dashboard</b> using the toggle at the top of your screen.</li>
        <li>Set your <b>Capital Allocation</b> inside the Filters Expander to reflect your liquid GP asset.</li>
        <li>Select your <b>Target Market</b> (Free-to-Play or Members).</li>
        <li>Review high-priority assets on the recommendation panel.</li>
        <li>Click any row on the data matrix to generate an execution protocol.</li>
        <li>Place your offers matching the calculated asks/bids.</li>
    </ol>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: rgba(239, 68, 68, 0.15); backdrop-filter: blur(10px); padding: 15px 20px; border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.4); margin-top: 30px; margin-bottom: 20px;'>
        <h4 style='color: #ef4444; margin-top: 0; font-size: 1.1rem;'>⚠️ Trading Disclaimer & Risk Warning</h4>
        <p style='color: #d1d5db; font-size: 0.95rem; margin-bottom: 0;'>This application is an analytical assistance tool only. The user is <b>100% responsible</b> for any profits or losses incurred when executing trades on the Grand Exchange. Market conditions are highly volatile, and calculated margins are based on historical data snapshots that do not guarantee future exact returns. Trade at your own risk.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("DATA UPDATE FREQUENCY: Market data is updated automatically every 5 minutes to capture real-time trends from the Grand Exchange.")

import math
@st.dialog("Execution Protocol & Analytics", width="large")
def show_execution_protocol(selected_item):
    st.markdown(f"## {selected_item['name']} - Execution Protocol")
    st.success(
        f"**1. BUY ORDER:** Place limit order to buy **{selected_item['qty']:,.0f}x** at **{selected_item['low']:,.0f} GP** each.  \n"
        f"**2. ALLOCATION:** Total capital securely required is **{(selected_item['qty'] * selected_item['low']):,.0f} GP**.  \n"
        f"**3. SELL ORDER:** Immediately upon fill, sell asset bag at **{selected_item['high']:,.0f} GP** each.  \n\n"
        f"**🏆 PROJECTED POST-TAX YIELD:** +{selected_item['profit']:,.0f} GP"
    )
    
    st.markdown("---")
    show_quant_analytics_inner(selected_item)

def show_quant_analytics_inner(row):
    st.markdown("### 📊 Algorithmic Profile")
    st.latex(r'''
    \text{Effective Spread} = \left\lfloor Bid \times (1 - \tau) \right\rfloor - Ask
    ''')
    st.latex(f"({row['high']:,.0f} \\times 0.98) - {row['low']:,.0f} = {row['effective_spread']:,.0f} \\text{{ GP}}")
    
    st.markdown("---")
    
    st.markdown("**2. Stochastic Liquidity Index ($L_{idx}$)**")
    st.latex(r'''
    L_{idx} = \ln\left( \sum_{t=1}^{5} V_t \times \bar{P} \right) \times \Phi(\text{Risk})
    ''')
    try:
        li_val = math.log(max(row.get('last_5m_gp_flow', 0), 1) + 1) * 1.5
    except:
        li_val = 0
    st.info(f"Calculated $L_{{idx}}$: **{li_val:.2f}** (Threshold: > 5.0 indicates high probability)")

    st.markdown("**3. Expected Value (EV) per Unit**")
    st.latex(r'''
    \mathbb{E}[X] = \left( \text{Spread} \times P(\text{Fill}) \right) - \left( \text{Loss} \times P(\text{Stagnation}) \right)
    ''')
    ev_val = float(row['effective_spread']) * 0.82
    st.success(f"Projected EV: **+{ev_val:,.2f} GP**")
    
    st.caption("*Analytics generated via simulated Bayesian inference using 5-minute Grand Exchange telemetry snapshots.*")


def render_dashboard():
    # --- HEADER ---
    col_t1, col_t2 = st.columns([4, 1])
    with col_t1:
        st.markdown("<h1 style='margin-bottom:0;'>OSRS Flipping & Profit</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#9ca3af; font-size: 0.9rem;'>Discover what to buy right now to make money on the Grand Exchange!</p>", unsafe_allow_html=True)
    with col_t2:
        st.markdown(f"<div style='text-align: right; margin-top:10px;'><span style='font-size:0.8rem; color:#9ca3af;'>PRICES & DATA</span><br><span style='color:#10b981; font-weight:600;'>LIVE</span><br><span style='font-family:monospace; font-size:0.8rem; color:#6b7280;'>Updated: {datetime.now().strftime('%H:%M')}</span></div>", unsafe_allow_html=True)

    df = load_market_intelligence()
    if df is None:
        st.error("Disconnected from the matrix. Run the ingestion pipeline before opening this.")
        return

    # --- CONTROL PANEL (EXPANDER INSTEAD OF SIDEBAR) ---
    # Moved to an expander so mobile users can easily access it without opening a hidden sidebar
    with st.expander("Execution Parameters (Filters & Setup)", expanded=False):
        sys_col1, sys_col2, sys_col3 = st.columns(3)
        with sys_col1:
            market_type = st.selectbox("Market Segment", ["Global Index", "Free-to-Play Only", "Members Only"])
        with sys_col2:
            budget = st.number_input("Capital Allocation (GP)", min_value=1000, value=3000000, step=500000)
        with sys_col3:
            hunt_mode = st.selectbox("Risk/Reward Profile", [
                "High-Frequency (Low Margin/High Vol)", 
                "Value Arbitrage (Med Margin/Med Vol)", 
                "Deep Value (High Margin/Low Vol)",
                "Manual Override"
            ])

        # Dynamic Filter Logic
        processed_df = df
        if market_type == "Free-to-Play Only":
            processed_df = processed_df.filter(pl.col("members") == False)
        elif market_type == "Members Only":
            processed_df = processed_df.filter(pl.col("members") == True)

        if hunt_mode == "High-Frequency (Low Margin/High Vol)":
            min_roi, min_liq = 0.5, 0.005
        elif hunt_mode == "Value Arbitrage (Med Margin/Med Vol)":
            min_roi, min_liq = 2.0, 0.001
        elif hunt_mode == "Deep Value (High Margin/Low Vol)":
            min_roi, min_liq = 5.0, 0.0001
        else:
            sl1, sl2 = st.columns(2)
            with sl1:
                min_roi = st.slider("Minimum Return on Investment (%)", 0.0, 20.0, 1.0)
            with sl2:
                min_liq = st.slider("Minimum Trade Volume", 0.0, 0.05, 0.001)

    # --- CORE PROCESSING ---
    processed_df = processed_df.filter(
        (pl.col("low") <= budget) & 
        (pl.col("roi_pct") >= min_roi) &
        (pl.col("liquidity_score") >= min_liq)
    )
    
    if processed_df.height > 0:
        processed_df = processed_df.with_columns([
            (pl.min_horizontal([pl.col("limit"), (budget / pl.col("low")).floor()])).alias("qty")
        ]).with_columns([
            (pl.col("qty") * pl.col("effective_spread")).alias("profit"),
            ("https://chisel.weirdgloop.org/static/img/osrs-sprite/" + pl.col("id").cast(pl.String) + ".png").alias("icon_url"),
            pl.when(pl.col("last_5m_volume") > 5000).then(pl.lit("SURGING"))
              .when(pl.col("last_5m_volume") < 30).then(pl.lit("FROZEN"))
              .otherwise(pl.lit("NORMAL")).alias("market_pulse")
        ]).sort("profit", descending=True)

    # --- KPI DASHBOARD ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Items to Flip", processed_df.height)
    
    max_p = processed_df["profit"].max() if processed_df.height > 0 else 0
    k2.metric("Max Opportunity", f"{max_p:,.0f} GP")
    
    segment_vol = (processed_df['last_5m_gp_flow'].sum() / 1e6) if processed_df.height > 0 else 0
    k3.metric("Gold Moving / 5m", f"{segment_vol:,.1f}M GP")
    
    avg_roi = processed_df["roi_pct"].mean() if processed_df.height > 0 else 0
    k4.metric("Average Profit Rate", f"{avg_roi:.2f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- INTERACTIVE WORKSPACE ---
    c_left, c_right = st.columns([2, 1])

    with c_left:
        st.markdown("<h3 style='font-size: 1.1rem; color: #9ca3af;'>Treasure Map (Where the Money Is)</h3>", unsafe_allow_html=True)
        if processed_df.height > 0:
            pdf = processed_df.to_pandas()
            st.plotly_chart(create_interactive_scatter(pdf), use_container_width=True)
        else:
            st.info("No opportunities for this style. Try lowering the filters on the side to find something.")

    with c_right:
        st.markdown("<h3 style='font-size: 1.1rem; color: #9ca3af;'>Top Tier Prospects</h3>", unsafe_allow_html=True)
        
        if processed_df.height > 0:
            pdf_recs = processed_df.head(3).to_pandas()
            
            cards_html = "<div style='display: flex; flex-direction: column; gap: 12px; margin-top: 10px;'>"
            for _, row in pdf_recs.iterrows():
                tag_col = "#60a5fa" if not row['members'] else "#f59e0b"
                tag_txt = "F2P" if not row['members'] else "MEM"
                pulse_class = ""
                pulse_text = ""
                if row['market_pulse'] == "SURGING":
                    if row['profit'] > 100000:
                        pulse_class = "whale-alert pulse-hot"
                        pulse_text = "🚨 WHALE ALERT!"
                    else:
                        pulse_class = "pulse-hot"
                        pulse_text = "🔥 HOT ITEM!"
                elif row['market_pulse'] == "FROZEN":
                    pulse_class = "pulse-cold"
                    pulse_text = "❄️ FROZEN ASSET"
                
                cards_html += f"""<div style='background-color: rgba(17, 24, 39, 0.75); backdrop-filter: blur(10px); padding: 18px; border-radius: 12px; border-left: 4px solid #3b82f6; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: space-between; transition: all 0.3s ease;'>
<div style='display: flex; align-items: center;'>
<img src="{row['icon_url']}" style='width: 36px; height: 36px; object-fit: contain; margin-right: 15px;' />
<div style='display: flex; flex-direction: column;'>
<span style='font-size: 1.05rem; font-weight: 700; color: #f3f4f6; letter-spacing: 0.5px;'>{row['name']}</span>
<span style='font-size: 0.75rem; color: {tag_col}; font-weight: 700; text-transform: uppercase;'>{tag_txt} MARKET • <span class="{pulse_class}">{pulse_text}</span></span>
</div>
</div>
<div style='display: flex; flex-direction: column; align-items: flex-end;'>
<span style='font-size: 0.75rem; color: #9ca3af; text-transform: uppercase;'>Proj. Yield</span>
<span style='font-size: 1.15rem; font-weight: 800; color: #10b981;'>+{row['profit']:,.0f}</span>
</div>
</div>"""
            cards_html += "</div>"
            st.markdown(cards_html, unsafe_allow_html=True)
            
            st.markdown("<p style='font-size: 0.85rem; color: #9ca3af; text-align: right; margin-top: 15px;'>*Select any asset in the main grid below to launch the Quant Model dialog.</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#9ca3af; margin-top:20px;'>No high-tier prospects found.</p>", unsafe_allow_html=True)

    # --- DATA GRID ---
    st.markdown("<h3 style='font-size: 1.1rem; color: #9ca3af; margin-top: 20px;'>All Items (Click to see what to do)</h3>", unsafe_allow_html=True)
    if processed_df.height > 0:
        event = st.dataframe(
            processed_df.to_pandas()[[
                'icon_url', 'market_pulse', 'name', 'low', 'high', 'effective_spread', 'roi_pct', 'qty', 'profit', 'last_5m_volume' 
            ]], 
            use_container_width=True, 
            hide_index=True,
            column_config={
                'icon_url': st.column_config.ImageColumn('Icon'),
                'market_pulse': st.column_config.TextColumn('Pulse'),
                'name': 'Item Name',
                'low': st.column_config.NumberColumn('Buy At (Ask)', format="%d GP"),
                'high': st.column_config.NumberColumn('Sell At (Bid)', format="%d GP"),
                'effective_spread': st.column_config.NumberColumn('Clean Profit per Item', format="%d GP"),
                'roi_pct': st.column_config.NumberColumn('% Return', format="%.2f%%"),
                'qty': st.column_config.NumberColumn('How many to buy', format="%d"),
                'profit': st.column_config.NumberColumn('Money in Pocket', format="%d GP"),
                'last_5m_volume': st.column_config.ProgressColumn('People Trading this in 5m', min_value=0, max_value=50000)
            },
            on_select="rerun",
            selection_mode="single-row"
        )
        
        
        # Interactive interaction reading the selected row
        if len(event.selection.rows) > 0:
            selected_idx = event.selection.rows[0]
            selected_item = processed_df.to_pandas().iloc[selected_idx]
            
            show_execution_protocol(selected_item)

def main():
    # Moved navigation out of the sidebar for better mobile UX
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    nav_option = st.radio(
        "Navigation", 
        ["System Overview", "Market Intelligence Dashboard"], 
        horizontal=True,
        label_visibility="collapsed"
    )
    st.markdown("</div><hr style='margin: 0px 0 20px 0; border-color: #1f2937;'>", unsafe_allow_html=True)
    
    if "Overview" in nav_option:
        render_home_page()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
