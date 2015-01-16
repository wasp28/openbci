#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from obci.configs import settings

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

class WiiBoardDeflectionsAnalysis(ConfiguredMultiplexerServer):
    DIRS=['up', 'right', 'down', 'left', 'baseline']
    @log_crash
    def __init__(self, addresses, p_type = peers.WII_BOARD_ANALYSIS):
        self.v = 0
        self.d = 0
        super(WiiBoardDeflectionsAnalysis, self).__init__(addresses=addresses, type=p_type)
        user_id = self.get_param('user_id')
        self.logger.info("Starting sway analysis for user: "+str(user_id))
        #todo - either calib or game - set stanie swobodne area from  user_id

        session_name = self.get_param('session_name')
        if session_name == 'ventures_calibration':
            pass
            # set maxes - left, right, up, down: either -1 1 (if used in scenario for calibration) 
        elif session_name == 'ventures_game':
            pass #set user-s max deflections from last calibration of user_id
        else:
            raise Exception ("Unknown session name - abort")

        self.ready()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.WII_BOARD_SIGNAL_MESSAGE:
            v = variables_pb2.SampleVector()
            v.ParseFromString(mxmsg.message)
            for s in v.samples:#todo - refactor in regard to utils/wii_2d_router
                msg = variables_pb2.IntVariable()
                sum_mass = sum(s.channels[0:4])
                x = (((s.channels[1] + s.channels[2]) - (s.channels[0] + s.channels[3]))/sum_mass) + 0.5
                y = (((s.channels[1] + s.channels[0]) - (s.channels[2] + s.channels[3]))/sum_mass) + 0.5
                #apply filtering somwere here
                sway_direction, sway_level = self._calculate_sway(x, y)
                msg.key = sway_direction
                msg.value = sway_level
                self.conn.send_message(message=msg.SerializeToString(),
                                       type=types.WII_BOARD_ANALYSIS_RESULTS, flush=True)
        else:
            pass #todo - log warning
        self.no_response()
    def _calculate_sway(self, x, y):
        #using self.maxes and self.stanie swobodne area
        #calculate sway direction and sway level 
        self.v = self.v + 0.25
        if not (self.v % 100):
            self.d = (self.d + 1) % 5
        return self.DIRS[self.d], (int(self.v) % 70)

if __name__ == "__main__":
    WiiBoardDeflectionsAnalysis(settings.MULTIPLEXER_ADDRESSES).loop()