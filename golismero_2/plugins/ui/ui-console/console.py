#!/usr/bin/python

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

from core.api.plugins.plugin import UIPlugin
from core.api.logger import Logger
from core.messaging.message import Message
from core.api.results.result import Result
from time import sleep

class ConsoleUIPlugin(UIPlugin):
    """
    This is a plugin that you can use as template.
    """

    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        """
        Check input user parameters

        Parameters will be passed as instance of 'GlobalParams"

        If any parameter is not correct o there is any error, 'ValueError'
        a exception must be raised.

        :param inputParams: input parameters to check
        :type inputParams: GlobalParams
        """
        #
        #
        # Put here your check code
        #
        #
        pass

    #----------------------------------------------------------------------
    def display_help(self):
        """Get the help message for this plugin."""
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
        raise NotImplementedError("All plugins must implement this method!")

    #----------------------------------------------------------------------
    def recv_info(self, info):
        """
        Callback method to receive information to be processed.

        :param info: input info to process
        :type info: some subclass of Result
        """
        #
        # Put here the code you want to execute when a info is received.
        #
        # This method act as a "main" function. All the functionality
        # must be put here.
        #
        # Example:
        #
        # Write a line in the log, for each message received.
        #
        # 1 - Include log library, at top of this file:
        #
        #     from core.api.logger import IO
        #
        # 2 - Write into log system
        #
        #     Logger.log("New message received!")
        #     Logger.log_verbose("This message will be displayed when verbose mode is enabled")
        #
        #     VERY IMPORTANT
        #     ==============
        #     NEVER USE 'print' function to display information. Use
        #     IO library instead.
        #

        print "UIUIUIUI"
        Logger.log("aaaa")
        if isinstance(info, Message):
            if info.message_type == Message.MSG_TYPE_INFO:
                m_result = info.message_info

                # Filter how to display the info
                if isinstance(m_result, Result):
                    # URL type
                    if m_results.result_type is Result.TYPE_INFORMATION:
                        Logger.log("+ New url found: %s." % str(m_result))




    #----------------------------------------------------------------------
    def get_accepted_info(self):
        """
        Return a list of constants describing
        which messages are accepted by this plugin.

        Messages types can be found at the Message class.

        :returns: list -- list with constants
        """
        #
        # Put here the list of type of info you want to receive.
        #
        # To do the list, you will need to use the constants of
        # Result class.
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
        return "aaa"