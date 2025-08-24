import chess
from typing import Dict
from uuid import uuid4

class GameManager:
    def __init__(self):
        self.games: Dict[str, chess.Board] = {}

    def create_game(self) -> str:
        game_id = str(uuid4())
        self.games[game_id] = chess.Board()
        return game_id

    def get_game(self, game_id: str) -> chess.Board:
        return self.games.get(game_id)

    def make_move(self, game_id: str, move_uci: str) -> bool:
        board = self.games.get(game_id)
        if not board:
            return False
        try:
            move = chess.Move.from_uci(move_uci)
            if move in board.legal_moves:
                board.push(move)
                return True
            return False
        except:
            return False

    def get_fen(self, game_id: str) -> str:
        board = self.games.get(game_id)
        return board.fen() if board else ""

    def game_over(self, game_id: str) -> bool:
        board = self.games.get(game_id)
        return board.is_game_over() if board else True

    def get_winner(self, game_id: str) -> str:
        board = self.games.get(game_id)
        if board:
            if board.is_checkmate():
                return 'w' if board.turn == chess.BLACK else 'b'
            return 'draw'
        return ""
