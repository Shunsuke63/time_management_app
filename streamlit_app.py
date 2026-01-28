import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- Supabase接続 (既存) ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

DAYS = ["月", "火", "水", "木", "金"]
PERIODS_LIST = [1, 2, 3, 4, 5]

# --- ユーザー切り替え (テスト用・既存) ---
# --- ユーザー切り替え (修正後) ---
st.sidebar.title("ユーザー設定")
current_user_name = st.sidebar.text_input("あなたの名前", value="自分の名前")

# 文字列をUUIDとして正しい形式に変更します
user_id_map = {
    "自分の名前": "00000000-0000-0000-0000-000000000001", 
    "友人A": "00000000-0000-0000-0000-000000000002", 
    "友人B": "00000000-0000-0000-0000-000000000003"
}
current_user_id = user_id_map.get(current_user_name, "00000000-0000-0000-0000-000000000099")

# --- UIセクション ---
tab1, tab2, tab3 = st.tabs(["🏠 ホーム", "📅 自分の時間割", "🔍 空きコマ検索"])

# --- Tab 2: 自分の時間割 (ここを強化) ---
with tab2:
    st.header(f"📅 {current_user_name} の時間割")

    # 1. データの取得
    res = supabase.table("schedules").select("*").eq("user_id", current_user_id).execute()
    my_schedules = res.data

    # 2. 表示用のDataFrame作成 (数理系らしくPandasで整形)
    # 行を時限、列を曜日にした空の表を作る
    df = pd.DataFrame(index=[f"{p}限" for p in PERIODS_LIST], columns=DAYS)
    df = df.fillna("-") # 空白をハイフンで埋める

    # 取得したデータを表に埋め込む
    for s in my_schedules:
        row = f"{s['period']}限"
        col = s['day']
        if col in DAYS and row in df.index:
            df.at[row, col] = s['subject_name']

    # 3. 時間割表の表示
    st.table(df) # きれいな表形式で表示

    st.divider()

    # 4. 登録・削除フォーム
    col_add, col_del = st.columns(2)
    
    with col_add:
        st.subheader("➕ 講義を追加")
        with st.form("add_form"):
            new_day = st.selectbox("曜日", DAYS)
            new_period = st.select_slider("時限", options=PERIODS_LIST)
            new_subject = st.text_input("講義名")
            if st.form_submit_button("登録"):
                # 重複を避けるため、同じ曜限の既存データを削除してから挿入（簡易upsert）
                supabase.table("schedules").delete().eq("user_id", current_user_id).eq("day", new_day).eq("period", new_period).execute()
                supabase.table("schedules").insert({
                    "user_id": current_user_id, 
                    "day": new_day, 
                    "period": new_period, 
                    "subject_name": new_subject
                }).execute()
                st.rerun() # 再描画して表を更新

    with col_del:
        st.subheader("🗑️ 講義を削除")
        with st.form("del_form"):
            del_day = st.selectbox("削除する曜日", DAYS)
            del_period = st.select_slider("削除する時限", options=PERIODS_LIST)
            if st.form_submit_button("削除"):
                supabase.table("schedules").delete().eq("user_id", current_user_id).eq("day", del_day).eq("period", del_period).execute()
                st.rerun()