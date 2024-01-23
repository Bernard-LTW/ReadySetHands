from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

players_queue = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/host')
def host():
    return render_template('host.html', queue=players_queue)

@socketio.on('raise_hand')
def handle_raise_hand(json):
    player_name = json['name']
    if player_name not in players_queue:
        players_queue.append(player_name)
        emit('update_queue', {'queue': players_queue}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True,allow_unsafe_werkzeug=True)
