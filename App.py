import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SAVE Real-View PRO")
st.markdown("""<style> .main { background-color: #0e1117; } </style>""", unsafe_allow_html=True)

# --- SIDEBAR & FORCE REFRESH ---
with st.sidebar:
    st.header("Terminal Controls")
    if st.button("🔄 Force Market Refresh"):
        st.cache_data.clear()
        st.rerun()
    st.write("Project: SAN-AM EXPRESS DELIVERY")

st.title("SAVE Real-View: Institutional AI Terminal")
st.write("Status: Live Gold Analysis | Liquidity Sweep Mode Active")

# 1. FETCH DATA WITH ERROR HANDLING
@st.cache_data(ttl=30)
def get_institutional_data():
    try:
        # 5m interval for high-accuracy liquidity tracking
        df = yf.download("GC=F", period="5d", interval="5m")
        if df.empty:
            raise ValueError("No data returned")
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        return df
    except Exception as e:
        return pd.DataFrame()

data = get_institutional_data()

if not data.empty:
    # --- LIVE PRICE METRICS ---
    last_price = float(data['Close'].iloc[-1])
    open_price = float(data['Open'].iloc[-1])
    change = last_price - open_price
    
    col1, col2 = st.columns(2)
    col1.metric("Live Gold Price (Futures)", f"${last_price:,.2f}", f"{change:+.2f}")
    
    # --- 🔒 CONSISTENCY LOCK ---
    now = datetime.now()
    seed_value = int(now.strftime("%Y%m%d%H")) 
    np.random.seed(seed_value)

    # --- AI LOGIC (Liquidity & S/R) ---
    inst_resistance = float(data['High'].tail(200).max())
    inst_support = float(data['Low'].tail(200).min())
    recent_volatility = float(data['Close'].std())
    recent_trend = float(data['Close'].diff().tail(20).mean())

    # 2. GENERATE GHOST PREDICTIONS
    fig = go.Figure()

    # REAL MARKET CANDLES
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Live Market',
        increasing_line_width=1, decreasing_line_width=1
    ))

    temp_price = last_price
    last_time = data.index[-1]

    # GHOST CANDLES LOGIC (Next 40 candles)
    for i in range(1, 41):
        future_time = last_time + timedelta(minutes=5 * i)
        
        # Institutional Rejection
        if temp_price >= inst_resistance:
            bias = -0.7 
        elif temp_price <= inst_support:
            bias = 0.7 
        else:
            bias = recent_trend * 1.6 
            
        move = bias + np.random.normal(0, recent_volatility * 0.12)
        new_close = temp_price + move
        
        # --- ⚡ LIQUIDITY SWEEP (SHADOW WICK) LOGIC ⚡ ---
        # Eh logic predict karda hai ki big move ton pehla wick kithe tak jayegi
        sweep_buffer = recent_volatility * 1.4 # High volatility wick prediction
        
        if bias > 0: # Bullish bias
            p_high = max(temp_price, new_close) + 0.1
            p_low = min(temp_price, new_close) - sweep_buffer # Wick down to sweep SL
        elif bias < 0: # Bearish bias
            p_high = max(temp_price, new_close) + sweep_buffer # Wick up to sweep SL
            p_low = min(temp_price, new_close) - 0.1
        else:
            p_high = max(temp_price, new_close) + 0.2
            p_low = min(temp_price, new_close) - 0.2
        
        color = 'rgba(0, 255, 0, 0.35)' if new_close >= temp_price else 'rgba(255, 0, 0, 0.35)'
        
        fig.add_trace(go.Candlestick(
            x=[future_time], open=[temp_price], 
            high=[p_high], low=[p_low], close=[new_close],
            increasing_line_color=color, decreasing_line_color=color,
            increasing_fillcolor=color, decreasing_fillcolor=color,
            showlegend=False, line_width=1.5 # Bold wicks for SL warning
        ))
        temp_price = new_close

    # 3. TRADINGVIEW STYLING
    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=800,
        yaxis=dict(side='right', gridcolor='#1f2937', tickformat='.2f'),
        margin=dict(l=0, r=50, t=10, b=10)
    )
    
    fig.add_hline(y=inst_resistance, line_dash="dash", line_color="red", annotation_text="LIQUIDITY CEILING")
    fig.add_hline(y=inst_support, line_dash="dash", line_color="green", annotation_text="LIQUIDITY FLOOR")

    st.plotly_chart(fig, use_container_width=True)
    st.info("⚠️ SHADOW WICKS: Long wicks show where the Market may 'Sweep' your Stop-Loss before going to TP.")

else:
    st.warning("⚠️ Market Closed or Fetch Error. Try the Force Refresh button.")
