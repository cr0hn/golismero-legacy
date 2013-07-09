#!/usr/bin/python
# -*- coding: utf-8 -*-


__doc__ = """
This file contains functions and methods to make tasks
parallel easily.
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


import threading
from threading import Semaphore

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
        """"""
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
        :type data: object
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
    A queue implementation that don't need picked anything.
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.__data        = []



    #----------------------------------------------------------------------
    def put(self, val):
        """
        Put value of passed param in the pool list.
        """
        if val:
            if isinstance(val, list):
                self.__data.extend(val)
            else:
                self.__data.append(val)
        else:
            raise ValueError("Value can't be empty")



    #----------------------------------------------------------------------
    def get(self):
        """
        :return: the first value of the input list.
        """
        if self.__data:
            return self.__data.pop(0)
        else:
            return None

    #----------------------------------------------------------------------
    def __len__(self):
        """"""
        return len(self.__data)



#-------------------------------------------------------------------------
class GolismeroPool(threading.Thread):
    """
    Pool for GolismeroThreads
    """

    #----------------------------------------------------------------------
    def __init__(self, pool_size = 5):
        if not isinstance(pool_size, int):
            raise TypeError("Expected int, got %s instead" % type(pool_size))
        if pool_size < 1:
            raise ValueError("pool_size must be great than 0.")

        # Number of maximun concurrent threads
        self.__sem_max_threads             = Semaphore(pool_size)
        self.__sem_available_data          = Semaphore(0)
        self.__sem_join                    = Semaphore(0)

        # Number os task running
        self.__count_task                  = 0

        # Stop var
        self.__continue                    = True
        # Join wanted?
        self.__join                        = False

        # Thread pool. Format: (function, values, return_value)
        self.__data_pool                   = set()

        # Executors buse
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

        super(GolismeroPool,self).__init__()

        # Start the pool
        self.start()

    #----------------------------------------------------------------------
    def run(self):
        """
        Execute a function or list of functions as daemon mode. This is: this
        method is not blocking.

        You can add any function or functions a their values to be processed. The
        process will be done in background, without lock the program execution.

        """
        #
        # The first while controls when there is not
        # processes added in the pool
        #
        while True:
            # Controls if there is any value to process
            self.__sem_available_data.acquire()

            if not self.__continue:
                break

            # Get function to process
            func, tmp_vals, queue = self.__data_pool.pop()
            m_vals = list(tmp_vals)

            # Get the length of the iterator
            self.__count_task += len(m_vals)

            for l_val in m_vals:
                # Get a slot
                self.__sem_max_threads.acquire()

                # Get executor
                f = self.__task_pool_available.pop()
                # Put to the busy task
                self.__task_pool_busy.add(f)

                f.add(func, l_val, queue)

    #----------------------------------------------------------------------
    def _release_sem(self):
        """
        Increases in 1 the value of the semaphore
        """
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
        """"""
        self.__join = True
        self.__sem_join.acquire()


    #----------------------------------------------------------------------
    def add(self, func, value):
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
            if value:
                m_data         = iter(value)

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
        Stop al threads in the pool
        """
        self.__continue = False

        # Signal to all threads to stop
        map(GolismeroThread.stop, self.__task_pool_available)

        # Unlock
        self.__sem_available_data.release()

    #----------------------------------------------------------------------
    def terminate(self):
        """
        Force to exit killing al threads
        """
        raise NotImplemented()




if __name__ == "__main__":
    p = GolismeroPool(5)
    l = [1,2,4,5,9,10,29,1919]
    r = p.add(lambda x: x+1, l)
    p.join()
    p.stop()

    print "####"
    for x in xrange(len(r)):
        print r.get()

