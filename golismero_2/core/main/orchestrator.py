#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com
  Mario Vilas | mvilas@gmail.com

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

from .console import Console
from ..api.config import Config
from ..api.logger import Logger
from ..common import OrchestratorConfig, AuditConfig
from ..database.cachedb import PersistentNetworkCache, VolatileNetworkCache
from ..managers.auditmanager import AuditManager
from ..managers.priscillapluginmanager import PriscillaPluginManager
from ..managers.uimanager import UIManager
from ..managers.rpcmanager import RPCManager, implementor
from ..managers.processmanager import ProcessManager, Context
from ..messaging.codes import MessageType, MessageCode, MessagePriority
from ..messaging.message import Message

from os import getpid
from time import sleep
from traceback import format_exc, print_exc
from signal import signal, SIGINT, SIG_DFL
from multiprocessing import Manager

__all__ = ["Orchestrator"]


class Orchestrator (object):
    """
    Orchestrator is the core (or kernel) of GoLismero.
    """

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()


    #----------------------------------------------------------------------
    def __init__(self, config):
        """
        Start the orchestrator.

        :param config: configuration of orchestrator.
        :type config: OrchestratorConfig
        """

        # Configuration
        self.__config = config

        # Set the color configuration
        Console.use_colors = config.colorize

        # Check the run mode
        if config.run_mode == config.RUN_MODE.master:
            raise NotImplementedError("Master mode not yet implemented!")
        if config.run_mode == config.RUN_MODE.slave:
            raise NotImplementedError("Slave mode not yet implemented!")
        if config.run_mode != config.RUN_MODE.standalone:
            raise ValueError("Invalid run mode: %r" % options.run_mode)

        # Incoming message queue
        if getattr(config, "max_process", 0) <= 0:
            from Queue import Queue
            self.__queue = Queue(maxsize = 0)
        else:
            self.__queue_manager = Manager()
            self.__queue = self.__queue_manager.Queue()

        # Set the Orchestrator context
        self.__context = Context( orchestrator_pid = getpid(),
                                         msg_queue = self.__queue,
                                      audit_config = self.__config )
        Config._set_context(self.__context)

        # Within the Orchestrator process, keep a static reference to it
        Context._orchestrator = self

        # Load the plugins
        self.__pluginManager = PriscillaPluginManager()
        success, failure = self.__pluginManager.find_plugins(self.__config.plugins_folder)
        if not success:
            raise RuntimeError("Failed to find any plugins!")
        self.__pluginManager.load_plugins(self.__config.enabled_plugins,
                                          self.__config.disabled_plugins,
                                          category = "all")

        # Network cache
        if  self.__config.use_cache_db or (
            self.__config.use_cache_db is None and
            self.__config.run_mode != OrchestratorConfig.RUN_MODE.standalone):
                self.__cache = PersistentNetworkCache()
        else:
                self.__cache = VolatileNetworkCache()

        # RPC manager
        self.__rpcManager = RPCManager(self)

        # Process manager
        self.__processManager = ProcessManager(self, self.__config)
        self.__processManager.start()

        # Audit manager
        self.__auditManager = AuditManager(self, self.__config)

        # UI manager
        if config.run_mode == OrchestratorConfig.RUN_MODE.standalone:
            self.__ui = UIManager(self, self.__config)
        else:
            self.__ui = None

        # Signal handler to catch Ctrl-C
        self.__old_signal_action = signal(SIGINT, self.__signal_handler)

        # Log the plugins that failed to load
        Logger.log_more_verbose("Found %d plugins" % len(success))
        if failure:
            Logger.log_error("Failed to load %d plugins" % len(failure))
            for plugin_name in failure:
                Logger.log_error_verbose("\t%s" % plugin_name)


    #----------------------------------------------------------------------
    # Manager getters (mostly used by RPC implementors)

    @property
    def pluginManager(self):
        return self.__pluginManager

    @property
    def cacheManager(self):
        return self.__cache

    @property
    def rpcManager(self):
        return self.__rpcManager

    @property
    def processManager(self):
        return self.__processManager

    @property
    def auditManager(self):
        return self.__auditManager

    @property
    def uiManager(self):
        return self.__ui


    #----------------------------------------------------------------------
    # RPC implementors for the database API.

    #MSG_RPC_DATA_ADD          = 110
    #MSG_RPC_DATA_REMOVE       = 111
    #MSG_RPC_DATA_GET          = 112
    #MSG_RPC_DATA_GET_KEYS     = 113
    #MSG_RPC_DATA_GET_ALL_KEYS = 114
    #MSG_RPC_DATA_COUNT        = 115
    #MSG_RPC_DATA_CHECK        = 116

    @implementor(MessageCode.MSG_RPC_DATA_ADD)
    def rpc_datadb_add(self, audit_name, *argv, **argd):
        return self.auditManager.get_audit(audit_name).database.add(*argv, **argd)

    @implementor(MessageCode.MSG_RPC_DATA_REMOVE)
    def rpc_datadb_remove(self, audit_name, *argv, **argd):
        return self.auditManager.get_audit(audit_name).database.remove(*argv, **argd)

    @implementor(MessageCode.MSG_RPC_DATA_GET)
    def rpc_datadb_get(self, audit_name, *argv, **argd):
        return self.auditManager.get_audit(audit_name).database.get(*argv, **argd)

    @implementor(MessageCode.MSG_RPC_DATA_KEYS)
    def rpc_datadb_keys(self, audit_name, *argv, **argd):
        return self.auditManager.get_audit(audit_name).database.keys(*argv, **argd)

    @implementor(MessageCode.MSG_RPC_DATA_COUNT)
    def rpc_datadb_count(self, audit_name, *argv, **argd):
        return self.auditManager.get_audit(audit_name).database.count(*argv, **argd)

    @implementor(MessageCode.MSG_RPC_DATA_CHECK)
    def rpc_datadb_check(self, audit_name, identity):
        return self.auditManager.get_audit(audit_name).database.has_key(identity)


    #----------------------------------------------------------------------
    def __signal_handler(self, signum, frame):
        """
        Signal handler to catch Control-C interrupts.
        """

        try:

            # Tell the user the message has been sent.
            Console.display("User cancel requested, stopping all audits...")

            # Send a stop message to the Orchestrator.
            message = Message(message_type = MessageType.MSG_TYPE_CONTROL,
                              message_code = MessageCode.MSG_CONTROL_STOP,
                              message_info = False,
                                  priority = MessagePriority.MSG_PRIORITY_HIGH)
            try:
                self.__queue.put_nowait(message)
            except Exception:
                exit(1)

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
        :type params: AuditConfig
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

            # If it's an RPC message...
            if message.message_type == MessageType.MSG_TYPE_RPC:

                # Execute the call.
                self.__rpcManager.execute_rpc(message.audit_name,
                                              message.message_code,
                                              * message.message_info)

                # The method now must return True because the message was sent.
                return True

            # If it's a control or info message, dispatch it to the audits.
            if self.__auditManager.dispatch_msg(message):

                # If it wasn't dropped, send it to the UI plugins.
                if self.__ui is not None:
                    self.__ui.dispatch_msg(message)

                # The method now must return True because the message was sent.
                return True

            # The method now must return False because the message was dropped.
            return False

        finally:

            # If it's a quit message...
            if  message.message_type == MessageType.MSG_TYPE_CONTROL and \
                message.message_code == MessageCode.MSG_CONTROL_STOP:

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
        return Context(getpid(), self.__queue, info, audit_name, audit_config)


    #----------------------------------------------------------------------
    def run(self, *audits):
        """
        Message loop.
        """
        try:

            # Start the UI.
            if self.__ui is not None:
                self.__ui.start()

            # If we have initial audits, start them.
            for params in audits:
                self.add_audit(params)

            # Message loop.
            while True:
                try:

                    # In standalone mode, if all audits have finished we have to stop.
                    if  self.__config.run_mode == OrchestratorConfig.RUN_MODE.standalone and \
                        not self.__auditManager.has_audits():
                            m = Message(message_type = MessageType.MSG_TYPE_CONTROL,
                                        message_code = MessageCode.MSG_CONTROL_STOP,
                                        message_info = True)  # True for finished, False for user cancel
                            self.dispatch_msg(m)

                    # Wait for a message to arrive.
                    try:
                        message = self.__queue.get()
                    except Exception:
                        # If this fails, kill the Orchestrator.
                        exit(1)
                    if not isinstance(message, Message):
                        raise TypeError("Expected Message, got %s" % type(message))

                    # Dispatch the message.
                    self.dispatch_msg(message)

                # If an exception is raised during message processing,
                # just log the exception and continue.
                except Exception:
                    Logger.log_error("Error processing message!\n%s" % format_exc())

        finally:

            # Stop the UI.
            try:
                if self.__ui is not None:
                    self.__ui.stop()
            except Exception:
                print_exc()


    #----------------------------------------------------------------------
    def close(self):
        """
        Release all resources held by the Orchestrator.
        """

        # Stop the process manager.
        try:
            self.processManager.stop()
        except:
            pass

        # Stop the audit manager.
        try:
            self.auditManager.close()
        except:
            pass

        # Compact and close the cache database.
        try:
            self.cacheManager.compact()
        except:
            pass
        try:
            self.cacheManager.close()
        except:
            pass
