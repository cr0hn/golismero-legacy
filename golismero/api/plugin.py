#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------
# Base classes for plugins
#-----------------------------------------------------------------------

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

from .config import Config

__doc__ = """
This module contains all the interfaces for make plugins for GoLismero.

.. warning::
   The classes: :py:class:`.Plugin`, :py:class:`.InformationPlugin` and :py:class:`.AdvancedPlugin` provides a base for the end plugin never will be inherited by any plugin.

There are 3 types of class you must inherit to develop a plugin:

- :py:class:`.TestingPlugin`: To develop a testing/hacking? plugin.
- :py:class:`.UIPlugin`: To develop a User Interface plugin
- :py:class:`.ReportPlugin`: to develop a plugin to report the results.

"""


class Plugin (object):
    """
    Base class for all plugins.
    """

    PLUGIN_TYPE_ABSTRACT = 0    # Not a real plugin type!
    PLUGIN_TYPE_TESTING  = 1
    PLUGIN_TYPE_UI       = 2
    PLUGIN_TYPE_GLOBAL   = 3

    PLUGIN_TYPE_FIRST = PLUGIN_TYPE_TESTING
    PLUGIN_TYPE_LAST  = PLUGIN_TYPE_GLOBAL

    PLUGIN_TYPE = PLUGIN_TYPE_ABSTRACT


    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        """
        Check input parameters passed by the user.

        Parameters will be passed as an instance of 'AuditConfig'.

        If any parameter is not correct o there is an error, an
        exception must be raised.

        :param inputParams: input parameters to check
        :type inputParams: AuditConfig
        """
        raise NotImplementedError("Plugin must implement this method!")


    #----------------------------------------------------------------------
    def display_help(self):
        """
        :returns: Get the help message for this plugin.
        :rtype: str
        """
        text = Config.plugin_info.description
        if not text:
            raise NotImplementedError("Plugin must implement this method!")
        return text


    #----------------------------------------------------------------------
    def _set_observer(self, observer):
        """
        .. warning::
           Called internally by GoLismero. Do not call or override!
        """
        return


#------------------------------------------------------------------------------
class InformationPlugin (Plugin):
    """
    Information plugins are the ones that receive information, and may also
    send it back. Thus they can form feedback loops among each other.
    """


    #----------------------------------------------------------------------
    def recv_info(self, info):
        """
        Callback method to receive information to be processed.

        :param info: input info to process
        :type info: Data
        """
        raise NotImplementedError("Plugin must implement this method!")


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        """
        Return a list of constants describing
        which messages are accepted by this plugin.

        Messages types can be found at the Message class.


        :returns: list with constants.
        :rtype: list.
        """
        raise NotImplementedError("Plugin must implement this method!")


#------------------------------------------------------------------------------
class AdvancedPlugin (InformationPlugin):
    """
    Advanced plugins are tipically **internal plugins**, either of the UI type
    or the Global type. These are not usually coded by users, but only
    shipped with GoLismero itself.
    """


    #----------------------------------------------------------------------
    def recv_msg(self, message):
        """
        Callback method to receive control messages to be processed.

        :param message: incoming message to process
        :type message: Message
        """
        raise NotImplementedError("Plugin must implement this method!")


    #----------------------------------------------------------------------
    def _set_observer(self, observer):
        """
        Called internally by GoLismero. Do not call or override!
        """
        self.__observer_ref = observer


    #----------------------------------------------------------------------
    def send_msg(self, message):
        """
        Plugins call this method to send messages back to GoLismero.

        .. warning::
           Do not override this method!
        """
        self.__observer_ref.send_msg(message)


#------------------------------------------------------------------------------
class TestingPlugin (InformationPlugin):
    """
    Testing plugins are the ones that perform the security tests.

    This is the base class for all Testing plugins.
    """

    PLUGIN_TYPE = Plugin.PLUGIN_TYPE_TESTING


#------------------------------------------------------------------------------
class UIPlugin (AdvancedPlugin):
    """
    User Interface plugins control the way in which the user interacts with GoLismero.

    This is the base class for all UI plugins.
    """

    PLUGIN_TYPE = Plugin.PLUGIN_TYPE_UI


#------------------------------------------------------------------------------
class GlobalPlugin (AdvancedPlugin):
    """
    Global plugins can control all stages of an audit.

    Tipically users don't code their own Global plugins.

    This is the base class for all Global plugins.
    """

    PLUGIN_TYPE = Plugin.PLUGIN_TYPE_GLOBAL


#------------------------------------------------------------------------------
class ReportPlugin (Plugin):
    """
    Report plugins control how results will be exported.

    This is the base class for all Report plugins.
    """


    #----------------------------------------------------------------------
    def is_supported(self, output_file):
        """
        Determine if this plugin supports the requested file format.

        :param output_file: Output file to generate.
        :type output_file: str | None

        :returns: True if this plugin supports the format, False otherwise.
        :rtype: bool.
        """
        raise NotImplementedError("Plugin must implement this method!")


    #----------------------------------------------------------------------
    def generate_report(self, output_file):
        """
        Run plugin and generate report.

        :param output_file: Output file to generate.
        :type output_file: str | None
        """
        raise NotImplementedError("Plugin must implement this method!")
