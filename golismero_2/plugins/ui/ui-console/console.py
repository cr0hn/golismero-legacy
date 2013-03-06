#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife.

Copyright (C) 2011-2013 - Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com

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

from core.api.config import Config
from core.api.plugin import UIPlugin
from core.api.results.information.information import Information
from core.api.results.result import Result
from core.messaging.message import Message
from core.main.console import Console
from core.api.colorize import *



class ConsoleUIPlugin(UIPlugin):
    """
    Console UI plugin.
    """

    #----------------------------------------------------------------------
    def display_help(self):
        #
        # Put here extended information, and usage details, to display when
        # a user run progan with "--plugin-info" option.
        #
        # Example:
        #
        # info =
        # """
        #    This text is will displayed when user need to see additional
        #    information about the plugin, and usage details.
        #
        #    Usage: This plugin need 'x' parameter to run... etc
        # """
        # return info
        #
        return """
            This is the console UI plugin. It provides a simple interface
            to work with GoLismero from the command line.

            This plugin has no options.
        """


    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        pass


    #----------------------------------------------------------------------
    def recv_info(self, info):
        #
        # Display in console
        #

        # Get verbosity level.
        m_verbosity_level = Config().audit_config.verbose

        #
        # Normal verbosity: Quiet + errors without traceback
        #
        if m_verbosity_level >= Console.STANDARD:

            # Messages with vulnerability types
            if  info.result_type == Result.TYPE_VULNERABILITY:
                Console.display("+ %s" % info.printable())

        #
        # More verbosity: Normal + Urls + important actions of plugins
        #
        if m_verbosity_level >= Console.VERBOSE:

            # Messages with information types
            if  info.result_type == Result.TYPE_INFORMATION and info.information_type == Information.INFORMATION_URL:
                # Call the function
                Console.display("+ %s" % info.printable_verbose())


        #
        # Even more verbosity: More + errors with tracebacks + no important actions of plugins
        #
        if m_verbosity_level >= Console.MORE_VERBOSE:
            pass


    #----------------------------------------------------------------------
    def recv_msg(self, message):
        #
        # Put here the code you want to execute when a control message is received.
        #

        if not isinstance(message, Message):
            raise TypeError("Expected Message, got %s instead" % type(message))

        # Get verbosity level.
        m_verbosity_level = Config().audit_config.verbose

        # Process control messages
        if message.message_type == Message.MSG_TYPE_CONTROL:

            # Show log messages
            # (The verbosity is already checked by Logger)
            if message.message_code == Message.MSG_CONTROL_LOG_MESSAGE:
                Console.display_error("- %s" % colorize(message.message_info, 'middle'))

            # Show log errors
            # (The verbosity is already checked by Logger)
            elif message.message_code == Message.MSG_CONTROL_LOG_ERROR:
                Console.display_error("- %s" % colorize(message.message_info, 'middle'))

            # Show plugin errors
            # (The verbosity is already checked by bootstrap)
            elif message.message_code == Message.MSG_CONTROL_ERROR:
                text = colorize("[!] Plugin error: ", 'high') + \
                       colorize(message.message_info, 'high')
                Console.display_error(text)


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        #
        # Put here the list of the type of info you want to receive.
        #
        # To build the list, you will need to use the constants of
        # the results package.
        #
        # Example:
        #
        # Receive XSS results and URLs, write this:
        #
        # 1 - Include libraries, at top of this file:
        #
        #     from core.api.results.information.information import Information
        #     from core.api.results.injection.injection import Injection
        #
        # 2 - Make the list with the info we want receive:
        #
        #     return list(Information.INFORMATION_URL, Injection.XSS_REFLECTED)
        #
        return None


