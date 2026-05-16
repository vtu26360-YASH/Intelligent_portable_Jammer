#!/usr/bin/env python3
from gnuradio import gr, blocks, analog, qtgui, filter
from PyQt5 import Qt, QtWidgets, QtCore
import sip, sys, threading, time, random
import numpy as np

class CognitiveAIJammer(gr.top_block, QtWidgets.QWidget):
    def __init__(self, samp_rate=2e6, center_freq=2400e6):
        gr.top_block.__init__(self, "Vel Tech AI-ECM Project")
        QtWidgets.QWidget.__init__(self)

        # --- 1. THE DYNAMIC ENVIRONMENT ---
        self.samp_rate = samp_rate
        self.target_src = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 0, 0.5)
        
        # --- 2. VIRTUAL HARDWARE ---
        self.jammer_src = analog.noise_source_c(analog.GR_GAUSSIAN, 0)
        self.probe = blocks.probe_signal_f()
        self.mag_sq = blocks.complex_to_mag_squared()
        
        # 3. SIGINT Monitor (Spectrum)
        self.gui_sink = qtgui.freq_sink_c(1024, filter.window.WIN_BLACKMAN_HARRIS, 
                                        center_freq, samp_rate, "SIGINT Monitor")
        
        # 4. SIGNAL FLOW
        self.adder = blocks.add_cc()
        self.connect(self.target_src, (self.adder, 0))
        self.connect(self.jammer_src, (self.adder, 1))
        self.connect(self.adder, blocks.throttle(gr.sizeof_gr_complex, samp_rate), self.gui_sink)
        self.connect(self.target_src, self.mag_sq, self.probe)

        # --- 5. PROFESSIONAL GUI SETUP ---
        self.setWindowTitle("Vel Tech AI Jammer - Cognitive Simulation")
        self.resize(1200, 650)
        grid = QtWidgets.QGridLayout(self)
        
        spec_widget = sip.wrapinstance(self.gui_sink.qwidget(), QtWidgets.QWidget)
        grid.addWidget(spec_widget, 0, 0, 1, 3)
        
        side_panel = QtWidgets.QVBoxLayout()
        
        # Power Meter (Visual feedback for the expert)
        self.pwr_meter = QtWidgets.QProgressBar()
        self.pwr_meter.setRange(0, 100)
        side_panel.addWidget(QtWidgets.QLabel("Target Signal Strength (SNR):"))
        side_panel.addWidget(self.pwr_meter)
        
        self.log_box = QtWidgets.QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background-color: #050505; color: #00ff00; font-family: 'Liberation Mono'; font-size: 11px;")
        side_panel.addWidget(QtWidgets.QLabel("AI Intelligence Feed:"))
        side_panel.addWidget(self.log_box)
        
        grid.addLayout(side_panel, 0, 3, 1, 1)

    @QtCore.pyqtSlot(float)
    def update_scenario(self, freq):
        self.target_src.set_frequency(freq)

    @QtCore.pyqtSlot(float, float, bool)
    def ai_update_gui(self, power, current_f, is_jamming):
        """Reports dynamic data instead of static text"""
        timestamp = time.strftime('%H:%M:%S')
        snr_pct = min(100, int(power * 400))
        self.pwr_meter.setValue(snr_pct)
        
        if is_jamming:
            msg = f"[{timestamp}] TARGET DETECTED at {current_f/1e3:+.1f} kHz offset. Power: {power:.4f}. Jamming Active."
            self.log_box.append(msg)
        else:
            self.log_box.append(f"[{timestamp}] SCANNING... No significant energy above threshold.")

if __name__ == '__main__':
    qapp = QtWidgets.QApplication(sys.argv)
    tb = CognitiveAIJammer()
    tb.start()
    tb.show()

    def main_automation_loop():
        # Possible frequencies the 'enemy' might use
        channels = [-700e3, -300e3, 0, 300e3, 700e3]
        while True:
            # 1. Random Enemy Behavior
            target_f = random.choice(channels)
            QtCore.QMetaObject.invokeMethod(tb, "update_scenario", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(float, target_f))
            
            # 2. Sensing Interval
            time.sleep(2)
            raw_power = tb.probe.level()
            
            # 3. AI Cognitive Threshold
            jam_active = False
            if raw_power > 0.04:
                tb.jammer_src.set_amplitude(0.75)
                jam_active = True
            else:
                tb.jammer_src.set_amplitude(0)
            
            # 4. Report the FINDINGS
            QtCore.QMetaObject.invokeMethod(tb, "ai_update_gui", QtCore.Qt.QueuedConnection, 
                                          QtCore.Q_ARG(float, raw_power), QtCore.Q_ARG(float, target_f), QtCore.Q_ARG(bool, jam_active))
            time.sleep(3)

    threading.Thread(target=main_automation_loop, daemon=True).start()
    sys.exit(qapp.exec_())