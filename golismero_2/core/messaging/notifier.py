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
        # Call super class constructor
        super(Notifier, self).__init__()

        # Message notification pool for plugins.
        # (message_type, list(Plugin_instance))
        self._notification_pool = dict()
        # Add special type "all"
        self._notification_pool["all"] = list()

        # Total messages pendants
        self._waiting_messages = Semaphore(1)

        # Controle executio adding a stop condition
        self._continue = True

        # Finish all plugins?
        self._is_finished = False

        # Plugins are running
        self._is_plugins_runnging = False

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
<<<<<<< HEAD
        if isinstance(plugin, list):
            map(self.__add_plugin, plugin)
        else:
            self._add_plugin(plugin)


    #----------------------------------------------------------------------
    #
    # Methods to implement
    #
    #----------------------------------------------------------------------
    def _add_plugin(self, plugin):
        """
        Add a plugin to manage

        :param plugin: a TestPlugin type to manage
        :type plugin: TestPlugin
        """
        pass

    #----------------------------------------------------------------------
    def nofity(self, message):
        """
        Notify messages to the plugins

        :param message: A message to send to plugins
        :type message: Message
        """
        pass
    #----------------------------------------------------------------------
    def stop(self):
        """
        Send a stop signal to notifier
        """
        self._continue = False
        self._waiting_messages.release()
        self._is_finished = True


    #----------------------------------------------------------------------
    def run(self):
        """
        Start notifier process
        """
        # Run until not stop signal received
        while self._continue:
            # Dispatch messages:
            #
            # For each plugin, send messages in their buffer
            self._is_plugins_runnging = True
            for l_notificator in self._plugins_buffer_pool.values():
                l_plugin_instance = l_notificator[0]
                for l_msg in l_notificator[1]:
                    # Send message to plugin.
                    #
                    # Run plugin in running pool
                    #l_plugin_instance.recv_info(l_msg.message_info)
                    self.__runner.execute(l_plugin_instance, "recv_info", (l_msg.message_info,))

            self._is_plugins_runnging = False
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
        Retrun true if all plugins are finished. False otherwise.

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
class AuditNofitier(Notifier):
    """
    This class manage the pools of messages for -Testing- plugins, and notify them
    when a message is received.
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        # Call super class constructor
        super(AuditNofitier, self).__init__()


    #----------------------------------------------------------------------
    def _add_plugin(self, plugin):
=======
        map(self.add_plugin, plugin)


    #----------------------------------------------------------------------
    def add_plugin(self, plugin):
>>>>>>> d246c4c20dab744ef5b779e54446f25d6709dda7
        """
        Add a plugin to manage.

        :param plugin: a Plugin type to manage
        :type plugin: Plugin
        """
        if not isinstance(plugin, Plugin):
            raise TypeError("Expected Plugin, got %s instead" % type(plugin))

        # For testing plugins only
        if isinstance(plugin, TestingPlugin):
            # Create lists as necessary, dependens of type of messages accepted
            # by plugins
            m_message_types = set(plugin.get_accepted_info()) # delete duplicates

            #
            if m_message_types:
                for l_type in m_message_types:
                    #
                    # Check if notification list exits at the pool. If not create them
                    if not l_type in self._notification_pool.keys():
                        self._notification_pool[l_type] = list()

                    # Add plugin to notification list, by their type.
                    self._notification_pool[l_type].append(plugin)

                    # Add message buffer for the plugin
                    if not plugin.__class__ in self._plugins_buffer_pool.keys():
                        self._plugins_buffer_pool[plugin.__class__] = [plugin, list()]

    #----------------------------------------------------------------------
    def notify(self, message):
        """
        Notify messages to the plugins.

        :param message: A message to send to plugins
        :type message: Message
        """
        if isinstance(message, Message):
            m_plugins_to_notify = []

            # Plugin that expect all types of messages
            m_plugins_to_notify.extend(self._notification_pool["all"])

            # Plugins that expects this type of message
            if message.message_info.result_subtype in self._notification_pool.keys():
                m_plugins_to_notify.extend(self._notification_pool[message.message_info.result_subtype])

            # Remove duplicates
            m_plugins_to_notify = set(m_plugins_to_notify)

            # Notify message to buffer list of each plugin
            for l_plugin in m_plugins_to_notify:
                self._plugins_buffer_pool[l_plugin.__class__][1].append(message)

            # Release the dispath
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
<<<<<<< HEAD
    def __init__(self):
        """Constructor"""
        # Call super class constructor
        super(UINotifier, self).__init__()
=======
    def run(self):
        """
        Start notifier process.
        """
>>>>>>> d246c4c20dab744ef5b779e54446f25d6709dda7



    #----------------------------------------------------------------------
    def _add_plugin(self, plugin):
        """
        Add a plugin to manage

        :param plugin: a TestPlugin type to manage
        :type plugin: TestPlugin
        """

        # For testing plugins only
        if isinstance(plugin, UIPlugin):
            # Add plugin to notification pool
            self._notification_pool["all"].append(plugin)

            # Create buffer for plugin
            if not plugin.__class__ in self._plugins_buffer_pool.keys():
                self._plugins_buffer_pool[plugin.__class__] = [plugin, list()]

    #----------------------------------------------------------------------
    def nofity(self, message):
        """
        Notify messages to the plugins

<<<<<<< HEAD
        :param message: A message to send to plugins
        :type message: Message
=======
        :returns: bool -- True if finished. False otherwise.
>>>>>>> d246c4c20dab744ef5b779e54446f25d6709dda7
        """
        if isinstance(message, Message):
            m_plugins_to_notify = []

            # Plugin that expect all types of messages
            m_plugins_to_notify.extend(self._notification_pool["all"])

            # Remove duplicates
            m_plugins_to_notify = set(m_plugins_to_notify)

            # Notify message to buffer list of each plugin
            for l_plugin in m_plugins_to_notify:
                self._plugins_buffer_pool[l_plugin.__class__][1].append(message)

            # Release the dispath
            self._waiting_messages.release()










