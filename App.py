import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SAVE Real-View PRO")
st.markdown("""<style> .main { background-color: #0e1117; } </style>""", unsafe_allow_html=True)

st.title("SAVE Real-View: Live Alignment Mode")

# 1. FETCH DATA (5m Interval)
@st.cache_data(ttl=15) # Faster refresh for Monday
def get_institutional_data():
    try:
        df = yf.download("GC=F", period="2d", interval="5m")
        if df.empty: return pd.DataFrame()
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        return df
    except: return pd.DataFrame()

data = get_institutional_data()

if not data.empty:
    # --- GET CURRENT LIVE DATA ---
    last_price = float(data['Close'].iloc[-1])
    # Time Alignment: Using the actual last candle time from the data
    last_time = data.index[-1] 
    
    st.metric("Live Gold Price", f"${last_price:,.2f}", delta="Aligned")

    # AI LOGIC
    inst_res = float(data['High'].tail(100).max())
    inst_sup = float(data['Low'].tail(100).min())
    volatility = float(data['Close'].tail(50).std())

    fig = go.Figure()

    # REAL MARKET CANDLES
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Market'
    ))

    # --- 2. GHOST PREDICTIONS (ALIGNED TO CURRENT TIME) ---
    temp_price = last_price
    np.random.seed(int(datetime.now().strftime("%H%M")))

    for i in range(1, 41):
        # Alignment Fix: Ensure time starts exactly after the last live candle
        future_time = last_time + timedelta(minutes=5 * i)
        
        bias = -0.5 if temp_price >= inst_res else (0.5 if temp_price <= inst_sup else 0)
        move = bias + np.random.normal(0, volatility * 0.1)
        new_close = temp_price + move
        
        # Professional Short Wicks
        p_high = max(temp_price, new_close) + (volatility * 0.25)
        p_low = min(temp_price, new_close) - (volatility * 0.25)
        
        color = 'rgba(0, 255, 150, 0.4)' if new_close >= temp_price else 'rgba(255, 50, 50, 0.4)'
        
        fig.add_trace(go.Candlestick(
            x=[future_time], open=[temp_price], high=[p_high], low=[p_low], close=[new_close],
            increasing_line_color=color, decreasing_line_color=color, showlegend=False
        ))
        temp_price = new_close

    # 3. STYLING & VIEW
    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=800,
        # Range Selector to focus on current price
        xaxis=dict(range=[last_time - timedelta(hours=4), last_time + timedelta(hours=3)])
    )
    
    fig.add_hline(y=inst_res, line_dash="dash", line_color="red")
    fig.add_hline(y=inst_sup, line_dash="dash", line_color="green")

    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Waiting for Live Market Stream...")
