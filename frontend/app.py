import streamlit as st
import requests
import json
import time
from typing import List, Optional, Dict, Any, Tuple

API_BASE_URL = "http://localhost:8000"

REQUEST_TIMEOUT = 3

MAX_RETRIES = 3

RETRY_INTERVAL = 1

GameState = Dict[str, Any]

def make_api_request(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    APIリクエストを実行する（リトライロジック付き）

    Args:
        method (str): HTTPメソッド（'get'または'post'）
        endpoint (str): APIエンドポイント
        data (Optional[Dict[str, Any]], optional): POSTリクエスト用のデータ

    Returns:
        Optional[Dict[str, Any]]: APIレスポンス。エラーの場合はNone
    """
    url = f"{API_BASE_URL}{endpoint}"
    
    for attempt in range(MAX_RETRIES):
        try:
            if method.lower() == 'get':
                response = requests.get(url, timeout=REQUEST_TIMEOUT)
            else:
                response = requests.post(url, json=data, timeout=REQUEST_TIMEOUT)
            
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            if attempt < MAX_RETRIES - 1:
                st.warning(f"APIリクエストに失敗しました。リトライします... ({attempt + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_INTERVAL)
            else:
                st.error(f"APIリクエストに失敗しました: {str(e)}")
                return None

def start_new_game() -> Optional[GameState]:
    """
    新しいゲームを開始する

    Returns:
        Optional[GameState]: 新しいゲームの初期状態。エラーの場合はNone
    """
    return make_api_request('post', '/start')

def get_game_state() -> Optional[GameState]:
    """
    現在のゲーム状態を取得する

    Returns:
        Optional[GameState]: 現在のゲーム状態。ゲームが開始されていない場合またはエラーの場合はNone
    """
    return make_api_request('get', '/')

def make_move(row: int, col: int) -> Optional[GameState]:
    """
    プレイヤーの手を処理する

    Args:
        row (int): 行のインデックス
        col (int): 列のインデックス

    Returns:
        Optional[GameState]: 手を適用した後のゲーム状態。エラーの場合はNone
    """
    return make_api_request('post', '/move', {"row": row, "col": col})

def reset_game() -> Optional[GameState]:
    """
    ゲームをリセットする

    Returns:
        Optional[GameState]: リセットされたゲームの状態。エラーの場合はNone
    """
    return make_api_request('get', '/reset')

def display_board(board: List[List[Optional[str]]]) -> None:
    """
    ゲームボードを表示する

    Args:
        board (List[List[Optional[str]]]): 現在のゲームボード
    """
    for i, row in enumerate(board):
        cols = st.columns(3)
        for j, cell in enumerate(row):
            if cell is None:
                button_text = " "
            else:
                button_text = cell
            
            if cols[j].button(button_text, key=f"cell_{i}_{j}", disabled=cell is not None):
                try:
                    st.session_state.game_state = make_move(i, j)
                    st.rerun()
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")

def main() -> None:
    """
    Streamlitアプリのメイン関数
    """
    st.title("マルバツゲーム（三目並べ）")
    
    default_game_state = {
        "board": [[None, None, None], [None, None, None], [None, None, None]],
        "current_player": "X",
        "status": "in_progress"
    }
    
    connection_status = st.empty()
    
    if "game_state" not in st.session_state:
        game_state = get_game_state()
        
        if game_state is None:
            game_state = start_new_game()
            
            if game_state is None:
                connection_status.error("バックエンドサーバーに接続できません。サーバーが起動しているか確認してください。")
                st.session_state.game_state = default_game_state
                st.session_state.connection_error = True
            else:
                st.session_state.game_state = game_state
                st.session_state.connection_error = False
        else:
            st.session_state.game_state = game_state
            st.session_state.connection_error = False
    
    # 現在のゲーム状態を取得
    game_state = st.session_state.game_state
    connection_error = st.session_state.get("connection_error", False)
    
    if game_state is None:
        game_state = default_game_state
        st.session_state.game_state = default_game_state
        connection_error = True
        st.session_state.connection_error = True
    
    if connection_error:
        connection_status.error("バックエンドサーバーに接続できません。サーバーが起動しているか確認してください。")
        st.warning("現在、オフラインモードで実行中です。バックエンドサーバーが起動したら、ページを更新してください。")
    else:
        connection_status.success("バックエンドサーバーに接続しています。")
    
    st.write(f"現在のプレイヤー: {game_state['current_player']}")
    st.write(f"ゲームの状態: {game_state['status']}")
    
    display_board(game_state["board"])
    
    if game_state["status"] == "x_won":
        st.success("プレイヤーXの勝利！")
    elif game_state["status"] == "o_won":
        st.success("プレイヤーOの勝利！")
    elif game_state["status"] == "draw":
        st.info("引き分けです！")
    
    if st.button("ゲームをリセット"):
        if connection_error:
            st.session_state.game_state = default_game_state
            st.rerun()
        else:
            new_game_state = reset_game()
            if new_game_state is None:
                st.error("ゲームのリセットに失敗しました。")
                st.session_state.connection_error = True
            else:
                st.session_state.game_state = new_game_state
                st.session_state.connection_error = False
            st.rerun()

if __name__ == "__main__":
    main()
