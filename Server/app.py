from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
# Enable CORS so your browser doesn't block the requests
CORS(app)

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('study_data.db')
    c = conn.cursor()
    # Create the table if it doesn't exist to prevent "Table not found" errors
    c.execute('''CREATE TABLE IF NOT EXISTS session_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  duration_seconds INTEGER,
                  task_type TEXT,
                  posture_avg INTEGER,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- GLOBAL STATE (Stores temporary data from the Pi) ---
current_data = {
    "is_active": False,
    "current_posture": "Good",
    "session_seconds": 0,
    "phone_usage_pct": 0,
    "posture_score": 0
}

@app.route('/')
def index():
    return render_template('index.html')

# 1. The Dashboard calls this every 2 seconds to update the UI
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(current_data)

# 2. The Raspberry Pi calls this to send real-time sensor data
@app.route('/api/events', methods=['POST'])
def handle_pi_events():
    global current_data
    data = request.json
    if data and "events" in data:
        # Get the latest sensor reading from the list
        latest = data["events"][-1]

        # Translate Pi data to your Dashboard's variables
        current_data["current_posture"] = "Bad" if latest["slouching"] else "Good"
        current_data["phone_usage_pct"] = 100 if latest["on_phone"] else 0
        current_data["posture_score"] = latest["posture_score"]
        current_data["is_active"] = True

        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

# 3. Routes for Dashboard control buttons
@app.route('/api/button/toggle', methods=['POST'])
def toggle_session():
    current_data["is_active"] = not current_data["is_active"]
    return jsonify({"status": "toggled", "state": current_data["is_active"]})

@app.route('/api/button/reset', methods=['POST'])
def reset_session():
    current_data["is_active"] = False
    current_data["session_seconds"] = 0
    return jsonify({"status": "reset"})

# 4. The Dashboard calls this when you click "STOP & SAVE"
@app.route('/api/sessions', methods=['POST', 'OPTIONS'])
def handle_session_save():
    # Handle the browser's preflight check
    if request.method == 'OPTIONS':
        return '', 204

    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    duration = data.get("duration_seconds", 0)
    task = data.get("task_type", "Focus")
    posture = data.get("posture_avg", 0)
    timestamp = data.get("timestamp", "")

    try:
        # Save the session to the SQLite database
        conn = sqlite3.connect('study_data.db')
        c = conn.cursor()
        c.execute('''INSERT INTO session_history (duration_seconds, task_type, posture_avg, timestamp)
                     VALUES (?, ?, ?, ?)''', (duration, task, posture, timestamp))
        conn.commit()
        conn.close()

        print(f"✅ Session Saved: {duration}s of {task} with {posture}% posture score.")
        return jsonify({"status": "success", "message": "Session saved to database"}), 200
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Run on port 5000 as configured in your Nginx site-available file
    app.run(host='127.0.0.1', port=5000)