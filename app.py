import streamlit as st
import yfinance as yf
from FinMind.data import DataLoader
import pandas as pd
import pytz
from datetime import datetime
import time

# --- 1. 使用者數據設定 (在這裡設定 5 個人的股票) ---
USERS = {
    "zhlne": {"password": "1007", "tw": ["2330", "0050","0052","006208"], "us": ["VOO"]},
    "cyyan": {"password": "0401", "tw": ["0050"], "us": ["VOO"]},
    "user2": {"password": "qwe", "tw": ["2303", "2881"], "us": ["MSFT"]},
    "user3": {"password": "zxc", "tw": ["2603"], "us": ["GOOGL"]},
    "user4": {"password": "789", "tw": ["2330"], "us": ["AMZN"]}
}

TW_TZ = pytz.timezone('Asia/Taipei')
dl = DataLoader()

# --- 2. 登入邏輯 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login():
    st.title("🔐 全球股市監控系統 - 登入")
    user = st.text_input("帳號")
    pw = st.text_input("密碼", type="password")
    if st.button("登入"):
        if user in USERS and USERS[user]["password"] == pw:
            st.session_state['logged_in'] = True
            st.session_state['user'] = user
            st.rerun()
        else:
            st.error("帳號或密碼錯誤")

# --- 3. 主程式介面 ---
if not st.session_state['logged_in']:
    login()
else:
    # 登入成功後，取得該使用者的股票清單
    current_user = st.session_state['user']
    user_config = USERS[current_user]
    
    st.set_page_config(page_title=f"{current_user} 的投資組合", layout="wide")
    st.sidebar.write(f"👤 當前使用者: **{current_user}**")
    if st.sidebar.button("登出"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.title(f"📈 {current_user} 的即時監控儀表板")

    def fetch_user_data():
        now_tw = datetime.now(TW_TZ)
        now_str = now_tw.strftime("%H:%M:%S")
        hour = now_tw.hour
        
        # 判斷時段
        is_tw_time = 9 <= hour < 14
        data_list = []

        if is_tw_time:
            st.subheader(f"🇹🇼 台股時段 ({now_str})")
            for sid in user_config["tw"]:
                try:
                    df = dl.taiwan_stock_daily(stock_id=sid, start_date=now_tw.strftime("%Y-%m-%d"))
                    price = df['close'].iloc[-1] if not df.empty else "讀取中"
                    data_list.append({"市場": "台股", "代號": sid, "價格": price})
                except: pass
        else:
            st.subheader(f"🇺🇸 美股時段 ({now_str})")
            for sid in user_config["us"]:
                try:
                    ticker = yf.Ticker(sid)
                    price = round(ticker.fast_info['last_price'], 2)
                    data_list.append({"市場": "美股", "代號": sid, "價格": price})
                except: pass
        return pd.DataFrame(data_list)

    # 顯示數據
    df_current = fetch_user_data()
    if not df_current.empty:
        cols = st.columns(len(df_current))
        for i, row in df_current.iterrows():
            with cols[i]:
                st.metric(label=f"{row['市場']} - {row['代號']}", value=row['價格'])
    
    st.info(f"💡 系統正在監控你設定的股票。每 30 秒自動更新一次。")
    time.sleep(30)
    st.rerun()