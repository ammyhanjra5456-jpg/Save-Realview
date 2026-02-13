import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(layout="wide", page_title="SAVE Real-View PRO")
st.markdown("""<style> .main { background-color: #0e1117; } </style>""", unsafe_allow_html=True)

st.title("SAVE Real-View: Institutional Terminal (Pro)")

# 1. FETCH DATA (Optimized for 15m Accuracy)
@st.cache_data(ttl=60)
def get_institutional_data():
    # 1 month is perfect for 15m intervals without errors
    df = yf.download("GC=F", period="1mo", interval="15m")
    if not df.empty:
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df

data = get_institutional_data()

if not data.empty:
    # --- METRICS & AI LOCK ---
    last_price = float(data['Close'].iloc[-1])
    np.random.seed(datetime.now().hour) 

    # --- INSTITUTIONAL LEVELS (Last 200 candles for stability) ---
    inst_resistance = float(data['High'].tail(200).max())
    inst_support = float(data['Low'].tail(200).min())
    
    # 2. DRAW CHART (TradingView Style)
    fig = go.Figure()

    # REAL MARKET (Thin candles like TradingView)
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Live Market',
        increasing_line_width=1.2, decreasing_line_width=1.2
    ))

    # GHOST PREDICTIONS
    temp_price = last_price
    last_time = data.index[-1]

    for i in range(1, 41):
        future_time = last_time + timedelta(minutes=15 * i)
        trend = float(data['Close'].diff().tail(30).mean())
        
        # Institutional logic: Bounce from S/R
        if temp_price >= inst_resistance:
            move = -0.7 + np.random.normal(0, 0.2)
        elif temp_price <= inst_support:
            move = 0.7 + np.random.normal(0, 0.2)
        else:
            move = (trend * 1.4) + np.random.normal(0, 0.3)
            
        new_close = temp_price + move
        color = 'rgba(0, 255, 0, 0.4)' if new_close >= temp_price else 'rgba(255, 0, 0, 0.4)'
        
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

    # TRADINGVIEW STYLING
    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=850,
        yaxis=dict(side='right', gridcolor='#1f2937', tickformat='.2f'),
        xaxis=dict(gridcolor='#1f2937'),
        margin=dict(l=0, r=50, t=10, b=10)
    )
    
    # Static Zones
    fig.add_hline(y=inst_resistance, line_dash="dash", line_color="red")
    fig.add_hline(y=inst_support, line_dash="dash", line_color="green")

    st.plotly_chart(fig, use_container_width=True)
    st.success(f"Live Price: ${last_price:,.2f} | Institutional AI Synced")

else:
    st.error("Data fetch limit reached. Please refresh in 1 minute.")
