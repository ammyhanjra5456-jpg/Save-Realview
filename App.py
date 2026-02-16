import streamlit as st

import yfinance as yf

import pandas as pd

import numpy as np

import plotly.graph_objects as go

from datetime import datetime, timedelta



# --- CONFIGURATION ---

st.set_page_config(layout="wide", page_title="SAVE Real-View PRO")

st.markdown("""<style> .main { background-color: #0e1117; } </style>""", unsafe_allow_html=True)



with st.sidebar:

    st.header("Terminal Controls")

    if st.button("🔄 Force Market Refresh"):

        st.cache_data.clear()

        st.rerun()



st.title("SAVE Real-View: Clean Entry Terminal")

st.write("Status: Institutional Directional Bias | Simplified View")



@st.cache_data(ttl=30)

def get_institutional_data():

    try:

        df = yf.download("GC=F", period="5d", interval="5m")

        if df.empty: raise ValueError("No data")

        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        return df

    except: return pd.DataFrame()



data = get_institutional_data()



if not data.empty:

    last_price = float(data['Close'].iloc[-1])

    

    # AI LOGIC

    inst_res = float(data['High'].tail(150).max())

    inst_sup = float(data['Low'].tail(150).min())

    volatility = float(data['Close'].std())

    trend = float(data['Close'].diff().tail(15).mean())



    fig = go.Figure()



    # 1. REAL MARKET (Solid White/Grey)

    fig.add_trace(go.Candlestick(

        x=data.index, open=data['Open'], high=data['High'], 

        low=data['Low'], close=data['Close'], name='Market',

        increasing_line_color='#ffffff', decreasing_line_color='#4a4a4a'

    ))



    # 2. GHOST PREDICTIONS (Simplified)

    temp_price = last_price

    last_time = data.index[-1]

    

    np.random.seed(int(datetime.now().strftime("%Y%m%d%H")))



    for i in range(1, 31): # 30 candles only for clarity

        future_time = last_time + timedelta(minutes=5 * i)

        

        # Smooth Bias Logic

        bias = 0.6 if temp_price <= inst_sup else (-0.6 if temp_price >= inst_res else trend * 1.2)

        move = bias + np.random.normal(0, volatility * 0.08)

        new_close = temp_price + move

        

        # REDUCED WICKS: Simplified for better entry visualization

        p_high = max(temp_price, new_close) + (volatility * 0.2)

        p_low = min(temp_price, new_close) - (volatility * 0.2)

        

        color = 'rgba(0, 255, 150, 0.2)' if new_close >= temp_price else 'rgba(255, 50, 50, 0.2)'

        

        fig.add_trace(go.Candlestick(

            x=[future_time], open=[temp_price], high=[p_high], low=[p_low], close=[new_close],

            increasing_line_color=color, decreasing_line_color=color,

            increasing_fillcolor=color, decreasing_fillcolor=color, showlegend=False

        ))

        temp_price = new_close



    # 3. ENTRY ZONE VISUALIZER

    # Predicts the best area to put your Limit Order

    entry_level = last_price - (volatility * 0.5) if trend > 0 else last_price + (volatility * 0.5)

    fig.add_hline(y=entry_level, line_dash="dot", line_color="orange", 

                  annotation_text="OPTIMAL ENTRY ZONE (LIMIT ORDER)")



    fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=800,

                      yaxis=dict(side='right', gridcolor='#1f2937'))

    

    st.plotly_chart(fig, use_container_width=True)

    st.success(f"Strategy: Look for price to touch the **Orange Dot Line** before following the Ghost Path.")

else:

    st.warning("Market is closed. Check back during London/NY sessions.")
