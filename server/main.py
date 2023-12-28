from flask import Flask, request, jsonify, Response
import flask
from flask_cors import CORS
from dataclasses import dataclass
import queue
import time
from threading import Thread

########
# GAME
########

MAP_WIDTH=1000
MAP_HEIGHT=500

PLAYER_RADIUS=5

TEAM_RED = "Red"
TEAM_BLUE = "Blue"

@dataclass
class Player:
    x: float
    y: float
    is_alive: bool
    has_flag: bool
    team: str
    name: str
    direction: float

@dataclass
class State:
    players: list[Player]

state = State([])

def add_player(name, team):
    startPosY = MAP_HEIGHT / 2
    startPosX = PLAYER_RADIUS if team == TEAM_RED else MAP_WIDTH - PLAYER_RADIUS
    state.players.append(Player(startPosX, startPosY, True, False, name, team))

def game_loop():
    while True:
        broadcast_state(state)
        time.sleep(0.1)



########
# APP
########

app = Flask(__name__)
CORS(app) 

if __name__ == "__main__":
    thread = Thread(target=game_loop)
    thread.start()
    app.run()


########
# ROUTES
########

@app.route("/register", methods=["POST"])
def register() -> Response:
    content = request.json
    assert content.get("team") in [TEAM_RED, TEAM_BLUE], "Team has to be either Red or Blue"
    assert content.get("name"), "Name cannot be empty"

    add_player(content.get("name"), content.get("team"))

    return jsonify(content)

@app.route("/set-direction", methods=["POST"])
def set_direction() -> Response:
    player_name = request.args.get('name')

    content = request.json

    for i in range(len(state.players)):
        if state.players[i].name == player_name:
            state.players[i].direction = content.get("direction")

    return jsonify({"ok": True})


########
# EVENTS
########

listeners = []

def format_sse(data: str, event=None) -> str:
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg

@app.route('/events', methods=['GET'])
def listen():
    def stream():
        listeners.append(messages := queue.Queue(maxsize=100))
        while True:
            msg = messages.get()
            yield msg
    return flask.Response(stream(), mimetype='text/event-stream')

def broadcast_state(state):
    msg = format_sse(data=str(state), event="state")

    for i in reversed(range(len(listeners))):
        try:
            listeners[i].put_nowait(msg)
        except queue.Full:
            del listeners[i]
