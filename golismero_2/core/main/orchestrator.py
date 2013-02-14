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
from core.managers.reportmanager import ReportManager
from core.managers.resultmanager import ResultManager
from core.managers.uimanager import UIManager
from core.managers.reportmanager import ReportManager
from core.managers.processmanager import ProcessManager

from core.main.commonstructures import IReceiver, Singleton
from core.messaging.message import Message
from time import sleep



class Orchestrator(Singleton, IReceiver):
    """
    Orchestrator is the core or kernel.

    """
    #----------------------------------------------------------------------
    def __init__(self, config):
        """
        Constructor.

        :param config: configuration of orchestrator.
        :type config: GlobalParams
        """

        # Init configuration
        self.__config = config

        # Init process manager
        ProcessManager().start()

        # 1 - Set and configure the Audit manager
        self.__auditManager = AuditManager(self)

        # 2 - Create and configure UI
        self.__ui = UIManager(self.__config, self)

        # 3 - Message manager
        self.__messageManager = MessageManager()

        # 4 - Initiazliate store manager
        self.__result_manager = ResultManager()

        # 5 - Add managers to message pools
        self.__messageManager.add_multiple_listeners([self.__ui, self.__auditManager])


    #----------------------------------------------------------------------
    def add_audit(self, params):
        """
        Start a new audit.

        :param params: Audit settings
        :type params: GlobalParams
        """
        self.__auditManager.new_audit(params)


    #----------------------------------------------------------------------
    def recv_msg(self, message):
        """
        Receive messages from audits and external receivers.
        If it's a result, store the info and resend the messages.
        Otherwise just ignore the messages.

        :param message: a mesage to send
        :type message: Message
        """
        if isinstance(message, Message):
            # Check if not in store yet. Then store and resend it.
            if not self.__result_manager.contains(message.message_info):
                #  Store it
                self.__result_manager.add_result(message.message_info)

                # Send
                self.__messageManager.send_message(message)


    #----------------------------------------------------------------------
    def wait(self):
        """
        Wait for the end of all audits.
        """

        # Wait for audits
        while not self.__auditManager.is_finished:
            sleep(0.050)

        # Stop UI and wait it.
        self.__ui.stop()
        while not self.__ui.is_finished:
            sleep(0.020)

        # Stop process manager
        ProcessManager().stop()


    #--------------------------------------------------------------------------
    #
    # START METHODS
    #
    #--------------------------------------------------------------------------
    def start(self):
        """
        Configure and start execution, as of run_mode config.

        :param run_mode: Constant contains run_mode.
        :type run_mode: int
        """
        #
        # Configure messagen as for run mode
        #
        if GlobalParams.RUN_MODE.standalone is runMode:
            # Console mode
            self.__messageManager.add_listener(AuditManager())

        elif GlobalParams.RUN_MODE.cloudclient is runMode:
            pass

        elif GlobalParams.RUN_MODE.cloudserver is runMode:
            pass

        else:
            raise ValueError("Invalid run mode: %r" % runMode)


    #----------------------------------------------------------------------
    def start_ui(self):
        """Start UI"""

        # init UI Manager
        self.__ui.run()


    #----------------------------------------------------------------------
    def start_report(self):
        """Start report generation"""
        ReportManager(self.__result_manager.get_results()).generate_report()



