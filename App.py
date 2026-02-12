import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="SAVE Real-View AI")
st.title("SAVE Real-View: AI Ghost Prediction")

@st.cache_data(ttl=60)
def get_reliable_data():
    # Try multiple symbols to ensure chart is NEVER empty
    for symbol in ["GC=F", "XAUUSD=X"]:
        df = yf.download(symbol, period="3d", interval="15m")
        if not df.empty:
            return df
    return pd.DataFrame()

data = get_reliable_data()

if not data.empty:
    # --- AI PREDICTION LOGIC ---
    data = data.copy()
    data['Time_Idx'] = np.arange(len(data))
    X = data[['Time_Idx']].values
    y = data['Close'].values.reshape(-1, 1)
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict next 12 candles (3 hours of future)
    future_indices = np.arange(len(data), len(data) + 12).reshape(-1, 1)
    future_preds = model.predict(future_indices).flatten()
    
    # --- PLOTTING ---
    fig = go.Figure()

    # 1. LIVE MARKET CANDLES
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Live Market'
    ))

    # 2. GHOST AI CANDLES
    last_time = data.index[-1]
    last_price = float(data['Close'].iloc[-1])

    for i in range(len(future_preds)):
        pred_time = last_time + timedelta(minutes=15 * (i+1))
        pred_close = float(future_preds[i])
        
        is_up = pred_close >= last_price
        color = 'rgba(0, 255, 0, 0.4)' if is_up else 'rgba(255, 0, 0, 0.4)'
        
        fig.add_trace(go.Candlestick(
            x=[pred_time], open=[last_price], 
            high=[max(last_price, pred_close) + 1.0],
            low=[min(last_price, pred_close) - 1.0], 
            close=[pred_close],
            increasing_line_color=color, decreasing_line_color=color,
            increasing_fillcolor=color, decreasing_fillcolor=color,
            name='Ghost AI'
        ))
        last_price = pred_close

    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=700,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.success(f"AI Prediction active for {last_time.strftime('%H:%M')} onwards (Dubai Time)")

else:
    st.error("Market data fetch nahi ho sakya. Kirpa karke 1 minute baad refresh karo.")
