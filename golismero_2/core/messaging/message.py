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


#------------------------------------------------------------------------------
class Message (object):
    """
    Messages send information, results and internal control events between the
    different components of GoLismero.

    They may be shared locally (console run mode) or serialized and sent across
    the network (cloud run modes).
    """


    #----------------------------------------------------------------------
    #
    # Constants for messages types
    #
    #----------------------------------------------------------------------
    MSG_TYPE_CONTROL = 0
    MSG_TYPE_INFO = 1
    MSG_TYPE_STATE = 2

    #----------------------------------------------------------------------
    #
    # Constants for messages info
    #
    #----------------------------------------------------------------------

    #----------------------------------------------------------------------
    # Control messages
    #----------------------------------------------------------------------
    # Global control
    MSG_CONTROL_OK = 0
    MSG_CONTROL_ACK = 1
    MSG_CONTROL_PAUSE = 2
    MSG_CONTROL_STOP = 3
    MSG_CONTROL_INTERRUPT = 4
    MSG_CONTROL_START = 5
    MSG_CONTROL_REGISTER = 6
    MSG_CONTROL_NEW_AUDIT = 7
    # Audit control
    MSG_CONTROL_START_AUDIT = 10
    MSG_CONTROL_STOP_AUDIT = 11
    MSG_CONTROL_PAUSE_AUDIT = 12
    MSG_CONTROL_INTERRUPT_AUDIT = 13
    # System control
    MSG_CONTROL_CORE_VERSION = 20
    MSG_CONTROL_CORE_VERSION_RESPONSE = 21
    MSG_CONTROL_PLUGIN_VERSION = 22
    MSG_CONTROL_PLUGIN_VERSION_RESPONSE = 23
    MSG_CONTROL_UPDATE_PLUGINS = 24
    MSG_CONTROL_UPDATE_CORE = 25
    MSG_CONTROL_SYSTEM_STATUS = 26 # Load of system
    MSG_CONTROL_SYSTEM_STATUS_RESPONSE = 27
    # Internal cache
    MSG_CONTROL_CACHE = 30
    MSG_CONTROL_RESPONSE_RESPONSE = 31

    #----------------------------------------------------------------------
    # Status messages
    #----------------------------------------------------------------------
    MSG_STATUS_ALIVE = 40
    MSG_STATUS_OK = 41
    MSG_STATUS_SYSTEM = 42
    MSG_STATUS_SYSTEM_RESPONSE = 43
    MSG_STATUS_AUDIT = 44
    MSG_STATUS_AUDIT_RESPONSE = 45



    #----------------------------------------------------------------------
    def __init__(self, message_info, message_type = 1): # By default, message type is Info message
        """
        :param message_info: the payload of the message.
        :type message_info: object -- type must be resolved at run time.

        :param message_type: specifies the type of message.
        :type mesage_type: int -- specified in a constant of Message class.
        """
        self.__message_info = message_info
        self.__message_type = message_type
        self.__audit_name = ""

    #----------------------------------------------------------------------
    def __get_message_info(self):
        """
        Get message info.
        """
        return self.__message_info

    message_info = property(__get_message_info)

    #----------------------------------------------------------------------
    def __get_message_type(self):
        """
        Get message type.

        :returns: int -- Constant
        """
        return self.__message_type

    message_type = property(__get_message_type)


    #----------------------------------------------------------------------
    #
    # This methods must be called only for Audit instance
    #
    #----------------------------------------------------------------------
    def __set_audit_name(self, name):
        """
        Set the audit name to which message belongs.

        :param name: audit name
        :type name: str
        """
        self.__audit_name = name

    #----------------------------------------------------------------------
    def __get_audit_name(self):
        """
        Get the audit name to which message belongs.

        :returns: str -- audit name
        """
        return self.__audit_name

    audit_name = property(__get_audit_name, __set_audit_name)
