#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
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

from golismero.api.config import Config
from golismero.api.plugin import UIPlugin
from golismero.api.data.resource.resource import Resource
from golismero.api.data.data import Data
from golismero.messaging.codes import MessageType, MessageCode
from golismero.messaging.message import Message
from golismero.main.console import Console, colorize

#
# Verbosity levels:
#
# Disabled: No output
# Standard: Disabled + errors without traceback
# Verbose: Standard + urls, important actions of plugins
# More verbose: Verbose + errors with tracebacks, unimportant actions of plugins
#

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

        # Processors functions
        funcs = {
            Resource.RESOURCE_URL : process_url,
            'url_disclouse': process_url_disclosure
        }

        # Get verbosity level.
        Console.level = Config.audit_config.verbose

        if Console.level >= Console.STANDARD:

            # Messages with vulnerability types
            if  info.data_type == Data.TYPE_VULNERABILITY:
                Console.display("%s" % funcs[info.vulnerability_type](info))

        if Console.level >= Console.VERBOSE:

            # Messages with information types
            if  info.data_type == Data.TYPE_RESOURCE and info.data_type == Resource.RESOURCE_URL:
                Console.display("+ %s" % funcs[info.RESOURCE_URL](info))


    #----------------------------------------------------------------------
    def recv_msg(self, message):
        #
        # Put here the code you want to execute when a control message is received.
        #

        if not isinstance(message, Message):
            raise TypeError("Expected Message, got %s instead" % type(message))

        # Set verbosity level.
        Console.level = Config.audit_config.verbose

        # Process control messages
        if message.message_type == MessageType.MSG_TYPE_CONTROL:

            # Show log messages
            # (The verbosity is sent by Logger)
            if message.message_code == MessageCode.MSG_CONTROL_LOG:
                (text, level, is_error) = message.message_info
                if Console.level >= level:
                    text = colorize(text, 'middle')
                    text = "[*] %s" % text
                    if is_error:
                        Console.display_error(text)
                    else:
                        Console.display(text)

            # Show plugin errors
            # (Only the description in standard level,
            # full traceback in more verbose level)
            elif message.message_code == MessageCode.MSG_CONTROL_ERROR:
                (description, traceback) = message.message_info
                text = "[!] Plugin error: " + description
                text = colorize(text, 'critical')
                traceback = colorize(traceback, 'critical')
                Console.display_error(text)
                Console.display_error_more_verbose(traceback)


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        #
        # Put here the list of the type of info you want to receive.
        #
        # To build the list, you will need to use the constants of
        # the data package.
        #
        # Example:
        #
        # Receive XSS vulnerability and URLs, write this:
        #
        # 1 - Include libraries, at top of this file:
        #
        #     from golismero.api.data.information.information import Information
        #     from golismero.api.data.injection.injection import Injection
        #
        # 2 - Make the list with the info we want receive:
        #
        #     return list(Resource.RESOURCE_URL, Injection.XSS_REFLECTED)
        #
        return None


#----------------------------------------------------------------------
def process_url(url):
    """Display URL info"""
    return "New URL: [%s] %s" % (
        url.method,
        colorize(url.url, 'info'),
    )


#----------------------------------------------------------------------
def process_url_disclosure(url):
    """Display URL discover"""
    # Split parts
    m_pos_discovered = url.url.find(url.discovered)
    m_prefix = url.url[:m_pos_discovered]
    m_content = url.url[m_pos_discovered: m_pos_discovered + len(url.discovered)]
    m_suffix = url.url[m_pos_discovered + len(url.discovered):] if (m_pos_discovered + len(url.discovered)) < len(url.url) else ""

    m_url = "%s%s%s" % (
        m_prefix,
        colorize(m_content, url.risk),
        m_suffix
    )

    return "%s: %s\n| Method: %s\n%s|-%s" % (
        colorize("!! Discovered", url.risk),
        m_url,
        url.method,
        '| Referer <- %s\n' % url.referer if url.referer else '',
        "-" * len(url.url)
    )