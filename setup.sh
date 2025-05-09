
echo "uvを使用して依存関係をインストールしています..."
uv pip install -r frontend/requirements.txt

echo "バックエンドサーバーを起動しています..."
uvicorn main:app --reload &
BACKEND_PID=$!

echo "フロントエンドを起動しています..."
cd frontend && streamlit run app.py

kill $BACKEND_PID
