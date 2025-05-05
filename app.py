from flask_socketio import SocketIO, emit, join_room
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sessions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6), unique=True, nullable=False)
    teacher_id = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Boolean, default=True)
    players = db.relationship('Player', backref='session', lazy=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    in_queue = db.Column(db.Boolean, default=False)

def generate_session_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Session.query.filter_by(code=code).first():
            return code

with app.app_context():
    db.create_all()

host_password = os.environ.get('HOST_PASSWORD', 'defaultpassword')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/host', methods=['GET', 'POST'])
def host():
    if request.method == 'POST':
        if request.form['password'] == host_password:
            session['authenticated'] = True
            session['teacher_id'] = f"teacher_{random.randint(1000, 9999)}"
        else:
            return 'Access Denied', 401

    if not session.get('authenticated'):
        return render_template('login.html')

    # Get active sessions for this teacher
    teacher_sessions = Session.query.filter_by(
        teacher_id=session.get('teacher_id'),
        active=True
    ).all()
    
    return render_template('host.html', sessions=teacher_sessions)

@app.route('/create_session', methods=['POST'])
def create_session():
    if not session.get('authenticated'):
        return redirect(url_for('host'))
    
    new_session = Session(
        code=generate_session_code(),
        teacher_id=session.get('teacher_id')
    )
    db.session.add(new_session)
    db.session.commit()
    
    return redirect(url_for('host'))

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        session_code = request.form.get('session_code')
        player_name = request.form.get('name')
        
        active_session = Session.query.filter_by(code=session_code, active=True).first()
        if not active_session:
            flash('Invalid or expired session code')
            return redirect(url_for('join'))
        
        new_player = Player(name=player_name, session_id=active_session.id)
        db.session.add(new_player)
        db.session.commit()
        
        session['player_id'] = new_player.id
        session['session_id'] = active_session.id
        return redirect(url_for('session_room', code=session_code))
    
    return render_template('join.html')

@app.route('/session/<code>')
def session_room(code):
    active_session = Session.query.filter_by(code=code, active=True).first()
    if not active_session:
        return redirect(url_for('index'))
    
    # Get the current player
    current_player = Player.query.get(session.get('player_id'))
    if not current_player:
        return redirect(url_for('join'))
    
    players = Player.query.filter_by(session_id=active_session.id, in_queue=True).all()
    return render_template('session.html', session=active_session, players=players, player=current_player)

@app.route('/delete_session/<int:session_id>', methods=['POST'])
def delete_session(session_id):
    if not session.get('authenticated'):
        return redirect(url_for('host'))
    
    session_to_delete = Session.query.get_or_404(session_id)
    
    # Verify the teacher owns this session
    if session_to_delete.teacher_id != session.get('teacher_id'):
        flash('Unauthorized to delete this session')
        return redirect(url_for('host'))
    
    # Delete all players in the session
    Player.query.filter_by(session_id=session_id).delete()
    
    # Delete the session
    db.session.delete(session_to_delete)
    db.session.commit()
    
    # Notify all clients in the room that the session is deleted
    emit('session_deleted', room=str(session_id), namespace='/')
    
    flash('Session deleted successfully')
    return redirect(url_for('host'))

@socketio.on('raise_hand')
def handle_raise_hand(json):
    if not session.get('player_id'):
        return
    
    player = Player.query.get(session['player_id'])
    if player:
        player.in_queue = True
        db.session.commit()
        
        # Get updated queue for the session
        queue = [p.name for p in Player.query.filter_by(
            session_id=player.session_id,
            in_queue=True
        ).all()]
        
        room = str(player.session_id)
        emit('update_queue', {'queue': queue, 'session_id': room}, room=room)

@socketio.on('clear_queue')
def handle_clear_queue(data):
    if not session.get('authenticated'):
        return
        
    session_id = data.get('session_id')
    if session_id:
        players = Player.query.filter_by(session_id=int(session_id), in_queue=True).all()
        for player in players:
            player.in_queue = False
        db.session.commit()
        
        emit('update_queue', {'queue': [], 'session_id': session_id}, room=str(session_id))

@socketio.on('join_room')
def on_join(data):
    if 'session_id' not in data:
        return
    room = str(data['session_id'])
    join_room(room)
    # Emit current queue state to the newly joined client
    if room:
        queue = [p.name for p in Player.query.filter_by(
            session_id=int(room),
            in_queue=True
        ).all()]
        emit('update_queue', {'queue': queue, 'session_id': room}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
