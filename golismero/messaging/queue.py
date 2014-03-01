#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Message transport using AMQP.
"""

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: https://github.com/golismero
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

__all__ = ["MessageTransport"]

from ..common import pickle
from ..api.config import Config
from ..api.text.text_utils import generate_random_string

from kombu import Connection
from os import getpid
from threading import RLock
from warnings import catch_warnings


#------------------------------------------------------------------------------
class MessageTransport (object):
    """
    Message transport using AMQP.
    """

    # XXX DEBUG
    DEBUG = False
    ##DEBUG = True


    #--------------------------------------------------------------------------
    def __init__(self, broker):
        """
        :param broker: Broker configuration URL.
        :type broker: str
        """

        # Call the superclass constructor.
        super(MessageTransport, self).__init__()

        # Save the broker configuration URL.
        self.__broker = broker

        # This saves a reference to all message queues.
        self._queues = []

        # Connect to the message broker.
        self.connect()


    #--------------------------------------------------------------------------
    @property
    def broker(self):
        """
        :returns: Broker configuration URL.
        :rtype: str
        """
        return self.__broker


    #--------------------------------------------------------------------------
    def connect(self):
        """
        Connect to the message broker.
        """
        with catch_warnings(record=True):
            self.debug("Connecting to: %s" % self.broker)
            self._connection = Connection(self.broker)
            self._connection.connect()


    #--------------------------------------------------------------------------
    def close(self):
        """
        Close all message queues and disconnect from the broker.
        """
        try:
            self.debug("Closing connection: %s" % self.broker)
        except Exception:
            pass
        try:
            try:
                for queue in list(self._queues):
                    try:
                        queue.close()
                    except Exception:
                        pass
            finally:
                try:
                    self._connection.release()
                finally:
                    self._connection = None
                    self.__queues = []
        except Exception:
            pass


    #--------------------------------------------------------------------------
    def start_queue(self, queue_name = None, persistent = True):
        """
        Start using a queue.

        :param queue_name: Name of the queue. Must be unique.
            If not given, a random name is chosen.
        :type queue_name: str

        :param persistent: True for a persistent queue, False otherwise.
        :type persistent: bool

        :returns: Message queue.
        :rtype: MessageQueue
        """

        # Wrap it with our class.
        self.debug("Starting queue: %s" % queue_name)
        queue = MessageQueue(self, queue_name, persistent)
        self.debug("Started queue: %s" % queue.name)

        # Save it in the list.
        self._queues.append(queue)

        # Return it.
        return queue


    #--------------------------------------------------------------------------
    def debug(self, msg):
        """
        Internally used function for logging debug messages.
        """
        if self.DEBUG:
            with open("msg-queue-%d.log" % getpid(), "a") as f:
                f.write(msg + "\n")


#------------------------------------------------------------------------------
class MessageQueue (object):
    """
    Message queue using AMQP.
    """


    #--------------------------------------------------------------------------
    def __init__(self, transport, queue_name, persistent):
        """
        :param transport: Message transport.
        :type transport: MessageTransport

        :param queue_name: Name of the queue. Must be unique.
            If not given, a random name is chosen.
        :type queue_name: str

        :param persistent: True for a persistent queue, False otherwise.
        :type persistent: bool
        """

        # Call the superclass constructor.
        super(MessageQueue, self).__init__()

        # Get the queue name.
        if not queue_name:
            if persistent:
                queue_name = "golismero-queue-" + generate_random_string()
            else:
                queue_name = "golismero-buffer-" + generate_random_string()

        # Instance the Kombu message queue.
        with catch_warnings(record=True):
            if persistent:
                kombu_queue = transport._connection.SimpleQueue(queue_name)
            else:
                kombu_queue = transport._connection.SimpleBuffer(queue_name)

        # Save the properties.
        self.__queue      = kombu_queue
        self.__transport  = transport
        self.__name       = queue_name
        self.__persistent = persistent
        self.__lock       = RLock()


    #--------------------------------------------------------------------------
    @property
    def transport(self):
        """
        :returns: Message transport.
        :rtype: MessageTransport
        """
        return self.__transport


    #--------------------------------------------------------------------------
    @property
    def broker(self):
        """
        :returns: Broker configuration URL.
        :rtype: str
        """
        return self.__transport.broker


    #--------------------------------------------------------------------------
    @property
    def name(self):
        """
        :returns: Name of the queue.
        :rtype: str
        """
        return self.__name


    #--------------------------------------------------------------------------
    @property
    def persistent(self):
        """
        :returns: True for a persistent queue, False otherwise.
        :rtype: bool
        """
        return self.__persistent


    #--------------------------------------------------------------------------
    def close(self):
        """
        Close the queue and release all resources.
        """
        try:
            self.debug("Closing queue: %s" % self.name)
        except Exception:
            pass
        try:
            self.__queue.close()
        finally:
            try:
                self.__transport._queues.remove(self)
            finally:
                self.__transport = None
                self.__queue     = None
                self.__lock      = None


    #--------------------------------------------------------------------------
    def get(self, *args, **kwargs):
        """
        Receive data from the queue.

        :returns: Data received.
        :rtype: *
        """
        if self.__lock is None:
            exit(1)
        self.debug("Reading from queue: %s" % self.name)
        with self.__lock:
            message = self.__queue.get(*args, **kwargs)
            message.ack()
        self.debug(
            "Read %d bytes from queue: %s" % (len(message.body), self.name))
        data = pickle.loads(message.body)
        try:
            self.debug("Read from queue %s: %r" % (self.name, data))
        except Exception:
            pass
        return data


    #--------------------------------------------------------------------------
    def put(self, data, *args, **kwargs):
        """
        Send data to the queue.

        :param data: Data to send.
        :type data: *
        """
        if self.__lock is None:
            exit(1)
        raw = pickle.dumps(data)
        try:
            self.debug("Sending to queue %s: %r" % (self.name, data))
        except Exception:
            self.debug(
                "Writing %d bytes into queue: %s" % (len(raw), self.name))
        with self.__lock:
            self.__queue.put(raw, *args, **kwargs)
        self.debug(
            "Wrote %d bytes into queue: %s" % (len(raw), self.name))


    #--------------------------------------------------------------------------
    def debug(self, msg):
        """
        Internally used function for logging debug messages.
        """
        if self.__transport.DEBUG:
            with open("msg-queue-%d.log" % getpid(), "a") as f:
                f.write(msg + "\n")
