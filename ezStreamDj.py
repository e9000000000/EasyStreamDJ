from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, send
import json

import sender.from_yt_playlist


app = Flask(__name__)
app.config['SECRET_KEY'] = 'iufwehnifeuf43'
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(message:str):
    if message.startswith('send '):
        jsn = json.loads(message.replace('send ', '', 1))
        channel_name = jsn['channel_name']
        playlist_id = jsn['playlist_id']
        cooldown = int(jsn['cooldown'])
        for result in sender.from_yt_playlist.send_from_playlist(channel_name, playlist_id, cooldown):
            send(result)


if __name__ == '__main__':
    app.env = 'development'
    socketio.run(app, port=13666)
