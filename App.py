import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(layout="wide", page_title="SAVE Real-View")

st.title("SAVE Real-View: Live Prediction Panel")
st.write("Project: SAN-AM EXPRESS DELIVERY")

# Fetch Gold Data (last 6 months for speed, can be increased)
@st.cache_data
def load_data():
    data = yf.download("XAUUSD=X", period="6mo", interval="1h")
    return data

data = load_data()

# Basic Plotly Chart
fig = go.Figure()
fig.add_trace(go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Market Data'))

# --- GHOST CANDLES LOGIC (Simplified Prediction) ---
# In real AI, this part reads 5-10 years of data.
last_date = data.index[-1]
last_close = data['Close'].iloc[-1]
prediction_days = 2

# Creating dummy ghost candles for demonstration
for i in range(1, prediction_days + 1):
    ghost_date = last_date + timedelta(hours=i)
    # Simple prediction: moving up
    ghost_close = last_close + (i * 2) 
    
    fig.add_trace(go.Candlestick(x=[ghost_date],
                    open=[last_close],
                    high=[ghost_close + 1],
                    low=[last_close - 1],
                    close=[ghost_close],
                    name='Ghost Prediction',
                    opacity=0.3)) # Transparent
    last_close = ghost_close

fig.update_layout(title='Gold Price with Ghost Candles',
                  yaxis_title='Price (USD)',
                  xaxis_title='Date',
                  template='plotly_dark')

st.plotly_chart(fig, use_container_width=True)
