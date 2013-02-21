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

__all__ = ["ProcessManager", "OOPObserver"]

from core.api.config import Config
from core.main.commonstructures import GlobalParams
from core.messaging.message import Message
from multiprocessing import Pool, Queue
from imp import load_source


# Serializable bootstrap function to run plugins in subprocesses.
# This is required for Windows support, since we don't have os.fork() there.
# See: http://docs.python.org/2/library/multiprocessing.html#windows
def bootstrap(context, func, argv, argd):
    observer = None
    try:
        try:
            # Create the OOP observer so the plugin can talk back
            observer = OOPObserver(context)

            # From now on we can talk back to the Orchestrator :)

            # TODO: hook stdout and stderr to catch print statements

            # Configure the plugin
            Config()._set_config(audit_name, audit_config)

            # Load the plugin module
            mod = load_source("_plugin_tmp_" + context.plugin_class.lower(),
                              context.plugin_module)

            # Get the plugin class
            cls = getattr(mod, context.plugin_class)

            # Instance the plugin
            instance = cls()

            # Set the OOP observer for the plugin
            instance._set_observer(observer)

            # Call the callback method
            getattr(instance, func)(*argv, **argd)

        # No matter what happens, send back an ACK
        finally:
            observer.send_ack()

    # Tell the Orchestrator there's been an error
    except:
        if observer is not None:
            import traceback
            message = Message(message_type = Message.MSG_TYPE_CONTROL,
                              message_code = Message.MSG_CONTROL_ERROR,
                              message_info = traceback.format_exc())
            observer.send_msg(message)
        else:

            # We can't tell the Orchestrator about this error! :(

            # XXX DEBUG
            import traceback
            traceback.print_exc()


#------------------------------------------------------------------------------
class ProcessManager (object):
    """
    Manages a pool of subprocesses to run plugins in them.
    """


    #----------------------------------------------------------------------
    def __init__(self, config):
        """Constructor.

        :param config: Configuration object
        :type config: GlobalParams
        """

        # maximum number of processes to create
        self.__max_processes       = getattr(config, "max_processes",       None)

        # maximum number of function calls to make before refreshing a subprocess
        self.__refresh_after_tasks = getattr(config, "refresh_after_tasks", None)

        # no process pool for now...
        self.__pool = None


    #----------------------------------------------------------------------
    def run_plugin(self, context, func, argv, argd):
        """
        Run a plugin in a pooled process.

        :param context: context for the OOP plugin execution
        :type context: Context

        :param func: name of the method to execute
        :type func: str

        :param argv: positional arguments to the function call
        :type argv: tuple

        :param argd: keyword arguments to the function call
        :type argd: dict
        """

        # If we have a process pool, run the plugin asynchronously
        if self.__pool is not None:
            return self.__pool.apply_async(bootstrap,
                    (context, func, argv, argd))

        # Otherwise just call the plugin directly
        return bootstrap(context, func, argv, argd)


    #----------------------------------------------------------------------
    def start(self):
        """
        Start the process manager.
        """

        # If we already have a process pool, do nothing
        if self.__pool is None:

            # Are we running the plugins in multiprocessing mode?
            if self.__max_processes is not None and self.__max_processes > 0:

                # Create the process pool
                self.__pool = Pool(self.__max_processes,
                                   maxtasksperchild = self.__refresh_after_tasks)

            # Are we running the plugins in single process mode?
            else:

                # No process pool then!
                self.__pool = None


    #----------------------------------------------------------------------
    def stop(self, wait = False):
        """
        Stop the process manager.

        :param wait: True to wait for the subprocesses to finish, False to kill them.
        :type wait: bool
        """

        # If we have a process pool...
        if self.__pool is not None:

            # Either wait patiently, or kill the damn things!
            if wait:
                self.__pool.close()
            else:
                self.__pool.terminate()
            self.__pool.join()

            # Destroy the process pool
            self.__pool = None


#------------------------------------------------------------------------------
class Context (object):
    """
    Serializable execution context for the plugins.
    """

    def __init__(self, plugin_module, plugin_class, audit_name, audit_config, msg_queue):
        """
        Serializable execution context for the plugins.

        :param plugin_module: Module where the plugin is to be loaded from.
        :type plugin_module: str

        :param plugin_class: Class name of the plugin.
        :type plugin_class: str

        :param audit_name: Name of the audit.
        :type audit_name: str

        :param audit_config: Name of the audit.
        :type audit_config: str

        :param msg_queue: Message queue where to send the responses.
        :type msg_queue: Queue
        """
        self.__plugin_module = plugin_module
        self.__plugin_class  = plugin_class
        self.__audit_name    = audit_name
        self.__audit_config  = audit_config
        self.__msg_queue     = msg_queue

    @property
    def plugin_module(self):
        "str -- Module where the plugin is to be loaded from."
        return self.__plugin_module

    @property
    def plugin_class(self):
        "str -- Class name of the plugin."
        return self.__plugin_class

    @property
    def audit_name(self):
        "str -- Name of the audit."
        return self.__audit_name

    @property
    def msg_queue(self):
        "str -- Message queue where to send the responses."
        return self.__msg_queue


#------------------------------------------------------------------------------
class OOPObserver (object):
    """
    Observer that proxies messages across different processes.
    """

    def __init__(self, context):
        """
        :param context: Execution context for the OOP observer.
        :type context: Context
        """
        super(OOPObserver, self).__init__()
        self.__context = context

    def send_ack(self):
        """
        Send ACK messages from the plugins to the orchestrator.
        """
        message = Message(message_type = Message.MSG_TYPE_CONTROL,
                          message_code = Message.MSG_CONTROL_ACK,
                          audit_name   = self.__context.audit_name)
        self.send_msg(message)

    def send_info(self, result):
        """
        Send results from the plugins to the orchestrator.

        :param result: Results to send
        :type result: Result
        """
        message = Message(message_info = result,
                          message_type = Message.MSG_TYPE_INFO,
                          audit_name   = self.__context.audit_name)
        self.send_msg(message)

    def send_msg(self, message):
        """
        Send control messages from the plugins to the orchestrator.

        :param message: Message to send
        :type message: Message
        """
        self.__context.msg_queue.put_nowait(message)
