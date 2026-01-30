# 🎓 大学空きコマ共有アプリ

大学生同士で時間割を共有し、リアルタイムで友達の空きコマを確認できるWebアプリです。
「今誰が空いているか？」を瞬時に把握して、一緒にランチや自習ができる仲間を見つけましょう！

## 🌐 アプリを試す

**👉 [アプリを開く](https://your-app-url.streamlit.app/)**

*アカウント作成は簡単！ユーザーIDとパスワードを設定するだけで始められます。*

---

## ✨ このアプリでできること

### 🔍 **今すぐ空いている友達を発見**
現在の時刻と曜日から、リアルタイムで友達の状況を自動判定
- 🔴 **講義中の友達** → 授業があるため連絡は控えめに
- 🟢 **空きコマ中の友達** → 一緒に過ごせるチャンス！

### 💬 **一言ステータスで今の気分をシェア**
「図書館で勉強中」「学食でランチ」「課題に追われてる...」など、
今何をしているかを友達に伝えられます

### 📅 **簡単時間割管理**
- 月〜金曜日の1〜5限に対応
- 講義名を登録するだけの簡単操作
- 見やすいグリッド形式で一目で確認

### 🔍 **特定の時間で空きコマ検索**
「明日の3限、誰が空いてる？」といった検索が可能
計画的に友達との時間を作れます

---

## 📱 使い方（3ステップで開始）

### 1️⃣ アカウント作成
- ユーザーID（英数字）を決める
- 表示名（本名など）を入力
- パスワードを設定

### 2️⃣ 時間割を登録
「📅 マイ時間割」タブで授業を追加
- 曜日を選択
- 時限を選択  
- 講義名を入力して登録

### 3️⃣ 友達の状況をチェック
「🏠 ホーム」タブで今すぐ確認
- 現在講義中の人
- 現在空きコマの人
- みんなの一言ステータス

---

## ⏰ 対応時間

| 時限 | 時間 |
|------|------|
| 1限 | 08:40 - 10:10 |
| 2限 | 10:25 - 11:55 |
| 3限 | 12:55 - 14:25 |
| 4限 | 14:40 - 16:10 |
| 5限 | 16:25 - 17:55 |

*授業時間外は全員が「空きコマ」として表示されます*

---

## 🎯 こんな時に便利

- **ランチタイム**: 「今誰が空いてる？一緒に学食行こう！」
- **自習時間**: 「図書館で勉強する仲間を探したい」
- **課題相談**: 「同じ授業を取ってる人で今空いてる人は？」
- **暇つぶし**: 「空きコマで暇...誰かいないかな？」

---

## 🚀 開発者向け情報

### 技術スタック
- **フロントエンド**: Streamlit
- **データベース**: Supabase (PostgreSQL)
- **認証**: Supabase Auth
- **デプロイ**: Streamlit Cloud

### ローカル開発
```bash
# リポジトリクローン
git clone <repository-url>
cd time_management_app

# 依存関係インストール
pip install streamlit pandas supabase

# Supabase設定
# .streamlit/secrets.toml に認証情報を設定

# アプリ起動
streamlit run streamlit_app.py
```

### データベース構造
```sql
-- ユーザープロフィール
CREATE TABLE profiles (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT DEFAULT ''
);

-- 時間割データ
CREATE TABLE schedules (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id),
  day TEXT NOT NULL,
  period INTEGER NOT NULL,
  subject_name TEXT NOT NULL
);
```

---

## 📞 お問い合わせ

- 🐛 **バグ報告**: [GitHub Issues](https://github.com/your-username/time_management_app/issues)
- 💡 **機能要望**: [GitHub Issues](https://github.com/your-username/time_management_app/issues)
- 🔧 **改善提案**: プルリクエスト大歓迎！

---

**👆 まずは[アプリを試してみる](https://your-app-url.streamlit.app/)！**