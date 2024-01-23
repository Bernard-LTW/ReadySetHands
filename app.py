from flask_socketio import SocketIO, emit
from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Set an environment variable for HOST_PASSWORD for security
host_password = os.environ.get('HOST_PASSWORD', 'defaultpassword')

players_queue = []
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/host', methods=['GET', 'POST'])
def host():
    if request.method == 'POST':
        if request.form['password'] == host_password:
            session['authenticated'] = True
        else:
            return 'Access Denied', 401

    if not session.get('authenticated'):
        return render_template('login.html')

    return render_template('host.html', queue=players_queue)

@socketio.on('raise_hand')
def handle_raise_hand(json):
    player_name = json['name']
    if player_name not in players_queue:
        players_queue.append(player_name)
        emit('update_queue', {'queue': players_queue}, broadcast=True)

@socketio.on('clear_queue')
def handle_clear_queue():
    global players_queue
    players_queue.clear()
    emit('update_queue', {'queue': players_queue}, broadcast=True)



if __name__ == '__main__':
    socketio.run(app, debug=True,allow_unsafe_werkzeug=True)
