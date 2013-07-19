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


__all__ = ["pmap"]

from thread import get_ident
from threading import Semaphore, Thread
from collections import Iterable

#----------------------------------------------------------------------
def pmap(func, *args, **kwargs):
    """
    Run a function in parallel.

    This function behaves pretty much like the built-in
    function map(), but it runs in parallel using threads:

        >>> from golismero.api.parallel import pmap
        >>> def triple(x):
        ...   return x * 3
        ...
        >>> pmap(triple, [1, 2, 3, 4, 5])
        [3, 6, 9, 12, 15]
        >>> def addition(x, y):
        ...   return x + y
        ...
        >>> pmap(addition, [1, 2, 3, 4, 5], [2, 4, 6, 8, 10])
        [3, 6, 9, 12, 15]

        >>> def printer(x, my_list):
               print "%s - %s" (x, str(my_list))

        >>> pmap(printer, "fixed_text", [1,2])
        fixed_text - 1
        fixed_text - 2


    .. warning: Unlike the built-in map() function, exceptions raised
                by the callback function will be silently ignored.

    :param func: A function or any other executable object.
    :type func: callable

    :param args: One or more iterables or simple params containing the parameters for each call.
    :type args: simple_param, simple_param, iterable, iterable...

    :keyword pool_size: Maximum amount of concurrent threads. Defaults to 4.
    :type pool_size: int

    :return: List with returned results, in the same order as the input data.
    :rtype: list
    """

    # Check for missing arguments.
    if len(args) <= 0:
        raise TypeError("Expected at least one positional argument")

    # Get the pool size.
    pool_size = kwargs.pop("pool_size", 4)

    # Check for extraneous keyword arguments.
    if kwargs:
        if len(kwargs) > 1:
            msg = "Unknown keyword arguments: "
        else:
            msg = "Unknown keyword argument: "
        raise TypeError(msg + ", ".join(kwargs))

    # Interpolate the arguments.
    if len(args) == 1:
        data = [ (x,) for x in args[0] ]
    else:
        data = map(None, *args)

        if all(isinstance(x, Iterable) for x in args):
            data = map(None, *args)
        else:
            le = max(map(len, filter(lambda x: isinstance(x, Iterable), args)))
            m_tmp_data = []
            for y in args:
                if not isinstance(y, Iterable):
                    print y
                    m_tmp_data.append(tuple([y for x in xrange(le)]))
                else:
                    m_tmp_data.append(y)
            data = map(None, *m_tmp_data)

    # Create the task group.
    m_task_group = GolismeroTaskGroup(func, data)

    # Create the pool.
    m_pool = GolismeroPool(pool_size)
    try:

        # Add the task and get the returned values.
        m_pool.add(m_task_group)

        # Wait for the tasks to end.
        m_pool.join_tasks()

    # Stop the pool.
    finally:
        m_pool.stop()

    # Return the list of results.
    return m_task_group.pack_output()


#-------------------------------------------------------------------------
class GolismeroTask(object):
    """
    A task to be executed.
    """

    def __init__(self, func, args, index, output):
        """
        :param func: A function or any other executable object.
        :type func: callable

        :param args: Tuple containing positional arguments.
        :type args: tuple

        :param index: Key for the output dictionary. Used later to sort the results.
        :type index: int

        :param output: Output dictionary that will receive the return value.
        :type output: dict(int -> *)
        """

        # Validate the parameters.
        if type(index) is not int:
            raise TypeError("Expected int, got %s instead" % type(index))
        if not hasattr(output, "__setitem__"):
            raise TypeError("Expected dict, got %s instead" % type(output))
        if not callable(func):
            raise TypeError("Expected callable (function, class, instance with __call__), got %s instead" % type(func))

        # Set the new task data.
        self.__func   = func       # Function to run.
        self.__args   = args       # Parameters for the function.
        self.__index  = index      # Index for the return value.
        self.__output = output     # Dictionary for return values.


    #----------------------------------------------------------------------
    @property
    def func(self):
        """
        :returns: A function or any other executable object.
        :rtype: callable
        """
        return self.__func

    @property
    def args(self):
        """
        :returns: Tuple containing positional arguments.
        :rtype: tuple
        """
        return self.__args

    @property
    def index(self):
        """
        :returns: Key for the output dictionary. Used later to sort the results.
        :rtype: int
        """
        return self.__index

    @property
    def output(self):
        """
        :returns: Output dictionary that will receive the return value.
        :rtype: dict(int -> *)
        """
        return self.__output


    #----------------------------------------------------------------------
    def run(self):
        """
        Run the task.
        """

        try:

            # Run the task.
            x = self.__func(*self.__args)

            # Store the results.
            self.__output[self.__index] = x

        except:

            # TODO: Return exceptions to the caller.
            pass


#-------------------------------------------------------------------------
class GolismeroTaskGroup(object):
    """
    A group of tasks to be executed.
    """

    def __init__(self, func, data):
        """
        :param func: A function or any other executable object.
        :type func: callable

        :param data: List of tuples containing the parameters for each call.
        :type data: list(tuple(*))
        """

        # Validate the parameters.
        if not callable(func):
            raise TypeError("Expected callable (function, class, instance with __call__), got %s instead" % type(func))

        # Set the new task group data.
        self.__func   = func       # Function to run.
        self.__data   = data       # Data to process.
        self.__output = {}         # Dictionary for return values.


    #----------------------------------------------------------------------
    @property
    def func(self):
        """
        :returns: A function or any other executable object.
        :rtype: callable
        """
        return self.__func

    @property
    def data(self):
        """
        :returns: List of tuples containing the parameters for each call.
        :rtype: list(tuple(*))
        """
        return self.__data

    @property
    def output(self):
        """
        :returns: Output dictionary that will receive the return values.
        :rtype: dict(int -> *)
        """
        return self.__output


    #----------------------------------------------------------------------
    def __len__(self):
        """
        :returns: Number of individual tasks for this task group.
        :rtype: int
        """
        return len(self.data)


    #----------------------------------------------------------------------
    def __iter__(self):
        """
        :returns: Iterator of individual tasks for this task group.
        :rtype: iter(GolismeroTask)
        """
        func = self.func
        output = self.output
        index = 0
        for args in self.data:
            yield GolismeroTask(func, args, index, output)
            index += 1


    #----------------------------------------------------------------------
    def pack_output(self):
        """
        Converts the output dictionary into an ordered list, where each
        element is the return value for each tuple of positional arguments.
        Missing elements are replaced with None.

        .. warning: Do not call until join() has been called!
        """
        output = self.output
        if not output:
            return [None] * len(self.data)
        get = output.get
        max_index = max(output.iterkeys())
        max_index = max(max_index, len(self.data) - 1)
        return [ get(i) for i in xrange(max_index + 1) ]


#-------------------------------------------------------------------------
class GolismeroThread(Thread):
    """
    Worker threads.
    """


    #----------------------------------------------------------------------
    def __init__(self):

        # Initialize our variables.
        self.__task            = None          # Task to run.
        self._callback         = None          # Callback set by the pool.
        self.__continue        = True          # Stop flag.
        self.__sem_available   = Semaphore(0)  # Semaphore for pending tasks.

        # Call the superclass constructor
        # *after* initializing our variables.
        super(GolismeroThread,self).__init__()


    #----------------------------------------------------------------------
    def run(self):
        """
        Thread run function.

        .. warning: This method is called automatically,
                    do not call it yourself.
        """

        # Check the user isn't a complete moron who doesn't read the docs.
        if self.ident != get_ident():
            raise SyntaxError("Don't call GolismeroThread.run() yourself!")

        # Loop until signaled to stop.
        while True:

            # Block until we receive a task.
            self.__sem_available.acquire()

            # If signaled to stop, break out of the loop.
            if not self.__continue:
                break

            # Run the task.
            if self.__task is not None:
                self.__task.run()

            # Run the callback.
            if self._callback is not None:
                self._callback(self)


    #----------------------------------------------------------------------
    def stop(self):
        """
        Signal the thread to stop.
        """
        self.__continue = False
        self.__sem_available.release()


    #----------------------------------------------------------------------
    def terminate(self):
        """
        Force the thread to terminate.
        """
        raise NotImplementedError()


    #----------------------------------------------------------------------
    def add(self, task):
        """
        Add a task for this worker thread.

        .. warning: This is not reentrant! If this method is called while
                    another task is still running, weird things may happen!

        :param task: Task to run.
        :type task: GolismeroTask
        """

        # Validate the parameters.
        if not isinstance(task, GolismeroTask):
            raise TypeError("Expected GolismeroTask, got %s instead" % type(task))

        # Set the task as current.
        self.__task = task

        # Signal the thread to run the task.
        self.__sem_available.release()


#-------------------------------------------------------------------------
class GolismeroPool(Thread):
    """
    Thread pool.
    """


    #----------------------------------------------------------------------
    def __init__(self, pool_size = 4):
        """
        :param pool_size: Maximum amount of concurrent threads allowed.
        :type pool_size: int
        """
        if not isinstance(pool_size, int):
            raise TypeError("Expected int, got %s instead" % type(pool_size))
        if pool_size < 1:
            raise ValueError("pool_size must be greater than 0")

        # Synchronization.
        self.__sem_max_threads    = Semaphore(pool_size)
        self.__sem_available_data = Semaphore(0)
        self.__sem_join           = Semaphore(0)

        # Number of tasks.
        self.__count_task = 0

        # Stop execution?
        self.__stop = False

        # Join wanted?
        self.__join = False

        # Pending tasks.
        self.__pending_tasks = set()

        # Busy worker threads.
        self.__busy_workers = set()

        # Available worker threads.
        self.__available_workers = set()

        # Setup the pool.
        add = self.__available_workers.add
        for l_p in xrange(pool_size):
            l_thread = GolismeroThread()
            l_thread._callback = self._worker_thread_finished
            add(l_thread)
            l_thread.start()

        # Superclass constructor.
        super(GolismeroPool, self).__init__()

        # Start the dispatcher thread.
        self.start()


    #----------------------------------------------------------------------
    def run(self):
        """
        Execute incoming background tasks until signaled to stop.

        .. warning: This method is called automatically,
                    do not call it yourself.
        """

        # Check the user isn't a complete moron who doesn't read the docs.
        if self.ident != get_ident():
            raise SyntaxError("Don't call GolismeroPool.run() yourself!")

        while True:

            # Blocks until a task group is received.
            self.__sem_available_data.acquire()

            # If stop is requested, break out of the loop.
            if self.__stop:
                break

            # Get task group to run.
            task_group = self.__pending_tasks.pop()

            # The length of the input data tells us how many
            # thread finish signals to expect.
            self.__count_task += len(task_group)

            # For each individual task...
            for task in task_group:

                # Block until a worker thread is available.
                self.__sem_max_threads.acquire()

                # Get a random available worker thread.
                f = self.__available_workers.pop()

                # Mark the worker thread as busy.
                self.__busy_workers.add(f)

                # Send the task to the worker thread.
                f.add(task)


    #----------------------------------------------------------------------
    def _worker_thread_finished(self, thread):

        # Move the completed task from the busy set to the available set.
        self.__busy_workers.remove(thread)
        self.__available_workers.add(thread)

        # Signal the pool that a worker thread is now available.
        self.__sem_max_threads.release()

        # Decrement the currently running tasks counter.
        self.__count_task -= 1

        # If no tasks are currently running and a join was requested,
        # unlock the caller of join().
        if self.__count_task <= 0 and self.__join:
            self.__sem_join.release()
            self.__join = False


    #----------------------------------------------------------------------
    def join_tasks(self):
        """
        Block until all tasks are completed.
        """
        self.__join = True
        self.__sem_join.acquire()


    #----------------------------------------------------------------------
    def add(self, task_group):
        """
        Add a task group to the pool for execution.

        :param task_group: A task group.
        :type task_group: GolismeroTaskGroup
        """

        # Add task group to the pending tasks set.
        self.__pending_tasks.add(task_group)

        # Signal the availability of new data.
        self.__sem_available_data.release()


    #----------------------------------------------------------------------
    def stop(self):
        """
        Stop all threads in the pool.

        The pool cannot be used again after calling this method.
        """

        # Signal the dispatcher thread we want to stop.
        self.__stop = True

        # Signal all available worker threads to stop.
        map(GolismeroThread.stop, self.__available_workers)

        # Signal all busy worker threads to stop.
        map(GolismeroThread.stop, self.__busy_workers)

        # Unlock the main loop.
        self.__sem_available_data.release()

        # Block until the dispatcher thread finishes.
        if self.ident != get_ident():
            self.join()


    #----------------------------------------------------------------------
    def terminate(self):
        """
        Force exit killing all threads.

        The pool cannot be used again after calling this method.
        """
        raise NotImplementedError()
