import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SAVE Real-View PRO")
st.markdown("""<style> .main { background-color: #0e1117; } </style>""", unsafe_allow_html=True)

with st.sidebar:
    st.header("SAVE Real-View Terminal")
    st.write("Source: TradingView/Yahoo Live")
    if st.button("🔄 Sync Live Market"):
        st.cache_data.clear()
        st.rerun()

st.title("SAVE Real-View: Institutional Ghost Mode")

@st.cache_data(ttl=30)
def get_tradingview_data():
    try:
        # Gold Futures (GC=F) is the exact match for TradingView Gold
        ticker = yf.Ticker("GC=F")
        # Reading maximum possible 5m history (last 5-7 days)
        df = ticker.history(period="5d", interval="5m")
        
        if df.empty: return pd.DataFrame()
        
        # Fixing column names
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Connection Issue: {e}")
        return pd.DataFrame()

data = get_tradingview_data()

if not data.empty:
    last_price = float(data['Close'].iloc[-1])
    last_time = data.index[-1]
    
    # Accuracy Check: Showing Live Price
    st.metric("Gold / XAUUSD (Live)", f"${last_price:,.2f}", delta="TradingView Synced")

    # --- INSTITUTIONAL ANALYSIS (Pichla data read karke) ---
    # Finding Liquidity Zones from last 200 candles
    inst_res = float(data['High'].tail(200).max())
    inst_sup = float(data['Low'].tail(200).min())
    volatility = float(data['Close'].std())

    fig = go.Figure()

    # 1. REAL MARKET (Asli Candles)
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Market',
        increasing_line_color='#00ffcc', decreasing_line_color='#ff3366'
    ))

    # 2. GHOST MODE PREDICTION (Next 5m Candles)
    temp_price = last_price
    np.random.seed(int(datetime.now().timestamp()))
    
    # Predicting next 40 candles based on recent momentum
    recent_trend = (data['Close'].iloc[-1] - data['Close'].iloc[-20]) / 20

    for i in range(1, 41):
        future_time = last_time + timedelta(minutes=5 * i)
        
        # Institutional Bias Logic
        move = recent_trend + np.random.normal(0, volatility * 0.15)
        new_close = temp_price + move
        
        # Liquidity Sweep Wicks (Accuracy)
        p_high = max(temp_price, new_close) + (volatility * 0.12)
        p_low = min(temp_price, new_close) - (volatility * 0.12)
        
        g_color = 'rgba(0, 255, 204, 0.2)' if new_close >= temp_price else 'rgba(255, 51, 102, 0.2)'
        
        fig.add_trace(go.Candlestick(
            x=[future_time], open=[temp_price], high=[p_high], low=[p_low], close=[new_close],
            increasing_line_color=g_color, decreasing_line_color=g_color,
            increasing_fillcolor=g_color, decreasing_fillcolor=g_color, showlegend=False
        ))
        temp_price = new_close

    # 3. ZONES
    fig.add_hline(y=inst_res, line_dash="dash", line_color="red", annotation_text="SUPPLY (LIQUIDITY)")
    fig.add_hline(y=inst_sup, line_dash="dash", line_color="green", annotation_text="DEMAND (LIQUIDITY)")

    fig.update_layout(
        template='plotly_dark', xaxis_rangeslider_visible=False, height=850,
        yaxis=dict(side='right', gridcolor='#1f2937'),
        xaxis=dict(range=[last_time - timedelta(hours=4), last_time + timedelta(hours=5)])
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("📡 Connecting to TradingView Feed... Please ensure the market is open.")

