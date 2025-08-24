from pydantic import BaseModel
from typing import Optional

class Move(BaseModel):
    from_square: str
    to_square: Optional[str] = None
    promotion: Optional[str] = None

class Player(BaseModel):
    id: str
    name: str

class GameState(BaseModel):
    fen: str
    turn: str  # 'w' o 'b'
    winner: Optional[str] = None
    is_draw: bool = False
