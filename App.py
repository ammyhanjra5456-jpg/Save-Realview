import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="SAVE Real-View")
st.title("SAVE Real-View: Live Prediction Panel")
st.write("Project: SAN-AM EXPRESS DELIVERY")

# Gold Futures (GC=F) is more reliable than XAUUSD=X on yfinance
@st.cache_data
def load_data():
    # Try Gold Futures first
    df = yf.download("GC=F", period="1mo", interval="1h")
    return df

data = load_data()

if data.empty:
    st.error("Data load nahi ho sakya. Kirpa karke thodi der baad refresh karo.")
else:
    # Basic Plotly Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='Market Data'))

    # GHOST CANDLES LOGIC
    last_date = data.index[-1]
    last_close = data['Close'].iloc[-1]
    
    # Predict next 5 candles (Ghost Mode)
    for i in range(1, 6):
        future_date = last_date + timedelta(hours=i)
        # Dummy prediction for now: slightly moving with trend
        prediction_move = (i * 1.5) 
        
        fig.add_trace(go.Candlestick(x=[future_date],
                        open=[last_close],
                        high=[last_close + prediction_move + 1],
                        low=[last_close + prediction_move - 1],
                        close=[last_close + prediction_move],
                        name='Ghost Candle',
                        increasing_line_color='rgba(0, 255, 0, 0.3)', # Fikki Green
                        decreasing_line_color='rgba(255, 0, 0, 0.3)', # Fikki Red
                        opacity=0.3))
        last_close = last_close + prediction_move

    fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
