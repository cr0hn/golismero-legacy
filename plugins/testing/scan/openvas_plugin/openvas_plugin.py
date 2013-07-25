#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Run the OpenVas scanner
"""

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: https://github.com/cr0hn/golismero/
Golismero project mail: golismero.project<@>gmail.com

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

from golismero.api.config import Config
from golismero.api.data.resource.ip import IP
from golismero.api.plugin import TestingPlugin


#------------------------------------------------------------------------------
class OpenVas(TestingPlugin):
	"""
	Run the OpenVas scanner
	"""


	#----------------------------------------------------------------------
	def get_accepted_info(self):
		return [IP]


	#----------------------------------------------------------------------
	def recv_info(self, info):

		m_target = info.url
		m_results = []


		#------------------------------------------------------------------

		return m_results

