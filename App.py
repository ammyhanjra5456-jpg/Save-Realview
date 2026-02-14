import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SAVE Real-View PRO")
st.markdown("""<style> .main { background-color: #0e1117; } </style>""", unsafe_allow_html=True)

st.title("SAVE Real-View: Institutional AI Terminal")

# --- 🔄 REFRESH BUTTON DIRECTLY ON MAIN SCREEN ---
col_btn1, col_btn2 = st.columns([1, 5])
with col_btn1:
    if st.button("🔄 REFRESH DATA"):
        st.cache_data.clear()
        st.rerun()

st.write("Status: Live Gold Analysis | Liquidity Sweep Mode Active")

# 1. FETCH DATA WITH ERROR HANDLING
@st.cache_data(ttl=30)
def get_institutional_data():
    try:
        df = yf.download("GC=F", period="5d", interval="5m")
        if df.empty:
            raise ValueError("No data returned")
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        return df
    except Exception as e:
        return pd.DataFrame()

data = get_institutional_data()

if not data.empty:
    last_price = float(data['Close'].iloc[-1])
    
    # --- LIVE PRICE METRICS ---
    st.metric("Live Gold Price (Futures)", f"${last_price:,.2f}")
    
    # AI LOGIC
    inst_resistance = float(data['High'].tail(200).max())
    inst_support = float(data['Low'].tail(200).min())
    recent_volatility = float(data['Close'].std())
    recent_trend = float(data['Close'].diff().tail(20).mean())

    # 2. GENERATE GHOST PREDICTIONS
    fig = go.Figure()

    # REAL MARKET
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Live Market'
    ))

    temp_price = last_price
    last_time = data.index[-1]
    np.random.seed(int(datetime.now().strftime("%Y%m%d%H")))

    for i in range(1, 41):
        future_time = last_time + timedelta(minutes=5 * i)
        bias = 0.7 if temp_price <= inst_support else (-0.7 if temp_price >= inst_resistance else recent_trend * 1.6)
        move = bias + np.random.normal(0, recent_volatility * 0.12)
        new_close = temp_price + move
        
        # Reduced Sweep Buffer for cleaner view
        sweep_buffer = recent_volatility * 0.8 
        p_high = max(temp_price, new_close) + (sweep_buffer if bias < 0 else 0.1)
        p_low = min(temp_price, new_close) - (sweep_buffer if bias > 0 else 0.1)
        
        color = 'rgba(0, 255, 0, 0.3)' if new_close >= temp_price else 'rgba(255, 0, 0, 0.3)'
        fig.add_trace(go.Candlestick(x=[future_time], open=[temp_price], high=[p_high], low=[p_low], close=[new_close],
                                    increasing_line_color=color, decreasing_line_color=color, showlegend=False))
        temp_price = new_close

    fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=800)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("⚠️ Forbidden/No Data. Please click the REFRESH DATA button above.")
