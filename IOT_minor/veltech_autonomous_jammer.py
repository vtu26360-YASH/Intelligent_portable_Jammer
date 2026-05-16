#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Vel Tech AI-ECM Digital Twin
# Author: Vel Tech
# Description: Autonomous AI-ECM Digital Twin
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from xmlrpc.server import SimpleXMLRPCServer
import threading
import sip



class veltech_autonomous_jammer(gr.top_block, Qt.QWidget):

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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "veltech_autonomous_jammer")

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
        self.jammer_freq = jammer_freq = 0
        self.jammer_amp = jammer_amp = 0
        self.enemy_freq = enemy_freq = 0

        ##################################################
        # Blocks
        ##################################################

        self._jammer_freq_range = qtgui.Range(-500000, 500000, 10000, 0, 200)
        self._jammer_freq_win = qtgui.RangeWidget(self._jammer_freq_range, self.set_jammer_freq, "Jammer Targeting (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._jammer_freq_win, 3, 5, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(5, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._jammer_amp_range = qtgui.Range(0, 1, 0.1, 0, 200)
        self._jammer_amp_win = qtgui.RangeWidget(self._jammer_amp_range, self.set_jammer_amp, "Jammer Power Output", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._jammer_amp_win, 4, 4, 1, 2)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._enemy_freq_range = qtgui.Range(-500000, 500000, 10000, 0, 200)
        self._enemy_freq_win = qtgui.RangeWidget(self._enemy_freq_range, self.set_enemy_freq, "Enemy Signal Offset (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._enemy_freq_win, 3, 4, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 5):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.xmlrpc_server_0 = SimpleXMLRPCServer(('localhost', 8080), allow_none=True)
        self.xmlrpc_server_0.register_instance(self)
        self.xmlrpc_server_0_thread = threading.Thread(target=self.xmlrpc_server_0.serve_forever)
        self.xmlrpc_server_0_thread.daemon = True
        self.xmlrpc_server_0_thread.start()
        self.throttle = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.target_signal = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, enemy_freq, 0.5, 0, 0)
        self.spectrum_display = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            2400000000, #fc
            samp_rate, #bw
            "Main SIGINT Environment Monitor", #name
            1,
            None # parent
        )
        self.spectrum_display.set_update_time(0.10)
        self.spectrum_display.set_y_axis((-100), 10)
        self.spectrum_display.set_y_label('Relative Gain', 'dB')
        self.spectrum_display.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.spectrum_display.enable_autoscale(False)
        self.spectrum_display.enable_grid(True)
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
        self.top_grid_layout.addWidget(self._spectrum_display_win, 0, 0, 4, 4)
        for r in range(0, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.power_meter = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1,
            None # parent
        )
        self.power_meter.set_update_time(0.10)
        self.power_meter.set_title("Hardware Signal Intelligence")

        labels = ['Target Power (SNR)', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.power_meter.set_min(i, 0)
            self.power_meter.set_max(i, 1)
            self.power_meter.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.power_meter.set_label(i, "Data {0}".format(i))
            else:
                self.power_meter.set_label(i, labels[i])
            self.power_meter.set_unit(i, units[i])
            self.power_meter.set_factor(i, factor[i])

        self.power_meter.enable_autoscale(False)
        self._power_meter_win = sip.wrapinstance(self.power_meter.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._power_meter_win, 2, 4, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.mag_sq = blocks.complex_to_mag_squared(1)
        self.jammer_noise = analog.noise_source_c(analog.GR_GAUSSIAN, 1, 0)
        self.jammer_mixer = blocks.multiply_vcc(1)
        self.jammer_lpf = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                50000,
                10000,
                window.WIN_HAMMING,
                6.76))
        self.jammer_lo = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, jammer_freq, 1, 0, 0)
        self.jammer_gain = blocks.multiply_const_cc(jammer_amp)
        self.jammer_display = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            2400000000, #fc
            samp_rate, #bw
            "Isolated Jammer Output Generation", #name
            1,
            None # parent
        )
        self.jammer_display.set_update_time(0.10)
        self.jammer_display.set_y_axis((-100), 10)
        self.jammer_display.set_y_label('Relative Gain', 'dB')
        self.jammer_display.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.jammer_display.enable_autoscale(False)
        self.jammer_display.enable_grid(False)
        self.jammer_display.set_fft_average(1.0)
        self.jammer_display.enable_axis_labels(True)
        self.jammer_display.enable_control_panel(False)
        self.jammer_display.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["red", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.jammer_display.set_line_label(i, "Data {0}".format(i))
            else:
                self.jammer_display.set_line_label(i, labels[i])
            self.jammer_display.set_line_width(i, widths[i])
            self.jammer_display.set_line_color(i, colors[i])
            self.jammer_display.set_line_alpha(i, alphas[i])

        self._jammer_display_win = sip.wrapinstance(self.jammer_display.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._jammer_display_win, 0, 4, 2, 2)
        for r in range(0, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.adder = blocks.add_vcc(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.adder, 0), (self.throttle, 0))
        self.connect((self.jammer_gain, 0), (self.adder, 1))
        self.connect((self.jammer_gain, 0), (self.jammer_display, 0))
        self.connect((self.jammer_lo, 0), (self.jammer_mixer, 1))
        self.connect((self.jammer_lpf, 0), (self.jammer_mixer, 0))
        self.connect((self.jammer_mixer, 0), (self.jammer_gain, 0))
        self.connect((self.jammer_noise, 0), (self.jammer_lpf, 0))
        self.connect((self.mag_sq, 0), (self.power_meter, 0))
        self.connect((self.target_signal, 0), (self.adder, 0))
        self.connect((self.target_signal, 0), (self.mag_sq, 0))
        self.connect((self.throttle, 0), (self.spectrum_display, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "veltech_autonomous_jammer")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.jammer_display.set_frequency_range(2400000000, self.samp_rate)
        self.jammer_lo.set_sampling_freq(self.samp_rate)
        self.jammer_lpf.set_taps(firdes.low_pass(1, self.samp_rate, 50000, 10000, window.WIN_HAMMING, 6.76))
        self.spectrum_display.set_frequency_range(2400000000, self.samp_rate)
        self.target_signal.set_sampling_freq(self.samp_rate)
        self.throttle.set_sample_rate(self.samp_rate)

    def get_jammer_freq(self):
        return self.jammer_freq

    def set_jammer_freq(self, jammer_freq):
        self.jammer_freq = jammer_freq
        self.jammer_lo.set_frequency(self.jammer_freq)

    def get_jammer_amp(self):
        return self.jammer_amp

    def set_jammer_amp(self, jammer_amp):
        self.jammer_amp = jammer_amp
        self.jammer_gain.set_k(self.jammer_amp)

    def get_enemy_freq(self):
        return self.enemy_freq

    def set_enemy_freq(self, enemy_freq):
        self.enemy_freq = enemy_freq
        self.target_signal.set_frequency(self.enemy_freq)




def main(top_block_cls=veltech_autonomous_jammer, options=None):

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
