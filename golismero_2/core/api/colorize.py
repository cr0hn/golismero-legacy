#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Author: Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com

Golismero project site: http://code.google.com/p/golismero/
Golismero project mail: golismero.project@gmail.com

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

#-----------------------------------------------------------------------
# Colored console output API
#-----------------------------------------------------------------------

__all__ = ["colorize"]

#
# DON'T CHANGE THIS INCLUDE. THE FORM:
# "from colorizer import *" => don't work on mac!!!
from thirdparty_libs.colorizer import *

from .config import Config

#----------------------------------------------------------------------
# Map of colors
m_colors = {

    # String log levels to color names
    'info': 'green',
    'low': 'cyan',
    'middle': 'magenta',
    'high' :'red',
    'critical' : 'yellow',

    # Integer log levels to color names
    0: 'green',
    1: 'cyan',
    2: 'magenta',
    3: 'red',
    4: 'yellow',

    # Color names mapped to themselves
    'green': 'green',
    'cyan': 'cyan',
    'magenta': 'magenta',
    'red': 'red',
    'yellow': 'yellow',
}

#----------------------------------------------------------------------
def colorize(text, level_or_color, is_color = True):
    """
    Colorize a text depends of type of alert:
    - Information
    - Low
    - Middle
    - Hight
    - Critical

    :param text: text to colorize.
    :type text: int with level (0-4) or string with values: info, low, middle, high, critical.

    :param level: color selected, by level.
    :type level: str or integer (0-4).

    :param color: indicates if output must be colorized or not.
    :type color: bool.

    :returns: str -- string with information to print.
    """


    if Config().audit_config.colorize and is_color:
        return colored(text, m_colors[level_or_color])
    else:
        return text
