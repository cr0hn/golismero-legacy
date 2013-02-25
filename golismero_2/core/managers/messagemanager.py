#!/usr/bin/env python
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

__all__ = ["MessageManager"]


#--------------------------------------------------------------------------
class MessageManager (object):
    """
    Manager for messages.
    """


    #----------------------------------------------------------------------
    def __init__(self, config):
        self.__observers = list() # List of observers to be notified


    #----------------------------------------------------------------------
    def add_listener(self, listener):
        """
        Add an object to be notified, and the category of pool to add.

        :param listener: IReceiver type to add to listeners.
        :type listener: IReceiver
        """

        # Select pool to add
        self.__observers.append(listener)


    #----------------------------------------------------------------------
    def add_multiple_listeners(self, listeners):
        """
        Add some multiple objects to be notified, and the category of pool to add.

        :param listener: IReceiver type to add to listeners.
        :type listener: IReceiver
        """
        self.__observers.extend(listeners)


    #----------------------------------------------------------------------
    def send_message(self, message):
        """
        Send a message to all listeners.

        :param message: message to send.
        :type message: Message
        """
        # Send message to category
        for i in self.__observers:
            i.dispatch_msg(message)
