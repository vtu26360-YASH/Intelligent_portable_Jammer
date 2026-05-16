from flask import Flask, render_template
from flask_socketio import SocketIO
import threading, time, random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Simulated System State
system_data = {
    "status": "Scanning",
    "targets_found": 0,
    "power_stability": "99.2%",
    "current_freq": "2.4 GHz"
}

def ai_jammer_logic():
    """Simulates the background AI logic and feeds the web dashboard"""
    while True:
        time.sleep(3)
        # Simulate AI detecting a target
        event_type = random.choice(["SCAN", "DETECT"])
        if event_type == "DETECT":
            system_data["targets_found"] += 1
            system_data["status"] = "Jamming"
            offset = random.choice([-300, 0, 300])
            msg = f"Target neutralized at {offset}kHz offset."
        else:
            system_data["status"] = "Scanning"
            msg = "Spectrum clear. Monitoring noise floor."

        # Push data to the web interface
        socketio.emit('update', {
            'msg': msg,
            'status': system_data["status"],
            'count': system_data["targets_found"],
            'power': system_data["power_stability"]
        })

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    threading.Thread(target=ai_jammer_logic, daemon=True).start()
    socketio.run(app, debug=True, port=5000)