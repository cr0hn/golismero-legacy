#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

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
from threading import Semaphore
from functools import partial

# Import theHarvester as a library.
import os, sys
cwd = os.path.abspath(os.path.split(__file__)[0])
cwd = os.path.join(cwd, ".")
sys.path.insert(0, cwd)

from openvas_lib import VulnscanManager

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

		m_sem = Semaphore(0)

		# Get the config
		m_user      = Config.plugin_extra_config["Defaults"]["user"]
		m_password  = Config.plugin_extra_config["Defaults"]["password"]
		m_host      = Config.plugin_extra_config["Defaults"]["host"]
		m_target    = info.address
		m_profile   = Config.plugin_extra_config["Defaults"]["profile"]

		m_host      = "192.168.0.208"
		m_target    = "192.168.0.194"
		m_profile   = "empty"

		# Configure the scanner
		m_scanner   = VulnscanManager.connectOpenVas(m_host,
		                                             m_user,
		                                             m_password)
		# Launch the scanner
		m_scan_id = m_scanner.launch_scan(m_target, profile=m_profile, callback=partial(lambda x: x.release(), m_sem))

		# Wait
		m_sem.acquire()

		#
		# Get results
		#
		m_openvas_results = m_scanner.get_results(m_scan_id)

		#
		# Remove the temporal scan
		#
		m_scanner.delete_scan(m_scan_id)


