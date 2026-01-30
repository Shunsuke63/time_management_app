import streamlit as st
import pandas as pd
import datetime
from datetime import timezone, timedelta
from supabase import create_client, Client

# --- 1. Supabase接続設定 ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

VIRTUAL_DOMAIN = "@student.app"

# --- 3. 認証フォーム ---
def login_form():
    st.title("🎓 空きコマ共有アプリ")
    auth_mode = st.tabs(["ログイン", "新規登録"])
    
    with auth_mode[0]:
        l_id = st.text_input("ユーザーID", key="l_id")
        l_pw = st.text_input("パスワード", type="password", key="l_pw")
        
        if st.button("ログイン", use_container_width=True):
            email = l_id + VIRTUAL_DOMAIN
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": l_pw})
                if res.user:
                    st.session_state.user = res.user
                    st.rerun()
            except Exception as e:
                st.error(f"ログイン失敗: {e}")

    with auth_mode[1]:
        r_id = st.text_input("希望するユーザーID", key="r_id", help="英数字のみ")
        r_name = st.text_input("表示名（本名など）", key="r_name")
        r_pw = st.text_input("パスワード設定", type="password", key="r_pw")
        
        if st.button("アカウント作成", use_container_width=True):
            if not r_id or not r_pw or not r_name:
                st.warning("すべての項目を入力してください。")
            else:
                email = r_id + VIRTUAL_DOMAIN
                try:
                    res = supabase.auth.sign_up({"email": email, "password": r_pw})
                    if res.user:
                        # プロフィールをDBに作成
                        supabase.table("profiles").upsert({
                            "id": res.user.id,
                            "name": r_name,
                            "status": "登録しました！"
                        }).execute()
                        st.success("登録完了！そのままログインしてください。")
                except Exception as e:
                    st.error(f"登録エラー: {e}")

if "user" not in st.session_state:
    st.session_state.user = None
if st.session_state.user is None:
    login_form()
    st.stop()

# --- 4. ログイン後の処理 ---
user_id = st.session_state.user.id

# 常に最新のプロフィール名を取得
try:
    p_data = supabase.table("profiles").select("name").eq("id", user_id).single().execute()
    current_user_name = p_data.data["name"] if p_data.data else "ゲスト"
except:
    current_user_name = "ゲスト"

# サイドバー設定
st.sidebar.title(f"👤 {current_user_name}")
if st.sidebar.button("ログアウト"):
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

# --- 5. 日本時間判定ロジック ---
DAYS = ["月", "火", "水", "木", "金"]
PERIODS_LIST = [1, 2, 3, 4, 5]
PERIODS_TIME = {1: ("08:40", "10:10"), 2: ("10:25", "11:55"), 3: ("12:55", "14:25"), 4: ("14:40", "16:10"), 5: ("16:25", "17:55")}

def get_current_info():
    # 本番サーバー(UTC)でも日本時間(JST)で取得
    JST = timezone(timedelta(hours=+9))
    now = datetime.datetime.now(JST)
    weekday = ["月", "火", "水", "木", "金", "土", "日"][now.weekday()]
    curr_time = now.strftime("%H:%M")
    curr_p = next((p for p, (s, e) in PERIODS_TIME.items() if s <= curr_time <= e), None)
    return weekday, curr_p

st.sidebar.caption(f"日本時刻: {datetime.datetime.now(timezone(timedelta(hours=+9))).strftime('%H:%M')}")

# --- 6. メインレイアウト ---
tab1, tab2, tab3 = st.tabs(["🏠 ホーム", "📅 マイ時間割", "🔍 空きコマ検索"])

# --- Tab 1: ホーム ---
with tab1:
    st.header("📍 友人の「今」")
    col_stat, col_btn = st.columns([3, 1])
    with col_stat:
        # keyをブラウザが推測しにくい名前に変更し、
        # typeを指定しないことで「ただの文字列入力」であることを強調します
        new_status = st.text_input(
            "一言ステータス", 
            placeholder="学食で寿司を食べる...", 
            key="user_status_update_field" # 推測されにくいキー名に変更
        )
    with col_btn:
        st.write("")
        if st.button("更新"):
            supabase.table("profiles").update({"status": new_status}).eq("id", user_id).execute()
            st.toast("ステータスを更新しました！")

    st.divider()
    curr_day, curr_p = get_current_info()
    st.subheader(f"📅 {curr_day}曜日 {f'{curr_p}限' if curr_p else '（授業時間外）'}")

    # ユーザーとスケジュールを取得
    all_users = supabase.table("profiles").select("name, status, schedules(day, period)").execute().data

    col_busy, col_free = st.columns(2)
    with col_busy:
        st.markdown("### 📖 講義中")
        for u in all_users:
            if any(s['day'] == curr_day and s['period'] == curr_p for s in u.get('schedules', [])):
                st.info(f"🔴 **{u['name']}**\n\n{u['status']}")
    with col_free:
        st.markdown("### ☕️ 空きコマ")
        for u in all_users:
            is_busy = any(s['day'] == curr_day and s['period'] == curr_p for s in u.get('schedules', []))
            if not is_busy and curr_p:
                st.success(f"🟢 **{u['name']}**\n\n{u['status']}")

# --- Tab 2: 自分の時間割 ---
with tab2:
    st.header("📅 マイ時間割")
    my_schedules = supabase.table("schedules").select("*").eq("user_id", user_id).execute().data
    df = pd.DataFrame(index=[f"{p}限" for p in PERIODS_LIST], columns=DAYS).fillna("-")
    for s in my_schedules:
        if s['day'] in DAYS:
            df.at[f"{s['period']}限", s['day']] = s['subject_name']
    st.table(df)

    st.divider()
    with st.form("add_lecture"):
        d, p, sub = st.selectbox("曜日", DAYS), st.select_slider("時限", options=PERIODS_LIST), st.text_input("講義名")
        if st.form_submit_button("登録"):
            supabase.table("schedules").delete().eq("user_id", user_id).eq("day", d).eq("period", p).execute()
            supabase.table("schedules").insert({"user_id": user_id, "day": d, "period": p, "subject_name": sub}).execute()
            st.rerun()

# --- Tab 3: 空きコマ検索 ---
with tab3:
    st.header("🔍 空きコマ検索")
    t_day = st.selectbox("曜日を選択", DAYS)
    t_p = st.select_slider("時限を選択", options=PERIODS_LIST)
    
    for u in all_users:
        if not any(s['day'] == t_day and s['period'] == t_p for s in u.get('schedules', [])):
            st.write(f"👤 **{u['name']}** （{u['status']}）")