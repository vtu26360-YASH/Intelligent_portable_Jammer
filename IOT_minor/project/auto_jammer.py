#!/usr/bin/env python3
from gnuradio import gr, blocks, analog, qtgui, filter
from PyQt5 import Qt, QtCore
import sys, sip

class AutomatedJammer(gr.top_block, Qt.QWidget):
    def __init__(self):
        gr.top_block.__init__(self, "AI Automated Flowgraph")
        Qt.QWidget.__init__(self)

        # 1. Automated Hardware Parameters
        samp_rate = 2e6
        center_freq = 2.4e9

        # 2. Automated Component Placement
        self.src = analog.noise_source_c(analog.GR_GAUSSIAN, 0.5)
        self.thr = blocks.throttle(gr.sizeof_gr_complex, samp_rate)
        
        # FIX: Added the 5th argument (Name String)
        self.snk = qtgui.freq_sink_c(
            1024, 
            filter.window.WIN_BLACKMAN_HARRIS, 
            center_freq, 
            samp_rate,
            "AI Adaptive Jammer Spectrum" # This was missing!
        )

        # 3. Automated Wiring
        self.connect(self.src, self.thr, self.snk)

        # 4. Automated GUI Generation
        self.layout = Qt.QVBoxLayout(self)
        # Using qwidget() for GNU Radio 3.10+
        self.py_widget = sip.wrapinstance(self.snk.qwidget(), Qt.QWidget)
        self.layout.addWidget(self.py_widget)
        self.setLayout(self.layout)

if __name__ == '__main__':
    qapp = Qt.QApplication(sys.argv)
    tb = AutomatedJammer()
    tb.start()
    tb.show()
    
    print(">>> AI Jammer Dashboard Active")
    sys.exit(qapp.exec_())