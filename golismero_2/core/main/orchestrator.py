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

from .commonstructures import GlobalParams
from .console import Console
from ..api.config import Config
from ..api.logger import Logger
from ..managers.auditmanager import AuditManager
from ..managers.messagemanager import MessageManager
from ..managers.priscillapluginmanager import PriscillaPluginManager
from ..managers.uimanager import UIManager
from ..managers.reportmanager import ReportManager
from ..managers.processmanager import ProcessManager, Context
from ..messaging.message import Message

from time import sleep
from traceback import format_exc
from signal import signal, SIGINT, SIG_DFL

import Queue
import multiprocessing

__all__ = ["Orchestrator"]


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
        if getattr(config, "max_processes", 1) == 1:
            self.__queue = Queue.PriorityQueue(maxsize = 0)
        else:
            # TODO: priority multiprocessing queue!
            self.__queue = multiprocessing.Queue()

        # Orchestrator context
        self.__context = Context(   msg_queue = self.__queue,
                                 audit_config = self.__config )
        Config()._set_context(self.__context)

        # Message manager
        self.__messageManager = MessageManager(self.__config)

        # Load the plugins
        self.__pluginManager = PriscillaPluginManager()
        success, failure = self.__pluginManager.find_plugins(self.__config.plugins_folder)
        Logger.log_more_verbose("Found %d plugins" % len(success))
        if failure:
            Logger.log_error("Failed to load %d plugins" % len(failure))
            if Logger.check_level(Logger.VERBOSE):
                for plugin_name in failure:
                    Logger.log_error_verbose("\t%s" % plugin_name)
        self.__pluginManager.load_plugins(self.__config.plugins)

        # Process manager
        self.__processManager = ProcessManager(self.__config)
        self.__processManager.start()

        # Audit manager
        self.__auditManager = AuditManager(self, self.__config)

        # UI manager
        if config.run_mode == GlobalParams.RUN_MODE.standalone:
            self.__ui = UIManager(self, self.__config)
            self.__messageManager.add_listener(self.__ui)

        # Load report manager
        self.__report_manager = ReportManager()

        # Signal handler to catch Ctrl-C
        self.__old_signal_action = signal(SIGINT, self.__signal_handler)


    @property
    def processManager(self):
        return self.__processManager


    #----------------------------------------------------------------------
    def __signal_handler(self, signum, frame):
        """
        Signal handler to catch Control-C interrupts.
        """

        try:

            # Send a stop message to the Orchestrator.
            message = Message(message_type = Message.MSG_TYPE_CONTROL,
                              message_code = Message.MSG_CONTROL_STOP,
                              message_info = False,
                                  priority = Message.MSG_PRIORITY_HIGH)
            self.__queue.put_nowait(message)

            # Tell the user the message has been sent.
            Console.display("User cancel requested, stopping all audits...")

        finally:

            # Only do this once, the next time raise KeyboardInterrupt.
            try:
                action, self.__old_signal_action = self.__old_signal_action, SIG_DFL
            except AttributeError:
                action = SIG_DFL
            signal(SIGINT, action)


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

        :returns: bool - True if the message was sent, False if it was dropped
        """
        if not isinstance(message, Message):
            raise TypeError("Expected Message, got %s instead" % type(message))

        try:

            # Dispatch the message to the audits.
            if self.__auditManager.dispatch_msg(message):

                # If it wasn't dropped, send it to the rest of the plugins.
                self.__messageManager.send_message(message)

                # The method now must return True because the message was sent.
                return True

            # The method now must return False because the message was dropped.
            return False

        finally:

            # If it's a quit message...
            if  message.message_type == Message.MSG_TYPE_CONTROL and \
                message.message_code == Message.MSG_CONTROL_STOP:

                # Stop the program execution
                if message.message_info:
                    exit(0)                   # Planned shutdown
                else:
                    raise KeyboardInterrupt() # User cancel


    #----------------------------------------------------------------------
    def get_context(self, audit_name, plugin):
        """
        Prepare a Context object to pass to the plugins.

        :param audit_name: Name of the audit.
        :type audit_name: str

        :param plugin: Plugin instance.
        :type plugin: Plugin

        :returns: Context -- OOP plugin execution context
        """

        # FIXME:
        # The only reason this method is here is because we need self.__queue.
        # Otherwise, by design it should belong to the ProcessManager.

        # Get the plugin information
        info = self.__pluginManager.get_plugin_info_from_instance(plugin)[1]

        # Get the audit configuration
        audit_config = self.__auditManager.get_audit(audit_name).params

        # Return the context instance
        return Context(self.__queue, info, audit_name, audit_config)


    #----------------------------------------------------------------------
    def msg_loop(self):
        """
        Message loop.
        """

        try:

            # Message loop.
            while True:
                try:

                    # In standalone mode, if all audits have finished we have to stop.
                    if  self.__config.run_mode == GlobalParams.RUN_MODE.standalone and \
                        not self.__auditManager.has_audits():
                            m = Message(message_type = Message.MSG_TYPE_CONTROL,
                                        message_code = Message.MSG_CONTROL_STOP,
                                        message_info = True)  # True for finished, False for user cancel
                            self.dispatch_msg(m)

                    # Wait for a message to arrive.
                    message = self.__queue.get()
                    if not isinstance(message, Message):
                        raise TypeError("Expected Message, got %s" % type(message))

                    # Dispatch the message.
                    self.dispatch_msg(message)

                # If an exception is raised during message processing,
                # just log the exception and continue.
                except Exception:
                    Logger.log_error("Error processing message!\n%s" % format_exc())

        finally:
            try:

                # Stop the UI.
                self.__ui.stop()

            finally:

                # Stop the process manager.
                self.__processManager.stop()


    #----------------------------------------------------------------------
    def start_ui(self):
        """Start UI"""

        # init UI Manager
        self.__ui.run()

    #----------------------------------------------------------------------
    def generate_reports(self, results):
        """Run report plugins"""
        self.__report_manager.generate_reports(self.__config, results)
