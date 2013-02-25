#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Author: Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com

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

from core.api.plugin import TestingPlugin
from core.api.results.information.information import Information
from core.api.logger import Logger
from core.api.results.information.url import Url
from time import sleep
from core.api.net.netmanager import *

class ExamplePlugin(TestingPlugin):
    """
    This plugin is used por testing purposes and as example of the use of plugins.
    """


    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        """
        Check input parameters passed by the user.

        Parameters will be passed as an instance of 'GlobalParams'.

        If any parameter is not correct o there is an error, an
        exception must be raised.

        :param inputParams: input parameters to check
        :type inputParams: GlobalParams
        """
        pass


    #----------------------------------------------------------------------
    def display_help(self):
        """Get the help message for this plugin."""
        # TODO: this could default to the description found in the metadata.
        return "This is an example plugin."


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        """
        Return a list of constants describing
        which messages are accepted by this plugin.

        Messages types can be found at the Message class.

        :returns: list -- list with constants
        """
        return [Information.INFORMATION_URL]

    #----------------------------------------------------------------------
    def recv_info(self, info):
        """Callback method to receive information to be processed."""
        #Logger.log("Example plugin. Received: %s\n" % info.url)

        #r = NetManager.get_connection()
        #p = r.get("/")

        #print str(info)

        #if isinstance(p, HTTP_Response):
            #print "aaaa" + str(p.http_code)

        # Test the file API
        #from core.api.file import FileManager as FF
        #F = FF()
        #assert F.exists("example.py")
        #assert F.isfile("example.py")
        #assert F.isdir(".")
        #assert F.samefile("example.py", "example.py")
        #Logger.log(str(F.listdir()))
        #Logger.log(str(list(F.walk())))
        #with F.open("example.py") as fp1:
            #with F.open("example.py") as fp2:
                #pass


        # Send a test message
