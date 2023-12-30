from flask import Flask, request, jsonify, Response

import flask
from dataclasses import dataclass, asdict
import queue
import time
from threading import Thread
import math
import json
import re

########
# GAME
########

MAP_WIDTH = 1000
MAP_HEIGHT = 500
BASE_SIZE = 175

PLAYER_RADIUS = 10
PLAYER_SPEED = 100  # px/sec
DEATH_COOLDOWN_SECONDS = 10
SPEED_UP_COOLDOWN_SECONDS = 10
SPEED_UP_DURATION_SECONDS = 1

TICS_PER_SECOND = 30

TEAM_RED = "Red"
TEAM_BLUE = "Blue"

app = Flask(__name__, static_url_path="", static_folder="../client")


@dataclass
class Player:
    x: float
    y: float
    died_at: float | None
    speed_up_at: float | None
    has_flag: bool
    team: str
    name: str
    direction: float


@dataclass
class State:
    players: list[Player]
    points: dict
    server_time: float | None


state = State([], {TEAM_RED: 0, TEAM_BLUE: 0}, None)


def game_loop():
    while True:
        state.server_time = time.time()
        update_positions(state.players)

        for i in range(len(state.players)):
            if is_dead(state.players[i]):
                state.players[i].died_at = time.time()
                state.players[i].has_flag = False

            elif (
                state.players[i].died_at != None
                and (time.time() - state.players[i].died_at) > DEATH_COOLDOWN_SECONDS
            ):
                state.players[i].died_at = None
                reset_player(state.players[i])

        has_flag = {
            TEAM_RED: has_someone_flag(TEAM_RED),
            TEAM_BLUE: has_someone_flag(TEAM_BLUE),
        }

        for p in state.players:
            if not has_flag[p.team] and is_in_base(other_team(p.team), p):
                has_flag[p.team] = True
                p.has_flag = True

        for p in state.players:
            if p.has_flag and is_in_base(p.team, p):
                state.points[p.team] += 1
                reset_map()
                break

        broadcast_state(state)
        time.sleep(1 / TICS_PER_SECOND - (time.time() - state.server_time))


def reset_map():
    for p in state.players:
        reset_player(p)


def has_someone_flag(team: str) -> bool:
    for p in state.players:
        if p.team == team and p.has_flag:
            return True
    return False


def move_player(p: Player) -> None:
    if p.died_at:
        return
    speed_modifier = 1
    if p.speed_up_at and state.server_time - p.speed_up_at < SPEED_UP_DURATION_SECONDS:
        speed_modifier = 1.5

    distance_per_tick = speed_modifier * PLAYER_SPEED / TICS_PER_SECOND
    p.x += math.cos(p.direction) * distance_per_tick
    p.y += math.sin(p.direction) * distance_per_tick
    ensure_player_on_map(p)


def are_overlapping(player1, player2):
    distance2 = (player1.x - player2.x) ** 2 + (player1.y - player2.y) ** 2
    return distance2 < (2 * PLAYER_RADIUS) ** 2


def update_positions(players):
    for i, player in enumerate(players):
        for j, other_player in enumerate(players):
            if i != j and are_overlapping(player, other_player):
                bounce(player, other_player)
        move_player(player)


def bounce(player, other_player):
    # Calculate the angle of the line connecting the centers
    dx = other_player.x - player.x
    dy = other_player.y - player.y
    collision_angle = math.atan2(dy, dx)

    # Reverse direction along this line
    player.direction = -collision_angle


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
    if p.died_at:
        return False
    if not is_on_enemy_ground(p):
        return False
    for o in state.players:
        if p.team == o.team or o.died_at != None:
            continue
        dist_sqare = (p.x - o.x) ** 2 + (p.y - o.y) ** 2

        if dist_sqare < ((PLAYER_RADIUS * 2) ** 2):
            return True
    return False


def add_player(name, team):
    player = Player(0, 0, None, None, False, team, name, 0.0)
    reset_player(player)
    state.players.append(player)


def reset_player(p: Player) -> None:
    p.x = (
        PLAYER_RADIUS + BASE_SIZE
        if p.team == TEAM_RED
        else MAP_WIDTH - PLAYER_RADIUS - BASE_SIZE
    )
    p.y = MAP_HEIGHT / 2
    p.has_flag = False
    p.died_at = None
    p.speed_up_at = None


def other_team(team: str) -> str:
    return TEAM_RED if team == TEAM_BLUE else TEAM_BLUE


########
# ROUTES
########


@app.route("/register", methods=["POST"])
def register() -> Response:
    content = request.json
    if content.get("team") not in [TEAM_RED, TEAM_BLUE]:
        return "Team has to be either Red or Blue", 400

    if not content.get("name"):
        return "Name cannot be empty", 400
    if content.get("name") in [p.name for p in state.players]:
        return "Name already taken", 400
    if len(content.get("name")) > 10:
        return "Name too long", 400
    if not re.match("^[a-zA-Z0-9]+$", content.get("name")):
        return "Only alphanumerical characters are allowed", 400

    add_player(content.get("name"), content.get("team"))

    return jsonify(content)


@app.route("/set-direction", methods=["POST"])
def set_direction() -> Response:
    player_name = request.args.get("name")

    content = request.json

    for i in range(len(state.players)):
        if state.players[i].name == player_name:
            state.players[i].direction = content.get("direction")

    return jsonify({"ok": True})


@app.route("/speed-up", methods=["POST"])
def speed_up() -> Response:
    player_name = request.args.get("name")

    for i in range(len(state.players)):
        if state.players[i].name == player_name and (
            state.players[i].speed_up_at is None
            or (time.time() - state.players[i].speed_up_at) > SPEED_UP_COOLDOWN_SECONDS
        ):
            state.players[i].speed_up_at = time.time()

    return jsonify({"ok": True})


@app.route("/kick", methods=["POST"])
def kick() -> Response:
    player_name = request.args.get("name")

    for i in range(len(state.players)):
        if state.players[i].name == player_name:
            del state.players[i]
            break

    return jsonify({"ok": True})


########
# EVENTS
########

listeners = []


def format_sse(data: str, event=None) -> str:
    msg = f"data: {data}\n\n"
    if event is not None:
        msg = f"event: {event}\n{msg}"
    return msg


@app.route("/events", methods=["GET"])
def listen():
    def stream():
        listeners.append(messages := queue.Queue(maxsize=100))
        while True:
            msg = messages.get()
            yield msg

    return flask.Response(stream(), mimetype="text/event-stream")


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
    app.run(host="0.0.0.0", debug=True)
