#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: https://github.com/golismero
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
from golismero.api.data.vulnerability import Vulnerability
from golismero.api.logger import Logger
from golismero.api.plugin import TestingPlugin

from threading import Event
from traceback import format_exc
from functools import partial

# Import the OpenVAS libraries from the plugin data folder.
# FIXME the library should go to thirdparty_libs once it's published!
import os, sys
sys.path.insert(0, os.path.abspath(os.path.split(__file__)[0]))
from openvas_lib import VulnscanManager, VulnscanException


#------------------------------------------------------------------------------
class OpenVASPlugin(TestingPlugin):


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [IP]


    #----------------------------------------------------------------------
    def recv_info(self, info):

        # Synchronization object to wait for completion.
        m_event = Event()

        # Get the config.
        m_user      = Config.plugin_args["user"]
        m_password  = Config.plugin_args["password"]
        m_host      = Config.plugin_args["host"]
        m_port      = Config.plugin_args["port"]
        m_timeout   = Config.plugin_args["timeout"]
        m_profile   = Config.plugin_args["profile"]

        # Sanitize the port and timeout.
        try:
            m_port = int(m_port)
        except Exception:
            m_port = 9390
        if m_timeout.lower().strip() in ("inf", "infinite", "none"):
            m_timeout = None
        else:
            try:
                m_timeout = int(m_timeout)
            except Exception:
                m_timeout = None

        # Connect to the scanner.
        try:
            m_scanner = VulnscanManager(m_host, m_user, m_password, m_port, m_timeout)
        except VulnscanException, e:
            t = format_exc()
            Logger.log_error("Error connecting to OpenVAS, aborting scan!")
            #Logger.log_error_verbose(str(e))
            Logger.log_error_more_verbose(t)
            return

        # Launch the scanner.
        m_scan_id = m_scanner.launch_scan(
            target = info.address,
            profile = m_profile,
            callback_end = partial(lambda x: x.set(), m_event),
            callback_progress = self.update_status
        )

        # Wait for completion.
        m_event.wait()

        try:

            # Get the scan results.
            m_openvas_results = m_scanner.get_results(m_scan_id)

            # Convert the scan results to the GoLismero data model.
            return self.parse_results(info, m_openvas_results)

        finally:

            # Clean up.
            m_scanner.delete_scan(m_scan_id)


    #----------------------------------------------------------------------
    @staticmethod
    def parse_results(ip, openvas_results):
        """
        Convert the OpenVAS scan results to the GoLismero data model.

        :param ip: (Optional) IP address to link the vulnerabilities to.
        :type ip: IP | None

        :param openvas_results: OpenVAS scan results.
        :type openvas_results: list(OpenVASResult)

        :returns: Scan results converted to the GoLismero data model.
        :rtype: list(Data)
        """
        #
        # XXX TODO
        #
        return []
