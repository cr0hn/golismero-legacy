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

__all__ = ["Message"]

from functools import total_ordering
from time import time


#------------------------------------------------------------------------------
@total_ordering
class Message (object):
    """
    Messages send information, vulnerabilities, resources and internal control
    events between the different components of GoLismero.

    They may be shared locally (console run mode) or serialized and sent across
    the network (cloud run modes).
    """


    #----------------------------------------------------------------------
    #
    # Constants for message types
    #
    #----------------------------------------------------------------------
    MSG_TYPE_CONTROL = 0
    MSG_TYPE_INFO    = 1
    MSG_TYPE_RPC     = 2
    MSG_TYPE_STATE   = 3

    MSG_TYPE_FIRST = MSG_TYPE_CONTROL
    MSG_TYPE_LAST  = MSG_TYPE_STATE


    #----------------------------------------------------------------------
    #
    # Constants for message codes
    #
    #----------------------------------------------------------------------


    #----------------------------------------------------------------------
    # Control messages
    #----------------------------------------------------------------------

    # Global control
    MSG_CONTROL_ACK = 0
    MSG_CONTROL_ERROR = 1
    MSG_CONTROL_START = 2
    MSG_CONTROL_STOP = 3
    #MSG_CONTROL_PAUSE = 4
    #MSG_CONTROL_CONTINUE = 5
    #MSG_CONTROL_REGISTER = 6

    # Audit control
    MSG_CONTROL_START_AUDIT = 10
    MSG_CONTROL_STOP_AUDIT = 11
    #MSG_CONTROL_PAUSE_AUDIT = 12
    #MSG_CONTROL_CONTINUE_AUDIT = 13

    # System control
    #MSG_CONTROL_CORE_VERSION = 20
    #MSG_CONTROL_CORE_VERSION_RESPONSE = 21
    #MSG_CONTROL_PLUGIN_VERSION = 22
    #MSG_CONTROL_PLUGIN_VERSION_RESPONSE = 23
    #MSG_CONTROL_UPDATE_PLUGINS = 24
    #MSG_CONTROL_UPDATE_CORE = 25
    #MSG_CONTROL_SYSTEM_STATUS = 26 # System load
    #MSG_CONTROL_SYSTEM_STATUS_RESPONSE = 27

    # Internal cache
    #MSG_CONTROL_CACHE = 30
    #MSG_CONTROL_CACHE_RESPONSE = 31

    # UI subsystem
    MSG_CONTROL_START_UI = 40
    MSG_CONTROL_STOP_UI = 41
    MSG_CONTROL_LOG_MESSAGE = 42
    MSG_CONTROL_LOG_ERROR = 43


    MSG_CONTROL_FIRST = MSG_CONTROL_ACK
    MSG_CONTROL_LAST  = MSG_CONTROL_LOG_ERROR


    #----------------------------------------------------------------------
    # Status messages
    #----------------------------------------------------------------------
    #MSG_STATUS_ALIVE = 0
    #MSG_STATUS_OK = 1
    #MSG_STATUS_SYSTEM = 2
    #MSG_STATUS_SYSTEM_RESPONSE = 3
    #MSG_STATUS_AUDIT = 4
    #MSG_STATUS_AUDIT_RESPONSE = 5

    #MSG_STATUS_FIRST = MSG_STATUS_ALIVE
    #MSG_STATUS_LAST  = MSG_STATUS_AUDIT_RESPONSE


    #----------------------------------------------------------------------
    #
    # Constants for message priorities
    #
    #----------------------------------------------------------------------

    MSG_PRIORITY_HIGH   = 0
    MSG_PRIORITY_MEDIUM = 1
    MSG_PRIORITY_LOW    = 2

    MSG_PRIORITY_FIRST = MSG_PRIORITY_HIGH
    MSG_PRIORITY_LAST  = MSG_PRIORITY_LOW


    #----------------------------------------------------------------------
    def __init__(self, message_type = MSG_TYPE_INFO,
                       message_code = 0,
                       message_info = None,
                         audit_name = None,
                           priority = 1):
        """
        :param message_type: specifies the type of message.
        :type mesage_type: int -- specified in a constant of Message class.

        :param message_code: specifies the code of message.
        :type message_code: int -- specified in a constant of Message class.

        :param message_info: the payload of the message.
        :type message_info: object -- type must be resolved at run time.

        :param audit_name: the name of the audit this message belongs to.
        :type audit_name: str

        :param priority: the priority level of the message.
        :type priority: int
        """

        # Validate the arguments
        if type(message_type) != int:
            raise TypeError("Expected int, got %s instead" % type(message_type))
        if not self.MSG_TYPE_FIRST <= message_type <= self.MSG_TYPE_LAST:
            raise ValueError("Invalid message type: %d" % message_type)
        if message_type != self.MSG_TYPE_INFO and type(message_code) != int:
            raise TypeError("Expected int, got %s instead" % type(message_code))
        if  message_type == self.MSG_TYPE_CONTROL and \
            not self.MSG_CONTROL_FIRST <= message_code <= self.MSG_CONTROL_LAST:
                raise ValueError("Invalid control message code: %d" % message_code)
        if audit_name is not None and type(audit_name) not in (str, unicode):
            raise TypeError("Expected int, got %s instead" % type(audit_name))
        if type(priority) != int:
            raise TypeError("Expected int, got %s instead" % type(priority))
        if not self.MSG_PRIORITY_FIRST <= priority <= self.MSG_PRIORITY_LAST:
            raise ValueError("Invalid priority level: %d" % priority)

        # Build the message object
        self.__message_type = message_type
        self.__message_code = message_code
        self.__message_info = message_info
        self.__audit_name   = audit_name
        self.__priority     = priority
        self.__timestamp    = time()

    @property
    def message_type(self):
        return self.__message_type

    @property
    def message_code(self):
        return self.__message_code

    @property
    def message_info(self):
        return self.__message_info

    @property
    def audit_name(self):
        return self.__audit_name

    @property
    def priority(self):
        return self.__priority

    @property
    def timestamp(self):
        return self.__timestamp


    #----------------------------------------------------------------------
    @property
    def is_ack(self):
        return (self.message_type == self.MSG_TYPE_CONTROL and
                self.message_code == self.MSG_CONTROL_ACK)


    #----------------------------------------------------------------------
    def __lt__(self, other):

        # Sort by priority, then by timestamp, then ACKs go last.
        return (  self.priority,  self.timestamp,  int(not  self.is_ack)) < \
               ( other.priority, other.timestamp,  int(not other.is_ack))


    #----------------------------------------------------------------------
    def __repr__(self):
        s = "<Message timestamp=%r, type=%r, code=%r, audit=%r, info=%r>"
        s %= (self.timestamp, self.message_type, self.message_code, self.message_info)
        return s
