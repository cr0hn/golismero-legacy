#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

__all__ = ["AuditNotifier", "UINotifier"]

from ..api.config import Config
from ..api.data import Data
##from ..api.logger import Logger
from ..api.plugin import Plugin
from .message import Message
from .codes import MessageType

from collections import defaultdict
##from traceback import format_exc
from warnings import warn


class Notifier (object):
    """
    Abstract class for message dispatchers.
    """


    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor."""

        # Call the superclass constructor.
        super(Notifier, self).__init__()

        # Info message notification list for plugins
        # that receive all information types.
        # list(str)
        self._notification_info_all = []

        # Info message notification mapping for plugins.
        # dict(info_type -> list(str))
        self._notification_info_map = defaultdict(list)

        # Control message notification mapping for plugins.
        # list(Plugin)
        self._notification_msg_list = []

        # Map of plugin names to plugin instances.
        # dict(str -> Plugin)
        self._map_name_to_plugin = {}


    #----------------------------------------------------------------------
    def add_multiple_plugins(self, plugins):
        """
        Add multiple plugins.

        :param plugins: Map of plugin names to plugin instances.
        :type plugins: dict(str -> Plugin)
        """
        for name, plugin in plugins.iteritems():
            self.add_plugin(name, plugin)


    #----------------------------------------------------------------------
    def add_plugin(self, name, plugin):
        """
        Add a plugin.

        :param name: The plugin name.
        :type name: str

        :param plugin: The plugin instance.
        :type plugin: Plugin
        """
        if not isinstance(plugin, Plugin):
            raise TypeError("Expected Plugin, got %s instead" % type(plugin))

        # Add the plugin to the names map.
        self._map_name_to_plugin[name] = plugin

        # Get the info types accepted by this plugin.
        m_message_types = plugin.get_accepted_info()
        m_message_types = self.__filter_accepted_info(m_message_types)

        # Special value 'None' means all information types.
        if m_message_types is None:
            self._notification_info_all.append(name)

        # Otherwise, it's a set of data subtype constants.
        else:

            # Register the plugin for each accepted type.
            for l_type in m_message_types:
                self._notification_info_map[l_type].append(name)

        # UI and Global plugins can receive control messages.
        if plugin.PLUGIN_TYPE in (Plugin.PLUGIN_TYPE_UI, Plugin.PLUGIN_TYPE_UI):
            self._notification_msg_list.append(plugin)


    #----------------------------------------------------------------------
    def __filter_accepted_info(self, accepted_info):
        """
        Process the return value from Plugin.get_accepted_info().

        :param accepted_info: Return value from Plugin.get_accepted_info().
        :type accepted_info: list(class | int) | None

        :returns: Set of data subtype constants.
        :rtype: set(int)
        """
        if accepted_info is not None:
            filtered_info = set()
            for item in accepted_info:
                if item is None:
                    filtered_info = None
                    break
                if type(item) not in (int, long):
                    if item.data_type == Data.TYPE_INFORMATION:
                        item = item.information_type
                    elif item.data_type == Data.TYPE_RESOURCE:
                        item = item.resource_type
                    elif item.data_type == Data.TYPE_VULNERABILITY:
                        item = item.vulnerability_type
                filtered_info.add(item)
            return filtered_info
        return None


    #----------------------------------------------------------------------
    def notify(self, message):
        """
        Dispatch messages to the plugins.

        :param message: A message to send to plugins
        :type message: Message
        """
        if not isinstance(message, Message):
            raise TypeError("Expected Message, got %s instead" % type(message))

        # Keep count of how many messages are sent.
        count = 0

        try:

            # Info messages are sent to the send_info() method.
            if message.message_type == MessageType.MSG_TYPE_DATA:
                audit_name = message.audit_name
                for data in message.message_info:

                    # Get the set of plugins to notify.
                    m_plugins_to_notify = self.get_plugins_to_notify(data)

                    # Dispatch message info to each plugin.
                    for plugin_name in m_plugins_to_notify:
                        plugin = self._map_name_to_plugin[plugin_name]
                        self.dispatch_info(plugin, audit_name, data)
                        count += 1

            # Control messages are sent to the send_msg() method.
            else:
                for plugin in self._notification_msg_list:
                    self.dispatch_msg(plugin, message)
                    count += 1

        # On error log the traceback.
        except Exception:
            ##Logger.log_error("Error sending message to plugins: %s" % format_exc())
            raise

        # Return the count of messages sent.
        return count


    #----------------------------------------------------------------------
    def get_plugins_to_notify(self, data):
        """
        Determine which plugins should receive this data object.

        :param data: Data object
        :type data: Data

        :returns: set(str) -- Set of plugin names.
        """

        m_plugins_to_notify = set()

        # Plugins that expect all types of info.
        m_plugins_to_notify.update(self._notification_info_all)

        # Plugins that expect this type of info.
        # TODO: should vulnerability types be processed like trees?
        m_type = None
        data_type = data.data_type
        if data_type == Data.TYPE_INFORMATION:
            m_type = data.information_type
        elif data_type == Data.TYPE_RESOURCE:
            m_type = data.resource_type
        elif data_type == Data.TYPE_VULNERABILITY:
            m_type = data.vulnerability_type
        else:
            warn("Data type not handled by notifier: %r" % data_type)
        if m_type in self._notification_info_map:
            m_plugins_to_notify.update(self._notification_info_map[m_type])
        ##else:  # XXX DEBUG
        ##    warn("Data type not handled by any plugins: %r" % data_type)

        return m_plugins_to_notify


    #----------------------------------------------------------------------
    def dispatch_info(self, plugin, audit_name, message_info):
        """
        Send information to the plugins.

        :param plugin: Target plugin
        :type plugin: Plugin

        :param audit_name: Audit name.
        :type audit_name: str

        :param message_info: Information to send to plugins
        :type message_info: Information
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def dispatch_msg(self, plugin, message):
        """
        Send messages to the plugins.

        :param plugin: Target plugin
        :type plugin: Plugin

        :param message: Message to send to plugins
        :type message: Message
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


#------------------------------------------------------------------------------
#
# Notifier for Audit manager
#
#------------------------------------------------------------------------------
class AuditNotifier(Notifier):
    """
    Audit message dispatcher. Sends messages to plugins.
    """


    #----------------------------------------------------------------------
    def __init__(self, audit):
        """
        Constructor.

        :param audit: Audit
        :type audit: Audit
        """
        super(AuditNotifier, self).__init__()
        self.__audit = audit
        self.__processing = defaultdict(set)


    #----------------------------------------------------------------------

    @property
    def audit(self):
        return self.__audit

    @property
    def orchestrator(self):
        return self.__audit.orchestrator

    @property
    def pluginManager(self):
        return self.__audit.orchestrator.pluginManager

    @property
    def current_stage(self):
        return self.__audit.current_stage

    @property
    def database(self):
        return self.__audit.database


    #----------------------------------------------------------------------
    def acknowledge(self, message):
        """
        Got an ACK for a message sent from this audit to the plugins.

        :param message: The message with the ACK.
        :type message: Message
        """

        # Get the identity and the plugin name.
        identity = message.message_info
        plugin_name = message.plugin_name

        # Only ACKs for data messages carry the identity.
        if identity:

            # Only ACKs for plugin messages carry the plugin name.
            if plugin_name:

                # Add the plugin to the already processed set.
                self.database.mark_plugin_finished(identity, plugin_name)

                # Remove the plugin from the currently processing data map.
                try:
                    self.__processing[identity].remove(plugin_name)
                except KeyError:
                    msg = "Got an unexpected ACK for data ID %s from plugin %s"
                    warn(msg % (identity, plugin_name))

            # If the stage was finished, mark it so.
            if self.__has_finished_stage(identity):
                self.database.mark_stage_finished(identity, self.current_stage)


    #----------------------------------------------------------------------
    def __has_finished_stage(self, identity):

        # XXX FIXME this is very inefficient!
        # this may be fixed by using just the data type
        # instead of the whole data object

        # Get the data object.
        data = self.database.get_data(identity)

        # Get the candidate plugins.
        pending_plugins = self.get_candidate_plugins(data)

        # If there are no plugins pending execution, we finished the stage.
        return not pending_plugins


    #----------------------------------------------------------------------
    def get_candidate_plugins(self, data):
        """
        Get the set of names of plugins that may handle this data object
        at the current execution stage.

        This ignores the plugin-to-plugin dependencies.

        :param data: Data object to find candidate plugins for.
        :type data: Data

        :returns: set(str) -- Set of candidate plugin names.
        """

        # Get the whole set of plugins that can handle this data.
        next_plugins = super(AuditNotifier, self).get_plugins_to_notify(data)

        # Filter out plugins that already received this data.
        past_plugins = self.database.get_past_plugins(data.identity)
        next_plugins.difference_update(past_plugins)

        # Filter out plugins that don't belong to the current stage.
        stage_plugins = self.pluginManager.stages[self.current_stage]
        next_plugins.intersection_update(stage_plugins)

        # Return them.
        return next_plugins


    #----------------------------------------------------------------------
    def is_runnable_stage(self, datalist, stage):
        """
        Determine if the given stage has any plugins that can handle the
        pending data.

        :param datalist: List of pending data.
        :type datalist: list(Data)

        :param stage: Current stage.
        :type stage: int

        :returns: bool
        """

        # Early exit if the list of data objects is empty.
        if not datalist:
            return False

        # Make a copy of the set of plugin names for this stage.
        available = set( self.pluginManager.stages[stage] )

        # Early exit if the stage is empty.
        if not available:
            return False

        # For each data object...
        for data in datalist:

            # If we have plugins in this stage that can handle this data,
            # then we can run this stage.
            candidates = self.get_candidate_plugins(data)
            if candidates.intersection(available):
                return True

        # If we reached this point that means we don't have any plugins
        # that can handle any of the data, so we skip the stage.
        return False


    #----------------------------------------------------------------------
    def get_plugins_to_notify(self, data):

        # Get the candidate plugins.
        next_plugins = self.get_candidate_plugins(data)

        # NOTE: the order of the following to filters is important!

        # Filter out plugins not belonging to the current batch.
        next_plugins = self.pluginManager.next_concurrent_plugins(next_plugins)

        # Filter out the currently running plugins.
        next_plugins.difference_update(self.__processing[data.identity])

        # Return the remanining plugins, if any.
        return next_plugins


    #----------------------------------------------------------------------
    def __run_plugin(self, plugin, method, payload):
        """
        Send messages or information to the plugins.

        :param plugin: Target plugin
        :type plugin: Plugin

        :param method: Callback method name
        :type method: str

        :param payload: Message or information to send to plugins
        :type payload: Message or data

        :raises RuntimeError: The plugin doesn't support the method.
        """

        # If the plugin doesn't support the callback method, drop the message
        if not hasattr(plugin, method):
            msg = "Tried to run plugin %r but it has no method %r"
            raise RuntimeError(msg % (plugin, method))

        # Get the Audit and Orchestrator instances
        audit        = self.__audit
        orchestrator = audit.orchestrator

        # Prepare the context for the OOP observer
        context = orchestrator.build_plugin_context(audit.name, plugin)

        # Add the plugin to the currently processing data map.
        if method == "recv_info":
            self.__processing[payload.identity].add(context.plugin_name)

        # Run the callback in a pooled process
        orchestrator.processManager.run_plugin(
            context, method, (payload,), {})


    #----------------------------------------------------------------------
    def dispatch_info(self, plugin, audit_name, message_info):
        """
        Send information to the plugins.

        :param plugin: Target plugin
        :type plugin: Plugin

        :param audit_name: Audit name.
        :type audit_name: str

        :param message_info: Information to send to plugins
        :type message_info: Information
        """

        # Validate the audit name.
        if audit_name is not None and audit_name != self.__audit.name:
            raise ValueError("Wrong audit! %r != %r" % (audit_name, self.__audit.name))

        # Run the plugin.
        self.__run_plugin(plugin, "recv_info", message_info)


    #----------------------------------------------------------------------
    def dispatch_msg(self, plugin, message):
        """
        Send messages to the plugins.

        :param plugin: Target plugin
        :type plugin: Plugin

        :param message: Message to send to plugins
        :type message: Message
        """
        self.__run_plugin(plugin, "recv_msg", message)


    #----------------------------------------------------------------------
    def start_report(self, plugin, output_file):
        """
        Start an audit report.

        :param plugin: Target plugin
        :type plugin: Plugin
        """
        self.__run_plugin(plugin, "generate_report", output_file)


#------------------------------------------------------------------------------
#
# Notifier for User Interface manager
#
#------------------------------------------------------------------------------
class UINotifier(Notifier):
    """
    Dispatcher of messages for UI plugins.
    """


    #----------------------------------------------------------------------
    def __init__(self, orchestrator):
        """
        Constructor.

        :param orchestrator: Orchestrator
        :type orchestrator: Orchestrator
        """
        super(UINotifier, self).__init__()
        self.__orchestrator = orchestrator


    #----------------------------------------------------------------------
    def dispatch_info(self, plugin, audit_name, message_info):
        """
        Send information to the plugins.

        :param plugin: Target plugin
        :type plugin: Plugin

        :param audit_name: Audit name.
        :type audit_name: str

        :param message_info: Information to send to plugins
        :type message_info: Information
        """
        self.__run_plugin(plugin, audit_name, "recv_info", message_info)


    #----------------------------------------------------------------------
    def dispatch_msg(self, plugin, message):
        """
        Send messages to the plugins.

        :param plugin: Target plugin
        :type plugin: Plugin

        :param message: Message to send to plugins
        :type message: Message
        """
        self.__run_plugin(plugin, message.audit_name, "recv_msg", message)


    #----------------------------------------------------------------------
    def __run_plugin(self, plugin, audit_name, method, payload):
        """
        Send messages or information to the plugins.

        :param plugin: Target plugin
        :type plugin: Plugin

        :param method: Callback method name
        :type method: str

        :param payload: Message or information to send to plugins
        :type payload: Message or data
        """

        # If the plugin doesn't support the callback method, drop the message.
        # XXX FIXME: maybe we want to raise an exception here instead.
        if not hasattr(plugin, method):
            return

        # Prepare the plugin execution context.
        if audit_name is not None:
            try:
                audit = self.__orchestrator.auditManager.get_audit(audit_name)
            except KeyError:
                audit = None
            if audit:
                context = self.__orchestrator.build_plugin_context(audit_name, plugin)
            else:
                context = Config._context
                warn("Received a message from a finished audit! %s" % payload,
                     RuntimeWarning)
        else:
            context = Config._context

        # Run the callback directly in our process.
        # XXX this allows UI plugins to have state, do we really want this?
        try:
            old_context = Config._context
            try:
                Config._context = context
                getattr(plugin, method)(payload)
            finally:
                Config._context = old_context

        # Log exceptions thrown by the plugins.
        except Exception:
            raise
            ##msg = "Plugin %s raised an exception:\n%s"
            ##msg = msg % (plugin.__class__.__name__, format_exc())
            ##Logger.log_error(msg)
