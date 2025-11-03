from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
import random, json, sqlite3, os

# -------------------
# Initialize app
# -------------------
app = Flask(__name__)
socketio = SocketIO(app)

# secret key stored in HTML and read on page load
SECRET_KEY_FILE = "static/secret_key.txt"
if os.path.exists(SECRET_KEY_FILE):
    with open(SECRET_KEY_FILE) as f:
        app.secret_key = f.read().strip()
else:
    app.secret_key = os.urandom(32).hex()
    with open(SECRET_KEY_FILE, "w") as f:
        f.write(app.secret_key)

# -------------------
# Developers
# -------------------
DEVELOPERS = ["Maplezi", "AziGD", "KH4CB5", "kav_kavernus"]

# -------------------
# Load auras
# -------------------
with open("auras.json") as f:
    auras = json.load(f)

# -------------------
# SQLite setup
# -------------------
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
conn.commit()

# -------------------
# Players storage
# -------------------
players = {}

# -------------------
# Helper functions
# -------------------
def get_current_season():
    from datetime import datetime
    now = datetime.now()
    month = now.month
    if month in [12, 1]:
        return "Christmas"
    elif month in [2, 3]:
        return "Valentine / Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    elif month in [10, 11]:
        return "Thanksgiving"
    else:
        return "Neutral Season"

current_season = get_current_season()
print(f"server season(ing) detected: {current_season}")

# -------------------
# Routes (fuck off kh4) 
# -------------------
@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    is_dev = session["username"] in DEVELOPERS
    return render_template("index.html", season=current_season, dev=is_dev, username=session["username"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        if c.fetchone():
            session["username"] = username
            return redirect(url_for("index"))
        return "Login failed"
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            session["username"] = username
            return redirect(url_for("index"))
        except:
            return "User already exists"
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# -------------------
# SocketIO events
# -------------------
@socketio.on("join")
def handle_join(data):
    name = data.get("name")
    if not name:
        return
    players[name] = None
    is_dev = name in DEVELOPERS
    if is_dev:
        emit("system_message", f"Dev {name} joined, welcome to the dev panel.", room=request.sid)
        emit("dev_panel", {"message": "You have dev powers."}, room=request.sid)
    else:
        emit("system_message", f"{name} joined the game! Season: {current_season}", broadcast=True)

@socketio.on("roll")
def handle_roll(data):
    name = data.get("name")
    if not name:
        return
    roll_result = random.randint(1, 1_000_000_000_000)
    players[name] = roll_result

    earned_auras = []
    for aura in auras:
        if random.random() < aura.get("chance", 0):
            earned_auras.append(aura.get("name"))
            if aura.get("chance", 0) < 0.001:
                emit("special_cutscene", {
                    "aura": aura.get("name"),
                    "message": f"🎬 Congrats {name}! You got a super rare aura: {aura.get('name')}!"
                }, room=request.sid)

    message = f"{name} rolled {roll_result}" + (f" and got aura(s): {', '.join(earned_auras)}" if earned_auras else "")
    message += f", Season: {current_season}"
    emit("roll_result", {"message": message}, broadcast=True)

# -------------------
# Run server
# -------------------
if __name__ == "__main__":
    socketio.run(app, debug=True)
