#!/usr/bin/env python
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
#      Mateusz Kruszynski <mateusz.kruszynski@gmail.com>
#

"""A subclass of VirtualEEGAmplifier. Redefines initialisation and
method get_next_value that returns next sample value.
Its only public method is do_sampling(), not needed to redefine here.
The class is internally used by virtual_amplifier.py.
"""

import math
import time
from multiplexer.multiplexer_constants import types
import virtual_eeg_amplifier

import amplifiers_logging as logger
LOGGER = logger.get_logger("function_amplifier")

class FunctionEEGAmplifier(virtual_eeg_amplifier.VirtualEEGAmplifier):
    """A subclass of VirtualEEGAmplifier. Redefines initialisation and
    method get_next_value that returns next sample value.
    Values are taken from predefined mathematical function.
    Its only public method is do_sampling(), not needed to redefine here."""
    def __init__(self):
        """Init all needed attributes:
        - self.sampling_rate
        - self.channel_numbers
        """
        super(FunctionEEGAmplifier, self).__init__()
        LOGGER.info("Run virtualeegamplifier from function.")
        self.sampling_rate = int(self.connection.query(
                message="SamplingRate", 
                type=types.DICT_GET_REQUEST_MESSAGE).message)
        l_function = self.connection.query(
            message="VirtualAmplifierFunction", 
            type=types.DICT_GET_REQUEST_MESSAGE).message
        self._function = l_function

    def _get_next_value(self, offset):
        """Return next sample value. Here next value generated by function."""
        return eval(self._function)
    def _get_sampling_start_time(self):
        """Sampling from function is in real time, so return current time."""
        return time.time()


