#!/usr/bin/python

# -*- coding: utf-8 -*-
"""
GoLismero 2.0 - The web kniffe.

Copyright (C) 2011-2013 - Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com

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



from core.main.auditmanager import AuditManager
from core.main.commonstructures import GlobalParams

#------------------------------------------------------------------------------
class Message (object):
    """
    This class contain information for message system
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
    MSG_CONTROL_ACK = 0
    MSG_CONTROL_PAUSE = 0
    MSG_CONTROL_STOP = 0
    MSG_CONTROL_INTERRUPT = 0
    MSG_CONTROL_START = 0
    MSG_CONTROL_REGISTER = 0
    MSG_CONTROL_NEW_AUDIT = 0
    # Audit control
    MSG_CONTROL_START_AUDIT = 0
    MSG_CONTROL_STOP_AUDIT = 0
    MSG_CONTROL_PAUSE_AUDIT = 0
    MSG_CONTROL_INTERRUPT_AUDIT = 0
    # System control
    MSG_CONTROL_CORE_VERSION = 0
    MSG_CONTROL_CORE_VERSION_RESPONSE = 0
    MSG_CONTROL_PLUGIN_VERSION = 0
    MSG_CONTROL_PLUGIN_VERSION_RESPONSE = 0
    MSG_CONTROL_UPDATE_PLUGINS = 0
    MSG_CONTROL_UPDATE_CORE = 0
    MSG_CONTROL_SYSTEM_STATUS = 0 # Load of system
    MSG_CONTROL_SYSTEM_STATUS_RESPONSE = 0
    # Internal cache
    MSG_CONTROL_CACHE = 0
    MSG_CONTROL_RESPONSE_RESPONSE = 0

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
    # Content messages
    #----------------------------------------------------------------------
    MSG_DATA_TEST = 160



    #----------------------------------------------------------------------
    def __init__(self, message_info, message_info_type, message_type = Message.MSG_TYPE_INFO):
        """
        :param message_info: information of message.
        :type message_info: object -- type must be resolved at run time.

        :param message_info_type: determinates the info that contain the message.
        :type message_info_type: int -- specified in a constant of Message class.

        :param message_type: determinates the type of message
        :type mesage_type: int -- specified in a constant of Message class.
        """
        self.__message_info = message_info
        self.__message_type = message_type
        self.__message_info_type = message_info_type
        self.__audit_name = ""

    #----------------------------------------------------------------------
    def __get_message_info(self):
        """
        Get message info.
        """
        return self.__message_info

    message_info = property(__get_message_info)

    #----------------------------------------------------------------------
    def get_message_type(self):
        """
        Get message type

        :returns: int -- Constant
        """
        return self.__message_type

    message_type = property(get_message_type)

    #----------------------------------------------------------------------
    def get_message_info_type(self):
        """
        Get message type

        :returns: int -- Constant
        """
        return self.__message_info_type

    message_info_type = property(get_message_info_type)




    #----------------------------------------------------------------------
    #
    # This methods must be called only for Audit instance
    #
    #----------------------------------------------------------------------
    def set_audit_name(self, name):
        """
        Set audit name to which message belongs. Only instance of Audit can
        be call it.

        :param name: audit name
        :type name: str
        """
        self.__audit_name = name

    #----------------------------------------------------------------------
    def get_audit_name(self):
        """
        Get audit name to which message belongs

        :returns: str --audit name for this message.
        """
        return self.__audit_name

    audit_name = property(get_audit_name, set_audit_name)




