# 🎓 大学空きコマ共有アプリ

友達の時間割を共有して、空きコマを一緒に過ごせる人を見つけるためのStreamlitアプリです。
リアルタイムで友達の状況を確認し、効率的にキャンパスライフを楽しめます。

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

## 🌟 主な機能

### 📍 リアルタイム状況確認
- 友達の現在の状況をリアルタイムで確認
- 「講義中」「空きコマ」の判定を自動で行う
- 各ユーザーのステータスメッセージを表示

### 📅 時間割管理
- 個人の時間割を登録・編集・削除
- 月〜金の1〜5限に対応（90分授業想定）
- 見やすいグリッド形式で表示

### 🔍 空きコマ検索
- 特定の曜日・時限で空いている友達を検索
- 効率的に一緒に過ごせる人を見つける

## 🚀 セットアップ方法

### 1. 必要な環境
- Python 3.11以上
- Supabaseアカウント（データベース用）

### 2. インストール
```bash
# リポジトリをクローン
git clone <repository-url>
cd time_management_app

# 必要なパッケージをインストール
pip install -r requirements.txt
```

### 3. データベースセットアップ
Supabaseで以下のテーブルを作成してください：

#### `profiles` テーブル
```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT DEFAULT ''
);
```

#### `schedules` テーブル
```sql
CREATE TABLE schedules (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id),
  day TEXT NOT NULL,
  period INTEGER NOT NULL,
  subject_name TEXT NOT NULL
);
```

### 4. 設定ファイル
`.streamlit/secrets.toml` ファイルを作成し、Supabaseの接続情報を設定：

```toml
SUPABASE_URL = "your_supabase_project_url"
SUPABASE_KEY = "your_supabase_anon_key"
```

### 5. アプリの起動
```bash
streamlit run streamlit_app.py
```

## 📱 使い方

### 初回利用時
1. サイドバーで自分の名前を入力
2. 「📅 自分の時間割」タブで授業を登録

### 日常の使用
1. **🏠 ホームタブ**：
   - 現在の状況を入力・更新
   - 友達の現在の状況を確認

2. **📅 自分の時間割タブ**：
   - 新しい授業を追加
   - 不要な授業を削除
   - 時間割の確認・編集

3. **🔍 空きコマ検索タブ**：
   - 曜日と時限を選択
   - 空いている友達を確認

### 時間割の時間設定
- 1限：09:00-10:30
- 2限：10:40-12:10  
- 3限：13:00-14:30
- 4限：14:40-16:10
- 5限：16:20-17:50

## 👥 多人数での利用

### テスト用ユーザー
アプリには以下のテストユーザーが用意されています：
- 自分の名前（デフォルト）
- 友人A
- 友人B

### 新しいユーザーの追加
[`streamlit_app.py`](streamlit_app.py)の`user_id_map`に新しいユーザーを追加：

```python
user_id_map = {
    "自分の名前": "00000000-0000-0000-0000-000000000001", 
    "友人A": "00000000-0000-0000-0000-000000000002", 
    "友人B": "00000000-0000-0000-0000-000000000003",
    "新しい友人": "00000000-0000-0000-0000-000000000004"  # 追加
}
```

## 🛠️ カスタマイズ

### 時間割の変更
[`PERIODS_TIME`](streamlit_app.py)辞書で各時限の時間を変更可能：

```python
PERIODS_TIME = {
    1: ("09:00", "10:30"),
    2: ("10:40", "12:10"),
    # ... 必要に応じて変更
}
```

### 曜日の追加
[`DAYS`](streamlit_app.py)リストで対象曜日を変更可能：

```python
DAYS = ["月", "火", "水", "木", "金", "土"]  # 土曜日を追加
```

## 🔧 開発環境

### Dev Container対応
VS Codeの開発コンテナに対応しています：
```bash
# コンテナで開発する場合
code .
# 「Reopen in Container」を選択
```

### 主要なファイル
- [`streamlit_app.py`](streamlit_app.py)：メインアプリケーション
- [`requirements.txt`](requirements.txt)：必要なPythonパッケージ
- [`.streamlit/secrets.toml`](.streamlit/secrets.toml)：設定ファイル（機密情報）

## 📝 ライセンス

Apache License 2.0 - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 🤝 貢献

プルリクエストや課題報告は大歓迎です！
改善案やバグ報告がありましたら、GitHubのIssuesをご利用ください。

## 📞 サポート

- 技術的な問題：GitHubのIssues
- 機能要望：プルリクエストまたはIssues
- データベーススキーマの詳細：Supabaseドキュメントを参照