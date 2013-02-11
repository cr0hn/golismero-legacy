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



from core.main.commonstructures import GlobalParams
from core.main.audit import AuditManager
from core.main.commonstructures import Singleton
from core.messaging.interfaces import IReceiver

#--------------------------------------------------------------------------
class MessageManager(Singleton):
    """"""

    #----------------------------------------------------------------------
    def __vinit__(self):
        """Virtual contructor"""
        self.__observers = [] # List of observers to be notified

    #----------------------------------------------------------------------
    def add_listener(self, listener):
        """
        Add some object to be notified
        """
        if isinstance(listener, IReceiver):
            MessageManager.__observers.append(listener)



    #----------------------------------------------------------------------
    def send_message(self, Message):
        """Send a message to all listeners"""
        for i in self.__observers:
            i.recv_msg(Message)

