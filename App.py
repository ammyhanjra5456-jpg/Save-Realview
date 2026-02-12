import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="SAVE Real-View AI")
st.title("SAVE Real-View: Institutional Ghost Mode")

@st.cache_data(ttl=30)
def get_live_data():
    df = yf.download("GC=F", period="2d", interval="15m")
    # Clean data to ensure no multi-index issues
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df

data = get_live_data()

if not data.empty:
    # --- FIXED LOGIC TO AVOID VALUEERROR ---
    # Convert everything to standard Python floats immediately
    last_close = float(data['Close'].iloc[-1])
    last_time = data.index[-1]
    volatility = float(data['Close'].std())
    recent_move = float(data['Close'].diff().tail(5).mean())

    fig = go.Figure()

    # LIVE DATA
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Live Market'
    ))

    # GHOST DATA (Prediction)
    temp_price = last_close
    for i in range(1, 41):
        future_time = last_time + timedelta(minutes=15 * i)
        
        # AI Logic: Trend + Random Noise
        prediction_move = recent_move + np.random.normal(0, volatility * 0.15)
        new_close = temp_price + prediction_move
        
        # COLOR LOGIC (Fixed for single boolean check)
        color = 'rgba(0, 255, 0, 0.3)' if new_close >= temp_price else 'rgba(255, 0, 0, 0.3)'
        
        fig.add_trace(go.Candlestick(
            x=[future_time], 
            open=[temp_price], 
            high=[max(temp_price, new_close) + 0.5],
            low=[min(temp_price, new_close) - 0.5], 
            close=[new_close],
            increasing_line_color=color, decreasing_line_color=color,
            increasing_fillcolor=color, decreasing_fillcolor=color,
            showlegend=False
        ))
        temp_price = new_close

    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=800,
        yaxis=dict(side='right', gridcolor='#333'),
        xaxis=dict(gridcolor='#333'),
        margin=dict(l=0, r=60, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Data load nahi hoya. GitHub requirements check karo.")
