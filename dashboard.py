import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Stock Market Data Analyzer",
    page_icon="📈",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

h1, h2, h3 {
    color: #00FFAA;
}

.stMetric {
    background-color: #1E1E1E;
    padding: 15px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("📈 Stock Market Data Analyzer")
st.write("Interactive Financial Analytics Dashboard")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Dashboard Controls")

stock = st.sidebar.text_input(
    "Enter Stock Ticker",
    value="AAPL"
)

start_date = st.sidebar.date_input(
    "Start Date",
    datetime(2023, 1, 1)
)

end_date = st.sidebar.date_input(
    "End Date",
    datetime.today()
)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data(ticker, start, end):

    data = yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=False
    )

    return data

try:

    df = load_data(stock, start_date, end_date)

    # =====================================================
    # FIX MULTIINDEX ISSUE
    # =====================================================

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Remove duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]

    if df.empty:
        st.error("No stock data found.")
        st.stop()

except Exception as e:
    st.error(f"Error fetching stock data: {e}")
    st.stop()

# =========================================================
# DATA CLEANING
# =========================================================

df = df.dropna()

# =========================================================
# CALCULATIONS
# =========================================================

# Daily Returns
df['Daily Return'] = df['Close'].pct_change()

# Moving Averages
df['MA20'] = df['Close'].rolling(window=20).mean()

df['MA50'] = df['Close'].rolling(window=50).mean()

# Volatility
volatility = df['Daily Return'].std() * np.sqrt(252)

# Prices
current_price = float(df['Close'].iloc[-1])

highest_price = float(df['High'].max())

lowest_price = float(df['Low'].min())

# Average Volume
average_volume = int(df['Volume'].mean())

# Sharpe Ratio
sharpe_ratio = (
    df['Daily Return'].mean() /
    df['Daily Return'].std()
) * np.sqrt(252)

# =========================================================
# COMPANY INFORMATION
# =========================================================

try:

    company = yf.Ticker(stock)

    info = company.info

    st.subheader("🏢 Company Information")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Company",
            info.get("shortName", "N/A")
        )

    with c2:
        st.metric(
            "Sector",
            info.get("sector", "N/A")
        )

    with c3:
        st.metric(
            "Industry",
            info.get("industry", "N/A")
        )

except:
    st.warning("Company information unavailable.")

# =========================================================
# KPI SECTION
# =========================================================

st.subheader("📊 Key Market Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Current Price",
        f"${current_price:.2f}"
    )

with col2:
    st.metric(
        "Highest Price",
        f"${highest_price:.2f}"
    )

with col3:
    st.metric(
        "Lowest Price",
        f"${lowest_price:.2f}"
    )

with col4:
    st.metric(
        "Volatility",
        f"{volatility:.2f}"
    )

# =========================================================
# STOCK DATA TABLE
# =========================================================

st.subheader("📄 Stock Dataset")

st.dataframe(df.tail(10))

# =========================================================
# DOWNLOAD BUTTON
# =========================================================

csv = df.to_csv().encode('utf-8')

st.download_button(
    label="⬇ Download Dataset",
    data=csv,
    file_name=f"{stock}_stock_data.csv",
    mime='text/csv'
)

# =========================================================
# CANDLESTICK CHART
# =========================================================

st.subheader("🕯 Candlestick Chart")

candlestick_fig = go.Figure(
    data=[
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Market Data'
        )
    ]
)

candlestick_fig.update_layout(
    template='plotly_dark',
    height=600,
    xaxis_rangeslider_visible=False,
    title=f"{stock} Candlestick Chart"
)

st.plotly_chart(
    candlestick_fig,
    use_container_width=True
)

# =========================================================
# MOVING AVERAGE CHART
# =========================================================

st.subheader("📈 Moving Average Analysis")

ma_fig = go.Figure()

# Closing Price
ma_fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Closing Price'
    )
)

# 20 MA
ma_fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df['MA20'],
        mode='lines',
        name='20-Day MA'
    )
)

# 50 MA
ma_fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df['MA50'],
        mode='lines',
        name='50-Day MA'
    )
)

ma_fig.update_layout(
    template='plotly_dark',
    height=600,
    title=f"{stock} Moving Average Analysis"
)

st.plotly_chart(
    ma_fig,
    use_container_width=True
)

# =========================================================
# DAILY RETURNS CHART
# =========================================================

st.subheader("📉 Daily Returns")

returns_fig = px.line(
    df,
    x=df.index,
    y='Daily Return',
    title='Daily Returns Over Time'
)

returns_fig.update_layout(
    template='plotly_dark',
    height=500
)

st.plotly_chart(
    returns_fig,
    use_container_width=True
)

# =========================================================
# RETURN DISTRIBUTION
# =========================================================

st.subheader("📊 Return Distribution")

hist_fig = px.histogram(
    df,
    x='Daily Return',
    nbins=50,
    title='Daily Return Distribution'
)

hist_fig.update_layout(
    template='plotly_dark',
    height=500
)

st.plotly_chart(
    hist_fig,
    use_container_width=True
)

# =========================================================
# RISK ANALYSIS
# =========================================================

st.subheader("⚠ Risk Analysis")

r1, r2, r3 = st.columns(3)

with r1:
    st.metric(
        "Sharpe Ratio",
        f"{sharpe_ratio:.2f}"
    )

with r2:
    st.metric(
        "Average Volume",
        f"{average_volume:,}"
    )

with r3:
    st.metric(
        "Trading Days",
        len(df)
    )

# =========================================================
# TREND DETECTION
# =========================================================

st.subheader("📌 Trend Detection")

latest_ma20 = float(df['MA20'].iloc[-1])

latest_ma50 = float(df['MA50'].iloc[-1])

if latest_ma20 > latest_ma50:
    st.success("Bullish Trend Detected 📈")

elif latest_ma20 < latest_ma50:
    st.error("Bearish Trend Detected 📉")

else:
    st.warning("Neutral Trend")

# =========================================================
# WATCHLIST
# =========================================================

st.subheader("⭐ Watchlist")

watchlist = [
    'AAPL',
    'MSFT',
    'GOOGL',
    'TSLA',
    'NVDA'
]

watchlist_data = []

for ticker in watchlist:

    try:

        temp = yf.download(
            ticker,
            period='5d',
            auto_adjust=False
        )

        if isinstance(temp.columns, pd.MultiIndex):
            temp.columns = temp.columns.get_level_values(0)

        temp = temp.loc[:, ~temp.columns.duplicated()]

        current = float(temp['Close'].iloc[-1])

        previous = float(temp['Close'].iloc[-2])

        change = ((current - previous) / previous) * 100

        watchlist_data.append({
            'Ticker': ticker,
            'Current Price': round(current, 2),
            'Daily Change %': round(change, 2)
        })

    except:
        pass

watchlist_df = pd.DataFrame(watchlist_data)

st.dataframe(watchlist_df)

# =========================================================
# FINAL INSIGHTS
# =========================================================

st.subheader("🧠 Final Insights")

if volatility > 0.4:
    risk_level = "High Risk"

elif volatility > 0.2:
    risk_level = "Moderate Risk"

else:
    risk_level = "Low Risk"

st.write(f"""
### Analysis Summary

- Stock analyzed: **{stock}**
- Current Price: **${current_price:.2f}**
- Highest Price: **${highest_price:.2f}**
- Lowest Price: **${lowest_price:.2f}**
- Estimated Risk Level: **{risk_level}**
- Moving averages help identify market trend direction
- Volatility measures investment risk
- Daily returns help evaluate stock performance consistency

""")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Educational Project Only — Not Financial Advice"
)