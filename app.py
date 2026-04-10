import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text
import yfinance as yf
from yfinance.exceptions import YFRateLimitError
from datetime import datetime, timedelta
import time
from datetime import datetime
import pytz
ist = pytz.timezone("Asia/Kolkata")


# ===============================
# STREAMLIT CONFIG
# ===============================
st.set_page_config(
    page_title="Market Analytics Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# DESIGN SYSTEM
# ===============================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">

<style>
:root {
  --bg:          #080c12;
  --bg2:         #0d1320;
  --surface:     rgba(16, 22, 35, 0.85);
  --surface2:    rgba(22, 30, 46, 0.7);
  --border:      rgba(255, 255, 255, 0.06);
  --border-hi:   rgba(99, 179, 237, 0.4);
  --accent:      #63b3ed;
  --green:       #68d391;
  --red:         #fc8181;
  --yellow:      #f6e05e;
  --muted:       #5a6a82;
  --text:        #e2eaf4;
  --text-dim:    #8fa3bc;
  --mono:        'JetBrains Mono', monospace;
  --display:     'Syne', sans-serif;
}

/* ── GLOBAL ── */
.stApp {
  background: var(--bg);
  color: var(--text);
  font-family: var(--mono);
}

/* canvas noise overlay */
.stApp::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
  background-size: 200px;
  opacity: 0.4;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] {
  color: var(--text) !important;
}

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox,
section[data-testid="stSidebar"] .stMultiSelect {
  font-family: var(--mono) !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label { color: var(--text-dim) !important; font-size: 0.7rem !important; text-transform: uppercase; letter-spacing: 0.1em; }

/* ── SELECTBOX ── */
div[data-baseweb="select"] > div {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  font-family: var(--mono) !important;
  font-size: 0.82rem !important;
}
div[data-baseweb="select"]:focus-within > div {
  border-color: var(--border-hi) !important;
  box-shadow: 0 0 0 3px rgba(99,179,237,0.12) !important;
}

/* ── MULTISELECT ── */
div[data-baseweb="tag"] {
  background: rgba(99,179,237,0.15) !important;
  border: 1px solid rgba(99,179,237,0.3) !important;
  border-radius: 4px !important;
}

/* ── BUTTONS ── */
.stButton > button {
  background: transparent !important;
  border: 1px solid var(--border-hi) !important;
  border-radius: 6px !important;
  color: var(--accent) !important;
  font-family: var(--mono) !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.08em !important;
  transition: all 0.2s ease !important;
}
.stButton > button:hover {
  background: rgba(99,179,237,0.1) !important;
  box-shadow: 0 0 16px rgba(99,179,237,0.25) !important;
  transform: translateY(-1px) !important;
}

/* ── METRICS ── */
div[data-testid="metric-container"] {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 18px;
  transition: border-color 0.2s, transform 0.2s;
}
div[data-testid="metric-container"]:hover {
  border-color: var(--border-hi);
  transform: translateY(-2px);
}
div[data-testid="metric-container"] label {
  color: var(--muted) !important;
  font-family: var(--mono) !important;
  font-size: 0.68rem !important;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-family: var(--mono) !important;
  font-size: 1.15rem !important;
  font-weight: 500 !important;
  color: var(--text) !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
  font-family: var(--mono) !important;
  font-size: 0.78rem !important;
}

/* ── PLOTLY CONTAINER ── */
div[data-testid="stPlotlyChart"] {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
}

/* ── HEADINGS ── */
h1, h2, h3 {
  font-family: var(--display) !important;
  color: var(--text) !important;
  letter-spacing: -0.02em;
}

/* ── SIGNAL BADGE ── */
.signal-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-family: var(--mono);
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.signal-buy   { background: rgba(104,211,145,0.12); border: 1px solid rgba(104,211,145,0.35); color: #68d391; }
.signal-sell  { background: rgba(252,129,129,0.12); border: 1px solid rgba(252,129,129,0.35); color: #fc8181; }
.signal-hold  { background: rgba(246,224,94,0.12);  border: 1px solid rgba(246,224,94,0.35);  color: #f6e05e; }
.signal-wait  { background: rgba(90,106,130,0.15);  border: 1px solid rgba(90,106,130,0.35);  color: #8fa3bc; }

/* ── INFO ROW ── */
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.78rem;
}
.info-row:last-child { border-bottom: none; }
.info-label { color: var(--muted); text-transform: uppercase; letter-spacing: 0.07em; font-size: 0.68rem; }
.info-val   { color: var(--text); font-weight: 500; }

/* ── TICKER BAR ── */
.ticker-bar {
  display: flex;
  gap: 24px;
  overflow: hidden;
  padding: 10px 0 6px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
}
.ticker-item { display: flex; flex-direction: column; }
.ticker-name { font-size: 0.62rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; }
.ticker-price { font-size: 0.88rem; font-weight: 500; }
.ticker-up   { color: var(--green); }
.ticker-down { color: var(--red); }

/* ── SECTION HEADER ── */
.section-header {
  font-family: var(--display);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: var(--muted);
  margin: 20px 0 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}

/* ── RISK PILL ── */
.risk-pill {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.68rem;
  font-family: var(--mono);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.risk-low    { background: rgba(104,211,145,0.15); color: #68d391; border: 1px solid rgba(104,211,145,0.25); }
.risk-medium { background: rgba(246,224,94,0.15);  color: #f6e05e; border: 1px solid rgba(246,224,94,0.25); }
.risk-high   { background: rgba(252,129,129,0.15); color: #fc8181; border: 1px solid rgba(252,129,129,0.25); }

/* ── ALERT BOX ── */
.alert-box {
  background: rgba(246,224,94,0.06);
  border: 1px solid rgba(246,224,94,0.2);
  border-radius: 10px;
  padding: 12px 16px;
  font-size: 0.78rem;
  color: var(--yellow);
  margin-bottom: 10px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.alert-icon { font-size: 0.9rem; flex-shrink: 0; margin-top: 1px; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,179,237,0.25); border-radius: 10px; }

/* ── CAPTION ── */
.stCaption { color: var(--muted) !important; font-family: var(--mono) !important; font-size: 0.68rem !important; }

/* ── TABS ── */
button[data-baseweb="tab"] {
  font-family: var(--mono) !important;
  font-size: 0.75rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  color: var(--muted) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
  color: var(--accent) !important;
}

/* ── WALKTHROUGH CARDS ── */
.wt-card {
  background: rgba(16, 22, 35, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 20px 22px;
  margin-bottom: 14px;
  transition: border-color 0.2s, transform 0.2s;
}
.wt-card:hover {
  border-color: rgba(99,179,237,0.3);
  transform: translateY(-2px);
}
.wt-card-title {
  font-family: 'Syne', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  color: #e2eaf4;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.wt-card-icon {
  font-size: 1.1rem;
}
.wt-card-body {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  color: #8fa3bc;
  line-height: 1.7;
}
.wt-tag {
  display: inline-block;
  padding: 2px 9px;
  border-radius: 999px;
  font-size: 0.65rem;
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-right: 5px;
  margin-bottom: 4px;
}
.wt-tag-blue   { background: rgba(99,179,237,0.12);  border: 1px solid rgba(99,179,237,0.3);  color: #63b3ed; }
.wt-tag-green  { background: rgba(104,211,145,0.12); border: 1px solid rgba(104,211,145,0.3); color: #68d391; }
.wt-tag-yellow { background: rgba(246,224,94,0.12);  border: 1px solid rgba(246,224,94,0.3);  color: #f6e05e; }
.wt-tag-red    { background: rgba(252,129,129,0.12); border: 1px solid rgba(252,129,129,0.3); color: #fc8181; }
.wt-step {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.wt-step:last-child { border-bottom: none; }
.wt-step-num {
  min-width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(99,179,237,0.12);
  border: 1px solid rgba(99,179,237,0.3);
  color: #63b3ed;
  font-size: 0.7rem;
  font-family: 'JetBrains Mono', monospace;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}
.wt-step-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  color: #8fa3bc;
  line-height: 1.6;
}
.wt-step-text strong { color: #e2eaf4; }
.wt-disclaimer {
  background: rgba(252,129,129,0.05);
  border: 1px solid rgba(252,129,129,0.2);
  border-radius: 12px;
  padding: 16px 20px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.76rem;
  color: #fc8181;
  line-height: 1.6;
  margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# DATABASE CONNECTION
# ===============================
@st.cache_resource
def get_engine():
    return create_engine(
        "mysql+mysqlconnector://root:jwZjmQxvpUWSfMBBTsHIprLVjXNgybAD@mainline.proxy.rlwy.net:24726/railway",
        pool_pre_ping=True,
        pool_recycle=300
    )

engine = get_engine()

# ===============================
# SYMBOL CONFIG
# ===============================
TOP_INDIA_SYMBOLS = {
    "NIFTY 50":  "^NSEI",
    "SENSEX":    "^BSESN",
}

MARKETS = {
    "India 🇮🇳": {
        "Reliance":      "RELIANCE.NS",
        "TCS":           "TCS.NS",
        "Infosys":       "INFY.NS",
        "Sun Pharma":    "SUNPHARMA.NS",
        "Dr Reddy's":    "DRREDDY.NS",
        "3M India":      "3MINDIA.NS",
        "MRF":           "MRF.NS",
        "Tata Steel":    "TATASTEEL.NS",
        "IDFC First Bank": "IDFCFIRSTB.NS",
        "HDFC Bank":     "HDFCBANK.NS",
        "Wipro":         "WIPRO.NS",
        "Bajaj Finance": "BAJFINANCE.NS",
    }
}

INTERVAL_CONFIG = {
    "15 Minutes": ("15m",  "7 DAY"),
    "1 Hour":     ("1h",   "30 DAY"),
    "1 Day":      ("1d",   None),
    "1 Week":     ("1wk",  None),
}

DEFAULT_PERIOD = "1y"

# ===============================
# AUTO-REFRESH STATE
# ===============================
if "last_refresh" not in st.session_state:
    ist = pytz.timezone("Asia/Kolkata")
    st.session_state.last_refresh = datetime.now(ist)
    
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

# ===============================
# DATA PIPELINE
# ===============================
def fetch_and_store(symbol: str, interval: str) -> bool:
    """Fetch from Yahoo Finance and upsert into DB. Returns True on success."""
    try:
        df = yf.Ticker(symbol).history(period=DEFAULT_PERIOD, interval=interval)
    except YFRateLimitError:
        st.warning("⚠ Yahoo Finance rate limit hit. Try again in a moment.")
        return False
    except Exception as e:
        st.warning(f"⚠ Fetch error for {symbol}: {e}")
        return False

    if df.empty:
        return False

    df = df.reset_index()
    df.rename(columns={
        "Datetime": "timestamp", "Date": "timestamp",
        "Open": "open_price", "High": "high_price",
        "Low": "low_price", "Close": "close_price",
        "Volume": "volume"
    }, inplace=True)

    df["symbol"] = symbol
    df = df[["symbol", "timestamp", "open_price", "high_price", "low_price", "close_price", "volume"]]
    df = df.dropna(subset=["open_price", "close_price"])
    df.drop_duplicates(subset=["symbol", "timestamp"], inplace=True)

    try:
        df.to_sql("stock_prices", engine, if_exists="append", index=False)
    except Exception:
        # Duplicate rows — silently skip
        pass

    return True


def ensure_initial_data():
    """Bootstrap DB if empty."""
    try:
        count = pd.read_sql("SELECT COUNT(*) AS c FROM stock_prices", engine)["c"][0]
    except Exception:
        count = 0

    if count == 0:
        with st.spinner("Bootstrapping database with initial data…"):
            for sym in ["^NSEI", "^BSESN", "TCS.NS", "RELIANCE.NS"]:
                fetch_and_store(sym, "1d")

ensure_initial_data()

# ===============================
# DB HELPERS
# ===============================
def load_stock(symbol: str, interval_sql_limit=None) -> pd.DataFrame:
    if interval_sql_limit:
        query = f"""
            SELECT * FROM stock_prices
            WHERE symbol='{symbol}'
            AND timestamp >= NOW() - INTERVAL {interval_sql_limit}
            ORDER BY timestamp
        """
    else:
        query = f"SELECT * FROM stock_prices WHERE symbol='{symbol}' ORDER BY timestamp"
    return pd.read_sql(query, engine)


def get_snapshot(symbol: str):
    """Return (latest_price, change, pct_change) or None."""
    df = pd.read_sql(
        f"SELECT close_price FROM stock_prices WHERE symbol='{symbol}' ORDER BY timestamp DESC LIMIT 2",
        engine
    )
    if len(df) < 2:
        return None
    latest = float(df.iloc[0]["close_price"])
    prev   = float(df.iloc[1]["close_price"])
    return round(latest, 2), round(latest - prev, 2), round((latest - prev) / prev * 100, 3)


# ===============================
# TECHNICAL INDICATORS
# ===============================
def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    c = df["close_price"]

    df["SMA20"]  = c.rolling(20).mean()
    df["SMA50"]  = c.rolling(50).mean()
    df["SMA200"] = c.rolling(200).mean()
    df["EMA20"]  = c.ewm(span=20, adjust=False).mean()
    df["EMA50"]  = c.ewm(span=50, adjust=False).mean()

    # Bollinger Bands
    df["BB_mid"]   = c.rolling(20).mean()
    df["BB_upper"] = df["BB_mid"] + 2 * c.rolling(20).std()
    df["BB_lower"] = df["BB_mid"] - 2 * c.rolling(20).std()

    # RSI
    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - 100 / (1 + rs)

    # MACD
    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    df["MACD"]        = ema12 - ema26
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_hist"]   = df["MACD"] - df["MACD_signal"]

    # VWAP (daily reset approximation)
    df["VWAP"] = (
        (df["close_price"] * df["volume"]).cumsum() / df["volume"].cumsum()
    )

    # ATR
    hl  = df["high_price"] - df["low_price"]
    hc  = (df["high_price"] - df["close_price"].shift()).abs()
    lc  = (df["low_price"]  - df["close_price"].shift()).abs()
    df["ATR"] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean()

    return df


def analyze(df: pd.DataFrame):
    latest = df.iloc[-1]
    c  = latest["close_price"]
    s50  = latest.get("SMA50",  np.nan)
    s200 = latest.get("SMA200", np.nan)
    rsi  = latest.get("RSI",    np.nan)
    macd = latest.get("MACD",   np.nan)
    sig  = latest.get("MACD_signal", np.nan)
    atr  = latest.get("ATR",    np.nan)

    support    = float(df["low_price"].rolling(20).min().iloc[-1])
    resistance = float(df["high_price"].rolling(20).max().iloc[-1])

    mean20 = float(df["close_price"].rolling(20).mean().iloc[-1])
    std20  = float(df["close_price"].rolling(20).std().iloc[-1])
    forecast_low  = round(mean20 - std20, 2)
    forecast_high = round(mean20 + std20, 2)

    # Trend
    if c > s50 and s50 > s200:
        trend, strength = "Bullish",  "Strong"
    elif c < s50 and s50 < s200:
        trend, strength = "Bearish",  "Strong"
    elif c > s50:
        trend, strength = "Bullish",  "Moderate"
    elif c < s50:
        trend, strength = "Bearish",  "Moderate"
    else:
        trend, strength = "Sideways", "Weak"

    # RSI zone
    rsi_zone = "Overbought" if rsi > 70 else ("Oversold" if rsi < 30 else "Neutral")

    # Risk (ATR / price)
    if not np.isnan(atr) and c > 0:
        vol_pct = atr / c * 100
        risk = "High" if vol_pct > 3 else ("Medium" if vol_pct > 1.5 else "Low")
    else:
        risk = "Unknown"

    # Suggested action
    near_support    = abs(c - support)    / c < 0.02
    near_resistance = abs(c - resistance) / c < 0.02
    macd_bullish    = (not np.isnan(macd)) and macd > sig

    if trend == "Bullish" and rsi < 65 and macd_bullish and not near_resistance:
        action = "Buy"
    elif trend == "Bearish" and rsi > 40:
        action = "Wait"
    elif near_resistance and rsi > 65:
        action = "Sell"
    elif trend == "Bullish" and near_resistance:
        action = "Hold"
    else:
        action = "Hold"

    # Alerts
    alerts = []
    if near_support:
        alerts.append("📍 Price near 20-day support zone")
    if near_resistance:
        alerts.append("🚧 Price approaching 20-day resistance")
    if rsi_zone == "Overbought":
        alerts.append("⚡ RSI overbought — momentum may fade")
    if rsi_zone == "Oversold":
        alerts.append("🔋 RSI oversold — watch for reversal")
    if not np.isnan(macd) and abs(macd - sig) < 0.05 * abs(macd + 0.001):
        alerts.append("🔀 MACD crossover zone detected")

    return {
        "trend":       trend,
        "strength":    strength,
        "rsi":         round(rsi, 1) if not np.isnan(rsi) else "N/A",
        "rsi_zone":    rsi_zone,
        "macd":        round(macd, 3) if not np.isnan(macd) else "N/A",
        "risk":        risk,
        "action":      action,
        "support":     round(support, 2),
        "resistance":  round(resistance, 2),
        "forecast_low":  forecast_low,
        "forecast_high": forecast_high,
        "alerts":      alerts,
    }


# ===============================
# CHART BUILDERS
# ===============================
DARK = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="JetBrains Mono, monospace", size=11, color="#8fa3bc"),
    margin=dict(l=12, r=12, t=32, b=12),
)

def build_main_chart(df, selected_indicators):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.60, 0.20, 0.20],
        vertical_spacing=0.03,
        subplot_titles=("", "Volume", "MACD")
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df["timestamp"],
        open=df["open_price"], high=df["high_price"],
        low=df["low_price"],   close=df["close_price"],
        increasing_line_color="#68d391", decreasing_line_color="#fc8181",
        increasing_fillcolor="rgba(104,211,145,0.7)",
        decreasing_fillcolor="rgba(252,129,129,0.7)",
        name="OHLC",
        line_width=1
    ), row=1, col=1)

    # SMAs
    if "SMA 20" in selected_indicators:
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["SMA20"], name="SMA 20"))

    if "SMA 50" in selected_indicators:
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["SMA50"], name="SMA 50"))

    if "SMA 200" in selected_indicators:
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["SMA200"], name="SMA 200"))

    if "EMA 20" in selected_indicators:
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["EMA20"],
            name="EMA 20"
        ), row=1, col=1)

    # Bollinger Bands
    if "Bollinger Bands" in selected_indicators and "BB_upper" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["BB_upper"],
            name="BB Upper", line=dict(dash="dot", width=1, color="#718096"),
            showlegend=False
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["BB_lower"],
            name="BB Lower", line=dict(dash="dot", width=1, color="#718096"),
            fill="tonexty", fillcolor="rgba(113,128,150,0.05)",
            showlegend=False
        ), row=1, col=1)

    # VWAP
    if "VWAP" in selected_indicators and "VWAP" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["VWAP"],
            name="VWAP", line=dict(dash="dash", width=1.2, color="#ed8936"),
            opacity=0.75
        ), row=1, col=1)

    # Forecast band
    mean20 = float(df["close_price"].rolling(20).mean().iloc[-1])
    std20  = float(df["close_price"].rolling(20).std().iloc[-1])
    fig.add_hrect(
        y0=mean20 - std20, y1=mean20 + std20,
        fillcolor="rgba(99,179,237,0.05)", line_width=0,
        row=1, col=1
    )

    # Volume bars
    colors = ["rgba(104,211,145,0.6)" if c >= o else "rgba(252,129,129,0.6)"
              for c, o in zip(df["close_price"], df["open_price"])]
    fig.add_trace(go.Bar(
        x=df["timestamp"], y=df["volume"],  
        marker_color=colors, name="Volume", showlegend=False
    ), row=2, col=1)

    # MACD
    if "MACD" in df.columns:
        hist_colors = ["rgba(104,211,145,0.7)" if v >= 0 else "rgba(252,129,129,0.7)"
                       for v in df["MACD_hist"]]
        fig.add_trace(go.Bar(
            x=df["timestamp"], y=df["MACD_hist"],
            marker_color=hist_colors, name="MACD Hist", showlegend=False
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["MACD"],
            name="MACD", line=dict(width=1.2, color="#63b3ed")
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["MACD_signal"],
            name="Signal", line=dict(width=1.2, color="#f6e05e")
        ), row=3, col=1)

    fig.update_layout(
        **DARK,
        height=680,
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01,
            xanchor="left", x=0,
            font=dict(size=10), bgcolor="rgba(0,0,0,0)"
        )
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.04)", zeroline=False)

    return fig


def build_rsi_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["RSI"],
        fill="tozeroy", fillcolor="rgba(99,179,237,0.08)",
        line=dict(width=1.5, color="#63b3ed"), name="RSI"
    ))
    fig.add_hline(y=70, line_dash="dot", line_color="#fc8181", opacity=0.6, annotation_text="70")
    fig.add_hline(y=30, line_dash="dot", line_color="#68d391", opacity=0.6, annotation_text="30")
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(252,129,129,0.05)", line_width=0)
    fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(104,211,145,0.05)", line_width=0)
    fig.update_layout(**DARK, height=220, title="RSI (14)", showlegend=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(range=[0, 100], showgrid=True, gridcolor="rgba(255,255,255,0.04)")
    return fig


def build_comparison_chart(symbols_map: dict):
    """Normalised price comparison (base=100)."""
    fig = go.Figure()
    COLORS = ["#63b3ed", "#68d391", "#f6e05e", "#fc8181", "#9f7aea", "#ed8936"]

    for i, (name, sym) in enumerate(symbols_map.items()):
        df = load_stock(sym)
        if df.empty:
            continue
        base = df["close_price"].iloc[0]
        normalised = df["close_price"] / base * 100
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=normalised,
            name=name, line=dict(width=1.5, color=COLORS[i % len(COLORS)])
        ))

    fig.add_hline(y=100, line_dash="dot", line_color="#5a6a82", opacity=0.5)
    fig.update_layout(**DARK, height=380, title="Relative Performance (base = 100)")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.04)")
    return fig


# ===============================
# SIDEBAR
# ===============================
st.sidebar.markdown("### ⚡ Market Analytics Dashboard")
st.sidebar.markdown("<div style='font-size:0.65rem;color:#5a6a82;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:16px;'>Market Intelligence</div>", unsafe_allow_html=True)

market      = st.sidebar.selectbox("Market", list(MARKETS.keys()))
stock_name  = st.sidebar.selectbox("Stock", list(MARKETS[market].keys()))
symbol      = MARKETS[market][stock_name]

interval_label = st.sidebar.selectbox("Interval", list(INTERVAL_CONFIG.keys()), index=2)
interval, sql_limit = INTERVAL_CONFIG[interval_label]

# Indicators (move here)
st.sidebar.markdown("---")
st.sidebar.markdown("#### Indicators")

indicator_options = st.sidebar.multiselect(
    "Select Indicators",
    ["SMA 20", "SMA 50", "SMA 200", "EMA 20", "VWAP", "Bollinger Bands"],
    default=["SMA 20", "EMA 20"]
)

# Chart overlays
#st.sidebar.markdown("---")

# Multi-stock comparison
st.sidebar.markdown("---")
compare_names = st.sidebar.multiselect(
    "Compare Stocks",
    [n for n in MARKETS[market].keys() if n != stock_name],
    max_selections=4
)

# Auto-refresh
st.sidebar.markdown("---")
auto_refresh = st.sidebar.toggle("Auto-Refresh (2 min)", value=st.session_state.auto_refresh)
st.session_state.auto_refresh = auto_refresh

if st.sidebar.button("🔄 Refresh Now"):
    with st.spinner(f"Fetching {stock_name}…"):
        fetch_and_store(symbol, interval)
        for idx_sym in TOP_INDIA_SYMBOLS.values():
            fetch_and_store(idx_sym, "1d")
    st.session_state.last_refresh = datetime.now(ist)
    st.rerun()

elapsed = (datetime.now(ist) - st.session_state.last_refresh).seconds
st.sidebar.markdown(
    f"<div style='font-size:0.65rem;color:#5a6a82;margin-top:8px;'>Last refresh: {elapsed}s ago</div>",
    unsafe_allow_html=True
)



    # ── Auto-refresh logic
    if auto_refresh and elapsed >= 120:
        fetch_and_store(symbol, interval)
        st.session_state.last_refresh = datetime.now(ist)
        st.rerun()


# ===============================
# LOAD & PROCESS DATA
# ===============================
df = load_stock(symbol, sql_limit)

if df.empty:
    st.warning(f"No data for {stock_name}. Click **Refresh Now** to fetch.")
    st.stop()

df = compute_indicators(df)
analysis = analyze(df)
latest_price = round(float(df["close_price"].iloc[-1]), 2)

# ===============================
# HEADER
# ===============================
st.markdown(
    f"""
    <div style="display:flex;align-items:baseline;gap:14px;margin-bottom:4px;">
      <span style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:#e2eaf4;">{stock_name}</span>
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#5a6a82;text-transform:uppercase;letter-spacing:0.1em;">{symbol} · {interval_label}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Market snapshot bar
cols_snap = st.columns(len(TOP_INDIA_SYMBOLS) + 1)
for col, (name, sym) in zip(cols_snap, TOP_INDIA_SYMBOLS.items()):
    snap = get_snapshot(sym)
    with col:
        if snap:
            p, ch, pct = snap
            color = "#68d391" if ch >= 0 else "#fc8181"
            arrow = "▲" if ch >= 0 else "▼"
            st.markdown(
                f"""<div style="background:rgba(16,22,35,0.8);border:1px solid rgba(255,255,255,0.06);
                    border-radius:10px;padding:10px 14px;">
                  <div style="font-size:0.62rem;color:#5a6a82;text-transform:uppercase;letter-spacing:0.1em;">{name}</div>
                  <div style="font-size:1rem;font-weight:600;color:#e2eaf4;font-family:'JetBrains Mono',monospace;">{p:,.2f}</div>
                  <div style="font-size:0.72rem;color:{color};font-family:'JetBrains Mono',monospace;">{arrow} {abs(pct):.2f}%</div>
                </div>""",
                unsafe_allow_html=True
            )

# Current stock quick bar
with cols_snap[-1]:
    snap_stock = get_snapshot(symbol)
    if snap_stock:
        p, ch, pct = snap_stock
        color = "#68d391" if ch >= 0 else "#fc8181"
        arrow = "▲" if ch >= 0 else "▼"
        st.markdown(
            f"""<div style="background:rgba(16,22,35,0.8);border:1px solid rgba(99,179,237,0.2);
                border-radius:10px;padding:10px 14px;">
              <div style="font-size:0.62rem;color:#63b3ed;text-transform:uppercase;letter-spacing:0.1em;">{stock_name}</div>
              <div style="font-size:1rem;font-weight:600;color:#e2eaf4;font-family:'JetBrains Mono',monospace;">₹{p:,.2f}</div>
              <div style="font-size:0.72rem;color:{color};font-family:'JetBrains Mono',monospace;">{arrow} {abs(pct):.2f}%</div>
            </div>""",
            unsafe_allow_html=True
        )

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ===============================
# TABS
# ===============================
tab1, tab2, tab3, tab4 = st.tabs(["📈  Chart", "📊  RSI / Oscillators", "⚖  Compare", "📘  Walkthrough"])

with tab1:
    left, right = st.columns([4, 1.6])

    with left:
        fig = build_main_chart(df, indicator_options)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        # Alerts
        if analysis["alerts"]:
            st.markdown("<div class='section-header'>Alerts</div>", unsafe_allow_html=True)
            for a in analysis["alerts"]:
                st.markdown(f"<div class='alert-box'><span class='alert-icon'>⚡</span>{a}</div>", unsafe_allow_html=True)

        # Action badge
        action = analysis["action"]
        badge_cls = {
            "Buy": "signal-buy", "Sell": "signal-sell",
            "Hold": "signal-hold", "Wait": "signal-wait"
        }.get(action, "signal-wait")
        icon = {"Buy": "↑", "Sell": "↓", "Hold": "⟳", "Wait": "◌"}.get(action, "•")
        st.markdown(
            f"""<div style='margin:12px 0 16px;'>
              <div style='font-size:0.62rem;color:#5a6a82;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;'>Suggested Action</div>
              <span class='signal-badge {badge_cls}'>{icon} {action}</span>
            </div>""",
            unsafe_allow_html=True
        )

        # KPI metrics
        st.markdown("<div class='section-header'>Key Metrics</div>", unsafe_allow_html=True)

        m1, m2 = st.columns(2)
        with m1:
            st.metric("Price",    f"₹{latest_price:,.2f}")
            st.metric("Trend",    analysis["trend"])
            st.metric("RSI",      analysis["rsi"])
        with m2:
            st.metric("Support",     f"₹{analysis['support']:,}")
            st.metric("Resistance",  f"₹{analysis['resistance']:,}")
            rsk = analysis["risk"]
            risk_cls = {"Low": "risk-low", "Medium": "risk-medium", "High": "risk-high"}.get(rsk, "")
            st.markdown(
                f"<div style='margin-top:4px;'><div style='font-size:0.65rem;color:#5a6a82;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:5px;'>Risk Level</div>"
                f"<span class='risk-pill {risk_cls}'>{rsk}</span></div>",
                unsafe_allow_html=True
            )

        st.markdown("<div class='section-header'>Forecast Band</div>", unsafe_allow_html=True)
        st.markdown(
            f"""<div style='background:rgba(99,179,237,0.06);border:1px solid rgba(99,179,237,0.15);
                border-radius:10px;padding:12px 14px;font-family:"JetBrains Mono",monospace;'>
              <div style='font-size:0.65rem;color:#5a6a82;margin-bottom:4px;'>Statistical (1σ)</div>
              <div style='font-size:0.9rem;color:#e2eaf4;'>₹{analysis['forecast_low']:,} – ₹{analysis['forecast_high']:,}</div>
            </div>""",
            unsafe_allow_html=True
        )

        st.markdown("<div class='section-header'>Indicators</div>", unsafe_allow_html=True)
        rows = [
            ("Momentum",   analysis["strength"]),
            ("RSI Zone",   analysis["rsi_zone"]),
            ("MACD",       str(analysis["macd"])),
        ]
        for label, val in rows:
            st.markdown(
                f"<div class='info-row'><span class='info-label'>{label}</span><span class='info-val'>{val}</span></div>",
                unsafe_allow_html=True
            )


with tab2:
    st.plotly_chart(build_rsi_chart(df), use_container_width=True)

    # MACD standalone
    fig_macd = go.Figure()
    if "MACD" in df.columns:
        hist_colors = ["rgba(104,211,145,0.7)" if v >= 0 else "rgba(252,129,129,0.7)" for v in df["MACD_hist"]]
        fig_macd.add_trace(go.Bar(x=df["timestamp"], y=df["MACD_hist"], marker_color=hist_colors, name="Histogram", showlegend=False))
        fig_macd.add_trace(go.Scatter(x=df["timestamp"], y=df["MACD"],        name="MACD",   line=dict(width=1.5, color="#63b3ed")))
        fig_macd.add_trace(go.Scatter(x=df["timestamp"], y=df["MACD_signal"], name="Signal", line=dict(width=1.5, color="#f6e05e")))
    fig_macd.update_layout(**DARK, height=280, title="MACD (12, 26, 9)")
    fig_macd.update_xaxes(showgrid=False)
    fig_macd.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.04)")
    st.plotly_chart(fig_macd, use_container_width=True)


with tab3:
    if not compare_names:
        st.info("Select stocks in the sidebar **Compare Stocks** to compare relative performance.")
    else:
        compare_map = {stock_name: symbol}
        for n in compare_names:
            compare_map[n] = MARKETS[market][n]
            fetch_and_store(MARKETS[market][n], interval)

        st.plotly_chart(build_comparison_chart(compare_map), use_container_width=True)

        # Summary table
        rows = []
        for n, sym in compare_map.items():
            snap = get_snapshot(sym)
            if snap:
                p, ch, pct = snap
                rows.append({"Stock": n, "Price (₹)": p, "Change": ch, "Change %": f"{pct:+.2f}%"})
        if rows:
            tdf = pd.DataFrame(rows).set_index("Stock")
            st.dataframe(tdf, use_container_width=True)


# ===============================
# WALKTHROUGH TAB
# ===============================
with tab4:

    # ── Hero
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(99,179,237,0.08) 0%,rgba(104,211,145,0.05) 100%);
                border:1px solid rgba(99,179,237,0.18);border-radius:16px;padding:28px 30px;margin-bottom:28px;">
      <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#e2eaf4;margin-bottom:8px;">
        📘 Dashboard Walkthrough
      </div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.82rem;color:#8fa3bc;line-height:1.7;max-width:720px;">
        A complete guide to every feature, panel, and indicator in the Market Analytics Dashboard.
        Use this page to understand what each tool does and how to read the signals it produces.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Section: Key Features
    st.markdown("<div class='section-header'>⚙ Key Features</div>", unsafe_allow_html=True)

    feat_col1, feat_col2 = st.columns(2)

    with feat_col1:
        st.markdown("""
        <div class='wt-card'>
          <div class='wt-card-title'><span class='wt-card-icon'>📡</span> Live Data via Yahoo Finance</div>
          <div class='wt-card-body'>
            Price data is pulled directly from Yahoo Finance using the <code>yfinance</code> library.
            Supports multiple timeframes from 15-minute intraday bars to weekly candles.
            Hit <strong>Refresh Now</strong> in the sidebar or enable <strong>Auto-Refresh</strong> to keep data current.
          </div>
        </div>
        <div class='wt-card'>
          <div class='wt-card-title'><span class='wt-card-icon'>🗄️</span> Persistent Database Storage</div>
          <div class='wt-card-body'>
            All fetched OHLCV data is stored in a MySQL database on Railway. This means the dashboard
            loads instantly from cached data and only calls Yahoo Finance when you explicitly refresh.
            Historical data accumulates over time for richer analysis.
          </div>
        </div>
        <div class='wt-card'>
          <div class='wt-card-title'><span class='wt-card-icon'>🧠</span> Automated Signal Engine</div>
          <div class='wt-card-body'>
            The dashboard computes a <strong>suggested action</strong> (Buy / Sell / Hold / Wait) by combining
            trend direction, RSI momentum, MACD crossover state, and proximity to support/resistance.
            It is a rule-based heuristic — not a guaranteed prediction.
          </div>
        </div>
        """, unsafe_allow_html=True)

    with feat_col2:
        st.markdown("""
        <div class='wt-card'>
          <div class='wt-card-title'><span class='wt-card-icon'>📊</span> Interactive Candlestick Chart</div>
          <div class='wt-card-body'>
            The main chart renders full OHLC candlesticks with volume bars and MACD subplot.
            Overlay any combination of SMA, EMA, VWAP, and Bollinger Bands from the sidebar.
            A shaded <strong>1σ forecast band</strong> shows the statistical price range based on the last 20 bars.
          </div>
        </div>
        <div class='wt-card'>
          <div class='wt-card-title'><span class='wt-card-icon'>⚠️</span> Smart Alerts Panel</div>
          <div class='wt-card-body'>
            Real-time alerts fire when the price enters a support/resistance zone, RSI crosses into
            overbought or oversold territory, or a MACD crossover is imminent. Alerts appear
            automatically in the right panel of the Chart tab — no configuration needed.
          </div>
        </div>
        <div class='wt-card'>
          <div class='wt-card-title'><span class='wt-card-icon'>⚖️</span> Multi-Stock Comparison</div>
          <div class='wt-card-body'>
            Select up to 4 additional stocks from the sidebar to compare relative performance.
            All series are normalised to a base of 100 so you can see which stock has gained or
            lost the most since the start of the stored history. A summary table lists latest prices and changes.
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Section: Indicators Explained
    st.markdown("<div class='section-header'>📈 Indicators Explained</div>", unsafe_allow_html=True)

    ind_col1, ind_col2 = st.columns(2)

    with ind_col1:
        st.markdown("""
        <div class='wt-card'>
          <div class='wt-card-title'><span class='wt-card-icon'>〰️</span> SMA — Simple Moving Average</div>
          <div class='wt-card-body'>
            <div style="margin-bottom:8px;">
              <span class='wt-tag wt-tag-blue'>SMA 20</span>
              <span class='wt-tag wt-tag-blue'>SMA 50</span>
              <span class='wt-tag wt-tag-blue'>SMA 200</span>
            </div>
            The SMA is the plain arithmetic average of closing prices over N periods. It smooths out
            short-term noise to reveal the underlying trend direction.<br><br>
            <strong>How to read it:</strong><br>
            • Price <strong>above</strong> SMA → bullish bias<br>
            • Price <strong>below</strong> SMA → bearish bias<br>
            • SMA 50 crossing above SMA 200 = <em>Golden Cross</em> (bullish)<br>
            • SMA 50 crossing below SMA 200 = <em>Death Cross</em> (bearish)
          </div>
        </div>

        <div class='wt-card'>
          <div class='wt-card-title'><span class='wt-card-icon'>〽️</span> EMA — Exponential Moving Average</div>
          <div class='wt-card-body'>
            <div style="margin-bottom:8px;">
              <span class='wt-tag wt-tag-green'>EMA 20</span>
              <span class='wt-tag wt-tag-green'>EMA 50</span>
            </div>
            The EMA applies exponentially more weight to recent candles, making it respond faster
            than the SMA to new price action. Preferred by short-term traders.<br><br>
            <strong>How to read it:</strong><br>
            • EMA reacts quicker to reversals than SMA<br>
            • Price bouncing off EMA 20 = dynamic support<br>
            • EMA 20 crossing EMA 50 upward = short-term bullish signal
          </div>
        </div>

        <div class='wt-card'>
          <div class='wt-card-title'><span class='wt-card-icon'>📏</span> Bollinger Bands</div>
          <div class='wt-card-body'>
            <div style="margin-bottom:8px;">
              <span class='wt-tag wt-tag-yellow'>Upper Band</span>
              <span class='wt-tag wt-tag-yellow'>Mid (SMA 20)</span>
              <span class='wt-tag wt-tag-yellow'>Lower Band</span>
            </div>
            Bollinger Bands consist of a 20-period SMA (middle) flanked by bands set ±2 standard
            deviations away. They expand during high volatility and contract during consolidation.<br><br>
            <strong>How to read it:</strong><br>
            • Price touching <strong>upper band</strong> → potentially overbought<br>
            • Price touching <strong>lower band</strong> → potentially oversold<br>
            • Bands squeezing tight → volatility breakout likely incoming
          </div>
        </div>
        """, unsafe_allow_html=True)

    with ind_col2:
        st.markdown("""
        <div class='wt-card'>
          <div class='wt-card-title'><span class='wt-card-icon'>💧</span> VWAP — Volume Weighted Avg Price</div>
          <div class='wt-card-body'>
            <div style="margin-bottom:8px;">
              <span class='wt-tag wt-tag-yellow'>Intraday</span>
              <span class='wt-tag wt-tag-blue'>Institutional Reference</span>
            </div>
            VWAP calculates the average price weighted by volume traded at each price level. It is the
            benchmark used by institutional desks to evaluate execution quality.<br><br>
            <strong>How to read it:</strong><br>
            • Price <strong>above</strong> VWAP → buyers in control; bullish intraday bias<br>
            • Price <strong>below</strong> VWAP → sellers in control; bearish intraday bias<br>
            • Most meaningful on intraday intervals (15 min / 1 hr)
          </div>
        </div>

        <div class='wt-card'>
          <div class='wt-card-title'><span class='wt-card-icon'>⚡</span> RSI — Relative Strength Index</div>
          <div class='wt-card-body'>
            <div style="margin-bottom:8px;">
              <span class='wt-tag wt-tag-red'>Overbought &gt; 70</span>
              <span class='wt-tag wt-tag-green'>Oversold &lt; 30</span>
            </div>
            RSI is a 0–100 momentum oscillator that compares average gains to average losses over
            the last 14 periods. It signals when a move may be exhausted.<br><br>
            <strong>How to read it:</strong><br>
            • RSI <strong>&gt; 70</strong> → overbought; pullback risk rises<br>
            • RSI <strong>&lt; 30</strong> → oversold; potential reversal or bounce<br>
            • RSI diverging from price = early warning of trend reversal<br>
            • Visible in the <strong>RSI / Oscillators</strong> tab
          </div>
        </div>

        <div class='wt-card'>
          <div class='wt-card-title'><span class='wt-card-icon'>🔀</span> MACD — Moving Avg Convergence Divergence</div>
          <div class='wt-card-body'>
            <div style="margin-bottom:8px;">
              <span class='wt-tag wt-tag-blue'>MACD Line</span>
              <span class='wt-tag wt-tag-yellow'>Signal Line</span>
              <span class='wt-tag wt-tag-green'>Histogram</span>
            </div>
            MACD = EMA(12) − EMA(26). The signal line is a 9-period EMA of MACD. The histogram
            shows the gap between them — growing bars mean strengthening momentum.<br><br>
            <strong>How to read it:</strong><br>
            • MACD crossing <strong>above</strong> signal → bullish crossover (buy signal)<br>
            • MACD crossing <strong>below</strong> signal → bearish crossover (sell signal)<br>
            • Histogram shrinking → momentum fading, crossover imminent
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Section: ATR & Risk
    st.markdown("<div class='section-header'>🛡 Risk Measurement — ATR</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='wt-card'>
      <div class='wt-card-title'><span class='wt-card-icon'>📐</span> ATR — Average True Range</div>
      <div class='wt-card-body'>
        ATR measures market volatility by averaging the true range (largest of: high−low, |high−prev close|, |low−prev close|)
        over 14 periods. The dashboard expresses ATR as a percentage of the current price to produce the
        <strong>Risk Level</strong> badge shown in the metrics panel.<br><br>
        <span class='wt-tag wt-tag-green'>Low  &lt; 1.5%</span>
        <span class='wt-tag wt-tag-yellow'>Medium  1.5 – 3%</span>
        <span class='wt-tag wt-tag-red'>High  &gt; 3%</span><br><br>
        A <strong>High</strong> risk reading means the stock is swinging aggressively and stop-losses need to be wider.
        A <strong>Low</strong> reading suggests the stock is in a quiet consolidation phase.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Section: How to Use (step by step)
    st.markdown("<div class='section-header'>🧭 How to Use the Dashboard</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='wt-card'>
      <div class='wt-card-body'>
        <div class='wt-step'>
          <div class='wt-step-num'>1</div>
          <div class='wt-step-text'><strong>Pick your stock & interval</strong> — Use the sidebar to select a market,
          stock, and time interval. Start with <em>1 Day</em> for a broad trend view, then switch to <em>1 Hour</em>
          or <em>15 Minutes</em> for entry/exit precision.</div>
        </div>
        <div class='wt-step'>
          <div class='wt-step-num'>2</div>
          <div class='wt-step-text'><strong>Refresh data</strong> — Click <em>Refresh Now</em> to pull the latest
          prices from Yahoo Finance into the database. Enable <em>Auto-Refresh</em> to keep it updating every 2 minutes
          while the dashboard is open.</div>
        </div>
        <div class='wt-step'>
          <div class='wt-step-num'>3</div>
          <div class='wt-step-text'><strong>Read the trend</strong> — In the Chart tab, check the <em>Trend</em> and
          <em>Momentum</em> fields on the right panel. If the trend is Bullish–Strong, the SMA 50 is above SMA 200
          and price is above both. Enable <em>SMA 200</em> to visualise this on the chart.</div>
        </div>
        <div class='wt-step'>
          <div class='wt-step-num'>4</div>
          <div class='wt-step-text'><strong>Check momentum with RSI & MACD</strong> — Open the <em>RSI / Oscillators</em>
          tab. If RSI is between 40–65 and MACD is above its signal line, momentum is healthy for a long trade.
          Avoid buying into RSI &gt; 70 unless you are a momentum trader.</div>
        </div>
        <div class='wt-step'>
          <div class='wt-step-num'>5</div>
          <div class='wt-step-text'><strong>Check the alerts & action badge</strong> — The alerts panel fires
          automatically when notable conditions are met. The <em>Suggested Action</em> badge synthesises all signals
          into a single recommendation. Always cross-check with your own research before acting.</div>
        </div>
        <div class='wt-step'>
          <div class='wt-step-num'>6</div>
          <div class='wt-step-text'><strong>Use the forecast band</strong> — The shaded blue band on the chart and
          the <em>Forecast Band</em> card show the ±1 standard deviation range around the 20-period mean.
          Statistically, ~68% of prices should stay within this band under normal conditions.</div>
        </div>
        <div class='wt-step'>
          <div class='wt-step-num'>7</div>
          <div class='wt-step-text'><strong>Compare stocks</strong> — Switch to the <em>Compare</em> tab after
          selecting peers in the sidebar. The normalised chart removes the price-scale difference so you can see
          which stock is performing best on a relative basis.</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Signals quick-reference
    st.markdown("<div class='section-header'>🚦 Signal Quick Reference</div>", unsafe_allow_html=True)

    sig_cols = st.columns(4)
    signals = [
        ("↑ BUY",  "signal-buy",  "Bullish trend · RSI < 65 · MACD bullish · not near resistance"),
        ("↓ SELL", "signal-sell", "Near resistance · RSI > 65 · momentum fading"),
        ("⟳ HOLD", "signal-hold", "Bullish trend but near resistance, or no clear trigger"),
        ("◌ WAIT", "signal-wait", "Bearish trend · RSI > 40 · wait for clearer setup"),
    ]
    for col, (label, cls, desc) in zip(sig_cols, signals):
        with col:
            st.markdown(
                f"""<div class='wt-card' style='text-align:center;'>
                  <div style='margin-bottom:10px;'>
                    <span class='signal-badge {cls}'>{label}</span>
                  </div>
                  <div class='wt-card-body' style='font-size:0.72rem;text-align:left;'>{desc}</div>
                </div>""",
                unsafe_allow_html=True
            )




# ===============================
# FOOTER
# ===============================
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
st.caption(
f"Market Analytics Dashboard · DB-driven analytics · {st.session_state.last_refresh.strftime('%d %b %Y %H:%M')} IST · BUILT BY NAVEEN RAJA"
)