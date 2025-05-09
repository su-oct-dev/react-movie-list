import streamlit as st
import requests
import json
from typing import List, Optional, Dict, Any, Tuple

API_BASE_URL = "http://localhost:8000"

GameState = Dict[str, Any]

def start_new_game() -> GameState:
    """
    新しいゲームを開始する

    Returns:
        GameState: 新しいゲームの初期状態
    """
    response = requests.post(f"{API_BASE_URL}/start")
    return response.json()

def get_game_state() -> Optional[GameState]:
    """
    現在のゲーム状態を取得する

    Returns:
        Optional[GameState]: 現在のゲーム状態。ゲームが開始されていない場合はNone
    """
    try:
        response = requests.get(f"{API_BASE_URL}/")
        return response.json()
    except:
        return None

def make_move(row: int, col: int) -> GameState:
    """
    プレイヤーの手を処理する

    Args:
        row (int): 行のインデックス
        col (int): 列のインデックス

    Returns:
        GameState: 手を適用した後のゲーム状態
    """
    response = requests.post(
        f"{API_BASE_URL}/move",
        json={"row": row, "col": col}
    )
    return response.json()

def reset_game() -> GameState:
    """
    ゲームをリセットする

    Returns:
        GameState: リセットされたゲームの状態
    """
    response = requests.get(f"{API_BASE_URL}/reset")
    return response.json()

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
    
    if "game_state" not in st.session_state:
        game_state = get_game_state()
        if game_state is None:
            game_state = start_new_game()
        st.session_state.game_state = game_state
    
    game_state = st.session_state.game_state
    
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
        st.session_state.game_state = reset_game()
        st.rerun()

if __name__ == "__main__":
    main()
