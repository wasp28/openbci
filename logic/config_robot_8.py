#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config(object):
    def __init__(self):
        self.number_of_decisions = 8
        self.number_of_states = 1

        # A list of all configs defined for every single state.
        self.states_configs = ['state', 'letters', 'actions', 'letters_solver', 'actions_solver']

        # A list of all configs defined as globals,
        # not assigned to any particular state.
        self.other_configs = []

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!! Only keys defined in states_configs and other_configs
        # will be visible in your application.!!!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # States transition matrix
        self.state = self.number_of_states * [self.number_of_decisions * [0]]
        self.state[0] = [0, 0, 0, 0, 0, 0, 0, 0]

        # Letters definition for every state. Normally for every state it should be a collection of strings.
        self.letters = self.number_of_states * [self.number_of_decisions * [""]]
        self.letters[0] = [u"Naprzód", u"Do tyłu", u"W prawo", u'W lewo', '', '', '', u'Zakończ']
        self.letters_solver = self.number_of_states * [self.number_of_decisions * [""]]

        self.actions = self.number_of_states * [self.number_of_decisions * [""]]
        self.actions[0] = ["robot('forward')", "robot('backward')", "robot('right')", "robot('left')",
                      "robot('camera_up')", "robot('camera_middle')", "robot('camera_down')",
                      "finish("+self._finish_params()+")"]

        self.actions_solver = self.number_of_states * [self.number_of_decisions * [""]]

    def _finish_params(self):
        return "x, x"