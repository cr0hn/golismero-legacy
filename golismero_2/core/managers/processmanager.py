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

__all__ = ["ProcessManager", "Context"]

from ..api.config import Config
from ..api.logger import Logger
from ..main.commonstructures import GlobalParams
from ..messaging.message import Message

from multiprocessing import Pool, Manager, Process
from imp import load_source
from traceback import format_exc, print_exc


#------------------------------------------------------------------------------

# Plugin class per-process cache. Used by the bootstrap function.
plugin_class_cache = dict()   # tuple(class, module) -> class object

# Serializable function to run plugins in subprocesses.
# This is required for Windows support, since we don't have os.fork() there.
# See: http://docs.python.org/2/library/multiprocessing.html#windows
def launcher(queue, max_process, refresh_after_tasks):

    # Instance the pool manager.
    pool = PluginPoolManager(max_process, refresh_after_tasks)

    # Start the pool manager.
    wait = True
    pool.start()
    try:

        # Consumer loop.
        while True:

            # Get the next plugin call to issue.
            item = queue.get()

            # Handle the message to quit.
            if item is True or item is False:
                wait = item
                return

            # Handle the message to call a plugin.
            pool.run_plugin(*item)

    finally:

        # Stop the pool manager.
        pool.stop(wait)

# Serializable bootstrap function to run plugins in subprocesses.
# This is required for Windows support, since we don't have os.fork() there.
# See: http://docs.python.org/2/library/multiprocessing.html#windows
def bootstrap(context, func, argv, argd):
##    import os          # XXX DEBUG
##    print os.getpid()  # XXX DEBUG
    verbose = 1
    try:
        try:
            try:
                # Get the verbosity
                verbose = context.audit_config.verbose

                # Set the logger verbosity
                Logger.set_level(verbose)

                # Configure the plugin
                Config()._set_context(context)

                # TODO: hook stdout and stderr to catch print statements

                # Create the OOP observer so the plugin can talk back
                observer = OOPObserver(context)

                # Try to get the plugin from the cache
                cache_key = (context.plugin_module, context.plugin_class)
                try:
                    cls = plugin_class_cache[cache_key]

                # If not in the cache, load the class
                except KeyError:

                    # Load the plugin module
                    mod = load_source(
                        "_plugin_tmp_" + context.plugin_class.replace(".", "_"),
                        context.plugin_module)

                    # Get the plugin class
                    cls = getattr(mod, context.plugin_class)

                    # Cache the plugin class
                    plugin_class_cache[cache_key] = cls

                # Instance the plugin
                instance = cls()

                # Set the OOP observer for the plugin
                instance._set_observer(observer)

                # Call the callback method
                retval = getattr(instance, func)(*argv, **argd)

                # If there's a return value, assume it's a list of results
                if retval is not None:
                    for result in retval:
                        try:
                            instance.send_info(result)
                        except Exception, e:
                            if verbose >= Logger.STANDARD:
                                if verbose >= Logger.MORE_VERBOSE:
                                    text = "%s\n%s" % (e.message, format_exc())
                                else:
                                    text = e.message
                                context.send_msg(message_type = Message.MSG_TYPE_CONTROL,
                                                 message_code = Message.MSG_CONTROL_ERROR,
                                                 message_info = text)

            # Tell the Orchestrator there's been an error
            except Exception, e:
                try:
                    if verbose >= Logger.STANDARD:
                        if verbose >= Logger.MORE_VERBOSE:
                            text = "%s\n%s" % (e.message, format_exc())
                        else:
                            text = e.message
                        context.send_msg(message_type = Message.MSG_TYPE_CONTROL,
                                         message_code = Message.MSG_CONTROL_ERROR,
                                         message_info = text)
                except Exception:
                    print_exc()

        # No matter what happens, send back an ACK
        finally:
            try:
                context.send_ack()
            except Exception:
                print_exc()

    # Tell the Orchestrator we need to stop
    except:

        # Send a message to the Orchestrator to stop
        context.send_msg(message_type = Message.MSG_TYPE_CONTROL,
                         message_code = Message.MSG_CONTROL_STOP,
                         message_info = False)


#------------------------------------------------------------------------------
class Context (object):
    """
    Serializable execution context for the plugins.
    """

    def __init__(self, msg_queue, plugin_info = None, audit_name = None, audit_config = None):
        """
        Serializable execution context for the plugins.

        :param msg_queue: Message queue where to send the responses.
        :type msg_queue: Queue

        :param plugin_info: Plugin information.
        :type plugin_info: PluginInfo

        :param audit_name: Name of the audit.
        :type audit_name: str

        :param audit_config: Name of the audit.
        :type audit_config: str
        """
        self.__plugin_info  = plugin_info
        self.__audit_name   = audit_name
        self.__audit_config = audit_config
        self.__msg_queue    = msg_queue

    @property
    def msg_queue(self):
        "str -- Message queue where to send the responses."
        return self.__msg_queue

    @property
    def plugin_info(self):
        "PluginInfo -- Plugin information."
        return self.__plugin_info

    @property
    def plugin_module(self):
        "str -- Module where the plugin is to be loaded from."
        return self.__plugin_info.plugin_module

    @property
    def plugin_class(self):
        "str -- Class name of the plugin."
        return self.__plugin_info.plugin_class

    @property
    def plugin_config(self):
        "dict -- Plugin configuration."
        return self.__plugin_info.plugin_config

    @property
    def audit_name(self):
        "str -- Name of the audit."
        return self.__audit_name

    @property
    def audit_config(self):
        "str -- Name of the audit."
        return self.__audit_config


    #----------------------------------------------------------------------
    def send_ack(self):
        """
        Send ACK messages from the plugins to the orchestrator.
        """
        self.send_msg(message_type = Message.MSG_TYPE_CONTROL,
                      message_code = Message.MSG_CONTROL_ACK)


    #----------------------------------------------------------------------
    def send_msg(self, message_type = Message.MSG_TYPE_INFO,
                       message_code = 0,
                       message_info = None):
        """
        Send messages from the plugins to the orchestrator.

        :param message_type: specifies the type of message.
        :type mesage_type: int -- specified in a constant of Message class.

        :param message_code: specifies the code of message.
        :type message_code: int -- specified in a constant of Message class.

        :param message_info: the payload of the message.
        :type message_info: object -- type must be resolved at run time.
        """
        message = Message(message_type = message_type,
                          message_code = message_code,
                          message_info = message_info,
                            audit_name = self.audit_name)
        self.send_raw_msg(message)


    #----------------------------------------------------------------------
    def send_raw_msg(self, message):
        """
        Send raw messages from the plugins to the orchestrator.

        :param message: Message to send
        :type message: Message
        """
        self.msg_queue.put_nowait(message)


    #----------------------------------------------------------------------
    def remote_call(self, rpc_code, *argv, **argd):
        """
        Make synchronous remote procedure calls on the orchestrator.

        :param rpc_code: RPC code
        :type rpc_code: int

        :returns: Depends on the call.
        """

        # Create the response queue.
        response_queue = Manager().Queue()

        # Send the RPC message.
        self.send_msg(message_type = Message.MSG_TYPE_RPC,
                      message_code = rpc_code,
                      message_info = (response_queue, argv, argd))

        # Get the response.
        return response_queue.get()


    #----------------------------------------------------------------------
    def async_remote_call(self, rpc_code, *argv, **argd):
        """
        Make asynchronous remote procedure calls on the orchestrator.

        :param rpc_code: RPC code
        :type rpc_code: int
        """

        # Send the RPC message.
        self.send_msg(message_type = Message.MSG_TYPE_RPC,
                      message_code = rpc_code,
                      message_info = (None, argv, argd))


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

    def send_info(self, result):
        """
        Send results from the plugins to the orchestrator.

        :param result: Results to send
        :type result: Result
        """
        self.send_msg(message_type = Message.MSG_TYPE_INFO,
                      message_info = result)

    def send_msg(self, message_type = Message.MSG_TYPE_INFO,
                       message_code = 0,
                       message_info = None):
        """
        Send messages from the plugins to the orchestrator.

        :param message_type: specifies the type of message.
        :type mesage_type: int -- specified in a constant of Message class.

        :param message_code: specifies the code of message.
        :type message_code: int -- specified in a constant of Message class.

        :param message_info: the payload of the message.
        :type message_info: object -- type must be resolved at run time.
        """
        self.__context.send_msg(message_type = message_type,
                                message_code = message_code,
                                message_info = message_info)

    def send_raw_msg(self, message):
        """
        Send raw messages from the plugins to the orchestrator.

        :param message: Message to send
        :type message: Message
        """
        self.__context.send_raw_msg(message)


#------------------------------------------------------------------------------
class PluginPoolManager (object):
    """
    Manages a pool of subprocesses to run plugins in them.
    """


    #----------------------------------------------------------------------
    def __init__(self, max_process, refresh_after_tasks):
        """Constructor.

        :param max_process: Maximum number of processes to create.
        :type max_process: int

        :param refresh_after_tasks: Maximum number of function calls to make before refreshing a subprocess.
        :type refresh_after_tasks: int
        """
        self.__max_processes       = max_process
        self.__refresh_after_tasks = refresh_after_tasks

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
        config = Config()
        old_context = config._get_context()
        try:
            return bootstrap(context, func, argv, argd)
        finally:
            config._set_context(old_context)


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
                self.__pool = Pool(
                    processes = self.__max_processes,
                    maxtasksperchild = self.__refresh_after_tasks)

            # Are we running the plugins in single process mode?
            else:

                # No process pool then!
                self.__pool = None


    #----------------------------------------------------------------------
    def stop(self, wait = True):
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

        # Clear the plugin instance cache
        plugin_class_cache.clear()


#------------------------------------------------------------------------------
class PluginLauncher (object):
    """
    Manages a pool of subprocesses to run plugins in them.
    """


    #----------------------------------------------------------------------
    def __init__(self, max_process, refresh_after_tasks):
        """Constructor.

        :param max_process: Maximum number of processes to create.
        :type max_process: int

        :param refresh_after_tasks: Maximum number of function calls to make before refreshing a subprocess.
        :type refresh_after_tasks: int
        """

        # Initialize the launcher process, but do not start it yet.
        self.__manager = Manager()
        self.__queue = self.__manager.Queue()
        self.__process = Process(target=launcher, args=(self.__queue, max_process, refresh_after_tasks))
        self.__alive = True


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

        # Raise an exception if the launcher had been stopped.
        if not self.__alive:
            raise RuntimeError("Plugin launcher was stopped")

        # Send the plugin run request to the launcher process.
        self.__queue.put_nowait( (context, func, argv, argd) )


    #----------------------------------------------------------------------
    def start(self):
        """
        Start the plugin launcher.
        """

        # Raise an exception if the launcher had been stopped.
        if not self.__alive:
            raise RuntimeError("Plugin launcher was stopped")

        # Start the launcher process.
        self.__process.start()


    #----------------------------------------------------------------------
    def stop(self, wait = True):
        """
        Stop the plugin launcher.

        :param wait: True to wait for the subprocesses to finish, False to kill them.
        :type wait: bool
        """

        # Raise an exception if the launcher was already stopped.
        if not self.__alive:
            raise RuntimeError("Plugin launcher was stopped")

        # Signal the launcher process to stop.
        self.__queue.put_nowait(wait)

        # Wait for the launcher process to stop.
        if wait:
            self.__process.join()
        else:
            self.__process.join(3)
            try:
                self.__process.terminate()
            except Exception:
                pass

        # Clean up.
        self.__alive   = False
        self.__process = None
        self.__queue   = None
        self.__manager = None


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
        self.__launcher = None

        # maximum number of processes to create
        self.__max_processes       = getattr(config, "max_process",         None)

        # maximum number of function calls to make before refreshing a subprocess
        self.__refresh_after_tasks = getattr(config, "refresh_after_tasks", None)


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

        # If we have a dispatcher, run the plugin asynchronously
        if self.__launcher is not None:
            self.__launcher.run_plugin(context, func, argv, argd)

        # Otherwise just call the plugin directly
        config = Config()
        old_context = config._get_context()
        try:
            return bootstrap(context, func, argv, argd)
        finally:
            config._set_context(old_context)


    #----------------------------------------------------------------------
    def start(self):
        """
        Start the process manager.
        """

        # If we already have a process pool, do nothing
        if self.__launcher is None:

            # Are we running the plugins in multiprocessing mode?
            if self.__max_processes is not None and self.__max_processes > 0:

                # Create the process pool
                self.__launcher = PluginLauncher(self.__max_processes,
                                                 self.__refresh_after_tasks)

                # Start it
                self.__launcher.start()

            # Are we running the plugins in single process mode?
            else:

                # No process pool then!
                self.__launcher = None


    #----------------------------------------------------------------------
    def stop(self, wait = True):
        """
        Stop the process manager.

        :param wait: True to wait for the subprocesses to finish, False to kill them.
        :type wait: bool
        """

        # If we have a process pool...
        if self.__launcher is not None:

            # Stop it.
            self.__launcher.stop(wait)

            # Clean up.
            self.__launcher = None
