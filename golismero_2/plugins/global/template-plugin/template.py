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

from core.api.plugin import GlobalPlugin
from core.api.logger import Logger

class TemplatePlugin(GlobalPlugin):
    """
    This is a plugin that you can use as template.
    """


    #----------------------------------------------------------------------
    def display_help(self):
        #
        #
        # Return here the help message to be shown when the user runs the
        # program with the "--plugin-info" switch.
        #
        # Example:
        #
        return """
           This text is will displayed when user need to see additional
           information about the plugin, and usage details.

           Usage: This plugin need 'x' parameter to run... etc
        """


    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        #
        #
        # Put here your check code. The inputParams variable is an instance
        # of GlobalParams. Raise an exception if there's an error.
        #
        #
        pass


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        #
        #
        # Return here the list of the types of info you want to receive.
        #
        # To build the list, you will need to use the constants of
        # the core.api.data package.
        #
        # An empty list means you don't get any info at all!
        #
        # To get all possible types of information, return None.
        #
        # Example:
        #
        # To receive XSS results and URLs, write this:
        #
        # 1 - Include libraries, at top of this file:
        #
        #     from core.api.data.information.information import Information
        #     from core.api.data.injection.injection import Injection
        #
        # 2 - Make the list with the info we want receive:
        #
        #     return list(Resource.RESOURCE_URL), Injection.XSS_REFLECTED)
        #
        #
        return None


    #----------------------------------------------------------------------
    def recv_info(self, info):
        #
        #
        # Put here the code you want to execute when info is received.
        #
        # This method acts as a "main" function. All the functionality
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
        #     NEVER USE 'print' function to display information.
        #     Use the logger instead.
        #
        Logger.log("Template plugin: It's works!")
