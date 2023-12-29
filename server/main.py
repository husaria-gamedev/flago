from flask import Flask, request, jsonify, Response
from datetime import datetime

import flask
from dataclasses import dataclass, asdict
import queue
import time
from threading import Thread
import math
import json


########
# GAME
########

MAP_WIDTH=1000
MAP_HEIGHT=500
BASE_SIZE = 175

PLAYER_RADIUS=10
PLAYER_SPEED=100 # px/sec
DEATH_COOLDOWN_SECONDS=15

TICS_PER_SECOND=30

TEAM_RED = "Red"
TEAM_BLUE = "Blue"

app = Flask(__name__, static_url_path='', static_folder='../client')

@dataclass
class Player:
    x: float
    y: float
    died_at: datetime | None
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

        for i in range(len(state.players)):
            if is_dead(state.players[i]):
                state.players[i] = datetime.now()
            elif state.players[i].died_at != None and  (datetime.now() -state.players[i].died_at).seconds > DEATH_COOLDOWN_SECONDS: 
                state.players[i].died_at = None
                move_to_start(state.players[i])

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

def is_in_base(base: str, p: Player) -> bool:
    if p.y < (MAP_HEIGHT - BASE_SIZE) / 2:
        return False
    if p.y > (MAP_HEIGHT + BASE_SIZE) / 2:
        return False
    
    if base == TEAM_BLUE and p.x < MAP_WIDTH - BASE_SIZE / 2:
        return False

    if base == TEAM_RED and p.x > BASE_SIZE / 2:
        return False

    return True

def is_on_enemy_ground(p: Player) -> bool:
    if is_in_base(other_team(p.team), p):
        return False
    if is_in_base((p.team), p):
        return True
    if p.team == TEAM_RED and p.x > MAP_WIDTH / 2:
        return True
    if p.team == TEAM_BLUE and p.x < MAP_WIDTH / 2:
        return True
    return False

def is_dead(p: Player) -> bool:
    for o in state.players:
        if not is_on_enemy_ground(p) or p.team == o.team :
            continue
        dist_sqare = (p.x - o.x) ** 2 + (p.y - o.y) ** 2
        if dist_sqare < ((PLAYER_RADIUS * 2) ** 2):
            return True
    return False

def add_player(name, team):
    player = Player(0, 0, True, False, team, name,  0.)
    move_to_start(player)
    state.players.append(player)

def move_to_start(p: Player) -> None:

    p.x = PLAYER_RADIUS + BASE_SIZE if p.team == TEAM_RED else MAP_WIDTH - PLAYER_RADIUS - BASE_SIZE
    p.y = MAP_HEIGHT / 2

def other_team(team: str) -> str:
    return TEAM_RED if team == TEAM_BLUE else TEAM_BLUE


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
    msg = format_sse(data=json.dumps(asdict(state)), event="state")

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
    app.run(host="0.0.0.0")
