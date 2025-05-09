

echo "uvを使用して依存関係をインストールしています..."
uv pip install -r frontend/requirements.txt

echo "バックエンドサーバーを起動しています..."
uvicorn main:app --reload &
BACKEND_PID=$!

echo "バックエンドサーバーの起動を待機しています..."
sleep 5

echo "フロントエンドを起動しています..."
cd frontend && streamlit run app.py

kill $BACKEND_PID
