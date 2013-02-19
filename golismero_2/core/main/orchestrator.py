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

from core.managers.auditmanager import AuditManager
from core.managers.messagemanager import MessageManager
from core.managers.priscillapluginmanager import PriscillaPluginManager
from core.managers.uimanager import UIManager
from core.managers.processmanager import ProcessManager, Context
from core.main.commonstructures import GlobalParams
from core.messaging.message import Message

from multiprocessing import Queue
from time import sleep



class Orchestrator (object):
    """
    Orchestrator is the core (or kernel) of GoLismero.
    """


    #----------------------------------------------------------------------
    def __init__(self, config):
        """
        Start the orchestrator.

        :param config: configuration of orchestrator.
        :type config: GlobalParams
        """

        # Configuration
        self.__config = config

        # Incoming message queue
        self.__queue = Queue()

        # Message manager
        self.__messageManager = MessageManager(self.__config)

        # API managers
        self.__init_api()

        # Load the plugins
        pluginManager = PriscillaPluginManager()
        pluginManager.find_plugins(self.__config.plugins_folder)
        pluginManager.load_plugins(self.__config.plugins)

        # Process manager
        self.__processManager = ProcessManager(self.__config)
        self.__processManager.start()

        # Audit manager
        self.__auditManager = AuditManager(self, self.__config)
        self.__messageManager.add_listener(self.__auditManager)

        # UI manager
        if config.run_mode == GlobalParams.RUN_MODE.standalone:
            self.__ui = UIManager(self, self.__config)
            self.__messageManager.add_listener(self.__ui)


    @property
    def processManager(self):
        return self.__processManager


    #----------------------------------------------------------------------
    def __init_api(self):
        """
        Init API managers.
        """
        from core.api.net.netmanager import NetManager


        # Configure networking
        NetManager.config(self.__config)


    #----------------------------------------------------------------------
    def add_audit(self, params):
        """
        Start a new audit.

        :param params: Audit settings
        :type params: GlobalParams
        """
        self.__auditManager.new_audit(params)


    #----------------------------------------------------------------------
    def dispatch_msg(self, message):
        """
        Process messages from audits or from the message queue, and send them
        forward to the plugins through the Message Manager when appropriate.

        :param message: incoming message
        :type message: Message
        """
        if not isinstance(message, Message):
            raise TypeError("Expected Message, got %s instead" % type(message))

        # Drop duplicated results from audits
        # XXX FIXME there should be a more elegant way to do this
        if  message.message_type == Message.MSG_TYPE_INFO:
            audit = self.__auditManager.get_audit(message.audit_name)
            if message.message_info in audit.database:
                return

        # Dispatch the message
        self.__messageManager.send_message(message)

        # If it's a quit message...
        if  message.message_type == Message.MSG_TYPE_CONTROL and \
            message.message_code == Message.MSG_CONTROL_STOP:

            # Stop the program execution
            raise KeyboardInterrupt()


    #----------------------------------------------------------------------
    def get_context(self, audit_name):
        """
        Prepare a Context object to pass to the plugins.
        """
        return Context(audit_name, self.__queue)


    #----------------------------------------------------------------------
    def msg_loop(self):
        """
        Message loop.
        """

        try:

            # Message loop.
            while True:

                # Wait for a message to arrive.
                message = self.__queue.get()
                if not isinstance(message, Message):
                    raise TypeError("Expected Message, got %s" % type(message))

                # Dispatch the message.
                self.dispatch_msg(message)

        finally:
            try:

                # Stop the UI
                self.__ui.stop()

            finally:

                # Stop the process manager
                self.__processManager.stop()


    #----------------------------------------------------------------------
    def start_ui(self):
        """Start UI"""

        # init UI Manager
        self.__ui.run()
