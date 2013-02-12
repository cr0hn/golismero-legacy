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

from core.plugins.priscillapluginmanager import PriscillaPluginManager
from core.messaging.notifier import Notifier
from core.messaging.message import Message
from core.messaging.interfaces import IReceiver
from core.main.commonstructures import Singleton, GlobalParams
from threading import Thread
from time import sleep

#------------------------------------------------------------------------------
class UIManager(Singleton, Thread, IReceiver):
    """
    This class manage the UI managers.
    """

    #----------------------------------------------------------------------
    def __vinit__(self):
        """Virtual contructor. Initialize common vars."""
        self.__receiver = None
        self.__notifier = None

    #----------------------------------------------------------------------
    def set_config(self, params, orchestrator):
        """
        Set the configuration for UI manager.

        :param params: global params for UI manager.
        :type params: GlobalParams
        """

        if not isinstance(params, GlobalParams):
            raise TypeError("Expected GlobalParams, got %s instead" % type(params))
        #if not isinstance(orchestrator, Orchestrator):
            #raise TypeError("Expected Orchestrator, got %s instead" % type(orchestrator))

        self.__params = params
        self.__receiver = orchestrator

    #----------------------------------------------------------------------
    def start(self):
        """Start UI specified by params."""

        if not self.__receiver or not self.__params:
            raise RuntimeError("Orchestrator not initialized")

        m_plugins = None

        # 1 - Get UI plugin, by params
        if self.__params.USER_INTERFACE is GlobalParams.USER_INTERFACE.console:
            # Add console UI plugins to nofitier
            m_plugins =  PriscillaPluginManager().get_all_plugins("ui")
        else:
            m_plugins =  PriscillaPluginManager().get_all_plugins("ui")

        # 2 - Configure plugins to be it own the target of messages
        for p in m_plugins.values():
            p.set_observer(self.__receiver)

        # 3 - Creates and start the notifier
        self.__notifier = Notifier()
        self.__notifier.start()

        # 4 - Asociate plugins to nofitier
        for l_plugin in m_plugins.values():
            self.__notifier.add_plugin(l_plugin)

    #----------------------------------------------------------------------
    def stop_ui(self):
        """Stop or break UI."""
        if self.__notifier.is_finished:
            #self.shutdown()
            sleep(0.005)

    #----------------------------------------------------------------------
    def recv_msg(self, message):
        """
        Send message info to UI plugins.

        :param message: The message unencapsulate to get info.
        :type message: Message
        """
        if isinstance(message, Message):
            self.__notifier.notify(message)