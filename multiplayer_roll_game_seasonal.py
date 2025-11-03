# multiplayer_roll_game_seasonal.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random
import json
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

# Developer accounts (fuck you maplezi for breaking my game - AziGD
# no fuck you AziGD - Maplezi
# syfm yall im tryna sleep - KH4CB5)
# add your username here cuz why the fuck not (i literally just woke up yall are fightong agai- oh ofcourse maple just killed azi in game - kav_kavernus)
DEVELOPERS = ["Maplezi", "AziGD", "KH4CB5", "kav_kavernus"]

# players storage (i drank coca cola rn - AziGD)
players = {}

# seasoned steak session (lmao nice - KH4CB5)
def get_current_season():
    now = datetime.utcnow()
    month = now.month
    if month == 11:
        return "Thanksgiving"
    elif month in [12, 1]:
        return "Christmas"
    elif month in [2, 3]:
        return "Valentine / Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    elif month in [10]:
        return "Halloween / Autumn"
    else:
        return "Neutral Season"

current_season = get_current_season()
print(f"server season(ing) detected: {current_season}")

# why not load the auras? (i swear to god SHUT THE FUCK UP CANADIAN MAPLE SAUCE - AziGD)
with open("auras.json", "r") as f:
    auras = json.load(f)

# routes (swag route is best also stop you two - KH4CB5)
# (no fuck you kh4 - Maplezi and AziGD)
@app.route('/')
def index():
    return render_template('index.html', season=current_season)

# sock events (beef steak, fuck you azi - Maplezi)
@socketio.on('join')
def handle_join(data):
    name = data.get('name')
    if not name:
        return
    players[name] = None
    is_dev = name in DEVELOPERS

    if is_dev:
        emit('system_message', f" dev {name} joined, wsp you have access to the dev panel.", room=request.sid)
        emit('dev_panel', {'message': "Welcome to your dev panel bitch."}, room=request.sid)
    else:
        emit('system_message', f"{name} has joined the game woohoo yay fun. current season(ed steak): {current_season}", broadcast=True)

@socketio.on('roll')
def handle_roll(data):
    name = data.get('name')
    if not name:
        return

    roll_result = random.randint(1, 1_000_000_000_000)  # why br7u (sybau 🥀💔 - AziGD)
    players[name] = roll_result
    
    # check auras cuz i did (im gonna fucking demote you two - KH4CB5)
    earned_auras = []
    for aura in auras:
        if random.random() < aura['chance']:
            earned_auras.append(aura['name'])

    # prepare message if needed (NO DONT PLS WERE SORRY - Maplezi and AziGD)
    # (they deserve it kh4 - kav_kavernus)
    if earned_auras:
        aura_str = ", ".join(earned_auras)
        message = f"🎉 {name} rolled {roll_result} and got aura(s): {aura_str}, woohoo yay fun, anyway heres the season: {current_season}"
    else:
        message = f"{name} rolled {roll_result} ggs, current season(ing steak) is {current_season}"

    emit('roll_result', {'message': message}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
