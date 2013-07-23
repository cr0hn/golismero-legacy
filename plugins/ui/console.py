#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from golismero.api.data import Data
from golismero.api.data.resource import Resource
from golismero.api.data.vulnerability.information_disclosure.url_disclosure import UrlDisclosure
from golismero.api.data.vulnerability.information_disclosure.default_error_page import DefaultErrorPage
from golismero.api.data.vulnerability.information_disclosure.url_suspicious import SuspiciousURL
from golismero.api.plugin import UIPlugin
from golismero.main.console import Console, colorize, colorize_substring
from golismero.messaging.codes import MessageType, MessageCode
from golismero.messaging.message import Message

import warnings

#
# Verbosity levels:
#
# Disabled: No output
# Standard: Disabled + errors without traceback
# Verbose: Standard + urls, important actions of plugins
# More verbose: Verbose + errors with tracebacks, unimportant actions of plugins
#

#----------------------------------------------------------------------
class ConsoleUIPlugin(UIPlugin):
    """
    This is the console UI plugin. It provides a simple interface
    to work with GoLismero from the command line.

    This plugin has no options.
    """


    #----------------------------------------------------------------------
    def __init__(self):
        self.already_seen_info = set()


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return None


    #----------------------------------------------------------------------
    def recv_info(self, info):

        # Ignore already seen data
        #if info.identity in self.already_seen_info:
            #return
        #self.already_seen_info.add(info.identity)

        if Console.level >= Console.STANDARD:

            # Messages with vulnerability types
            if  info.data_type == Data.TYPE_VULNERABILITY:
                l_text = "%s Vulnerability '%s' dicovered. Risk level: %s." % (
                    colorize("<!>", info.risk),
                    colorize(info.vulnerability_type, info.risk),
                    colorize(str(info.risk), info.risk)
                )

                Console.display(l_text)

    #----------------------------------------------------------------------
    def recv_msg(self, message):
        if not isinstance(message, Message):
            raise TypeError("Expected Message, got %s instead" % type(message))

        if message.message_type == MessageType.MSG_TYPE_STATUS and \
           message.message_code == MessageCode.MSG_STATUS_PLUGIN_STEP:

            if Console.level >= Console.VERBOSE:
                m_id, m_progress, m_text = message.message_info

                #The counter
                m_progress_txt = colorize("[%s/100]" % "{:2d}".format(int(m_progress * 100)), "white")
                #m_text = "%s %s: Status: %s." % (m_progress_txt, m_id, m_text)
                m_text = "%s Status: %s." % (m_progress_txt, m_text)
                Console.display(m_text)