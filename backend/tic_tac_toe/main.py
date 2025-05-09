from typing import List, Optional, Tuple, Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum

app = FastAPI(title="マルバツゲーム", description="FastAPIを使用した三目並べゲーム")

class PlayerMark(str, Enum):
    """
    プレイヤーのマーク（X または O）を表す列挙型
    """
    X = "X"
    O = "O"

class GameStatus(str, Enum):
    """
    ゲームの状態を表す列挙型
    """
    IN_PROGRESS = "in_progress"
    X_WON = "x_won"
    O_WON = "o_won"
    DRAW = "draw"

class GameState(BaseModel):
    """
    ゲームの状態を表すモデル
    """
    board: List[List[Optional[PlayerMark]]]
    current_player: PlayerMark
    status: GameStatus

class MoveRequest(BaseModel):
    """
    プレイヤーの手を表すリクエストモデル
    """
    row: int
    col: int

game: Optional[GameState] = None

def create_empty_board() -> List[List[Optional[PlayerMark]]]:
    """
    空のゲームボードを作成する

    Returns:
        List[List[Optional[PlayerMark]]]: 3x3の空のゲームボード
    """
    return [[None for _ in range(3)] for _ in range(3)]

def check_winner(board: List[List[Optional[PlayerMark]]]) -> Optional[PlayerMark]:
    """
    ボードを確認して勝者を判定する

    Args:
        board (List[List[Optional[PlayerMark]]]): 現在のゲームボード

    Returns:
        Optional[PlayerMark]: 勝者のマーク。勝者がいない場合はNone
    """
    for row in board:
        if row[0] is not None and row[0] == row[1] == row[2]:
            return row[0]
    
    for col in range(3):
        if board[0][col] is not None and board[0][col] == board[1][col] == board[2][col]:
            return board[0][col]
    
    if board[0][0] is not None and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    
    if board[0][2] is not None and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    
    return None

def is_board_full(board: List[List[Optional[PlayerMark]]]) -> bool:
    """
    ボードが埋まっているかどうかを確認する

    Args:
        board (List[List[Optional[PlayerMark]]]): 現在のゲームボード

    Returns:
        bool: ボードが埋まっている場合はTrue、そうでない場合はFalse
    """
    for row in board:
        for cell in row:
            if cell is None:
                return False
    return True

def update_game_status(game_state: GameState) -> GameStatus:
    """
    ゲームの状態を更新する

    Args:
        game_state (GameState): 現在のゲーム状態

    Returns:
        GameStatus: 更新されたゲームステータス
    """
    winner = check_winner(game_state.board)
    
    if winner == PlayerMark.X:
        return GameStatus.X_WON
    elif winner == PlayerMark.O:
        return GameStatus.O_WON
    elif is_board_full(game_state.board):
        return GameStatus.DRAW
    else:
        return GameStatus.IN_PROGRESS

def switch_player(current_player: PlayerMark) -> PlayerMark:
    """
    プレイヤーを交代する

    Args:
        current_player (PlayerMark): 現在のプレイヤー

    Returns:
        PlayerMark: 次のプレイヤー
    """
    return PlayerMark.O if current_player == PlayerMark.X else PlayerMark.X

def is_valid_move(row: int, col: int, board: List[List[Optional[PlayerMark]]]) -> bool:
    """
    指定された手が有効かどうかを確認する

    Args:
        row (int): 行のインデックス
        col (int): 列のインデックス
        board (List[List[Optional[PlayerMark]]]): 現在のゲームボード

    Returns:
        bool: 手が有効な場合はTrue、そうでない場合はFalse
    """
    if not (0 <= row < 3 and 0 <= col < 3):
        return False
    
    return board[row][col] is None

@app.get("/", response_model=GameState)
def get_game_state() -> GameState:
    """
    現在のゲーム状態を取得する

    Returns:
        GameState: 現在のゲーム状態
    """
    if game is None:
        raise HTTPException(status_code=404, detail="ゲームが開始されていません")
    return game

@app.post("/start", response_model=GameState)
def start_new_game() -> GameState:
    """
    新しいゲームを開始する

    Returns:
        GameState: 新しいゲームの初期状態
    """
    global game
    game = GameState(
        board=create_empty_board(),
        current_player=PlayerMark.X,
        status=GameStatus.IN_PROGRESS
    )
    return game

@app.post("/move", response_model=GameState)
def make_move(move: MoveRequest) -> GameState:
    """
    プレイヤーの手を処理する

    Args:
        move (MoveRequest): プレイヤーの手（行と列のインデックス）

    Returns:
        GameState: 手を適用した後のゲーム状態

    Raises:
        HTTPException: ゲームが開始されていない、ゲームが終了している、または無効な手の場合
    """
    global game
    
    if game is None:
        raise HTTPException(status_code=404, detail="ゲームが開始されていません")
    
    if game.status != GameStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="ゲームは既に終了しています")
    
    if not is_valid_move(move.row, move.col, game.board):
        raise HTTPException(status_code=400, detail="無効な手です")
    
    game.board[move.row][move.col] = game.current_player
    
    game.status = update_game_status(game)
    
    if game.status == GameStatus.IN_PROGRESS:
        game.current_player = switch_player(game.current_player)
    
    return game

@app.get("/reset", response_model=GameState)
def reset_game() -> GameState:
    """
    ゲームをリセットする

    Returns:
        GameState: リセットされたゲームの状態
    """
    return start_new_game()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
