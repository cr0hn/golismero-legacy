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
from core.api.results.information.information import Information
from time import sleep

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

        # URL type
        if info.result_type is Result.TYPE_INFORMATION and info.result_subtype == Information.INFORMATION_URL:
            Logger.log("+ New url found: %s." % str(info))


    #----------------------------------------------------------------------
    def recv_msg(self, message):
        #
        # Put here the code you want to execute when a control message is received.
        #

        print "CONTROL"
        Logger.log("bbb")


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