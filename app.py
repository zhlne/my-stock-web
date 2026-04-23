import streamlit as st
import yfinance as yf
import pandas as pd
import pytz
from datetime import datetime
import time

# --- 1. 使用者數據設定 ---
USERS = {
    "zhlne": {"password": "1007", "tw": ["2330", "0050","0052","006208"], "us": ["VOO"]},
    "cyyan": {"password": "0401", "tw": ["0050"], "us": ["VOO"]},
    "user2": {"password": "qwe", "tw": ["2303", "2881"], "us": ["MSFT"]},
    "user3": {"password": "zxc", "tw": ["2603"], "us": ["GOOGL"]},
    "user4": {"password": "789", "tw": ["2330"], "us": ["AMZN"]}
}

TW_TZ = pytz.timezone('Asia/Taipei')

# --- 2. 登入邏輯 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login():
    st.title("🔐 全球股市監控系統")
    user = st.text_input("帳號")
    pw = st.text_input("密碼", type="password")
    if st.button("登入"):
        if user in USERS and USERS[user]["password"] == pw:
            st.session_state['logged_in'] = True
            st.session_state['user'] = user
            st.rerun()
        else:
            st.error("帳號或密碼錯誤")

if not st.session_state['logged_in']:
    login()
else:
    current_user = st.session_state['user']
    user_config = USERS[current_user]
    
    st.set_page_config(page_title=f"{current_user} 的投資組合", layout="wide")
    st.sidebar.write(f"👤 當前使用者: {current_user}")
    if st.sidebar.button("登出"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.title(f"📈 {current_user} 的即時監控儀表板")

    # --- 3. 數據抓取函式 ---
    def fetch_price(symbol, market="TW"):
        try:
            # 台股代號需要加上 .TW (上市) 或 .TWO (上櫃)
            ticker_sym = f"{symbol}.TW" if market == "TW" else symbol
            ticker = yf.Ticker(ticker_sym)
            
            # 使用 fast_info 獲取最新價格，效率較高
            price = ticker.fast_info['last_price']
            
            # 獲取前一日收盤價來計算漲跌
            prev_close = ticker.fast_info['previous_close']
            change = price - prev_close
            return round(price, 2), round(change, 2)
        except:
            return "N/A", 0

    # 顯示目前時間
    now_tw = datetime.now(TW_TZ)
    st.write(f"🕒 更新時間：{now_tw.strftime('%Y-%m-%d %H:%M:%S')}")

    # 分成兩欄顯示：台股與美股
    col_tw, col_us = st.columns(2)

    with col_tw:
        st.subheader("🇹🇼 台灣市場")
        for sid in user_config["tw"]:
            p, c = fetch_price(sid, "TW")
            st.metric(label=f"台股 {sid}", value=p, delta=c)

    with col_us:
        st.subheader("🇺🇸 美國市場")
        for sid in user_config["us"]:
            p, c = fetch_price(sid, "US")
            st.metric(label=f"美股 {sid}", value=p, delta=c)

    st.info(f"💡 系統自動監控中，每 30 秒更新一次。")
    
    # 這裡的 sleep 會讓 Streamlit 暫停，30秒後自動重新整理
    time.sleep(30)
    st.rerun()