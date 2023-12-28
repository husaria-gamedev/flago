from flask import Flask, request, jsonify, Response
from flask_socketio import SocketIO
from dataclasses import dataclass

app = Flask(__name__)
socket = SocketIO(app)


@dataclass
class Player:
    x: int
    y: int
    is_alive: bool
    has_flag: bool
    team: str


@dataclass
class State:
    players: list[Player]
    blue_points: int
    red_points: int


@app.route("/register", methods=["POST"])
def register() -> Response:
    content = request.json
    assert content.get("team") in ["Red", "Blue"], "Team has to be either Red or Blue"
    assert content.get("name"), "Name cannot be empty"

    player_id = len(state.players)
    state.players.append(Player(500, 500, True, False, content["team"]))

    return jsonify({"id": player_id, **content})


@socket.on("connect")
def connect() -> None:
    print("[CLIENT CONNECTED]:", request.sid)


@socket.on("disconnect")
def disconn():
    print("[CLIENT DISCONNECTED]:", request.sid)


if __name__ == "__main__":
    state = State([], 0, 0)
    socket.run(app)
