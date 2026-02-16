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
    st.header("Institutional Terminal")
    if st.button("🔄 Force Market Refresh"):
        st.cache_data.clear()
        st.rerun()

st.title("SAVE Real-View: Institutional Liquidity Mode")
st.write("Status: High-Accuracy Prediction | Liquidity Sweep Active")

# --- ILAJ START: Forbidden Error Fix ---
@st.cache_data(ttl=15)
def get_institutional_data():
    try:
        # Ticker method is more stable against forbidden errors
        gold = yf.Ticker("GC=F")
        df = gold.history(period="2d", interval="5m")
        
        if df.empty: return pd.DataFrame()
        
        # Cleaning column names (handling multi-index if necessary)
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        return df
    except Exception as e:
        # Shows exactly what the error is if it happens
        st.error(f"Data Fetch Error: {e}")
        return pd.DataFrame()
# --- ILAJ END ---

data = get_institutional_data()

if not data.empty:
    last_price = float(data['Close'].iloc[-1])
    last_time = data.index[-1]
    
    high_low = data['High'] - data['Low']
    atr = high_low.tail(20).mean()
    
    st.metric("Gold Live (XAU/USD)", f"${last_price:,.2f}", delta=f"ATR: {atr:.2f}")
    
    inst_res = float(data['High'].tail(100).max())
    inst_sup = float(data['Low'].tail(100).min())
    trend = float(data['Close'].diff().tail(15).mean())

    fig = go.Figure()

    # 1. REAL MARKET
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Market',
        increasing_line_color='#ffffff', decreasing_line_color='#4a4a4a',
        increasing_fillcolor='#ffffff', decreasing_fillcolor='#4a4a4a'
    ))

    # 2. GHOST PREDICTIONS
    temp_price = last_price
    for i in range(1, 41): 
        future_time = last_time + timedelta(minutes=5 * i)
        dist_to_res = inst_res - temp_price
        dist_to_sup = temp_price - inst_sup
        
        bias = trend * 2.0
        if dist_to_res < (atr * 2): bias -= (atr * 0.5) 
        if dist_to_sup < (atr * 2): bias += (atr * 0.5) 
        
        move = bias + (np.random.randn() * atr * 0.4)
        new_close = temp_price + move
        
        sweep_up = (atr * 0.8) if np.random.random() > 0.8 else (atr * 0.2)
        sweep_down = (atr * 0.8) if np.random.random() > 0.8 else (atr * 0.2)
        
        p_high = max(temp_price, new_close) + sweep_up
        p_low = min(temp_price, new_close) - sweep_down
        
        color = 'rgba(0, 255, 150, 0.4)' if new_close >= temp_price else 'rgba(255, 50, 50, 0.4)'
        
        fig.add_trace(go.Candlestick(
            x=[future_time], open=[temp_price], high=[p_high], low=[p_low], close=[new_close],
            increasing_line_color=color, decreasing_line_color=color, showlegend=False
        ))
        temp_price = new_close

    # 3. AUTO-REVERSAL DETECTOR
    if last_price >= (inst_res - atr) or last_price <= (inst_sup + atr):
        signal_color = "red" if last_price >= (inst_res - atr) else "green"
        fig.add_trace(go.Scatter(
            x=[last_time], y=[last_price],
            mode="markers+text",
            marker=dict(size=15, color=signal_color, symbol="diamond"),
            text=["⚠️ POSSIBLE REVERSAL"],
            textposition="top center",
            name="Signal"
        ))

    # 4. LAYOUT & ZONES
    fig.add_hline(y=inst_res, line_dash="dash", line_color="red", annotation_text="INSTITUTIONAL SUPPLY")
    fig.add_hline(y=inst_sup, line_dash="dash", line_color="green", annotation_text="INSTITUTIONAL DEMAND")

    fig.update_layout(
        template='plotly_dark', xaxis_rangeslider_visible=False, height=850,
        yaxis=dict(side='right', gridcolor='#1f2937'),
        xaxis=dict(range=[last_time - timedelta(hours=5), last_time + timedelta(hours=4)])
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("📡 Connecting to Exchange... Ensure Gold is trading.")
