from gevent import monkey
monkey.patch_all()

import flask_socketio
from collections import defaultdict
from flask import Flask, request, send_from_directory

from user import User


app = Flask(__name__)
socketio = flask_socketio.SocketIO(app, async_mode="gevent", logger=True, engineio_logger=True)


@app.route("/")
def base():
    return send_from_directory("static", "index.html")

@app.route("/<path:path>")
def home(path):
    return send_from_directory("static", path)

# Global dictionary of users, indexed by room
connected_users = defaultdict(list)
# Global dictionary of disconnected users, indexed by room
disconnected_users = defaultdict(list)


@socketio.on("join room")
def join_room(data):
    sid = request.sid
    username = data["username"]
    room = data["room"]
    flask_socketio.join_room(room)
    # If the user is rejoining, change their sid
    for room, users in disconnected_users.items():
        for user in users:
            if user.name == username:
                socketio.send(f"{username} has rejoined the room.", room=room)
                user.sid = sid
                # Add the user back to the connected users list
                connected_users[room].append(user)
                # Remove the user from the disconnected list
                disconnected_users[room].remove(user)
                return True
    # If the user is new, create a new user
    socketio.send(f"{username} has joined the room.", room=room)
    user = User(username, socketio, room, sid)
    connected_users[room].append(user)
    return True

    
@socketio.on("disconnect")
def disconnect():
    sid = request.sid
    # Find the room and user with this sid
    user_found = False
    for room, users in connected_users.items():
        for user in users:
            if user.sid == sid:
                user_found = True
                break
        if user_found:
            break
    # If a matching user was not found, do nothing
    if not user_found:
        return
    room = user.room
    socketio.send(f"{user.name} has left the room.", room=room)
    # Remove the user from the room
    connected_users[room].remove(user)
    # Add the user to the disconnected list
    disconnected_users[room].append(user)
    flask_socketio.leave_room(room)


@socketio.on("collect colors")
def collect_colors(data):
    room = data["room"]
    for user in connected_users[room]:
        color = user.call("send color", data)
        print(f"{user.name}'s color is {color}.")
    

if __name__ == "__main__":
    socketio.run(app, debug=True)