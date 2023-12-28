from flask import Flask, request, jsonify, Response
import flask
from flask_cors import CORS
from dataclasses import dataclass
import queue
import time
from threading import Thread

app = Flask(__name__)
CORS(app) 

listeners = []

@dataclass
class Player:
    x: int
    y: int
    is_alive: bool
    has_flag: bool
    team: str
    name: str


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
    state.players.append(Player(500, 500, True, False, content["team"], content["name"]))

    return jsonify({"id": player_id, **content})


@app.route('/events', methods=['GET'])
def listen():
    def stream():
        listeners.append(messages := queue.Queue(maxsize=100))
        while True:
            msg = messages.get()
            yield msg
    return flask.Response(stream(), mimetype='text/event-stream')

def broadcast(msg):
    for i in reversed(range(len(listeners))):
        try:
            listeners[i].put_nowait(msg)
        except queue.Full:
            del listeners[i]

def format_sse(data: str, event=None) -> str:
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg

def keep_broadcasting():
    while True:
        time.sleep(0.1)
        msg = format_sse(data=str(state), event="state")
        broadcast(msg=msg)

if __name__ == "__main__":
    state = State([], 0, 0)
    thread = Thread(target=keep_broadcasting)
    thread.start()
    app.run()
