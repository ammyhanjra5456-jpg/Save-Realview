import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Project Name: SAVE Real-View
st.set_page_config(layout="wide", page_title="SAVE Real-View AI")
st.title("SAVE Real-View: Institutional Ghost Prediction")

# 1. Fetch Real Data (Gold)
@st.cache_data(ttl=30)
def get_gold_data():
    # Fetching 15m data for the last 5 days
    df = yf.download("GC=F", period="5d", interval="15m")
    return df

data = get_gold_data()

if not data.empty:
    # 2. Institutional Ghost Logic
    last_price = float(data['Close'].iloc[-1])
    last_time = data.index[-1]
    
    # Analyze momentum to predict future
    recent_trend = data['Close'].diff().tail(10).mean()
    
    # 3. DRAW CHART (TradingView Look)
    fig = go.Figure()

    # Live Candles
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Live Market'
    ))

    # Ghost Prediction Candles (Next 10)
    current_ghost_price = last_price
    for i in range(1, 11):
        future_time = last_time + timedelta(minutes=15 * i)
        
        # AI Logic: Predict next move based on trend
        prediction = current_ghost_price + recent_trend + np.random.normal(0, 1.5)
        
        is_up = prediction >= current_ghost_price
        color = 'rgba(0, 255, 0, 0.35)' if is_up else 'rgba(255, 0, 0, 0.35)'
        
        fig.add_trace(go.Candlestick(
            x=[future_time], open=[current_ghost_price], 
            high=[max(current_ghost_price, prediction) + 0.5],
            low=[min(current_ghost_price, prediction) - 0.5], 
            close=[prediction],
            increasing_line_color=color, decreasing_line_color=color,
            increasing_fillcolor=color, decreasing_fillcolor=color,
            name='Ghost AI Prediction'
        ))
        current_ghost_price = prediction

    # TRADINGVIEW Look
    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=700,
        yaxis=dict(side='right', gridcolor='rgba(255,255,255,0.05)'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        margin=dict(l=0, r=50, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.success(f"Ghost AI Active: {last_time.strftime('%H:%M')} Dubai Time")
else:
    st.error("Market data not available.")
