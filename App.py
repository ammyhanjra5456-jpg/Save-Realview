import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="SAVE Real-View AI")
st.title("SAVE Real-View: AI Ghost Prediction")

# 1. Fetch REAL-TIME GOLD Data
@st.cache_data(ttl=30)
def get_gold_data():
    # XAUUSD=X is most stable for live view
    df = yf.download("XAUUSD=X", period="1d", interval="15m")
    return df

data = get_gold_data()

if not data.empty:
    # 2. AI GHOST LOGIC (Based on Momentum)
    # Predicting next 8 candles (2 hours)
    last_price = float(data['Close'].iloc[-1])
    last_time = data.index[-1]
    
    # Simple Momentum AI
    prices = data['Close'].values[-20:] # Last 20 candles
    avg_move = np.mean(np.diff(prices))
    
    # 3. CREATE CHART (TradingView Style)
    fig = go.Figure()

    # LIVE DATA
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Live Market'
    ))

    # GHOST DATA
    current_ghost_price = last_price
    for i in range(1, 9):
        future_time = last_time + timedelta(minutes=15 * i)
        # Adding a bit of AI random walk based on momentum
        prediction = current_ghost_price + avg_move + np.random.uniform(-1.5, 1.5)
        
        is_up = prediction >= current_ghost_price
        color = 'rgba(0, 255, 0, 0.4)' if is_up else 'rgba(255, 0, 0, 0.4)'
        
        fig.add_trace(go.Candlestick(
            x=[future_time], open=[current_ghost_price], 
            high=[max(current_ghost_price, prediction) + 0.8],
            low=[min(current_ghost_price, prediction) - 0.8], 
            close=[prediction],
            increasing_line_color=color, decreasing_line_color=color,
            increasing_fillcolor=color, decreasing_fillcolor=color,
            name='Ghost Prediction'
        ))
        current_ghost_price = prediction

    # TRADINGVIEW LOOK SETTINGS
    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=700,
        yaxis=dict(side='right', gridcolor='rgba(255,255,255,0.1)'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        margin=dict(l=0, r=50, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.info("Institutional AI active. Ghost Candles representing the next 2 hours based on 15m trend.")

else:
    st.error("Market data load nahi hoya. Check your connection or refresh.")
