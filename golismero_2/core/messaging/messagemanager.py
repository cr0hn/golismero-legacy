#!/usr/bin/python

# -*- coding: utf-8 -*-
"""
GoLismero 2.0 - The web knife.

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



from core.main.commonstructures import GlobalParams
from core.main.audit import AuditManager

#--------------------------------------------------------------------------
class MessageManager:
    """"""

    #----------------------------------------------------------------------
    def __init__(self, runMode):
        """
        :param runMode: Enum type that specify run mode to start Message system
        :type runMode: enum
        """
        self.__observers = [] # List of observer will be notified
        # Start notification system depend of run mode
        if GlobalParams.RUN_MODE.standalone == runMode:
            self.__observers.append(AuditManager())
        elif GlobalParams.RUN_MODE.cloudclient == runMode:
            pass
        elif GlobalParams.RUN_MODE.cloudserver == runMode:
            pass
        else:
            raise ValueError("worng runMode")

    #----------------------------------------------------------------------
    def send_message(self, Message):
        """Send a message to all listeners"""
        for i in self.__observers:
            i.send_msg(Message)

