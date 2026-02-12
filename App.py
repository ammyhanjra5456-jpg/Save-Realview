import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="SAVE Real-View AI")
st.title("SAVE Real-View: AI Ghost Prediction")

# 1. Load Real-Time Gold Data (GC=F for reliability)
@st.cache_data(ttl=60)
def get_ai_data():
    df = yf.download("GC=F", period="2d", interval="15m") 
    return df

data = get_ai_data()

if not data.empty:
    # 2. AI Model Training
    data = data.copy()
    data['Time_Idx'] = np.arange(len(data))
    X = data[['Time_Idx']].values
    y = data['Close'].values.reshape(-1, 1)
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict next 8 candles
    future_indices = np.arange(len(data), len(data) + 8).reshape(-1, 1)
    future_preds = model.predict(future_indices).flatten() # Convert to flat list
    
    # 3. DRAW CHART
    fig = go.Figure()

    # Live Data
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], 
                                 low=data['Low'], close=data['Close'], name='Live Market'))

    # Ghost Prediction Logic
    last_time = data.index[-1]
    last_price = float(data['Close'].iloc[-1])

    for i in range(len(future_preds)):
        pred_time = last_time + timedelta(minutes=15 * (i+1))
        pred_close = float(future_preds[i])
        
        # Sahi Color Logic (Checking single value)
        is_up = pred_close >= last_price
        color = 'rgba(0, 255, 0, 0.4)' if is_up else 'rgba(255, 0, 0, 0.4)'
        
        fig.add_trace(go.Candlestick(
            x=[pred_time], 
            open=[last_price], 
            high=[max(last_price, pred_close) + 0.5],
            low=[min(last_price, pred_close) - 0.5], 
            close=[pred_close],
            increasing_line_color=color, 
            decreasing_line_color=color,
            increasing_fillcolor=color,
            decreasing_fillcolor=color,
            name='Ghost AI'
        ))
        last_price = pred_close

    fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=700)
    st.plotly_chart(fig, use_container_width=True)
    st.info("Institutional Pattern AI Active: Predicting next movement based on current momentum.")

else:
    st.error("Market Data load nahi ho sakya. Kirpa karke refresh karo.")
