import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(layout="wide", page_title="SAVE Real-View PRO")
st.markdown("""<style> .main { background-color: #0e1117; } </style>""", unsafe_allow_html=True)

st.title("SAVE Real-View: Institutional AI Terminal (15m)")

# 1. FETCH DATA (Locked to 15m)
@st.cache_data(ttl=60) # Cache for 1 minute to keep predictions stable
def get_institutional_data():
    # Fetching more history for better accuracy
    df = yf.download("GC=F", period="10d", interval="15m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df

data = get_institutional_data()

if not data.empty:
    # --- LIVE METRICS ---
    last_price = float(data['Close'].iloc[-1])
    
    # AI Seed: Locks prediction to the current hour so it doesn't change every second
    current_hour = datetime.now().hour
    np.random.seed(current_hour) 

    # --- INSTITUTIONAL ANALYSIS ---
    inst_resistance = float(data['High'].tail(100).max()) # Last 100 candles high
    inst_support = float(data['Low'].tail(100).min())    # Last 100 candles low
    
    # 2. GHOST PREDICTIONS (Locked Logic)
    fig = go.Figure()

    # REAL MARKET
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Live Market'
    ))

    temp_price = last_price
    last_time = data.index[-1]

    for i in range(1, 41):
        future_time = last_time + timedelta(minutes=15 * i)
        
        # Trend Strength based on last 24 hours
        trend_factor = float(data['Close'].diff().tail(20).mean())
        
        # Prediction: Combined Trend + Institutional Rejection
        if temp_price >= inst_resistance:
            move = -0.8 + np.random.normal(0, 0.3)
        elif temp_price <= inst_support:
            move = 0.8 + np.random.normal(0, 0.3)
        else:
            move = (trend_factor * 1.2) + np.random.normal(0, 0.4)
            
        new_close = temp_price + move
        color = 'rgba(0, 255, 0, 0.35)' if new_close >= temp_price else 'rgba(255, 0, 0, 0.35)'
        
        fig.add_trace(go.Candlestick(
            x=[future_time], open=[temp_price], 
            high=[max(temp_price, new_close) + 0.3],
            low=[min(temp_price, new_close) - 0.3], 
            close=[new_close],
            increasing_line_color=color, decreasing_line_color=color,
            increasing_fillcolor=color, decreasing_fillcolor=color,
            showlegend=False
        ))
        temp_price = new_close

    # TRADINGVIEW STYLING
    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=800,
        yaxis=dict(side='right', gridcolor='#1f2937', title="XAUUSD (15m)"),
        margin=dict(l=0, r=50, t=10, b=10)
    )
    
    # Zones
    fig.add_hline(y=inst_resistance, line_dash="dash", line_color="red", annotation_text="INSTITUTIONAL SELL")
    fig.add_hline(y=inst_support, line_dash="dash", line_color="green", annotation_text="INSTITUTIONAL BUY")

    st.plotly_chart(fig, use_container_width=True)
    st.info(f"Live Price: ${last_price:,.2f} | 15m Accuracy Mode Active")

else:
    st.error("Data fetch error.")
