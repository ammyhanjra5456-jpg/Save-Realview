import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas_datareader.data as web

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SAVE Real-View PRO")
st.markdown("""<style> .main { background-color: #0e1117; } </style>""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Institutional Terminal")
    if st.button("🔄 Force Market Refresh"):
        st.cache_data.clear()
        st.rerun()

st.title("SAVE Real-View: Institutional Liquidity Mode")
st.write("Status: Ultra-Stable Data Mode (Anti-Forbidden)")

@st.cache_data(ttl=60)
def get_institutional_data():
    try:
        # Fetching Gold Price using Stooq (Alternative to Yahoo)
        end = datetime.now()
        start = end - timedelta(days=5)
        df = web.DataReader('GC.F', 'stooq', start, end)
        
        if df.empty: return pd.DataFrame()
        
        # Stooq returns data in reverse, so we sort it
        df = df.sort_index()
        return df
    except Exception as e:
        return pd.DataFrame()

data = get_institutional_data()

if not data.empty:
    last_price = float(data['Close'].iloc[-1])
    last_time = data.index[-1]
    
    # ATR Calculation
    high_low = data['High'] - data['Low']
    atr = high_low.tail(20).mean()
    
    st.metric("Gold Live (XAU/USD)", f"${last_price:,.2f}", delta=f"ATR: {atr:.2f}")
    
    inst_res = float(data['High'].tail(50).max())
    inst_sup = float(data['Low'].tail(50).min())
    trend = float(data['Close'].diff().tail(10).mean())

    fig = go.Figure()

    # 1. REAL MARKET
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], 
        low=data['Low'], close=data['Close'], name='Market',
        increasing_line_color='#ffffff', decreasing_line_color='#4a4a4a'
    ))

    # 2. GHOST PREDICTIONS
    temp_price = last_price
    for i in range(1, 31): 
        future_time = last_time + timedelta(minutes=15 * i)
        move = (trend * 1.5) + (np.random.randn() * atr * 0.5)
        new_close = temp_price + move
        
        p_high = max(temp_price, new_close) + (atr * 0.4)
        p_low = min(temp_price, new_close) - (atr * 0.4)
        
        color = 'rgba(0, 255, 150, 0.4)' if new_close >= temp_price else 'rgba(255, 50, 50, 0.4)'
        fig.add_trace(go.Candlestick(
            x=[future_time], open=[temp_price], high=[p_high], low=[p_low], close=[new_close],
            increasing_line_color=color, decreasing_line_color=color, showlegend=False
        ))
        temp_price = new_close

    # 3. REVERSAL SIGNAL
    if last_price >= (inst_res - (atr*0.5)) or last_price <= (inst_sup + (atr*0.5)):
        sig_col = "red" if last_price >= (inst_res - (atr*0.5)) else "green"
        fig.add_trace(go.Scatter(x=[last_time], y=[last_price], mode="markers+text",
                                 marker=dict(size=15, color=sig_col, symbol="diamond"),
                                 text=["⚠️ REVERSAL"], textposition="top center"))

    # 4. LAYOUT
    fig.add_hline(y=inst_res, line_dash="dash", line_color="red", annotation_text="SUPPLY")
    fig.add_hline(y=inst_sup, line_dash="dash", line_color="green", annotation_text="DEMAND")

    fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=800,
                      yaxis=dict(side='right'),
                      xaxis=dict(range=[last_time - timedelta(days=1), last_time + timedelta(hours=8)]))
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("📡 Data source is resetting. Please wait 1 minute and refresh.")
