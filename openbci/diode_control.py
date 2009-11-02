#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#      Krzysztof Kulewski <kulewski@gmail.com>
#      Magdalena Michalska <jezzy.nietoperz@gmail.com>
#



import numpy, cPickle, os, time, sys, random, samples_pb2, variables_pb2, blinker 
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client

class DiodeControl:

    def __init__(self):

        self.connection = connect_client(type = peers.DIODE)
        # num of blinks per square
        self.blinks = int(self.connection.query(message = "Blinks", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        # how long a blink should last
        self.blinkPeriod = float(self.connection.query(message = "BlinkPeriod", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        # num of squares into which display is devided
        self.squares = int(self.connection.query(message = "Squares", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.numOfRepeats = len(self.connection.query(message = "TrainingSequence", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message.split(" "))
        self.seq = []
        self.count = 0
    def generateSequence(self, blinks, squares, reps):
        seq = []
        for i in range(squares):
            [seq.append(i) for x in range(blinks * reps)]
        random.shuffle(seq)
        return seq
        

    def start(self):
        # 
        d = self.squares * [-1]
        
        # sequence to blink
        self.seq = self.generateSequence(self.blinks, self.squares, self.numOfRepeats)
        s = ""
        for x in self.seq:
            s += str(x) + ","
        s = s[:len(s) - 1]
        var = variables_pb2.Variable()
        var.key = "DiodSequence"
        var.value = s
        self.conn.send_message(message = var.SerializeToString(), type = types.DICT_SET_MESSAGE, flush=True)
        #self.connection.send_message(message = "", type = types.DIODE_MESSAGE, flush=True, timeout=1)
        for x in self.seq:
            blinker.blink_p300(x, 0.5)
            time.sleep(.75)
            tstamp = time.time()
            msg = variables_pb2.Blink()
            msg.index = x
            #self.count
            msg.timestamp = tstamp
            print "BLINK " 
            #str(self.count)
            #self.count += 1
            
            self.connection.send_message(message = msg.SerializeToString(), type = types.DIODE_MESSAGE, flush=True)
            print str(self.count)
            self.count += 1

if __name__ == "__main__":
   DiodeControl().start()


