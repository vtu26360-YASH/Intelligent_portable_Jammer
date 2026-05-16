#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Vel Tech AI-ECM Digital Twin
# Description: Vel Tech AI-ECM Digital Twin Simulation
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import sip
import threading



class veltech_ai_jammer(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Vel Tech AI-ECM Digital Twin", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Vel Tech AI-ECM Digital Twin")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "veltech_ai_jammer")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2000000

        ##################################################
        # Blocks
        ##################################################

        self.throttle = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.target_signal = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 0, 0.5, 0, 0)
        self.spectrum_display = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            2400000000, #fc
            samp_rate, #bw
            "SIGINT Monitor", #name
            1,
            None # parent
        )
        self.spectrum_display.set_update_time(0.10)
        self.spectrum_display.set_y_axis((-140), 10)
        self.spectrum_display.set_y_label('Relative Gain', 'dB')
        self.spectrum_display.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.spectrum_display.enable_autoscale(False)
        self.spectrum_display.enable_grid(False)
        self.spectrum_display.set_fft_average(1.0)
        self.spectrum_display.enable_axis_labels(True)
        self.spectrum_display.enable_control_panel(False)
        self.spectrum_display.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.spectrum_display.set_line_label(i, "Data {0}".format(i))
            else:
                self.spectrum_display.set_line_label(i, labels[i])
            self.spectrum_display.set_line_width(i, widths[i])
            self.spectrum_display.set_line_color(i, colors[i])
            self.spectrum_display.set_line_alpha(i, alphas[i])

        self._spectrum_display_win = sip.wrapinstance(self.spectrum_display.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._spectrum_display_win)
        self.jammer_noise = analog.noise_source_c(analog.GR_GAUSSIAN, 0.7, 0)
        self.adder = blocks.add_vcc(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.adder, 0), (self.throttle, 0))
        self.connect((self.jammer_noise, 0), (self.adder, 1))
        self.connect((self.target_signal, 0), (self.adder, 0))
        self.connect((self.throttle, 0), (self.spectrum_display, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "veltech_ai_jammer")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.target_signal.set_sampling_freq(self.samp_rate)
        self.throttle.set_sample_rate(self.samp_rate)
        self.spectrum_display.set_frequency_range(2400000000, self.samp_rate)




def main(top_block_cls=veltech_ai_jammer, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
