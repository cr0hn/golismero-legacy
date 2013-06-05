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
from golismero.api.plugin import UIPlugin
from golismero.messaging.codes import MessageType, MessageCode, MessagePriority
from golismero.messaging.message import Message

import time
import warnings


#----------------------------------------------------------------------
class TestUIPlugin(UIPlugin):
    """
    Test UI plugin.
    """


    #----------------------------------------------------------------------
    def display_help(self):
        return "Test UI that shows all events and data objects."


    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        pass


    #----------------------------------------------------------------------
    def recv_info(self, info):
        if not isinstance(info, Data):
            raise TypeError("Expected Data, got %s instead" % type(info))
        print "-" * 79
        print "Info: %r" % info
        print


    #----------------------------------------------------------------------
    def recv_msg(self, message):
        if not isinstance(message, Message):
            raise TypeError("Expected Message, got %s instead" % type(message))

        print "-" * 79
        print "Message:"
        print "  Timestamp: %s" % time.asctime(message.timestamp)
        print "  Audit:     %s" % message.audit_name
        print "  Plugin:    %s" % message.plugin_name
        print "  Type:      %s" % MessageType.get_name(message.message_type)
        print "  Code:      %s" % MessageCode.get_name(message.message_code)
        print "  Priority:  %s" % MessagePriority.get_name(message.priority)
        print "  Payload:   %r" % message.message_info
        print


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        pass
