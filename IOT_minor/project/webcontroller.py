import sys, threading, time, random
from flask import Flask, render_template
from flask_socketio import SocketIO
from gnuradio import gr, blocks, analog, filter
import eventlet

# --- 1. THE RADIO LOGIC (The Engine) ---
class IntegratedFlowgraph(gr.top_block):
    def __init__(self, samp_rate=2e6):
        gr.top_block.__init__(self, "Web-Integrated Jammer")
        
        # Scenario: A moving target and our reactive jammer
        self.target_src = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 0, 0.5)
        self.jammer_src = analog.noise_source_c(analog.GR_GAUSSIAN, 0)
        
        # Sensor: Measuring energy level
        self.probe = blocks.probe_signal_f()
        self.mag_sq = blocks.complex_to_mag_squared()
        
        # Signal Path
        self.adder = blocks.add_cc()
        self.connect(self.target_src, (self.adder, 0))
        self.connect(self.jammer_src, (self.adder, 1))
        self.connect(self.adder, blocks.throttle(gr.sizeof_gr_complex, samp_rate), blocks.null_sink(gr.sizeof_gr_complex))
        
        # Sensing Path
        self.connect(self.target_src, self.mag_sq, self.probe)

# --- 2. WEB SERVER SETUP ---
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

stats = {"total_neutralized": 0}

@app.route('/')
def index():
    return render_template('index.html')

# --- 3. THE AI BRIDGE (Sends data to Web) ---
def ai_monitor_thread(tb):
    """Senses energy and updates the Web Dashboard live"""
    channels = [-600e3, 0, 600e3]
    while True:
        time.sleep(2)
        # 1. Simulate Enemy Movement
        current_f = random.choice(channels)
        tb.target_src.set_frequency(current_f)
        
        # 2. AI Sensing
        power = tb.probe.level()
        is_jamming = False
        
        if power > 0.05:
            tb.jammer_src.set_amplitude(0.8)
            is_jamming = True
            stats["total_neutralized"] += 1
            status_msg = f"Target Locked at {current_f/1e3:+.1f} kHz. Neutralizing..."
        else:
            tb.jammer_src.set_amplitude(0)
            status_msg = "Scanning... Spectrum Clear."

        # 3. PUSH DATA TO WEB (This makes the dashboard move)
        socketio.emit('jammer_update', {
            'msg': status_msg,
            'jamming': is_jamming,
            'count': stats["total_neutralized"],
            'power': round(power * 100, 2),
            'offset': f"{current_f/1e3:+.1f} kHz"
        })

if __name__ == '__main__':
    # Initialize GNU Radio
    tb = IntegratedFlowgraph()
    tb.start()
    
    # Start AI Monitor
    threading.Thread(target=ai_monitor_thread, args=(tb,), daemon=True).start()
    
    # Run Flask with eventlet for real-time performance
    socketio.run(app, host='0.0.0.0', port=5000)