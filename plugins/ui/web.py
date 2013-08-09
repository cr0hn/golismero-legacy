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

from golismero.api.config import Config
from golismero.api.logger import Logger
from golismero.api.plugin import UIPlugin, get_plugin_info
from golismero.messaging.codes import MessageType, MessageCode

import time
import warnings

try:
    # The fastest JSON parser available for Python.
    from cjson import decode as json_decode
    from cjson import encode as json_encode
except ImportError:
    try:
        # Faster than the built-in module, usually found.
        from simplejson import loads as json_decode
        from simplejson import dumps as json_encode
    except ImportError:
        # Built-in module since Python 2.6, very very slow!
        from json import loads as json_decode
        from json import dumps as json_encode


#----------------------------------------------------------------------
class WebUIPlugin(UIPlugin):
    """
    Web UI plugin.
    """


    #----------------------------------------------------------------------
    def __init__(self):
        #
        # TODO
        #
        pass


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return []


    #----------------------------------------------------------------------
    def recv_info(self, info):
        pass


    #----------------------------------------------------------------------
    def recv_msg(self, message):

        if message.message_type == MessageType.MSG_TYPE_CONTROL:

            if message.message_code == MessageCode.MSG_CONTROL_START_UI:
                self.start_ui()

            elif message.message_code == MessageCode.MSG_CONTROL_STOP_UI:
                self.stop_ui()

            elif message.message_code == MessageCode.MSG_CONTROL_START_AUDIT:
                self.notify_audit_start(message.audit_name)

            elif message.message_code == MessageCode.MSG_CONTROL_STOP_AUDIT:
                self.notify_audit_stop(message.audit_name, message.message_info)

            elif message.message_code == MessageCode.MSG_CONTROL_LOG:
                plugin_name = self.get_plugin_name(message)
                (text, level, is_error) = message.message_info
                if is_error:
                    self.notify_error_log(message.audit_name, plugin_name, text, level)
                else:
                    self.notify_log(message.audit_name, plugin_name, text, level)

            elif message.message_code == MessageCode.MSG_CONTROL_ERROR:
                plugin_name = self.get_plugin_name(message)
                (description, traceback) = message.message_info
                text = "Error: " + description
                self.notify_error_log(message.audit_name, plugin_name, text, Logger.STANDARD)
                text = "Exception raised: %s\n%s" % (description, traceback)
                self.notify_error_log(message.audit_name, plugin_name, text, Logger.MORE_VERBOSE)

            elif message.message_code == MessageCode.MSG_CONTROL_WARNING:
                plugin_name = self.get_plugin_name(message)
                for w in message.message_info:
                    formatted = warnings.formatwarning(w.message, w.category, w.filename, w.lineno, w.line)
                    text = "Warning: " + w.message
                    self.notify_log(message.audit_name, plugin_name, text, Logger.STANDARD)
                    text = "Warning details: " + formatted
                    self.notify_log(message.audit_name, plugin_name, text, Logger.MORE_VERBOSE)

        elif message.message_type == MessageType.MSG_TYPE_STATUS:

            if message.message_type == MessageCode.MSG_STATUS_PLUGIN_BEGIN:
                plugin_name = self.get_plugin_name(message)
                self.notify_progress(message.audit_name, plugin_name, message.message_info, 0.0)

            elif message.message_type == MessageCode.MSG_STATUS_PLUGIN_END:
                plugin_name = self.get_plugin_name(message)
                self.notify_progress(message.audit_name, plugin_name, message.message_info, 100.0)

            elif message.message_code == MessageCode.MSG_STATUS_PLUGIN_STEP:
                plugin_name = self.get_plugin_name(message)
                identity, progress = message.message_info
                self.notify_progress(message.audit_name, plugin_name, identity, progress)

            elif message.message_code == MessageCode.MSG_STATUS_STAGE_UPDATE:
                self.notify_stage_update(message.audit_name, message.message_info)


    #----------------------------------------------------------------------
    @staticmethod
    def get_plugin_name(message):
        if message.plugin_name:
            return get_plugin_info(message.plugin_name).display_name
        return "GoLismero"


    #----------------------------------------------------------------------
    def start_ui(self):
        bind_address = Config.plugin_config.get("bind_address", "127.0.0.1")
        bind_port    = int( Config.plugin_config.get("bind_port", "8080") )
        #
        # TODO
        #
        raise NotImplementedError("Plugin under construction!")


    #----------------------------------------------------------------------
    def stop_ui(self):
        #
        # TODO
        #
        pass


    #----------------------------------------------------------------------
    def notify_audit_start(self, audit_name):
        #
        # TODO
        #
        pass


    #----------------------------------------------------------------------
    def notify_audit_stop(self, audit_name, status):
        #
        # TODO
        #
        pass


    #----------------------------------------------------------------------
    def notify_log(self, audit_name, plugin_name, text, level):
        #
        # TODO
        #
        pass


    #----------------------------------------------------------------------
    def notify_error_log(self, audit_name, plugin_name, text, level):
        #
        # TODO
        #
        pass


    #----------------------------------------------------------------------
    def notify_progress(self, audit_name, plugin_name, identity, progress):
        #
        # TODO
        #
        pass


    #----------------------------------------------------------------------
    def notify_stage_update(self, audit_name, stage):
        #
        # TODO
        #
        pass
