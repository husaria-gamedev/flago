from flask import Flask, request, jsonify, Response
import flask
from flask_cors import CORS
from dataclasses import dataclass, asdict
import queue
import time
from threading import Thread
import math


########
# GAME
########

MAP_WIDTH=1000
MAP_HEIGHT=500

PLAYER_RADIUS=5
PLAYER_SPEED=10 # px/sec

TICS_PER_SECOND=10

TEAM_RED = "Red"
TEAM_BLUE = "Blue"

app = Flask(__name__)
CORS(app) 

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

def game_loop():
    while True:
        for i in range(len(state.players)):
            move_player(state.players[i])

        broadcast_state(state)
        time.sleep(1 / TICS_PER_SECOND)

def move_player(p: Player) -> None:
    distance_per_tick = PLAYER_SPEED / TICS_PER_SECOND
    p.x += math.cos(p.direction) * distance_per_tick
    p.y += math.sin(p.direction) * distance_per_tick
    ensure_player_on_map(p)

def ensure_player_on_map(p: Player) -> None:
    if p.x < PLAYER_RADIUS:
        p.x = PLAYER_RADIUS
    if p.x > MAP_WIDTH - PLAYER_RADIUS:
        p.x = MAP_WIDTH - PLAYER_RADIUS

    if p.y < PLAYER_RADIUS:
        p.y = PLAYER_RADIUS
    if p.y > MAP_HEIGHT - PLAYER_RADIUS:
        p.y = MAP_HEIGHT - PLAYER_RADIUS

def add_player(name, team):
    startPosY = MAP_HEIGHT / 2
    startPosX = PLAYER_RADIUS if team == TEAM_RED else MAP_WIDTH - PLAYER_RADIUS
    state.players.append(Player(startPosX, startPosY, True, False, team, name,  0.))




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
    msg = format_sse(data=asdict(state), event="state")

    for i in reversed(range(len(listeners))):
        try:
            listeners[i].put_nowait(msg)
        except queue.Full:
            del listeners[i]

########
# APP
########


if __name__ == "__main__":
    thread = Thread(target=game_loop)
    thread.start()
    app.run()
