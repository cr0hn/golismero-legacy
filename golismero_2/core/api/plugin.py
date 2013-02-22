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

#-----------------------------------------------------------------------
#
#
# This file contains interfaces and base classes for plugins
#
#
#-----------------------------------------------------------------------

from .results.result import Result


class Plugin (object):
    """
    Base class for plugins.

    Contains helper methods for plugins, and defines an interface that
    will be implemented by subclasses.

    All plugins must derive from this class, or one if its subclasses.
    """

    PLUGIN_TYPE_ABSTRACT = 0    # Not a real plugin type!
    PLUGIN_TYPE_TESTING  = 1
    PLUGIN_TYPE_REPORT   = 2
    PLUGIN_TYPE_UI       = 3
    PLUGIN_TYPE_GLOBAL   = 4

    PLUGIN_TYPE_FIRST = PLUGIN_TYPE_TESTING
    PLUGIN_TYPE_LAST  = PLUGIN_TYPE_GLOBAL

    PLUGIN_TYPE = PLUGIN_TYPE_ABSTRACT


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
        raise NotImplementedError("All plugins must implement this method!")


    #----------------------------------------------------------------------
    def display_help(self):
        """Get the help message for this plugin."""
        # TODO: this could default to the description found in the metadata.
        raise NotImplementedError("All plugins must implement this method!")


    #----------------------------------------------------------------------
    def recv_info(self, info):
        """
        Callback method to receive information to be processed.

        :param info: input info to process
        :type info: Result
        """
        raise NotImplementedError("All plugins must implement this method!")


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        """
        Return a list of constants describing
        which messages are accepted by this plugin.

        Messages types can be found at the Message class.

        :returns: list -- list with constants
        """
        raise NotImplementedError("All plugins must implement this method!")


    #----------------------------------------------------------------------
    def _set_observer(self, observer):
        """
        Called internally by GoLismero. Do not call or override!
        """
        self.__observer_ref = observer


    #----------------------------------------------------------------------
    def send_info(self, information):
        """
        Plugins call this method to send information back to GoLismero.

        Do not override this method!
        """
        if not isinstance(information, Result):
            raise ValueError("Expected Result, got %r instead" % type(information))

        self.__observer_ref.send_info(information)


#------------------------------------------------------------------------------
class TestingPlugin (Plugin):
    """
    Testing plugins are the ones that perform the security tests.

    This is the base class for all Testing plugins.
    """

    PLUGIN_TYPE = Plugin.PLUGIN_TYPE_TESTING


#------------------------------------------------------------------------------
class ReportPlugin (Plugin):
    """
    Report plugins control how results will be exported.

    This is the base class for all Report plugins.
    """

    PLUGIN_TYPE = Plugin.PLUGIN_TYPE_REPORT


#------------------------------------------------------------------------------
class UIPlugin (Plugin):
    """
    User Interface plugins control the way in which the user interacts with GoLismero.

    This is the base class for all UI plugins.
    """

    PLUGIN_TYPE = Plugin.PLUGIN_TYPE_UI


    #----------------------------------------------------------------------
    def recv_msg(self, message):
        """
        Callback method to receive control messages to be processed.

        :param message: incoming message to process
        :type message: Message
        """
        raise NotImplementedError("All UI plugins must implement this method!")


#------------------------------------------------------------------------------
class GlobalPlugin (Plugin):
    """
    Global plugins can control all stages of an audit.

    Tipically users don't code their own Global plugins.

    This is the base class for all Global plugins.
    """

    PLUGIN_TYPE = Plugin.PLUGIN_TYPE_GLOBAL


    #----------------------------------------------------------------------
    def recv_msg(self, message):
        """
        Callback method to receive control messages to be processed.

        :param message: incoming message to process
        :type message: Message
        """
        raise NotImplementedError("All UI plugins must implement this method!")
