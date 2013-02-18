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

from core.main.commonstructures import  GlobalParams
from core.messaging.message import Message
from multiprocessing import Pool, Queue


# Serializable bootstrap function to run plugins in subprocesses.
# This is required for Windows support, since we don't have os.fork() there.
# See: http://docs.python.org/2/library/multiprocessing.html#windows
def bootstrap(context, module, clazz, init_argv, init_argd, func, argv, argd):
    try:
        cls = __import__(module, fromlist=[clazz])
        instance = cls(*init_argv, **init_argd)
        if context is not None and hasattr(instance, "_set_observer"):
            instance._set_observer( OOPObserver(context) )
        return getattr(instance, func)(*argv, **argd)
    except:
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
    def execute(self, context, module, clazz, init_argv, init_argd, func, argv, argd):
        """
        Run a plugin in a pooled process.

        :param context: context for the bootstrap function
        :type context: Context

        :param module: module where the class is defined
        :type module: str

        :param clazz: class of the plugin to run, must be serializable
        :type clazz: str

        :param init_argv: positional arguments to the constructor
        :type init_argv: tuple

        :param init_argd: keyword arguments to the constructor
        :type init_argd: dict

        :param func: name of the method to execute, all extra arguments to this function will be passed to it
        :type func: str

        :param argv: positional arguments to the function call
        :type argv: tuple

        :param argd: keyword arguments to the function call
        :type argd: dict
        """

        # If we have a process pool, run the plugin asynchronously
        if self.__pool is not None:
            return self.__pool.apply_async(bootstrap,
                    (context,
                     module, clazz, init_argv, init_argd,
                     func, argv, argd))

        # Otherwise just call the plugin directly
        return bootstrap(context,
                         module, clazz, init_argv, init_argd,
                         func, argv, argd)


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
    Serializable execution context for the OOP Observer.
    """

    def __init__(self, audit_name, msg_queue):
        self.__audit_name = audit_name
        self.__msg_queue  = msg_queue

    @property
    def audit_name(self):
        return self.__audit_name

    @property
    def msg_queue(self):
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
        super(OOPObserver, self).__init__(self)
        self.__context = context

    def send_info(self, result):
        """
        Send results from the plugins to the orchestrator.

        :param result:
        """
        message = Message(message_info = result,
                          message_type = Message.MSG_TYPE_INFO,
                          audit_name   = self.__context.audit_name)
        self.__context.msg_queue.put_nowait(message)
