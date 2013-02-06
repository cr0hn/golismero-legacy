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


from core.messaging.interfaces import IReceiver
from core.main.commonstructures import GlobalParams
from core.messaging.messagemanager import MessageManager
from core.main.audit import AuditManager

class Orchestrator(IReceiver):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, options):
        """Constructor"""
        if not isinstance(options, GlobalParams):
            raise TypeError()

        # Run mode
        self.__runMode = options.RunMode

        # Message manager
        self.__messageManager = MessageManager(self.__runMode)
        self.__auditManager = AuditManager()

    #----------------------------------------------------------------------
    def add_audit(self, globalParams):
        """
        Add new audit to the pool

        :param globalParams: parameter for and audit
        :type globalParams: GlobalParams
        """
        self.__auditManager.new_audit(globalParams)


    #----------------------------------------------------------------------
    def recv_msg(self, message):
        """
        Send a message to the audits
        """
        self.__messageManager.send_message(message)