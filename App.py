import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="SAVE Real-View AI")
st.title("SAVE Real-View: AI Ghost Prediction")

# 1. Fetch Real Data
@st.cache_data(ttl=60)
def get_gold_data():
    # Use GC=F (Futures) for better accuracy
    df = yf.download("GC=F", period="2d", interval="15m")
    return df

data = get_gold_data()

if not data.empty:
    # 2. AI Model for Prediction
    data_copy = data.copy()
    data_copy['Time_Idx'] = np.arange(len(data_copy))
    X = data_copy[['Time_Idx']].values
    y = data_copy['Close'].values.reshape(-1, 1)
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict next 10 candles
    future_indices = np.arange(len(data_copy), len(data_copy) + 10).reshape(-1, 1)
    future_preds = model.predict(future_indices).flatten()
    
    # 3. DRAW CHART (TradingView Look & Feel)
    fig = go.Figure()

    # Live Market Candles
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Live Market'
    ))

    # Ghost Prediction Candles
    last_time = data.index[-1]
    last_price = float(data['Close'].iloc[-1])

    for i in range(len(future_preds)):
        pred_time = last_time + timedelta(minutes=15 * (i+1))
        pred_close = float(future_preds[i])
        
        # Color based on trend
        is_up = pred_close >= last_price
        color = 'rgba(0, 255, 0, 0.3)' if is_up else 'rgba(255, 0, 0, 0.3)'
        
        fig.add_trace(go.Candlestick(
            x=[pred_time], 
            open=[last_price], 
            high=[max(last_price, pred_close) + 0.5],
            low=[min(last_price, pred_close) - 0.5], 
            close=[pred_close],
            increasing_line_color=color, 
            decreasing_line_color=color,
            name='Ghost AI'
        ))
        last_price = pred_close

    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=700,
        title="Gold Price Prediction",
        yaxis_title="Price (USD)"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.success("AI Ghost Mode Active: Live Data + Future Prediction")

else:
    st.error("Data load nahi ho sakya. Kirpa refresh karo.")
