#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block Even
# Generated: Mon Jul  9 10:07:21 2018
##################################################

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from max_receive_power import max_receive_power  # grc-generated hier_block
from max_to_zmq_pub import max_to_zmq_pub  # grc-generated hier_block
from optparse import OptionParser
import time


class top_block_even(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block Even")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 250e3
        self.keep_one_in_n = keep_one_in_n = 50
        self.gain = gain = 0
        self.fftlen = fftlen = 1024
        self.f0 = f0 = 2405.1e6

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0_4 = uhd.usrp_source(
        	",".join(("ip_addr=192.168.10.6", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0_4.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0_4.set_center_freq(f0, 0)
        self.uhd_usrp_source_0_4.set_gain(gain, 0)
        self.uhd_usrp_source_0_4.set_antenna("TX/RX", 0)
        self.uhd_usrp_source_0_2 = uhd.usrp_source(
        	",".join(("ip_addr=192.168.10.4", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0_2.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0_2.set_center_freq(f0, 0)
        self.uhd_usrp_source_0_2.set_gain(gain, 0)
        self.uhd_usrp_source_0_2.set_antenna("TX/RX", 0)
        self.uhd_usrp_source_0_0 = uhd.usrp_source(
        	",".join(("ip_addr=192.168.10.2", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0_0.set_center_freq(f0, 0)
        self.uhd_usrp_source_0_0.set_gain(gain, 0)
        self.uhd_usrp_source_0_0.set_antenna("TX/RX", 0)
        self.max_to_zmq_pub_1_4 = max_to_zmq_pub(
            zmq_socket_addr="tcp://*:4446",
        )
        self.max_to_zmq_pub_1_2 = max_to_zmq_pub(
            zmq_socket_addr="tcp://*:4444",
        )
        self.max_to_zmq_pub_1_0 = max_to_zmq_pub(
            zmq_socket_addr="tcp://*:4442",
        )
        self.max_receive_power_0_4 = max_receive_power(
            fftlen=fftlen,
            keep_one_in_n=keep_one_in_n,
        )
        self.max_receive_power_0_2 = max_receive_power(
            fftlen=fftlen,
            keep_one_in_n=keep_one_in_n,
        )
        self.max_receive_power_0_0 = max_receive_power(
            fftlen=fftlen,
            keep_one_in_n=keep_one_in_n,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.max_receive_power_0_0, 0), (self.max_to_zmq_pub_1_0, 0))    
        self.connect((self.max_receive_power_0_0, 1), (self.max_to_zmq_pub_1_0, 1))    
        self.connect((self.max_receive_power_0_2, 0), (self.max_to_zmq_pub_1_2, 0))    
        self.connect((self.max_receive_power_0_2, 1), (self.max_to_zmq_pub_1_2, 1))    
        self.connect((self.max_receive_power_0_4, 0), (self.max_to_zmq_pub_1_4, 0))    
        self.connect((self.max_receive_power_0_4, 1), (self.max_to_zmq_pub_1_4, 1))    
        self.connect((self.uhd_usrp_source_0_0, 0), (self.max_receive_power_0_0, 0))    
        self.connect((self.uhd_usrp_source_0_2, 0), (self.max_receive_power_0_2, 0))    
        self.connect((self.uhd_usrp_source_0_4, 0), (self.max_receive_power_0_4, 0))    

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0_2.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0_4.set_samp_rate(self.samp_rate)

    def get_keep_one_in_n(self):
        return self.keep_one_in_n

    def set_keep_one_in_n(self, keep_one_in_n):
        self.keep_one_in_n = keep_one_in_n
        self.max_receive_power_0_0.set_keep_one_in_n(self.keep_one_in_n)
        self.max_receive_power_0_2.set_keep_one_in_n(self.keep_one_in_n)
        self.max_receive_power_0_4.set_keep_one_in_n(self.keep_one_in_n)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.uhd_usrp_source_0_0.set_gain(self.gain, 0)
        	
        self.uhd_usrp_source_0_2.set_gain(self.gain, 0)
        	
        self.uhd_usrp_source_0_4.set_gain(self.gain, 0)
        	

    def get_fftlen(self):
        return self.fftlen

    def set_fftlen(self, fftlen):
        self.fftlen = fftlen
        self.max_receive_power_0_0.set_fftlen(self.fftlen)
        self.max_receive_power_0_2.set_fftlen(self.fftlen)
        self.max_receive_power_0_4.set_fftlen(self.fftlen)

    def get_f0(self):
        return self.f0

    def set_f0(self, f0):
        self.f0 = f0
        self.uhd_usrp_source_0_0.set_center_freq(self.f0, 0)
        self.uhd_usrp_source_0_2.set_center_freq(self.f0, 0)
        self.uhd_usrp_source_0_4.set_center_freq(self.f0, 0)


def main(top_block_cls=top_block_even, options=None):

    tb = top_block_cls()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
