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

from core.api.plugins.plugin import TestingPlugin, UIPlugin, Plugin
from core.messaging.message import Message
from threading import Thread, Semaphore
from core.main.commonstructures import Interface
from time import sleep
from core.managers.processmanager import ProcessManager
from collections import defaultdict

class Notifier(Thread, Interface):
    """
    This is an abstract class for manage the pools of messages, and notify them
    when a message is received.
    """

    #----------------------------------------------------------------------
    #
    # Abstract methods
    #
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor."""

        # Call superclass constructor
        super(Notifier, self).__init__()

        # Message notification pool for plugins.
        # (message_type, list(Plugin_instance))
        self._notification_pool = defaultdict(list)

        # Add special type "all"
        self._notification_pool["all"] = list()

        # Total pending messages
        self._waiting_messages = Semaphore(1)

        # Control execution by adding a stop condition
        self._continue = True

        # Finish all plugins?
        self._is_finished = False

        # Plugins are running
        self._are_plugins_running = False

        # Pool list for each plugin:
        #   Each plugin has they own message list, that act as a buffer. Message will
        #   add to it, and will be sent as plugin as needed.
        #   (plugin_class_name, [plugin_instance. list(messages)]
        self._plugins_buffer_pool = dict()

        # Running pool
        self.__runner = ProcessManager()


    #----------------------------------------------------------------------
    def add_multiple_plugins(self, plugin_list):
        """
        Add a list of plugins.

        :param plugin: list of plugins to add
        :type plugin: list(Plugin)
        """
        map(self.add_plugin, plugin)


    #----------------------------------------------------------------------
    #
    # Methods to implement
    #
    #----------------------------------------------------------------------
    def add_plugin(self, plugin):
        """
        Add a plugin to manage.

        :param plugin: a TestPlugin type to manage
        :type plugin: TestPlugin
        """
        pass

    #----------------------------------------------------------------------
    def notify(self, message):
        """
        Notify messages to the plugins.

        :param message: A message to send to plugins
        :type message: Message
        """
        pass

    #----------------------------------------------------------------------
    def stop(self):
        """
        Send a stop signal to notifier.
        """
        self._continue = False
        self._waiting_messages.release()
        self._is_finished = True


    #----------------------------------------------------------------------
    def run(self):
        """
        Start notifier process.
        """

        # Run until not stop signal received
        while self._continue:

            # Dispatch messages:
            #

            # For each plugin, send messages in their buffer
            self._are_plugins_running = True
            for l_plugin_instance, l_msg_list in self._plugins_buffer_pool.itervalues():
                for l_msg in l_msg_list:

                    # Send message to plugin.
                    #

                    # Run plugin in running pool
                    #l_plugin_instance.recv_info(l_msg.message_info)
                    clazz = l_plugin_instance.__class__.__name__
                    module = l_plugin_instance.__class__.__module__
                    self.__runner.execute(module, clazz, "recv_info", (l_msg.message_info,))

            self._are_plugins_running = False
            self._waiting_messages.acquire()

        # Set finished to true
        self._is_finished = True


    #----------------------------------------------------------------------
    #
    # Properties
    #
    #----------------------------------------------------------------------
    def _get_is_finished(self):
        """
        Return true if all plugins are finished. False otherwise.

        :returns: bool -- True is finished. False otherwise.
        """
        return self._is_finished

    is_finished = property(_get_is_finished)

    #----------------------------------------------------------------------
    def _get_plugins_running(self):
        """Are any plugin running?"""
        return self._plugins_running
    is_plugins_running = property(_get_plugins_running)


#------------------------------------------------------------------------------
#
# Notificator for Audit manager
#
#------------------------------------------------------------------------------
class AuditNotifier(Notifier):
    """
    This class manage the pools of messages for -Testing- plugins, and notify them
    when a message is received.
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        # Call superclass constructor
        super(AuditNotifier, self).__init__()


    #----------------------------------------------------------------------
    def add_plugin(self, plugin):
        """
        Add a plugin to manage.

        :param plugin: a TestingPlugin to manage
        :type plugin: TestingPlugin
        """
        if not isinstance(plugin, TestingPlugin):
            raise TypeError("Expected TestingPlugin, got %s instead" % type(plugin))

        # For testing plugins only
        if isinstance(plugin, TestingPlugin):

            # Create lists as necessary, dependens of type of messages accepted
            # by plugins
            m_message_types = set(plugin.get_accepted_info()) # delete duplicates

            if not m_message_types:
                raise ValueError("Testing plugins must accept info!")

            for l_type in m_message_types:

                # Add plugin to notification list, by their type.
                self._notification_pool[l_type].append(plugin)

                # Add message buffer for the plugin
                if not plugin.__class__ in self._plugins_buffer_pool:
                    self._plugins_buffer_pool[plugin.__class__] = [plugin, list()]

    #----------------------------------------------------------------------
    def notify(self, message):
        """
        Notify messages to the plugins.

        :param message: A message to send to plugins
        :type message: Message
        """
        if isinstance(message, Message):
            m_plugins_to_notify = set()

            # Plugins that expect all types of messages
            m_plugins_to_notify.update(self._notification_pool["all"])

            # Plugins that expect this type of messages
            if message.message_info.result_subtype in self._notification_pool:
                m_plugins_to_notify.update(self._notification_pool[message.message_info.result_subtype])

            # Notify message to buffer list of each plugin
            for l_plugin in m_plugins_to_notify:
                self._plugins_buffer_pool[l_plugin.__class__][1].append(message)

            # Release the dispatch
            self._waiting_messages.release()



#------------------------------------------------------------------------------
#
# Notificator for User Interface manager
#
#------------------------------------------------------------------------------
class UINotifier(Notifier):
    """
    This class manage the pools of messages for -UI- plugins, and notify them
    when a message is received.
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        # Call superclass constructor
        super(UINotifier, self).__init__()


    #----------------------------------------------------------------------
    def add_plugin(self, plugin):
        """
        Add a plugin to manage

        :param plugin: a UIPlugin type to manage
        :type plugin: UIPlugin
        """

        # For testing plugins only
        if isinstance(plugin, UIPlugin):

            # Add plugin to notification pool
            self._notification_pool["all"].append(plugin)

            # Create buffer for plugin
            if not plugin.__class__ in self._plugins_buffer_pool:
                self._plugins_buffer_pool[plugin.__class__] = [plugin, list()]

    #----------------------------------------------------------------------
    def notify(self, message):
        """
        Notify messages to the plugins.

        :param message: A message to send to plugins
        :type message: Message
        """
        if isinstance(message, Message):

            # Notify message to buffer list of each plugin
            for l_plugin in self._notification_pool["all"]:
                self._plugins_buffer_pool[l_plugin.__class__][1].append(message)

            # Release the dispatch
            self._waiting_messages.release()


