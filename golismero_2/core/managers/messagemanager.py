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




from core.main.commonstructures import Singleton, IReceiver
from core.managers.uimanager import UIManager
from core.managers.auditmanager import AuditManager


#--------------------------------------------------------------------------
class MessageManager(Singleton):
    """
    Manager for messages.
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Virtual contructor"""

        # For singleton pattern
        if self._is_instanced:
            return

        self.__observers = list() # List of observers to be notified

    #----------------------------------------------------------------------
    def add_listener(self, listener):
        """
        Add some object to be notified, and the category of pool to add.

        :param listener: IReceiver type to add to listeners.
        :type listener: IReceiver

        :param category: Category to add the object.
        :type category: str -- valid values: ["all", "testing", "ui", "report"]

        """

        # Select pool to add
        if isinstance(listener, list):
            for i in listener:
                self.__observers.extend(listener)
        else:
            self.__observers.append(listener)


    #----------------------------------------------------------------------
    def send_message(self, message):
        """
        Send a message to all listeners

        :param message: message to send.
        :type message: Message

        :param category: The category to send messages.
        :type category: str -- available categories:  ["all", "testing", "ui", "report"]

        """
        # Send message to category
        for i in self.__observers:
            i.recv_msg(message)


