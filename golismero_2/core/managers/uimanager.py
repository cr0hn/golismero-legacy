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

from .priscillapluginmanager import PriscillaPluginManager
from ..messaging.notifier import UINotifier
from ..messaging.message import Message
from ..main.commonstructures import GlobalParams


#------------------------------------------------------------------------------
class UIManager (object):
    """
    Dispatcher of messages for the UI plugins.
    """


    #----------------------------------------------------------------------
    def __init__(self, orchestrator, config):
        """
        Constructor.

        :param orchestrator: Orchestrator
        :type orchestrator: Orchestrator

        :param config: Configuration for audit
        :type config: GlobalParams
        """

        # Keep a reference to the orchestrator
        self.__orchestrator = orchestrator

        # Init and start notifier
        self.__notifier = UINotifier()

        # Load UI plugins
        m_plugins = PriscillaPluginManager().load_plugins(config.plugins, "ui")

        # Configure plugins to be it own the target of messages and add to notifier
        for p in m_plugins.itervalues():
            p._set_observer(self)
            self.__notifier.add_plugin(p)


    #----------------------------------------------------------------------
    def run(self):
        """
        Launch the UI.
        """
        message = Message(message_type = Message.MSG_TYPE_CONTROL,
                          message_code = Message.MSG_CONTROL_START_UI)
        self.__orchestrator.dispatch_msg(message)


    #----------------------------------------------------------------------
    def dispatch_msg(self, message):
        """
        Dispatch incoming messages to all UI plugins.

        :param message: The message to send.
        :type message: Message
        """
        if not isinstance(message, Message):
            raise TypeError("Expected Message, got %s instead" % type(message))

        # Filter out ACKs but send all other messages.
        if  message.message_type != Message.MSG_TYPE_CONTROL or \
            message.message_code != Message.MSG_CONTROL_ACK:
                self.__notifier.notify(message)


    #----------------------------------------------------------------------
    def send_info(self, information):
        """
        Send information from the plugins back to the Orchestrator.

        :param information: The information to send.
        :type information: Result
        """
        message = Message(message_type = Message.MSG_TYPE_INFO,
                          message_info = information)
        self.__orchestrator.dispatch_msg(message)


    #----------------------------------------------------------------------
    def stop(self):
        """
        Stop UI plugins
        """
        pass
