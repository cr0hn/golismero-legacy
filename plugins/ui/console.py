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
                if m_progress:
                    m_progress_txt = colorize("[%s/100]" % "{:2.2f}".format(m_progress*100.0), "white")
                else:
                    m_progress_txt = colorize("[U]", "white")

                #m_text = "%s %s: Status: %s." % (m_progress_txt, m_id, m_text)
                m_text = "%s Status: %s" % (m_progress_txt, (m_text if m_text else "working"))
                Console.display(m_text)

        # Process control messages
        if message.message_type == MessageType.MSG_TYPE_CONTROL:

            # Show log messages
            # (The verbosity is sent by Logger)
            #if message.message_code == MessageCode.MSG_CONTROL_LOG:
                #(text, level, is_error) = message.message_info
                #if Console.level >= level:
                    #text = colorize(text, 'middle')
                    #text = "[*] %s" % text
                    #if is_error:
                        #Console.display_error(text)
                    #else:
                        #Console.display(text)

            # Show plugin errors
            # (Only the description in standard level,
            # full traceback in more verbose level)
            if message.message_code == MessageCode.MSG_CONTROL_ERROR:
                (description, traceback) = message.message_info
                text = "[!] Plugin error (%s): %s" % (message.plugin_name, description)
                text = colorize(text, 'critical')
                traceback = colorize(traceback, 'critical')
                Console.display_error(text)
                Console.display_error_more_verbose(traceback)

            # Show plugin warnings
            # (Only the description in verbose level,
            # full traceback in more verbose level)
            elif message.message_code == MessageCode.MSG_CONTROL_WARNING:
                for w in message.message_info:
                    if Console.level >= Console.MORE_VERBOSE:
                        formatted = warnings.formatwarning(w.message, w.category, w.filename, w.lineno, w.line)
                    elif Console.level >= Console.VERBOSE:
                        formatted = warnings.formatwarning(w.message, w.category)
                    else:
                        formatted = None
                    if formatted:
                        text = "[!] Plugin warning (%s): %s" % (message.plugin_name, formatted)
                        text = colorize(text, 'low')
                        Console.display_error(text)
