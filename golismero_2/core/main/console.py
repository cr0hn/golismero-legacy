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

from sys import stdout, stderr

class Console():
    """"""

    __display_out = stdout
    __display_error = stderr
    __display_level = 0 # standard

    #----------------------------------------------------------------------
    #
    # Verbose levels
    #
    #----------------------------------------------------------------------
    DISABLED = 0
    STANDARD = 1
    VERBOSE = 2
    MORE_VERBOSE = 3


    #----------------------------------------------------------------------
    @staticmethod
    def configure(ConsoleOut = None, ConsoleError = None, ConsoleLevel = 0):

        if ConsoleOut:
            Consoleger.__displayout = ConsoleOut

        if ConsoleError:
            Consoleger.__displayerror = ConsoleError

        if ConsoleLevel >= 0 and ConsoleLevel <= 3:
            Consoleger.__displaylevel = ConsoleLevel



    #----------------------------------------------------------------------
    @staticmethod
    def __display(message):
        """
        Write a message into output

        :param message: message to write
        :type message: str
        """
        try:
            if message:
                Console.__displayout.writelines("%s\n" % message)
                Console.__displayout.flush()
        except Exception,e:
            print "[!] Error while writen into output file or console: %s" % e.message

    #----------------------------------------------------------------------
    @staticmethod
    def display(message):
        """
        Write a message into output

        :param message: message to write
        :type message: str
        """
        if Console.__displaylevel == Console.MORE_VERBOSE or Console.__displaylevel == Console.VERBOSE or Console.__displaylevel == Console.STANDARD:
            Console.__display(message)

    #----------------------------------------------------------------------
    @staticmethod
    def display_verbose(self, message):
        """
        Write a message into output with more verbosity

        :param message: message to write
        :type message: str
        """
        if Console.__displaylevel == Console.MORE_VERBOSE or Console.__displaylevel == Console.VERBOSE:
            Console.__display(message)

    #----------------------------------------------------------------------
    @staticmethod
    def display_more_verbose(self, message):
        """
        Write a message into output with even more verbosity

        :param message: message to write
        :type message: str
        """
        if Console.__displaylevel == Console.MORE_VERBOSE:
            Console.__display(message)


    #----------------------------------------------------------------------
    @staticmethod
    def __display_error(message):
        """
        Write a error message into output

        :param message: message to write
        :type message: str"""
        try:
            if message:
                Console.__displayerror.writelines("%s\n" % message)
                Console.__displayerror.flush()
        except Exception,e:
            print "[!] Error while writen into output file or console: %s" % e.message


    #----------------------------------------------------------------------
    @staticmethod
    def display_error(message):
        """
        Write a error message into output

        :param message: message to write
        :type message: str"""
        if Console.__displaylevel == Console.MORE_VERBOSE or Console.__displaylevel == Console.VERBOSE or Console.__displaylevel == Console.STANDARD:
            Console.__displayerror(message)

    #----------------------------------------------------------------------
    @staticmethod
    def display_error_verbose(message):
        """
        Write a error message into output with more verbosity

        :param message: message to write
        :type message: str
        """
        if Console.__displaylevel == Console.VERBOSE or Console.__displaylevel == Console.STANDARD:
            Console.__displayerror(message)

