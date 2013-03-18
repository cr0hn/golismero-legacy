#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com
  Mario Vilas | mvilas@gmail.com

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

from .codes import *

from time import time


#------------------------------------------------------------------------------
class Message (object):
    """
    Messages send information, vulnerabilities, resources and internal control
    events between the different components of GoLismero.

    They may be shared locally (console run mode) or serialized and sent across
    the network (cloud run modes).
    """


    #----------------------------------------------------------------------
    def __init__(self, message_type = MessageType.MSG_TYPE_DATA,
                       message_code = MessageCode.MSG_DATA_NEW,
                       message_info = None,
                         audit_name = None,
                           priority = MessagePriority.MSG_PRIORITY_MEDIUM):
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
        if message_type not in MSG_CODES:
            raise ValueError("Invalid message type: %d" % message_type)
        if message_type != MessageType.MSG_TYPE_DATA and type(message_code) != int:
            raise TypeError("Expected int, got %s instead" % type(message_code))
        if  message_type == MessageType.MSG_TYPE_CONTROL and \
            not message_code in MSG_CONTROL_CODES:
                raise ValueError("Invalid control message code: %d" % message_code)
        if audit_name is not None and type(audit_name) not in (str, unicode):
            raise TypeError("Expected int, got %s instead" % type(audit_name))
        if type(priority) != int:
            raise TypeError("Expected int, got %s instead" % type(priority))
        if priority not in MSG_PRIORITIES:
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
        return (self.message_type == MessageType.MSG_TYPE_CONTROL and
                self.message_code == MessageCode.MSG_CONTROL_ACK)


    #----------------------------------------------------------------------
    def __repr__(self):
        s  = "<Message timestamp=%r, type=%r, code=%r, audit=%r, info=%r>"
        s %= (self.timestamp, self.message_type, self.message_code, self.message_info)
        return s
