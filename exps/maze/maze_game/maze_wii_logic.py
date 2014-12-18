# -*- coding: utf-8 -*-
#!/usr/bin/env python
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
#     Anna Chabuda <anna.chabuda@gmail.com>
#
import pygame
pygame.mixer.init()
import time

from pygame.locals import *

from maze_logic import MazeLogic

from maze_wii_level import MazeWiiLevel
from arrow.wii_arrow import WiiArrow

from constants.constants_game import FRAME_RATE

class Sample(object):
    """docstring for Sample"""
    def __init__(self, direction):
        super(Sample, self).__init__()
        self.type = 'wii'
        self.value = 50
        self.direction = direction

def get_sample():
    for i in range(200000):
      if i<100:
        return Sample('up')
      else:
        return Sample('down')


class MazeWiiLogic(MazeLogic):
    def __init__(self, start_level, start_wii_level, sesion_number, sesion_duration, 
                 time_board_display, time_left_out, maze_path_display, tagger, sesion_type):
        super(MazeWiiLogic, self).__init__(start_level, sesion_number, sesion_duration, 
                                           time_board_display, time_left_out, 
                                           maze_path_display, tagger, sesion_type)
        self.start_wii_level = start_wii_level
        self.wii_level = MazeWiiLevel()
        self._init_wii_arrows()

    def _init_wii_arrows(self):
        self.wii_arrows = {'right' : WiiArrow('right'),
                           'left':  WiiArrow('left'),
                           'down' : WiiArrow('down'),
                           'up' : WiiArrow('up')}

    def set_current_wii_level(self, level):
        self.current_wii_level = level

    def get_current_wii_level(self):
        return self.current_wii_level

    def update_current_wii_level(self):
        self.current_wii_level += 1

    def set_current_arrow_direction(self, direction):
        self.current_arrow_direction = direction

    def get_current_arrow_direction(self):
        return self.current_arrow_direction

    def get_current_arrow(self):
        if self.current_arrow_direction != None:
            return self.wii_arrows[self.current_arrow_direction]
        else:
            return None

    def is_move(self):
        if self.current_arrow_direction != None:
            return self.wii_arrows[self.current_arrow_direction].is_move()
        else:
            return False

    def load_wii_level(self):
        for arrow in self.wii_arrows.values():
            self.wii_level.load_level(arrow.direction, self.get_current_wii_level())
            level_params = self.wii_level.get_level(arrow.direction)
            arrow.set_level(*level_params)
            self.screen.load_wii_level_arrow_proportion(arrow.direction, level_params[2:])

    def draw_game_with_arrow(self, arrow_type):
        self.screen.draw_game_with_wii_arrow(arrow_type,
                                             self.get_current_arrow().get_arrow_level(),
                                             self.get_current_arrow().get_area_state(),
                                             self.get_level_array(),
                                             self.get_ball_position_x(),
                                             self.get_ball_position_y(),
                                             self.get_current_level(),
                                             self.get_level_time(),
                                             self.get_sesion_time())

    def draw_game_with_arrow_update(self, arrow_type):
        self.screen.draw_game_with_wii_arrow_update(arrow_type,
                                                    self.get_current_arrow().get_arrow_level(),
                                                    self.get_current_arrow().get_area_state(),
                                                    self.get_level_array(),
                                                    self.get_ball_position_x(),
                                                    self.get_ball_position_y(),
                                                    self.get_current_level(),
                                                    self.get_level_time(),
                                                    self.get_sesion_time())
        

    def update_screen(self):
        sample = get_sample()
        if sample.type == 'wii':
            if sample.direction == self.get_current_arrow_direction():
                self.get_current_arrow().update(sample.value)
                self.draw_game_with_arrow(sample.direction)
            elif sample.direction == '0':
                if self.get_current_arrow_direction() != None:
                    self.get_current_arrow().reset()
                self.draw_game()
            else:
                if self.get_current_arrow_direction() != None:
                    self.get_current_arrow().reset()
                    self.set_current_arrow_direction(sample.direction)
                    self.get_current_arrow().update(sample.value)
                    self.draw_game_with_arrow_update(sample.direction)
                else:
                    self.set_current_arrow_direction(sample.direction)
                    self.get_current_arrow().update(sample.value)
                    self.draw_game_with_arrow(sample.direction)
            if self.is_move():
                self.move(self.get_current_arrow_direction())
                self.get_current_arrow().reset()
                self.set_current_arrow_direction(None)

        for event in pygame.event.get():
            if event.type == QUIT:
                    self.exit_game()

            elif event.type == KEYDOWN:           
                if event.key == K_ESCAPE:
                    self.exit_game()

                elif event.key == K_p:
                    self.make_pause()

    def main(self):    
        self.set_current_level(self.start_level)
        self.load_level()  
        self.set_current_wii_level(self.start_wii_level)
        self.load_wii_level()
        self.set_current_arrow_direction(None)
        self.screen.display_screen('start')
        self.screen.display_screen('instruction')
        self.sesion_start() 
        self.level_start()
        while self.get_current_level()<= self.levels_quantity and self.status:
            if not self.get_level_status():
                self.level_timeout()
            else:
                self.update_screen()
            time.sleep(1/FRAME_RATE)
        self.finish_game()