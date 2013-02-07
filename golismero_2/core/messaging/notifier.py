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

from core.api.plugins.plugin import TestingPlugin
from core.messaging.message import Message


class Notifier(object):
    """
    This class manage the pools of messages for each plugin, and notify them
    when a message is received.
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        # Message notification pool for plugins.
        self.__message_pool = dict()



    #----------------------------------------------------------------------
    def add_plugin(self, plugin):
        """
        Plugin to manage
        """
        if not isinstance(plugin, TestingPlugin):
            raise TypeError("Expected TestingPlugin, got %s instead" % type(auditParams))

        # Create lists as necessary, dependens of type of messages accepted
        # by plugins
        m_message_types = plugin.get_accepted_info()
        if m_message_types:
            for l_type in m_message_types:
                # Check if notification list exits
                if not l_type in self.__message_pool:
                    self.__message_pool[l_type] = list()

                # Add plugin to notification list
                self.__message_pool[l_type] = plugin

    #----------------------------------------------------------------------
    def nofity(self, message):
        """
        Notify messages to the plugins
        """
        if isinstance(message, Message):
            if message.message_info.result_subtype in self.__message_pool.keys():
                m_notifications = self.__message_pool[message.message_info.result_subtype]

                for l_plugin in m_notifications:
                    l_plugin.recv_info(message)


