#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
API for parallel execution within GoLismero plugins.
"""

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: http://golismero-project.com
Golismero project mail: golismero.project<@>gmail.com


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


__all__ = ["parallel"]

import threading
from threading import Semaphore


#----------------------------------------------------------------------
def parallel(func, data, pool_size=4):
    """
    Run a function in parallel.

    :param func: A function or any other executable object.
    :type func: callable

    :param values: List of parameters
    :type values: list(object)

    :return: a list with re results.
    :rtype: list
    """
    # Create the pool
    m_pool   = GolismeroPool(pool_size)
    # Add the task an get the returned value
    m_return = m_pool.add(func, data)

    # Wait for ending and stop the pool
    m_pool.join()
    m_pool.stop()

    return [m_return.get() for x in xrange(len(m_return)) ]


#-------------------------------------------------------------------------
class GolismeroThread(threading.Thread):
    """
    Worker for threads
    """


    #----------------------------------------------------------------------
    def __init__(self):

        self.__func            = None
        self.__data            = None
        self.__queue           = None
        self._callback         = None

        # Set stop condition
        self.__continue        = True

        # Sem to run processes
        self.__sem_available = Semaphore(0)

        super(GolismeroThread,self).__init__()


    #----------------------------------------------------------------------
    def run(self):
        """
        Thread run function
        """
        while True:
            self.__sem_available.acquire()

            if not self.__continue:
                break

            # Run process
            x = None
            if self.__data:
                x = self.__func(self.__data)
            else:
                x = self.__func()

            # Store the results
            if x:
                self.__queue.put(x)

            # Run the callback
            if self._callback:
                self._callback()


    #----------------------------------------------------------------------
    def stop(self):
        """
        Marks the threads to stop
        """
        self.__continue = False
        self.__sem_available.release()


    #----------------------------------------------------------------------
    def terminate(self):
        """
        Force the thread to terminate.
        """
        raise NotImplemented()


    #----------------------------------------------------------------------
    def add(self, func, data, queue):
        """
        Add a function and a data to process.

        :param func: function to run.
        :type func: executable function.

        :param data: an object pass as parameter to the function.
        :type data: object.

        :param queue: a queue where will be put the results of the execution of the functions.
        :type queue: GolismeroQueue
        """

        if func is None:
            raise ValueError("func can't be empty")
        if queue is None:
            raise ValueError("queue can't be empty")

        self.__func  = func
        self.__data  = data
        self.__queue = queue

        # Signal to continue the execution
        self.__sem_available.release()


#------------------------------------------------------------------------------
class GolismeroQueue(object):
    """
    A thread-safe queue implementation. Unlike that in the standard
    multiprocessing module, this one doesn't require any pickling.
    """


    #----------------------------------------------------------------------
    def __init__(self):

        # We'll exploit the fact that in CPython the list operations are
        # atomic. However in other VMs we'll need to use syncronization
        # objects here instead.
        self.__data = []


    #----------------------------------------------------------------------
    def put(self, val):
        """
        Put value at the end of the queue.

        :param val: Value to pass.
        :type val: *
        """
        self.__data.append(val)


    #----------------------------------------------------------------------
    def get(self):
        """
        :return: Extract the value at the beginning of the queue.
        :rtype: *
        """
        if self.__data:
            return self.__data.pop(0)
        else:
            return None


    #----------------------------------------------------------------------
    def __len__(self):
        return len(self.__data)


#-------------------------------------------------------------------------
class GolismeroPool(threading.Thread):
    """
    Thread pool.
    """


    #----------------------------------------------------------------------
    def __init__(self, pool_size = 5):
        """
        :param pool_size: Maximum amount of concurrent threads allowed by this pool.
        :type pool_size: int
        """
        if not isinstance(pool_size, int):
            raise TypeError("Expected int, got %s instead" % type(pool_size))
        if pool_size < 1:
            raise ValueError("pool_size must be great than 0.")

        # Synchronization
        self.__sem_max_threads             = Semaphore(pool_size)
        self.__sem_available_data          = Semaphore(0)
        self.__sem_join                    = Semaphore(0)

        # Number of tasks
        self.__count_task                  = 0

        # Stop execution?
        self.__continue                    = True

        # Join wanted?
        self.__join                        = False

        # Thread pool. Format: (function, values, return_queue)
        self.__data_pool                   = set()

        # Executors busy
        self.__task_pool_busy              = set()

        # Executors available
        self.__task_pool_available         = set()
        self.__task_pool_available_add     = self.__task_pool_available.add

        # Setup the pool
        for l_p in xrange(pool_size):
            l_thread             = GolismeroThread()
            l_thread._callback   = self._release_sem
            l_thread.start()

            self.__task_pool_available_add(l_thread)

        # Superclass constructor
        super(GolismeroPool,self).__init__()

        # Start the pool
        self.start()


    #----------------------------------------------------------------------
    def run(self):
        """
        Execute a function or list of functions in daemon mode (non-blocking).

        You can add any function or functions and their values to be processed.
        Execution will be done in background.
        """
        while True:

            # Blocks until input data is available
            self.__sem_available_data.acquire()

            # If stop is requested, break out of the loop
            if not self.__continue:
                break

            # Get task to run
            func, tmp_vals, queue = self.__data_pool.pop()

            # Convert iterators and the like into a real list
            m_vals = list(tmp_vals)

            # Get the length of the input data
            self.__count_task += len(m_vals)

            # For each input value...
            for l_val in m_vals:

                # Get a slot
                self.__sem_max_threads.acquire()

                # Get executor
                f = self.__task_pool_available.pop()

                # Mask the executor as busy
                self.__task_pool_busy.add(f)

                # Add the task
                f.add(func, l_val, queue)


    #----------------------------------------------------------------------
    def _release_sem(self):

        # Switch wait tasks <-> avail tasks
        self.__task_pool_available.add(self.__task_pool_busy.pop())

        # Global threads pool
        self.__sem_max_threads.release()

        # Unlock concrete pool
        self.__count_task -= 1

        if self.__count_task <= 0 and self.__join:
            self.__sem_join.release()
            self.__join = False


    #----------------------------------------------------------------------
    def join(self):
        """
        Block until all tasks are completed.
        """
        self.__join = True
        self.__sem_join.acquire()


    #----------------------------------------------------------------------
    def add(self, func, values):
        """
        Add a function to the pool for execution.

        :param func: a GolismeroThread object.
        :type func: GolismeroThread.

        :param values: list of values to process.
        :type values: object or list(object)

        :return: an GolismeroQueue where will be puted the results of the threads.
        :rtype: GolismeroQueue
        """
        if func:
            m_return_value = GolismeroQueue()

            m_data = None
            if values:
                m_data = iter(values)

            # Add task to the pool
            self.__data_pool.add((func, m_data, m_return_value))

            # Signal to inform the avalibility of new data
            self.__sem_available_data.release()

            # Return the pointer to the values
            return m_return_value
        else:
            raise ValueError("func can't be empty")


    #----------------------------------------------------------------------
    def stop(self):
        """
        Stop all threads in the pool.
        """

        # Signal to all threads to stop
        self.__continue = False
        map(GolismeroThread.stop, self.__task_pool_available)

        # Unlock
        self.__sem_available_data.release()


    #----------------------------------------------------------------------
    def terminate(self):
        """
        Force to exit killing all threads.
        """
        raise NotImplementedError()


#----------------------------------------------------------------------
if __name__ == "__main__":
    #
    # This code is used for testing
    #
    #p = GolismeroPool(5)
    l = [1,2,4,5,9,10,29,1919]
    f = lambda x: x+1
    r = parallel(f, l)

    print r
