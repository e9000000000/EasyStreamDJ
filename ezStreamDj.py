from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_socketio import SocketIO, send
import json
import webbrowser

import sender.from_yt_playlist
from config import HOST, PORT, API_KEY
from utils import change_api_key_in_config


app = Flask(__name__)
app.config['SECRET_KEY'] = 'iufwehnifeuf43'
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    if API_KEY == '':
        return redirect(url_for('settings'))
    return render_template('index.html', host=HOST, port=PORT)

@socketio.on('message')
def handle_message(message:str):
    if message.startswith('send '):
        jsn = json.loads(message.replace('send ', '', 1))
        channel_name = jsn['channel_name']
        playlist_id = jsn['playlist_id']
        cooldown = int(jsn['cooldown'])
        for result in sender.from_yt_playlist.send_from_playlist(channel_name, playlist_id, cooldown):
            send(result)


@app.route('/settings/', methods=['GET', 'POST'])
def settings():
    global API_KEY
    if request.method == 'POST':
        api_key = request.form['api_key']
        change_api_key_in_config(api_key)
        API_KEY = api_key

        return redirect(url_for('index'))
    else:
        return render_template('settings.html')


if __name__ == '__main__':
    app.env = 'development'
    webbrowser.open(f'http://{HOST}:{PORT}')
    socketio.run(app, host=HOST, port=PORT)
