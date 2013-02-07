#!/usr/bin/python

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
# This file contain interfaces an abstract classes for plugins
#
#
#-----------------------------------------------------------------------

from core.api.results.result import Result


class Plugin():
    """
    Abstract class for plugins

    Contains helper methods for plugins, and defines an interface that
    will be implemented by subclasses.

    All plugins must derive from this class.
    """


    #----------------------------------------------------------------------
    def run(self):
        """Plugin entry point. Your code goes here!"""
        raise NotImplementedError("All plugins must implement this method!")

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
        :type info: some subclass of Result
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
    def set_observer(self, observer):
        """
        Set observer for the plugins
        """
        #if not isinstance(observer, Audit):
        #    raise ValueError("Expected Orchestrator, got %r instead" % type(observer))

        self.__observer_ref = observer

    #----------------------------------------------------------------------
    def send_info(self, information):
        """Send information to the Audit"""
        if not isinstance(information, Result):
            raise ValueError("Expected Orchestrator, got %r instead" % type(information))

        self.__observer_ref.recv_msg(information)

#------------------------------------------------------------------------------
class TestingPlugin (Plugin):
    """
    Testing plugins are the ones that perform the security tests.

    This is the base class for all Testing plugins.
    """

    #----------------------------------------------------------------------
    def __init__(self):
        pass



#------------------------------------------------------------------------------
class UIPlugin (Plugin):
    """
    User Interface plugins control the way in which the user interacts with GoLismero.

    This is the base class for all UI plugins.
    """

    #----------------------------------------------------------------------
    def __init__(self):
        pass


#------------------------------------------------------------------------------
class GlobalPLugin (Plugin):
    """
    Global plugins can control all stages of an audit.

    Tipically users don't code their own Global plugins.

    This is the base class for all Global plugins.
    """

    #----------------------------------------------------------------------
    def __init__(self):
        pass

#------------------------------------------------------------------------------
class ResultsPlugin (Plugin):
    """
    Result plugins control how results will be exported.

    This is the base class for all Result plugins.
    """

    #----------------------------------------------------------------------
    def __init__(self):
        pass
