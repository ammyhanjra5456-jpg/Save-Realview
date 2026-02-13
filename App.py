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
st.write("Live Gold Analysis | Consistent Prediction Mode")

# 1. FETCH DATA (5-minute interval as requested earlier)
@st.cache_data(ttl=30)
def get_institutional_data():
    df = yf.download("GC=F", period="5d", interval="5m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df

data = get_institutional_data()

if not data.empty:
    # --- LIVE PRICE METRICS ---
    last_price = float(data['Close'].iloc[-1])
    open_price = float(data['Open'].iloc[-1])
    change = last_price - open_price
    
    col1, col2 = st.columns(2)
    col1.metric("Live Gold Price", f"${last_price:,.2f}", f"{change:+.2f}")
    
    # --- 🔒 CONSISTENCY LOCK LOGIC ---
    # Prediction nu current date aur hour naal lock kita hai taaki refresh te badle na
    now = datetime.now()
    seed_value = int(now.strftime("%Y%m%d%H")) 
    np.random.seed(seed_value)

    # --- AI LOGIC ---
    inst_resistance = float(data['High'].tail(100).max())
    inst_support = float(data['Low'].tail(100).min())
    recent_volatility = float(data['Close'].std())
    recent_trend = float(data['Close'].diff().tail(30).mean())

    # 2. GENERATE GHOST PREDICTIONS
    fig = go.Figure()

    # REAL MARKET CANDLES
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Live Market',
        increasing_line_width=1.2, decreasing_line_width=1.2
    ))

    # GHOST CANDLES (Consistent Path)
    temp_price = last_price
    last_time = data.index[-1]

    for i in range(1, 41):
        future_time = last_time + timedelta(minutes=5 * i)
        
        # Smart Money Logic
        if temp_price >= inst_resistance:
            bias = -0.5 
        elif temp_price <= inst_support:
            bias = 0.5 
        else:
            bias = recent_trend * 1.2 
            
        # Move is now consistent because of the seed
        move = bias + np.random.normal(0, recent_volatility * 0.1)
        new_close = temp_price + move
        
        is_up = bool(new_close >= temp_price)
        color = 'rgba(0, 255, 0, 0.35)' if is_up else 'rgba(255, 0, 0, 0.35)'
        
        fig.add_trace(go.Candlestick(
            x=[future_time], open=[temp_price], 
            high=[max(temp_price, new_close) + 0.2],
            low=[min(temp_price, new_close) - 0.2], 
            close=[new_close],
            increasing_line_color=color, decreasing_line_color=color,
            increasing_fillcolor=color, decreasing_fillcolor=color,
            showlegend=False, line_width=1
        ))
        temp_price = new_close

    # 3. TRADINGVIEW STYLING
    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=800,
        yaxis=dict(side='right', gridcolor='#1f2937', tickformat='.2f'),
        xaxis=dict(gridcolor='#1f2937'),
        margin=dict(l=0, r=50, t=10, b=10)
    )
    
    fig.add_hline(y=inst_resistance, line_dash="dash", line_color="red", annotation_text="SELL ZONE")
    fig.add_hline(y=inst_support, line_dash="dash", line_color="green", annotation_text="BUY ZONE")

    st.plotly_chart(fig, use_container_width=True)
    st.info("AI Analysis: Prediction is LOCKED for this hour for consistency.")

else:
    st.error("Market data not available.")
