import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SAVE Real-View PRO")
# FIXED: Changed unsafe_ignore_html to unsafe_allow_html
st.markdown("""<style> .main { background-color: #0e1117; } </style>""", unsafe_allow_html=True)

st.title("SAVE Real-View: Institutional AI Terminal")
st.write("Status: Live Institutional Flow | High Accuracy Mode")

# 1. FETCH DATA (5m Interval - Faster)
@st.cache_data(ttl=10) # Reduced TTL for faster live updates
def get_institutional_data():
    try:
        df = yf.download("GC=F", period="2d", interval="5m")
        if df.empty: return pd.DataFrame()
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        return df
    except: return pd.DataFrame()

data = get_institutional_data()

if not data.empty:
    last_price = float(data['Close'].iloc[-1])
    last_time = data.index[-1]
    
    st.metric("Live Gold Price (XAU/USD)", f"${last_price:,.2f}")
    
    # INSTITUTIONAL LOGIC
    inst_res = float(data['High'].tail(150).max())
    inst_sup = float(data['Low'].tail(150).min())
    volatility = float(data['Close'].tail(50).std())
    trend = float(data['Close'].diff().tail(15).mean())

    fig = go.Figure()

    # REAL MARKET CANDLES
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Market'
    ))

    # --- 2. GHOST PREDICTIONS (Aligned) ---
    temp_price = last_price
    np.random.seed(int(datetime.now().strftime("%H%M")))

    for i in range(1, 41):
        future_time = last_time + timedelta(minutes=5 * i)
        
        # Institutional Bias Logic
        bias = -0.5 if temp_price >= inst_res else (0.5 if temp_price <= inst_sup else trend * 0.8)
        move = bias + np.random.normal(0, volatility * 0.1)
        new_close = temp_price + move
        
        # Professional Short Wicks
        p_high = max(temp_price, new_close) + (volatility * 0.25)
        p_low = min(temp_price, new_close) - (volatility * 0.25)
        
        color = 'rgba(0, 255, 0, 0.4)' if new_close >= temp_price else 'rgba(255, 0, 0, 0.4)'
        
        fig.add_trace(go.Candlestick(
            x=[future_time], open=[temp_price], high=[p_high], low=[p_low], close=[new_close],
            increasing_line_color=color, decreasing_line_color=color, showlegend=False
        ))
        temp_price = new_close

    # 3. LAYOUT & INSTITUTIONAL LINES
    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=750,
        yaxis=dict(side='right'),
        # Fixes the zoom issue
        xaxis=dict(range=[last_time - timedelta(hours=6), last_time + timedelta(hours=3)])
    )
    
    fig.add_hline(y=inst_res, line_dash="dash", line_color="#ff4b4b", annotation_text="INST. SELL")
    fig.add_hline(y=inst_sup, line_dash="dash", line_color="#00ff00", annotation_text="INST. BUY")

    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Waiting for Live Market Stream...")

