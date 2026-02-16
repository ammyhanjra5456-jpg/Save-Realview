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
    st.header("Terminal Controls")
    if st.button("🔄 Force Market Refresh"):
        st.cache_data.clear()
        st.rerun()

st.title("SAVE Real-View: Institutional AI Terminal")
st.write("Status: Live 5m Flow | Stable Prediction Mode")

@st.cache_data(ttl=15)
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
    
    st.metric("Gold (XAU/USD) Live", f"${last_price:,.2f}")
    
    # AI LOGIC
    inst_res = float(data['High'].tail(100).max())
    inst_sup = float(data['Low'].tail(100).min())
    volatility = float(data['Close'].tail(50).std())
    trend = float(data['Close'].diff().tail(15).mean())

    fig = go.Figure()

    # 1. REAL MARKET (Institutional White/Grey)
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Market',
        increasing_line_color='#ffffff', decreasing_line_color='#4a4a4a',
        increasing_fillcolor='#ffffff', decreasing_fillcolor='#4a4a4a'
    ))

    # 2. GHOST PREDICTIONS (NO-SEED STABLE LOGIC)
    temp_price = last_price
    
    # Simple prediction without large number seeds to prevent crash
    for i in range(1, 31): 
        future_time = last_time + timedelta(minutes=5 * i)
        
        # Bias Logic
        bias = 0.5 if temp_price <= inst_sup else (-0.5 if temp_price >= inst_res else trend * 1.5)
        # Using direct random move
        move = bias + (np.random.randn() * volatility * 0.1)
        new_close = temp_price + move
        
        # Accuracy Wicks
        p_high = max(temp_price, new_close) + (volatility * 0.15)
        p_low = min(temp_price, new_close) - (volatility * 0.15)
        
        color = 'rgba(0, 255, 150, 0.3)' if new_close >= temp_price else 'rgba(255, 50, 50, 0.3)'
        
        fig.add_trace(go.Candlestick(
            x=[future_time], open=[temp_price], high=[p_high], low=[p_low], close=[new_close],
            increasing_line_color=color, decreasing_line_color=color, showlegend=False
        ))
        temp_price = new_close

    # 3. LAYOUT
    fig.update_layout(
        template='plotly_dark', xaxis_rangeslider_visible=False, height=800,
        yaxis=dict(side='right', gridcolor='#1f2937'),
        xaxis=dict(range=[last_time - timedelta(hours=4), last_time + timedelta(hours=3)])
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("📡 Market Data loading... Refresh after 5 seconds.")
