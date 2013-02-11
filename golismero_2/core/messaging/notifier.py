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

from core.api.plugins.plugin import TestingPlugin, Plugin
from core.messaging.message import Message
from threading import Thread
from time import sleep


class Notifier(Thread):
    """
    This class manage the pools of messages for each plugin, and notify them
    when a message is received.
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        # Call super class constructor
        super(Notifier, self).__init__()


        # Message notification pool for plugins.
        # (message_type, list(Plugin_instance))
        self.__notification_pool = dict()

        # Pool list for each plugin:
        #   Each plugin has they own message list, that act as a buffer. Message will
        #   add to it, and will be sent as plugin as needed.
        #   (plugin_class_name, [plugin_instance. list(messages)]
        self.__plugins_buffer_pool = dict()

        # Total messages pendants
        self.__non_dispached_msg = 0

        # Stop attemps: when no message in pool of any plugin, will be wail these number of times
        # before stop the process
        self.__stop_attemps = 5

        # Finish all plugins?
        self.__finished_plugins = False




    #----------------------------------------------------------------------
    def add_plugin(self, plugin):
        """
        Add a plugin or list of plugins

        :param plugin: a plugin or plugin list to add
        :type plugin: TestPlugin | list(TestPlugin)
        """
        if isinstance(plugin, list):
            map(self.__add_plugin, plugin)
        else:
            self.__add_plugin(plugin)


    #----------------------------------------------------------------------
    def __add_plugin(self, plugin):
        """
        Add a plugin to manage

        :param plugin: a TestPlugin type to manage
        :type plugin: TestPlugin
        """
        if not isinstance(plugin, Plugin):
            raise TypeError("Expected TestingPlugin, got %s instead" % type(plugin))

        # Create lists as necessary, dependens of type of messages accepted
        # by plugins
        m_message_types = set(plugin.get_accepted_info()) # delete duplicates
        if m_message_types:
            for l_type in m_message_types:
                #
                # Check if notification list exits at the pool
                if not l_type in self.__notification_pool.keys():
                    self.__notification_pool[l_type] = list()
                # Add plugin to notification list
                self.__notification_pool[l_type].append(plugin)

                # Add message buffer for the plugin
                if not plugin.__class__ in self.__plugins_buffer_pool.keys():
                    self.__plugins_buffer_pool[plugin.__class__] = [plugin, list()]


    #----------------------------------------------------------------------
    def nofity(self, message):
        """
        Notify messages to the plugins

        :param message: A message to send to plugins
        :type message: Message
        """
        if isinstance(message, Message):
            # Get pool of plugins to send this message
            if message.message_info.result_subtype in self.__notification_pool.keys():
                m_plugins_to_notify = self.__notification_pool[message.message_info.result_subtype]

                # Add as pendant msg as notify process listen to
                self.__non_dispached_msg += len(m_plugins_to_notify)

                # Add message to their buffer list
                for l_plugin in m_plugins_to_notify:
                    self.__plugins_buffer_pool[l_plugin.__class__][1].append(message)


    #----------------------------------------------------------------------
    def run(self):
        """
        Start notifier process
        """

        # Wait for plugins receive first message with target
        sleep(0.050)

        # Run until stop attemps are 0
        while self.__stop_attemps > 0:
            # Dispatch messages.
            while self.__non_dispached_msg > 0:
                for l_notificator in self.__plugins_buffer_pool.values():
                    l_plugin_instance = l_notificator[0]
                    for l_msg in l_notificator[1]:
                        # Send message to plugin
                        l_plugin_instance.recv_info(l_msg.message_info)
                        # When messsage is processed, remove it from non dispached list
                        self.__non_dispached_msg -= 1
                # Wait 250 ms
                sleep(0.250)

            # Decrease attemps
            self.__stop_attemps -= 1

        # Set finished to true
        self.__finished_plugins = True


    #----------------------------------------------------------------------
    def __get_is_finished(self):
        """
        Retrun true if all plugins are finished. False otherwise.

        :returns: bool -- True is finished. False otherwise.
        """
        return self.__finished_plugins

    is_finished = property(__get_is_finished)