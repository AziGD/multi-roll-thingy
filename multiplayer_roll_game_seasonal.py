# multiplayer_roll_game_sqlite.py
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
import random
import sqlite3
import json
from datetime import datetime, timezone

# -------------------- Flask + SocketIO --------------------
app = Flask(__name__)
app.secret_key = "supersecretkey"  # replace with a secure key
socketio = SocketIO(app)

# -------------------- Developer accounts --------------------
DEVELOPERS = ["Maplezi", "AziGD", "KH4CB5", "kav_kavernus"]

# -------------------- Load Auras --------------------
with open("auras.json", "r") as f:
    auras = json.load(f)

# -------------------- Database helpers --------------------
DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def signup_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    hashed = generate_password_hash(password)
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    if row and check_password_hash(row[0], password):
        return True
    return False

# -------------------- Season --------------------
def get_current_season():
    now = datetime.now(timezone.utc)
    month = now.month
    if month in [12, 1]:
        return "Christmas"
    elif month in [2, 3]:
        return "Valentine / Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    elif month == 11:
        return "Thanksgiving"
    elif month in [10]:
        return "Halloween"
    else:
        return "Neutral Season"

current_season = get_current_season()
print(f"server season(ing) detected: {current_season}")

# -------------------- Players --------------------
players = {}

# -------------------- Routes --------------------
@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'], season=current_season)
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if signup_user(username, password):
            return redirect(url_for('login'))
        return "Username already exists!"
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if login_user(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        return "Invalid credentials!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# -------------------- SocketIO events --------------------
@socketio.on('join')
def handle_join(data):
    name = session.get('username')
    if not name:
        return
    players[name] = None
    is_dev = name in DEVELOPERS

    if is_dev:
        emit('system_message', f"Dev {name} joined, you have access to the dev panel.", room=request.sid)
        emit('dev_panel', {'message': "Welcome to your dev panel!"}, room=request.sid)
    else:
        emit('system_message', f"{name} has joined the game. Current season: {current_season}", broadcast=True)

@socketio.on('roll')
def handle_roll(data):
    name = session.get('username')
    if not name:
        return

    roll_result = random.randint(1, 1_000_000_000_000)
    players[name] = roll_result

    earned_auras = []
    for aura in auras:
        chance = aura.get('chance', 0)
        if random.random() < chance:
            earned_auras.append(aura.get('name', 'Unknown Aura'))

            # special cutscene for super rare auras (chance < 1/1000)
            if chance < 0.001:
                emit('special_cutscene', {
                    'aura': aura.get('name', 'Unknown Aura'),
                    'message': f"🎬 Congrats {name}! You got a super rare aura: {aura.get('name')}!"
                }, room=request.sid)

    if earned_auras:
        aura_str = ", ".join(earned_auras)
        message = f"🎉 {name} rolled {roll_result} and got aura(s): {aura_str}, season: {current_season}"
    else:
        message = f"{name} rolled {roll_result} ggs, season: {current_season}"

    emit('roll_result', {'message': message}, broadcast=True)

# -------------------- Main --------------------
if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True)
