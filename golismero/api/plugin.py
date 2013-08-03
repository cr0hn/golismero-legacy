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

__all__ = [
    "UIPlugin", "ImportPlugin", "TestingPlugin", "ReportPlugin",
    "get_plugin_info",
]

from .config import Config
from ..common import Singleton
from ..messaging.codes import MessageCode


#------------------------------------------------------------------------------
def get_plugin_info(plugin_name = None):
    """
    Get the plugin information for the requested plugin.

    :param plugin_name: Full plugin name.
        Example: "testing/recon/spider".
        Defaults to the calling plugin name.
    :type plugin_name: str

    :returns: Plugin information.
    :rtype: PluginInfo

    :raises KeyError: The plugin was not found.
    """
    if not plugin_name:
        plugin_name = Config.plugin_name
    return Config._context.remote_call(
        MessageCode.MSG_RPC_PLUGIN_GET_INFO, plugin_name)


#------------------------------------------------------------------------------
class _PluginState (Singleton):
    """
    Container of plugin state variables.

    State variables are stored in the audit database.
    That way plugins can maintain state regardless of which process
    (or machine!) is running them at any given point in time.
    """


    #--------------------------------------------------------------------------
    __sentinel = object()
    @classmethod
    def get(cls, name, default = __sentinel):
        """
        Get the value of a state variable.

        :param name: Name of the variable.
        :type name: str

        :param default: Optional default value. If set, when the name
                        is not found the default is returned instead
                        of raising KeyError.
        :type default: *

        :returns: Value of the variable.
        :rtype: *

        :raises KeyError: The variable was not defined.
        """
        try:
            return Config._context.remote_call(
                MessageCode.MSG_RPC_STATE_GET, Config.plugin_name, name)
        except KeyError:
            if default is not cls.__sentinel:
                return default
            raise


    #--------------------------------------------------------------------------
    @staticmethod
    def check(name):
        """
        Check if a state variable has been defined.

        :param name: Name of the variable to test.
        :type name: str

        :returns: True if the variable was defined, False otherwise.
        :rtype: bool
        """
        return Config._context.remote_call(
            MessageCode.MSG_RPC_STATE_CHECK, Config.plugin_name, name)


    #--------------------------------------------------------------------------
    @staticmethod
    def set(name, value):
        """
        Set the value of a state variable.

        :param name: Name of the variable.
        :type name: str

        :param value: Value of the variable.
        :type value: *
        """
        Config._context.async_remote_call(
            MessageCode.MSG_RPC_STATE_ADD, Config.plugin_name, name, value)


    #--------------------------------------------------------------------------
    @staticmethod
    def remove(name):
        """
        Remove a state variable.

        :param name: Name of the variable.
        :type name: str

        :raises KeyError: The variable was not defined.
        """
        Config._context.async_remote_call(
            MessageCode.MSG_RPC_STATE_REMOVE, Config.plugin_name, name)


    #--------------------------------------------------------------------------
    @staticmethod
    def get_names():
        """
        Get the names of the defined state variables.

        :returns: Names of the defined state variables.
        :rtype: set(str)
        """
        Config._context.async_remote_call(
            MessageCode.MSG_RPC_STATE_KEYS, Config.plugin_name)


    #--------------------------------------------------------------------------
    # Overloaded operators.

    def __getitem__(self, name):
        'x.__getitem__(y) <==> x[y]'
        return self.get(name)

    def __setitem__(self, name, value):
        'x.__setitem__(i, y) <==> x[i]=y'
        return self.set(name, value)

    def __delitem__(self, name):
        'x.__delitem__(y) <==> del x[y]'
        return self.remove(name)

    def __contains__(self, name):
        'D.__contains__(k) -> True if D has a key k, else False'
        return self.check(name)

# Instance the singleton.
PluginState = _PluginState()


#------------------------------------------------------------------------------
class Plugin (object):
    """
    Base class for all plugins.
    """

    PLUGIN_TYPE_ABSTRACT = 0    # Not a real plugin type!
    PLUGIN_TYPE_UI       = 1
    PLUGIN_TYPE_IMPORT   = 2
    PLUGIN_TYPE_TESTING  = 3
    PLUGIN_TYPE_REPORT   = 4

    PLUGIN_TYPE_FIRST = PLUGIN_TYPE_TESTING
    PLUGIN_TYPE_LAST  = PLUGIN_TYPE_REPORT

    PLUGIN_TYPE = PLUGIN_TYPE_ABSTRACT

    # Useful alias for the plugin state container.
    state = PluginState


    #--------------------------------------------------------------------------
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


    #--------------------------------------------------------------------------
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


    #--------------------------------------------------------------------------
    def _set_observer(self, observer):
        """
        .. warning::
           Called internally by GoLismero. Do not call or override!
        """
        return


    #--------------------------------------------------------------------------
    def update_status(self, text = None, progress = None):
        """
        Plugins can call this method to tell the user of the current
        progress of whatever the plugin is doing.

        .. warning::
           Do not override this method!

        :param text: Optional status text.
        :type text: str | None

        :param progress: Progress percentage [0, 100] as a float,
                         or None to indicate progress can't be measured.
        :type progress: float | None
        """
        Config._context.send_status(text, progress)


    #--------------------------------------------------------------------------
    def update_status_step(self, step = None, total = 100.0, partial = 100.0, text = None):
        """
        Plugins can call this method to tell the user of the current
        state of process for a concrete instant of time.

        The step indicates the indicates the concrete value from a total
        amount of information. The total amount of information to process
        is repressented by 'total' var.

        .. warning::
           Do not override this method!

        Example:

        - step = 1
        - total = 80
        - The step == 1, represent the 1.25% of the total of process.

        The optional partial param allow us to say the weight of the total
        value respresent in the global status.

        Example:

        - The global process is the 100%.
        - A concrete piece of code represent the 20% of the total process.
        - The concrete piece has 80 values

        Then, each step of status increment must be made in increments of 0.25%
        until the total of percent value asignated to the piece of code: 20%:

        0.25 * 80 values = 20% (the total percent for this piece of code)

        Example::
            values_to_process = [0,1,2,4] # 40% of rest of task
            values_len = len(values_to_process)
            for i, val in enumerate(values_to_process, start=1):
                self.update_status_step(i, values_len, partial=40, text="Text for update")

        :param step: amount of values of total.
        :type step: float | int

        :param total: the total amount of values to process.
        :type total: float | int

        :param partial: Optional value in the range [0, 100] that represents the weight of the process has.
        :type partial: float | int

        :param text: Optional status text.
        :type text: str | None
        """
        try:

            if step is None:
                m_progress = None
            else:
                m_total   = float(total)
                m_step    = float(step)
                m_partial = float(partial)
                if 0.0 < m_partial <= 100.0:
                    m_progress = (m_step/m_total) * (m_partial)
                else:
                    raise ValueError("partial value must be in range: [0, 100]")

        except ValueError:
            raise ValueError("Input parameters must be numeric")
        except ZeroDivisionError:
            raise ValueError("Total cannot be zero")

        self.update_status(text, m_progress)


#------------------------------------------------------------------------------
class InformationPlugin (Plugin):
    """
    Information plugins are the ones that receive information, and may also
    send it back. Thus they can form feedback loops among each other.
    """


    #--------------------------------------------------------------------------
    def recv_info(self, info):
        """
        Callback method to receive data to be processed.

        This is the most important method of a plugin.
        Here's where most of the logic resides.

        :param info: Data to be processed.
        :type info: Data
        """
        raise NotImplementedError("Plugins must implement this method!")


    #--------------------------------------------------------------------------
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


    #--------------------------------------------------------------------------
    def get_accepted_info(self):
        return None               # Most UI plugins will want all data objects.


    #--------------------------------------------------------------------------
    def recv_msg(self, message):
        """
        Callback method to receive control messages to be processed.

        :param message: incoming message to process
        :type message: Message
        """
        raise NotImplementedError("Plugins must implement this method!")


    #--------------------------------------------------------------------------
    def send_msg(self, message):
        """
        Plugins call this method to send messages back to GoLismero.

        .. warning::
           Do not override this method!
        """
        self.__observer_ref.send_msg(message)


    #--------------------------------------------------------------------------
    def _set_observer(self, observer):
        self.__observer_ref = observer


#------------------------------------------------------------------------------
class ImportPlugin (Plugin):
    """
    Import plugins collect previously found resources from other tools
    and store them in the audit database right before the audit starts.

    This is the base class for all Import plugins.
    """

    PLUGIN_TYPE = Plugin.PLUGIN_TYPE_IMPORT


    #--------------------------------------------------------------------------
    def is_supported(self, input_file):
        """
        Determine if this plugin supports the requested file format.

        Tipically, here is where Import plugins examine the file extension.

        :param input_file: Input file to parse.
        :type input_file: str

        :returns: True if this plugin supports the format, False otherwise.
        :rtype: bool
        """
        raise NotImplementedError("Plugins must implement this method!")


    #--------------------------------------------------------------------------
    def import_results(self, input_file):
        """
        Run plugin and import the results into the audit database.

        This is the entry point for Import plugins,
        where most of the logic resides.

        :param input_file: Input file to parse.
        :type input_file: str
        """
        raise NotImplementedError("Plugins must implement this method!")


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


    #--------------------------------------------------------------------------
    def is_supported(self, output_file):
        """
        Determine if this plugin supports the requested file format.

        Tipically, here is where Report plugins examine the file extension.

        :param output_file: Output file to generate.
        :type output_file: str

        :returns: True if this plugin supports the format, False otherwise.
        :rtype: bool
        """
        raise NotImplementedError("Plugins must implement this method!")


    #--------------------------------------------------------------------------
    def generate_report(self, output_file):
        """
        Run plugin and generate the report.

        This is the entry point for Report plugins,
        where most of the logic resides.

        :param output_file: Output file to generate.
        :type output_file: str
        """
        raise NotImplementedError("Plugins must implement this method!")
