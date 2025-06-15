import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- Setup ---
st.set_page_config(page_title=" Purple Market Tracker", layout="wide")

# --- CSS ---
st.markdown("""
    <style>
    body {
        background-color: #fdfbff;
    }
    .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    .header {
        font-size: 28px;
        font-weight: bold;
        color: #8000ff;
        padding-bottom: 10px;
    }
    .search-box input {
        border: none;
        padding: 8px;
        border-radius: 20px;
        width: 100%;
        font-size: 14px;
    }
    .symbol-button {
        background-color: #d6b3ff;
        padding: 8px;
        border-radius: 5px;
        margin: 5px 0;
        font-weight: bold;
        color: #4b0082;
        cursor: pointer;
        border: none;
    }
    .selected-symbol {
        background-color: #8000ff !important;
        color: white !important;
    }
    .chart-border {
        border: 3px solid #8000ff;
        border-radius: 10px;
        padding: 5px;
    }
    .button-row button {
        background-color: #8000ff !important;
        color: white !important;
        border-radius: 5px;
        margin-right: 10px;
        font-weight: bold;
    }
    .top-row {
        background-color: #e8cbff;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- File I/O ---
WATCHLIST_FILE = "watchlist.csv"
# EXPORT_FILE = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

def save_watchlist(symbols):
    df = pd.DataFrame(symbols, columns=["Symbol"])
    df.to_csv(WATCHLIST_FILE, index=False)

def load_watchlist():
    try:
        return pd.read_csv(WATCHLIST_FILE)["Symbol"].tolist()
    except:
        return ["AAPL"]

# --- App State ---
if "symbols" not in st.session_state:
    st.session_state.symbols = load_watchlist()
if "selected_symbol" not in st.session_state:
    st.session_state.selected_symbol = st.session_state.symbols[0]
if "range" not in st.session_state:
    st.session_state.range = "1d"

# --- Sidebar ---
with st.sidebar:
    st.markdown("### Watchlist")
    new_symbol = st.text_input("Search", placeholder="Type symbol...").upper()

    col1, col2, col3, col4 = st.columns(4)
    if col1.button("Add") and new_symbol and new_symbol not in st.session_state.symbols:
        st.session_state.symbols.append(new_symbol)
        save_watchlist(st.session_state.symbols)

    if col2.button("Delete") and new_symbol in st.session_state.symbols:
        st.session_state.symbols.remove(new_symbol)
        save_watchlist(st.session_state.symbols)

    if col3.button("Save"):
        save_watchlist(st.session_state.symbols)
    if col4.button("Load"):
        st.session_state.symbols = load_watchlist()

    for sym in st.session_state.symbols:
        if st.button(sym, use_container_width=True):
            st.session_state.selected_symbol = sym

# --- Data Fetching ---
def get_data(symbol, period):
    ticker = yf.Ticker(symbol)

    if period == "1d":
        interval = "5m"
    elif period == "5d":
        interval = "15m"
    elif period == "1mo":
        interval = "1d"
    else:
        interval = "1d"

    hist = ticker.history(period=period, interval=interval)
    info = ticker.info
    return hist, info

symbol = st.session_state.selected_symbol
period = st.session_state.range
data, info = get_data(symbol, period)

# --- Header ---
st.markdown(f'<div class="header">{info.get("shortName", symbol)} ({symbol})</div>', unsafe_allow_html=True)
price = info.get("regularMarketPrice", 0)
change = info.get("regularMarketChange", 0)
percent = info.get("regularMarketChangePercent", 0)
st.markdown(f"### {price:.2f} {info.get('currency', '')} <span style='color:green'>+{change:.2f} ({percent:.2f}%)</span>", unsafe_allow_html=True)
currentTime = now = datetime.now()
st.caption("As of " + currentTime.strftime("%H:%M:%S"))

# --- Time Buttons ---
st.markdown('<div class="button-row">', unsafe_allow_html=True)
colA, colB, colC = st.columns(3)
if colA.button("1D"):
    st.session_state.range = "1d"
if colB.button("1W"):
    st.session_state.range = "5d"
if colC.button("1M"):
    st.session_state.range = "1mo"
st.markdown('</div>', unsafe_allow_html=True)

# --- Chart ---
st.markdown('<div class="chart-border">', unsafe_allow_html=True)
if not data.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data["Close"],
        line=dict(color='#8000ff', width=2),
        mode='lines'
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        height=400
    )
    fig.update_xaxes(showgrid=True, fixedrange=True)
    fig.update_yaxes(showgrid=True, fixedrange=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No chart data available.")
st.markdown('</div>', unsafe_allow_html=True)

# --- Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Bid", info.get("bid", "N/A"))
col2.metric("Ask", info.get("ask", "N/A"))
col3.metric("Last Close", info.get("previousClose", "N/A"))

# --- Export Button ---
if st.button("Export to CSV"):
    export_df = pd.DataFrame([{
        "Symbol": symbol,
        "Price": price,
        "Change": change,
        "Change %": f"{percent:.2f}%",
        "Bid": info.get("bid", "N/A"),
        "Ask": info.get("ask", "N/A"),
        "Last Close": info.get("previousClose", "N/A")
    }])
    export_df.to_csv(EXPORT_FILE, index=False)
    st.success(f"Exported to {EXPORT_FILE}")
