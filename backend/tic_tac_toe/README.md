# マルバツゲーム（三目並べ）FastAPI アプリケーション

FastAPIを使用した三目並べゲームのAPIサーバーです。

## 機能

- 新しいゲームの開始
- 現在のゲーム状態の取得
- プレイヤーの手の処理
- ゲームのリセット

## 必要条件

- Python 3.8以上
- FastAPI
- Uvicorn

## インストール方法

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windowsの場合
venv\Scripts\activate
# macOS/Linuxの場合
source venv/bin/activate

# 必要なパッケージをインストール
pip install fastapi uvicorn
```

## 実行方法

```bash
# アプリケーションを起動
uvicorn main:app --reload
```

サーバーが起動したら、ブラウザで http://localhost:8000/docs にアクセスして、Swagger UIからAPIを操作できます。

## APIエンドポイント

- `GET /`: 現在のゲーム状態を取得
- `POST /start`: 新しいゲームを開始
- `POST /move`: プレイヤーの手を処理（リクエストボディに行と列のインデックスを指定）
- `GET /reset`: ゲームをリセット

## 使用例

1. `/start` エンドポイントを呼び出して新しいゲームを開始
2. `/move` エンドポイントを呼び出してプレイヤーの手を処理（例: `{"row": 0, "col": 0}`）
3. `/` エンドポイントを呼び出して現在のゲーム状態を確認
4. 必要に応じて `/reset` エンドポイントを呼び出してゲームをリセット

## ゲームのルール

- プレイヤーは交互に手を打ちます（最初はXから）
- 縦、横、または対角線に3つ同じマークを並べると勝利
- すべてのマスが埋まると引き分け
