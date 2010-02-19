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
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

"""Module to handle ugm configuration.
Public interface (for UgmConfigManager):
CONFIG FILE HANDLING:
- update_from_file()
- update_to_file()

GETTERS:
- get_config_for()
- get_ugm_fields()
- get_attributes_config()

SETTERS:
- set_full_config()
- set_config()

UGM_UPDATE_MESSAGE handling:
- set_config_from_message()
- set_full_config_from_message()
- config_from_message()
- config_to_message()
- update_message_is_full()
- update_message_is_simple()
"""
import copy
class UgmAttributesManager(object):
    """Manager possible keys and values for config.
    Attributes:
    - attributes_def - define all possible config keys and 
    all possible values for every key
    - attributes_for_elem - define all required keys for every stimulus type
    """
    def __init__(self):
        self.attributes_def = {
            'id':{'value':'int'}, # Required for every stimulus, 
            # used for identyfication while updating

            'width_type':{'value':['absolute', 'relative']}, 
            # Determines how to interpret 'width' property and consequently
            # how to compute stimulus`es width.
            # 'absolute' = width is stimulus`es real width in pixels
            # 'relative' = width is a float representing a fraction of 
            # stimulus`es parent`s width to be computed from. Eg. if width
            # = 0.25 then real width is 1/4 of stimulus`es parent`s width.

            'width':{'value':'float'},
            # Stimulus`es real or fraction width depending on 'width_type'

            'height_type':{'value':['absolute', 'relative']},
            # Same as width_type

            'height':{'value':'float'},
            # Same as width
            
            'position_horizontal_type':{
                'value':['absolute', 'relative', 'aligned']},
            # Type of horizontal positioning. It defines how to interpret
            # 'position_horizontal' property.
            #
            # 'absolute' = 'position_horizontal' is stimulus`es top-left
            # corner`s absolute (in pixels) horizontal distance from 
            # parent`s top-left corner
            #
            # 'relative' = 'position_horizontal' is stimulus`es top-left
            # corner`s horizontal distance from parent`s top-left corner
            # computed as a fraction of parent`s absolute width; eg
            # if 'position_horizontal' = 0.25 then self`s top-left corner
            # is located 0.25*(self`s parent`s width) pixels from 
            # self`s parent`s top-left corner
            #
            # 'aligned' - stimulus is aligned relative to its parent.
            # eg. to left, right, center.

            'position_horizontal':{
                'value':['int', 'float', ['left','center','right']],
                'depend_from':'position_horizontal_type'},
            # For every corresponding position_horizontal_type define its
            # value types

            'position_vertical_type':{
                'value':['absolute', 'relative', 'aligned']},
            # Same as position_horizontal_type

            'position_vertical':{
                'value':['int', 'float', ['top','center','bottom']],
                'depend_from':'position_vertical_type'},
            # Same as position_horizontal

            'color':{'value':'string'},
            # Stimulus`es background color (in format #222111)

            'stimulus_type':{'value':['rectangle', 'image', 'text']},
            # Stimulus`es type

            'image_path':{'value':'string'},
            # A path to stimulus`es image (used by UgmImageStimulus)
            # It migth be just a path or path like ugm.resources.file.png.
            # In this second situation a file will be searched in resources
            # directory in ugm package.
            
            'message':{'value':'string'},
            # A text message of UgmTextStimulus

            'font_family':{'value':'string'},
            # Font family (as string) for UgmTextStimulus

            'font_color':{'value':'string'},
            # Font color (in format #222111) for UgmTextStimulus

            'font_size':{'value':'int'},
            # Font size for UgmTextStimulus

            'stimuluses':{'value':'list'}
            # A list of child stimuluses for current stimulus.
            # It is reasonable, as we might want to position some stimuluses
            # relative to other specific 'containing' stimuluses
            }
	# TODO: Stimuluses as attribute?
        self.attributes_for_elem = {
	    'field':['id', 'width_type', 'width', 'height_type',
                     'height', 'position_horizontal_type',
                     'position_horizontal', 'position_vertical_type',
                     'position_vertical', 'color'],
            'rectangle':['id', 'width_type', 'width', 'height_type',
                         'height', 'position_horizontal_type',
                         'position_horizontal', 'position_vertical_type',
                         'position_vertical', 'color'],
            'image':['id', 'position_horizontal_type',
                     'position_horizontal', 'position_vertical_type',
                     'position_vertical', 'image_path'],
            'text':['id', 'position_horizontal_type',
                    'position_horizontal', 'position_vertical_type',
                    'position_vertical', 'message', 'font_family',
                    'font_size', 'font_color']
            }

class UgmConfigManager(object):
    """Manage ugm stimuluses configuration. Handle file storing and 
    in-memory representation.
    Attributes:
    - _config_file - string representing config file as 
    python module path, eg ugm.configs.ugm_config
    (for file ...../ugm/configs/ugm_config.py)
    - _fields = a python-list taken from config file representing ugm config
    """
    def __init__(self, p_config_file='ugm.configs.ugm_config'):
        """Init manager from config in format 
        package.subpackage...module_with_configuration."""
        self._config_file = p_config_file
        self.update_from_file()
    # ----------------------------------------------------------------------
    # CONFIG FILE MANAGMENT ------------------------------------------------
    def update_from_file(self, p_config_file=None):
        """Import config file from p_config_file or self._config_file
        if p_config_file is None. If we have config in file xxxx.py then
        p_config_file should be a string in format:
        xxxx or aaa.bbb.xxxx if file xxxx.py is in package aaa.bbb."""
        if p_config_file:
            self._config_file = p_config_file
        l_config_module = self._get_module_from_config(self._config_file)
        reload(l_config_module) # To be sure that the file is imported
        self.set_full_config(l_config_module.fields)

    def update_to_file(self, p_config_file=None):
        """Write self`s configuration stored in self._fields to file
        defined by path p_config_file or to self._config_file if
        p_config_file is not defined. p_config_file should be a path
        to the file, eg. 'a/b/c/config.py'. """
        if p_config_file:
            l_file_path = p_config_file
        else:
            l_module_path = self._get_module_from_config(self._config_file).__file__
            l_file_path = ''.join([l_module_path[:l_module_path.rfind('.')],
                                   '.py']) # Replace .pyc with .py
        l_file = open(l_file_path, 'w') #TODO -try except
        l_file.write(''.join(["fields = ", repr(self._fields)]))
        l_file.close()
    def _get_module_from_config(self, p_config_file):
        """ For given string p_config_file representing config file
        in format aaa.bbb.ccc return module instance representing the file
        """

        # In case l_config_file is in format aaa.bbb.ccc lets add aaa.bbb to
        # fromlist parameter in import call:
        l_dot = self._config_file.rfind('.')
        if l_dot == -1:
            l_config_module = __import__(p_config_file)
        else:
            l_config_module = __import__(p_config_file, 
                                         fromlist = [p_config_file[:l_dot]])
        return l_config_module

    # CONFIG FILE MANAGMENT ------------------------------------------------
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # PUBLIC GETTERS -------------------------------------------------------
    def get_config_for(self, p_id):
        """Return configuration dictionary for stimulus with p_id id."""
        return copy.deepcopy(self._configs(p_id))

    def get_ugm_fields(self):
        """Return a list of dictionaries representing configuration
        of every UgmField.
        Notice, that we don`t return in-memory list, but we return 
        a deep copy, as gui might want to alter config while processing."""
        return copy.deepcopy(self._fields)
    def get_attributes_config(self):
        """See UgmAttributesManager."""
        l_mgr = UgmAttributesManager()
        return {'attributes_def':
                    l_mgr.attributes_def,
                'attributes_for_elem':
                    l_mgr.attributes_for_elem
                }
    # PUBLIC GETTERS -------------------------------------------------------
    # ----------------------------------------------------------------------
    def _configs(self, p_id):
        """Return configuration dictionary for stimulus with p_id id."""
        return self._get_recursive_config(self._fields, p_id)
    def _get_recursive_config(self, p_fields, p_id):
        """Return configuration dictionary for stimulus with p_id id. 
        Internal method used by _config"""
        for i in p_fields:
            if i['id'] == p_id:
                return i
            j = self._get_recursive_config(i['stimuluses'], p_id)
            if j != None:
                return j
        return None

    # ----------------------------------------------------------------------
    # PUBLIC SETTERS -------------------------------------------------------
    def set_full_config(self, p_config_fields):
        """Set self`s in-memory ugm configuration to p_config_fields 
        being a list of dictionaries representin ugm stimuluses."""
        self._fields = p_config_fields

    def set_full_config_from_message(self, p_msg):
        """Set self`s in-memory ugm configuration based on a list of 
        dictionaries extracted from p_msg string representing it."""
        l_full_config = self.config_from_message(p_msg)
        self.set_full_config(l_full_config)

    def set_config(self, p_elem_config):
        """Update config for stimulus with id p_elem_config['id'].
        For dictionary representing that stimulus override attributes
        defined id p_elem_config."""

        # Don`create a new entry, use existing one so 
        # that corresponding element in self._fields is also updated
        l_elem = self._configs(p_elem_config['id'])
        for i_key, i_value in p_elem_config.iteritems():
            l_elem[i_key] = i_value

    def set_config_from_message(self, p_msg):
        """Update config for stimuluses with data extracted 
        from p_msg string representing it."""

        l_configs = self.config_from_message(p_msg)
        for i_config in l_configs:
            self.set_config(i_config)

    # PUBLIC SETTERS -------------------------------------------------------
    # ----------------------------------------------------------------------
    def update_message_is_full(self, p_msg_type):
        """Return true if p_msg_type represents full_update_message."""
        return p_msg_type == 0
    def update_message_is_simple(self, p_msg_type):
        """Return true if p_msg_type represents simple update message."""
        return p_msg_type == 1
    def config_from_message(self, p_msg):
        """Create python configuration structure 
        from message string p_msg."""
        return eval(p_msg)
    def config_to_message(self):
        """Create and return string from self`s configuration structure."""
        return str(self._fields)