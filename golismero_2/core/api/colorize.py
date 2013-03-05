#!/usr/bin/python
# -*- coding: utf-8 -*-

from thirdparty_libs.colorizer import *
from core.api.config import Config

__all__ = ["colorize"]

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



#----------------------------------------------------------------------
def colorize(text, level):
	"""
	Colorize a text depends of type of alert:
	- Information
	- Low
	- Middle
	- Hight
	- Critical

	:param text: text to colorize.
	:type text: int with level (0-4) or string with values: info, low, middle, high, critical.
	"""

	# Colors
	m_colors = {
	   'info': 'cyan',
	   'low': 'green',
	   'middle': 'yellow',
	   'high' :'red',
	   'critical' : 'purple'
	}

	# Map for integers params as level
	m_colors["0"] = m_colors['info']
	m_colors["1"] = m_colors['low']
	m_colors["2"] = m_colors['middle']
	m_colors["3"] = m_colors['high']
	m_colors["4"] = m_colors['critical']

	# Ge colorize option
	if Config().audit_config.colorize:
		return colored(text, m_colors[str(level)])
	else:
		return text

