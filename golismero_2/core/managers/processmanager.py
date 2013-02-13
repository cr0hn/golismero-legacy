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
from multiprocessing import Pool, Process, Value
from threading import Thread, Lock, Semaphore
from time import sleep

#semaphore_input_work = Semaphore(0)
semaphore_input_work = Semaphore(0)
semaphore_process = Semaphore(0)

#------------------------------------------------------------------------------
class ProcessManager(Thread, Singleton):
    """
    This class manages processes.

    To run a function you must do the following:

    # Definitions
    class A():
       def show(self, message):
          print "hello " + message

    # Main
    a = A()
    p = ProcessManager()
    p.execute(A, 'show', ('world',))

    """

    #----------------------------------------------------------------------
    def __init__(self, max_process = 2):
        """Constructor.

        :param max_process: maximun number of processes to create
        :type max_process: int
        """
        # For singleton pattern
        if self._is_instanced:
            return

        super(ProcessManager, self).__init__()

        # Create the pool of processors
        self.__exec_pool = list(CustomProcess(x, self.call_back) for x in xrange(max_process))
        # List with the availability process. Fill the list with id of process
        self.__availability_workers = list(x for x in xrange(max_process))

        # Procces to wait to be executed
        self.__wait_pool = list()

        # Mutex for waiting pool
        self.__mutex_waiting_process_pool = Lock()
        # Mutex for available workers
        self.__mutex_available_worker = Lock()

        # Semaphores:
        # 1 - Control for work inputs
        #semaphore_input_work = Semaphore(0)
        # 2 - Control for process availability
        #semaphore_process = Semaphore(max_process)

        # Start process
        for p in self.__exec_pool:
            p.start()

        # For controle stop of thread
        self.__stop = False


    #----------------------------------------------------------------------
    def run(self):
        """Execute pooled processes."""
        while not self.__stop:

            # Wait calls
            if len(self.__wait_pool) < 1:
                semaphore_input_work.acquire()

            # extract the process to run
            self.__mutex_waiting_process_pool.acquire()
            e = self.__wait_pool.pop()
            self.__mutex_waiting_process_pool.release()

            # looking for an available process
            if not len(self.__availability_workers):
                semaphore_process.acquire()

            # Get a worker
            self.__mutex_available_worker.acquire()
            m_worker = self.__availability_workers.pop()
            self.__mutex_available_worker.release()

            # Run process
            self.__exec_pool[m_worker].execute(e[0], e[1], e[2])

    #----------------------------------------------------------------------
    def execute(self, obj, func, func_params):
        """
        Add a function to be executed, with its params, in a pooled process.

        :param obj: object that contain method to execute.
        :type obj: object

        :param func: function to execute
        :type func: function

        :param func_params: parameters of function. Tupple, as: (param1, param2,)
        :type func_params: tupple
        """

        # Add the process
        self.__mutex_waiting_process_pool.acquire()
        self.__wait_pool.append([obj, func, func_params])
        self.__mutex_waiting_process_pool.release()

        # Notify for new message
        semaphore_input_work.release()

    def call_back(self, process_id):
        """Notifier when a process has finished running a function"""
        # Update the state of process, identified by 'process_id' to "available"

        self.__mutex_available_worker.acquire()
        self.__availability_workers.append(process_id)
        self.__mutex_available_worker.release()

        # Notify for new process availabe
        semaphore_process.release()

    #----------------------------------------------------------------------
    def stop(self):
        """
        Stop process manager.
        """
        for i in self.__exec_pool:
            i.stop()

        # Mark thread to stop
        self.__stop = True



#------------------------------------------------------------------------------
class CustomProcess(Process):
    """
    This class executes a function with its params.
    """

    __stop = Value("i", 0) # With value for shared memory between processes

    #----------------------------------------------------------------------
    def __init__(self, process_id, call_back):
        """Constructor."""
        super(CustomProcess, self).__init__()

        self.__id = process_id
        self.__call_back = call_back

    #----------------------------------------------------------------------
    def stop(self):
        """Stop the process."""
        CustomProcess.__stop.value = 1


    #----------------------------------------------------------------------
    def run(self):
        """Run and wait for process."""
        while not CustomProcess.__stop.value:
            sleep(0.05)

    #----------------------------------------------------------------------
    def execute(self, obj, func, args):
        """
        Execute a function, with its params, in a pooled process.

        :param obj: object that contain method to execute.
        :type obj: object

        :param func: function to execute
        :type func: function

        :param func_params: parameters of function. Tuple, as: (param1, param2,)
        :type func_params: tuple
        """
        getattr(obj, func)(args[0])

        # callback
        self.__call_back(self.__id)