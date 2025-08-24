from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from models import Move, GameState
from game_manager import GameManager
from typing import List
import json
import os

app = FastAPI()
manager = GameManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar a dominios específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections: dict[str, List[WebSocket]] = {}

@app.post("/create_game")
async def create_game():
    game_id = manager.create_game()
    return {"game_id": game_id}

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()
    if game_id not in active_connections:
        active_connections[game_id] = []
    active_connections[game_id].append(websocket)

    try:
        fen = manager.get_fen(game_id)
        await websocket.send_text(json.dumps({"fen": fen}))

        while True:
            data = await websocket.receive_text()
            move_data = json.loads(data)
            move_uci = move_data.get("move")

            if not move_uci:
                await websocket.send_text(json.dumps({"error": "No se recibió movimiento"}))
                continue

            valid = manager.make_move(game_id, move_uci)
            if not valid:
                await websocket.send_text(json.dumps({"error": "Movimiento inválido"}))
                continue

            fen = manager.get_fen(game_id)
            game_over = manager.game_over(game_id)
            winner = manager.get_winner(game_id)

            response = {
                "fen": fen,
                "game_over": game_over,
                "winner": winner
            }

            for connection in active_connections[game_id]:
                await connection.send_text(json.dumps(response))

            if game_over:
                for conn in active_connections[game_id]:
                    await conn.close()
                active_connections.pop(game_id)
                break

    except WebSocketDisconnect:
        active_connections[game_id].remove(websocket)
        if len(active_connections[game_id]) == 0:
            active_connections.pop(game_id)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

