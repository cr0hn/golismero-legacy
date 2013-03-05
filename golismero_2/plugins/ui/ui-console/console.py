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

from colorizer import *
from time import sleep



class ConsoleUIPlugin(UIPlugin):
    """
    Console UI plugin.
    """

    # Colors
    color_info = 'cyan'
    color_low = 'green'
    color_middle = 'yellow'
    color_high = 'red'

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
        # Defines functions for INFORMATION types
        #
        m_info_funcs = {
            Information.INFORMATION_URL : self.display_info_url
        }

        #
        # Defines functions for VULNERABILITY types
        #
        m_vuln_funcs = {
            "url_disclouse" : self.display_vuln_url_disclouse
        }


        # Colorize output?
        self.__colorize = Config().audit_config.colorize

        #
        # Normal verbosity: Quiet + errors without traceback
        #
        if m_verbosity_level >= Console.STANDARD:

            # Messages with vulnerability types
            if  info.result_type == Result.TYPE_VULNERABILITY:
                m_vuln_funcs[info.vulnerability_type]

        #
        # More verbosity: Normal + Urls + important actions of plugins
        #
        if m_verbosity_level >= Console.VERBOSE:

            # Messages with information types
            if  info.result_type == Result.TYPE_INFORMATION:
                # Call the function
                m_info_funcs[info.information_type](info)



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

        # Colorize output?
        self.__colorize = Config().audit_config.colorize

        # Process control messages
        if message.message_type == Message.MSG_TYPE_CONTROL:

            # Show log messages
            # (The verbosity is already checked by Logger)
            if message.message_code == Message.MSG_CONTROL_LOG_MESSAGE:
                Console.display_error(self.colorize(message.message_info, ConsoleUIPlugin.color_middle), attrs=("dark",))

            # Show log errors
            # (The verbosity is already checked by Logger)
            elif message.message_code == Message.MSG_CONTROL_LOG_ERROR:
                Console.display_error(self.colorize(message.message_info, ConsoleUIPlugin.color_high), attrs=("dark",))

            # Show plugin errors
            # (The verbosity is already checked by bootstrap)
            elif message.message_code == Message.MSG_CONTROL_ERROR:
                text = self.colorize("[!] Plugin error: ", ConsoleUIPlugin.color_high) + \
                       self.colorize(message.message_info, ConsoleUIPlugin.color_high, attrs=("dark",))
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



    #----------------------------------------------------------------------
    #
    # Display information types
    #
    #----------------------------------------------------------------------
    def display_info_url(self, info):
        """
        How to display URL informations.

        :param info: information type
        """
        Console.display("[i] %s" % self.colorize(str(info), ConsoleUIPlugin.color_info))


    #----------------------------------------------------------------------
    #
    # Display vulnerability types
    #
    #----------------------------------------------------------------------
    def display_vuln_url_disclouse(self, info):
        """
        How to display discovered URLs.

        :param info: vulnerability type
        """
        if not info:
            return

        # Split parts
        m_pos_discovered = info.url.find(info.discovered)
        m_prefix = info.url[:m_pos_discovered]
        m_content = info.url[m_pos_discovered: m_pos_discovered + len(info.discovered)]
        m_suffix = info.url[m_pos_discovered + len(info.discovered):] if (m_pos_discovered + len(info.discovered)) < len(info.url) else ""

        # Print info
        Console.display("[i] %s%s%s" %
                        m_prefix,
                        self.colorize(m_content, ConsoleUIPlugin.color_red),
                        m_suffix)


    #----------------------------------------------------------------------
    def colorize(self, text, color, on_color=None, attrs=None):
        """Determitates if output must be colorized"""
        if self.__colorize:
            return colored(text, color, on_color, attrs)
        else:
            return text