import streamlit as st
import pandas as pd
import datetime
from supabase import create_client, Client

# --- 1. Supabase接続設定 ---
# .streamlit/secrets.toml に URL と KEY が設定されていることが前提です
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. 定数・共通ロジック ---
DAYS = ["月", "火", "水", "木", "金"]
PERIODS_LIST = [1, 2, 3, 4, 5]

# 大学の時間割（標準的な90分コマ）の定義
PERIODS_TIME = {
    1: ("09:00", "10:30"),
    2: ("10:40", "12:10"),
    3: ("13:00", "14:30"),
    4: ("14:40", "16:10"),
    5: ("16:20", "17:50"),
}

def get_current_info():
    """現在の曜日と何限目かを判定するロジック"""
    now = datetime.datetime.now()
    # 日本語の曜日に変換
    weekday_list = ["月", "火", "水", "木", "金", "土", "日"]
    weekday = weekday_list[now.weekday()]
    current_time = now.strftime("%H:%M")
    
    current_period = None
    for p, (start, end) in PERIODS_TIME.items():
        if start <= current_time <= end:
            current_period = p
            break
    return weekday, current_period

# --- 3. ユーザー切り替え (テスト用の擬似ログイン) ---
st.sidebar.title("👤 ユーザー設定")
current_user_name = st.sidebar.text_input("あなたの名前", value="自分の名前")

# データベースのUUID制約に合わせ、正しいUUID形式の文字列を使用します
user_id_map = {
    "自分の名前": "00000000-0000-0000-0000-000000000001", 
    "友人A": "00000000-0000-0000-0000-000000000002", 
    "友人B": "00000000-0000-0000-0000-000000000003"
}
# マップにない名前の場合はテスト用共通IDを割り当て
current_user_id = user_id_map.get(current_user_name, "00000000-0000-0000-0000-000000000099")

# --- 4. メインUIレイアウト ---
st.title("🎓 大学空きコマ共有アプリ")
tab1, tab2, tab3 = st.tabs(["🏠 ホーム", "📅 自分の時間割", "🔍 空きコマ検索"])

# --- Tab 1: ホーム（リアルタイム状況） ---
with tab1:
    st.header("📍 友人の「今」")
    
    # ステータス更新フォーム
    col_stat, col_btn = st.columns([3, 1])
    with col_stat:
        new_status = st.text_input("今の状況を更新", placeholder="例：学食で寿司を食べてる")
    with col_btn:
        st.write("") # スペース調整
        if st.button("更新", use_container_width=True):
            # プロフィールを更新（存在しなければ作成）
            supabase.table("profiles").upsert({
                "id": current_user_id, 
                "name": current_user_name, 
                "status": new_status
            }).execute()
            st.toast("ステータスを更新しました！")

    st.divider()

    # 現在の曜日・時限を取得
    curr_day, curr_p = get_current_info()
    st.subheader(f"🕒 現在: {curr_day}曜日 {f'{curr_p}限' if curr_p else '（時間外）'}")

    # 全ユーザーのプロフィールとスケジュールを一括取得
    try:
        res = supabase.table("profiles").select("name, status, schedules(day, period)").execute()
        all_users = res.data
    except Exception as e:
        st.error("データの取得に失敗しました。DBのセットアップを確認してください。")
        all_users = []

    col_busy, col_free = st.columns(2)
    
    with col_busy:
        st.markdown("### 📖 講義中")
        for user in all_users:
            # 現在の曜日に講義が入っているか判定
            is_busy = any(s['day'] == curr_day and s['period'] == curr_p for s in user.get('schedules', []))
            if is_busy:
                st.info(f"🔴 **{user['name']}**\n\n{user['status']}")

    with col_free:
        st.markdown("### ☕️ 空きコマ（暇）")
        for user in all_users:
            is_busy = any(s['day'] == curr_day and s['period'] == curr_p for s in user.get('schedules', []))
            # 講義がなく、かつ現在は授業時間内である場合（または土日など）
            if not is_busy:
                st.success(f"🟢 **{user['name']}**\n\n{user['status']}")

# --- Tab 2: 自分の時間割（管理画面） ---
with tab2:
    st.header(f"📅 {current_user_name} の時間割")

    # 1. データの取得
    res = supabase.table("schedules").select("*").eq("user_id", current_user_id).execute()
    my_schedules = res.data

    # 2. Pandasでグリッド形式に整形
    df = pd.DataFrame(index=[f"{p}限" for p in PERIODS_LIST], columns=DAYS)
    df = df.fillna("-") 

    for s in my_schedules:
        row = f"{s['period']}限"
        col = s['day']
        if col in DAYS and row in df.index:
            df.at[row, col] = s['subject_name']

    # 3. 表示
    st.table(df) 

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
                # 同じコマの既存データを削除してから挿入
                supabase.table("schedules").delete().eq("user_id", current_user_id).eq("day", new_day).eq("period", new_period).execute()
                supabase.table("schedules").insert({
                    "user_id": current_user_id, 
                    "day": new_day, 
                    "period": new_period, 
                    "subject_name": new_subject
                }).execute()
                st.rerun()

    with col_del:
        st.subheader("🗑️ 講義を削除")
        with st.form("del_form"):
            del_day = st.selectbox("曜日", DAYS, key="del_day")
            del_period = st.select_slider("時限", options=PERIODS_LIST, key="del_period")
            if st.form_submit_button("削除"):
                supabase.table("schedules").delete().eq("user_id", current_user_id).eq("day", del_day).eq("period", del_period).execute()
                st.rerun()

# --- Tab 3: 空きコマ検索 ---
with tab3:
    st.header("🔍 空きコマの友人を検索")
    st.write("特定の曜日・時限を指定して、空いている人を一覧表示します。")
    
    target_day = st.selectbox("曜日を選択", DAYS, key="search_day")
    target_period = st.select_slider("時限を選択", options=PERIODS_LIST, key="search_period")
    
    # 判定ロジック
    free_list = []
    if all_users:
        for user in all_users:
            is_busy = any(s['day'] == target_day and s['period'] == target_period for s in user.get('schedules', []))
            if not is_busy:
                free_list.append(user)
    
    if free_list:
        st.success(f"✅ {target_day}曜{target_period}限に空いている友人")
        for u in free_list:
            st.write(f"👤 **{u['name']}** （ステータス：{u['status']}）")
    else:
        st.info("この時間に空いている友人はいないようです。")