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

from core.messaging.interfaces import IReceiver
from core.main.commonstructures import GlobalParams
from core.messaging.messagemanager import MessageManager
from core.main.audit import AuditManager
from core.main.commonstructures import Singleton
from core.results.resultmanager import ResultManager
from core.messaging.message import Message
from time import sleep
from core.main.uimanager import UIManager
from multiprocessing import Process

class Orchestrator(IReceiver, Singleton):
    """Orchestrator is the core or kernel."""


    #----------------------------------------------------------------------
    def __vinit__(self):
        """Initialize self. MANDATORY"""

        # Set and configure the Audit manager
        self.__auditManager = AuditManager()
        self.__auditManager.set_orchestrator(self)

        # Message manager
        self.__messageManager = MessageManager()

        # Initiazliate store manager
        self.__store_manager = ResultManager()

        # Create UI, add to message managers, and start it
        self.__ui = UIManager()

    #----------------------------------------------------------------------
    def set_config(self, config):
        """
        Set orchestator configuration

        :param config: configuration for orchestator
        :type config: GlobalParams
        """
        if not isinstance(config, GlobalParams):
            raise TypeError("Expected GlobalParams, got %s instead" % type(config))

        # init UI Manager
        self.__ui.config(config, self)
        self.__ui.start()
        self.__messageManager.add_listener(self.__ui)


    #----------------------------------------------------------------------
    def add_audit(self, params):
        """
        Start a new audit

        :param params: Audit settings
        :type params: GlobalParams
        """
        self.__auditManager.new_audit(params)


    #----------------------------------------------------------------------
    def recv_msg(self, message):
        """
        Receive messages from audits and external receivers. Store de info, if
        is a result, and resend.
        """
        if isinstance(message, Message):
            # If message contain a result type
            if message.message_info.result_subtype is Message.MSG_TYPE_INFO:
                # Check if not in store yet. Then store and resend it
                if not self.__store_manager.contains(message.message_info):
                    #  Store it
                    self.__store_manager.add_result(message.message_info)
                    # Resend the message
                    self.__messageManager.send_message(message)

    #----------------------------------------------------------------------
    def wait(self):
        """
        Wait for the end of all audits.
        """
        while self.__auditManager.is_finished is False:
            sleep(0.250)

        # Stop UI
        self.__ui.stop_ui()

    #----------------------------------------------------------------------
    def start_ui(self, params):
        """Start UI"""
        pass


    #----------------------------------------------------------------------
    def __set_run_mode(self, run_mode):
        """Set and configure execution, as of run_mode config.

        :param run_mode: Constant contains run_mode.
        :type run_mode: int
        """
        # Configure messagen as for run mode
        if GlobalParams.RUN_MODE.standalone is runMode:
            self.__messageManager.add_listener(AuditManager())
        elif GlobalParams.RUN_MODE.cloudclient is runMode:
            pass
        elif GlobalParams.RUN_MODE.cloudserver is runMode:
            pass
        else:
            raise ValueError("Invalid run mode: %r" % runMode)

