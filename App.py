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

# --- 🔄 REFRESH BUTTON (HUN SAAMNE DIKHEGA) ---
if st.button("🔄 REFRESH MARKET DATA (Fix Forbidden Error)"):
    st.cache_data.clear()
    st.rerun()

st.write("Status: Live Gold Analysis | Clean Liquidity Mode")

# 1. FETCH DATA
@st.cache_data(ttl=30)
def get_institutional_data():
    try:
        df = yf.download("GC=F", period="5d", interval="5m")
        if df.empty: return pd.DataFrame()
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        return df
    except:
        return pd.DataFrame()

data = get_institutional_data()

if not data.empty:
    last_price = float(data['Close'].iloc[-1])
    st.metric("Live Gold Price (XAU/USD)", f"${last_price:,.2f}")
    
    # AI LOGIC
    inst_resistance = float(data['High'].tail(150).max())
    inst_support = float(data['Low'].tail(150).min())
    recent_volatility = float(data['Close'].std())
    recent_trend = float(data['Close'].diff().tail(20).mean())

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Market'))

    temp_price = last_price
    last_time = data.index[-1]
    np.random.seed(int(datetime.now().strftime("%Y%m%d%H")))

    # 2. GHOST PREDICTIONS (CLEAN WICKS)
    for i in range(1, 41):
        future_time = last_time + timedelta(minutes=5 * i)
        bias = 0.7 if temp_price <= inst_support else (-0.7 if temp_price >= inst_resistance else recent_trend * 1.5)
        move = bias + np.random.normal(0, recent_volatility * 0.1)
        new_close = temp_price + move
        
        # --- ⚡ CLEAN WICK LOGIC (0.6 Multiplier) ⚡ ---
        sweep_buffer = recent_volatility * 0.6 
        p_high = max(temp_price, new_close) + (sweep_buffer if bias < 0 else 0.05)
        p_low = min(temp_price, new_close) - (sweep_buffer if bias > 0 else 0.05)
        
        color = 'rgba(0, 255, 0, 0.4)' if new_close >= temp_price else 'rgba(255, 0, 0, 0.4)'
        fig.add_trace(go.Candlestick(x=[future_time], open=[temp_price], high=[p_high], low=[p_low], close=[new_close],
                                    increasing_line_color=color, decreasing_line_color=color, showlegend=False))
        temp_price = new_close

    fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=750)
    fig.add_hline(y=inst_resistance, line_dash="dash", line_color="red", annotation_text="CEILING")
    fig.add_hline(y=inst_support, line_dash="dash", line_color="green", annotation_text="FLOOR")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("⚠️ Data connection lost. Click the REFRESH button above.")
