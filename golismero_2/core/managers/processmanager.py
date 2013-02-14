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

from core.main.commonstructures import Singleton
from multiprocessing import Pool

# Serializable bootstrap function for subprocesses.
# This is requied for Windows support, since we don't have os.fork() there.
# See: http://docs.python.org/2/library/multiprocessing.html#windows
def bootstrap(module, clazz, func, *argv, **argd):
    cls = __import__(module, fromlist=[clazz])
    return getattr(cls(), func)(*argv, **argd)

#------------------------------------------------------------------------------
class ProcessManager(Singleton):
    """
    This class manages processes.

    To run a function you must do the following::

        # Definitions
        class A():
            def show(self, message):
                print "hello " + message

        # Main
        if __name__ == '__main__':
            a = A()
            p = ProcessManager()
            p.execute(__name__, 'A', 'show', ('world',))
    """

    #----------------------------------------------------------------------
    def __init__(self, max_processes = None, refresh_after_tasks = None):
        """Constructor.

        :param max_processes: maximum number of processes to create
        :type max_processes: int

        :param refresh_after_tasks: maximum number of function calls to make before refreshing a subprocess
        :type refresh_after_tasks: int
        """
        super(ProcessManager, self).__init__()
        self.__pool = Pool(max_processes, maxtasksperchild = refresh_after_tasks)

    #----------------------------------------------------------------------
    def execute(self, clazz, func, *argv, **argd):
        """
        Add a function to be executed, with its params, in a pooled process.

        :param module: module where the class is defined
        :type module: str

        :param clazz: class of the plugin to run, must be serializable
        :type clazz: str

        :param func: name of the method to execute, all extra arguments to this function will be passed to it
        :type func: str
        """
        self.__pool.apply_async(bootstrap, (clazz, func, argv, argd))

    #----------------------------------------------------------------------
    def start(self):
        """
        Start the process manager.
        """
        pass

    #----------------------------------------------------------------------
    def stop(self, wait = False):
        """
        Stop the process manager.

        :param wait: True to wait for the subprocesses to finish, False to kill them.
        :type wait: bool
        """
        if wait:
            self.__pool.close()
        else:
            self.__pool.terminate()
        self.__pool.join()
