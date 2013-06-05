#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: https://github.com/cr0hn/golismero/
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

from golismero.api.data import Data
from golismero.api.logger import Logger
from golismero.api.plugin import GlobalPlugin
from golismero.messaging.codes import MessageType, MessageCode, MessagePriority
from golismero.messaging.message import Message

import time
import warnings


#----------------------------------------------------------------------
class TestGlobalPlugin(GlobalPlugin):
    """
    Test global plugin support.
    """


    #----------------------------------------------------------------------
    def display_help(self):
        return "Plugin to test global plugin support."


    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        pass


    #----------------------------------------------------------------------
    def recv_info(self, info):
        if not isinstance(info, Data):
            raise TypeError("Expected Data, got %s instead" % type(info))
        Logger.log("Global plugin received info: " + info.identity)


    #----------------------------------------------------------------------
    def recv_msg(self, message):
        if not isinstance(message, Message):
            raise TypeError("Expected Message, got %s instead" % type(message))

        if message.message_type == MessageType.MSG_TYPE_CONTROL:
            if message.message_code == MessageCode.MSG_CONTROL_START_AUDIT:
                msg = Message(message_type = MessageType.MSG_TYPE_CONTROL,
                              message_code = MessageCode.MSG_CONTROL_LOG,
                              message_info = ("Global plugin detected audit start", 1, False),
                              audit_name   = message.audit_name,
                              priority     = MessagePriority.MSG_PRIORITY_LOW)
                self.send_msg(msg)
            elif message.message_code == MessageCode.MSG_CONTROL_STOP_AUDIT:
                msg = Message(message_type = MessageType.MSG_TYPE_CONTROL,
                              message_code = MessageCode.MSG_CONTROL_LOG,
                              message_info = ("Global plugin detected audit stop", 1, False),
                              audit_name   = message.audit_name,
                              priority     = MessagePriority.MSG_PRIORITY_LOW)
                self.send_msg(msg)


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        pass
