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
    # Constants for message types
    #
    #----------------------------------------------------------------------
    MSG_TYPE_CONTROL = 0
    MSG_TYPE_INFO = 1
    MSG_TYPE_STATE = 2

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
    MSG_CONTROL_OK = 0
    MSG_CONTROL_ERROR = 1
    MSG_CONTROL_ACK = 2
    MSG_CONTROL_START = 3
    MSG_CONTROL_STOP = 4
    MSG_CONTROL_PAUSE = 5
    MSG_CONTROL_INTERRUPT = 6
    MSG_CONTROL_REGISTER = 7
    # Audit control
    MSG_CONTROL_NEW_AUDIT = 10
    MSG_CONTROL_START_AUDIT = 11
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
    MSG_CONTROL_SYSTEM_STATUS = 26 # System load
    MSG_CONTROL_SYSTEM_STATUS_RESPONSE = 27
    # Internal cache
    MSG_CONTROL_CACHE = 30
    MSG_CONTROL_CACHE_RESPONSE = 31
    # UI subsystem
    MSG_CONTROL_START_UI = 40
    MSG_CONTROL_STOP_UI = 41

    MSG_CONTROL_FIRST = MSG_CONTROL_OK
    MSG_CONTROL_LAST  = MSG_CONTROL_STOP_UI

    #----------------------------------------------------------------------
    # Status messages
    #----------------------------------------------------------------------
    MSG_STATUS_ALIVE = 0
    MSG_STATUS_OK = 1
    MSG_STATUS_SYSTEM = 2
    MSG_STATUS_SYSTEM_RESPONSE = 3
    MSG_STATUS_AUDIT = 4
    MSG_STATUS_AUDIT_RESPONSE = 5

    MSG_STATUS_FIRST = MSG_STATUS_ALIVE
    MSG_STATUS_LAST  = MSG_STATUS_AUDIT_RESPONSE


    #----------------------------------------------------------------------
    def __init__(self, message_type = MSG_TYPE_INFO,
                       message_code = 0,
                       audit_name   = None,
                       message_info = None):
        """
        :param message_type: specifies the type of message.
        :type mesage_type: int -- specified in a constant of Message class.

        :param message_code: specifies the code of message.
        :type message_code: int -- specified in a constant of Message class.

        :param audit_name: the name of the audit this message belongs to.
        :type audit_name: str

        :param message_info: the payload of the message.
        :type message_info: object -- type must be resolved at run time.
        """
        self.__message_type = message_type
        self.__message_code = message_code
        self.__audit_name   = audit_name
        self.__message_info = message_info


    @property
    def message_type(self):
        return self.__message_type

    @property
    def message_code(self):
        return self.__message_code

    @property
    def audit_name(self):
        return self.__audit_name

    @property
    def message_info(self):
        return self.__message_info
