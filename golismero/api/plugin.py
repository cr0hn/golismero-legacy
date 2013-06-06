#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains the base classes for GoLismero plugins.

To write your own plugin, you must derive from one of the following base classes:

- :py:class:`.TestingPlugin`: To write a testing/hacking plugin.
- :py:class:`.UIPlugin`: To write a User Interface plugin.
- :py:class:`.ReportPlugin`: to write a plugin to report the results.
"""

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

__all__ = ["TestingPlugin", "UIPlugin", "ReportPlugin"]

from .config import Config


class Plugin (object):
    """
    Base class for all plugins.
    """

    PLUGIN_TYPE_ABSTRACT = 0    # Not a real plugin type!
    PLUGIN_TYPE_TESTING  = 1
    PLUGIN_TYPE_UI       = 2
    PLUGIN_TYPE_REPORT   = 3

    PLUGIN_TYPE_FIRST = PLUGIN_TYPE_TESTING
    PLUGIN_TYPE_LAST  = PLUGIN_TYPE_REPORT

    PLUGIN_TYPE = PLUGIN_TYPE_ABSTRACT


    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        """
        Optional method to check input parameters passed by the user.

        Parameters will be passed as an instance of 'AuditConfig'.

        If any parameter is not correct o there is an error, an
        exception must be raised.

        :param inputParams: input parameters to check
        :type inputParams: AuditConfig

        :raises Exception: The plugin detected a configuration error.
        """
        pass


    #----------------------------------------------------------------------
    def display_help(self):
        """
        Optional method to display the help message for this plugin.

        If not overridden, it defaults to returning the Description
        setting in the plugin descriptor file, or the class docstring
        if the Description setting is missing.

        :returns: The help message for this plugin.
        :rtype: str
        """
        text = Config.plugin_info.description
        if not text:
            text = getattr(self, "__doc__", None)
            if not text:
                raise NotImplementedError(
                    "Plugins that don't define a description in their"
                    " config file nor their class documentation must"
                    " implement the display_help() method")
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
        Callback method to receive data to be processed.

        This is the most important method of a plugin.
        Here's where most of the logic resides.

        :param info: Data to be processed.
        :type info: Data
        """
        raise NotImplementedError("Plugins must implement this method!")


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        """
        Return a list of constants describing
        which data types are accepted by the recv_info method.

        :returns: Data type constants.
        :rtype: list
        """
        raise NotImplementedError("Plugins must implement this method!")


#------------------------------------------------------------------------------
class UIPlugin (InformationPlugin):
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
        raise NotImplementedError("Plugins must implement this method!")


    #----------------------------------------------------------------------
    def _set_observer(self, observer):
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
class ReportPlugin (Plugin):
    """
    Report plugins control how results will be exported.

    This is the base class for all Report plugins.
    """

    PLUGIN_TYPE = Plugin.PLUGIN_TYPE_REPORT


    #----------------------------------------------------------------------
    def is_supported(self, output_file):
        """
        Determine if this plugin supports the requested file format.

        Tipically, here is where Report plugins examine the file extension.

        :param output_file: Output file to generate.
        :type output_file: str | None

        :returns: True if this plugin supports the format, False otherwise.
        :rtype: bool
        """
        raise NotImplementedError("Plugins must implement this method!")


    #----------------------------------------------------------------------
    def generate_report(self, output_file):
        """
        Run plugin and generate the report.

        This is the entry point for Report plugins,
        where most of the logic resides.

        :param output_file: Output file to generate.
        :type output_file: str | None
        """
        raise NotImplementedError("Plugins must implement this method!")
