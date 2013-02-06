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


from sys import stdout, stderr

class IOConsole():
    """"""

    __logout = stdout
    __logerror = stderr
    __loglevel = 1 # standard

    #----------------------------------------------------------------------
    #
    # Log levels
    #
    #----------------------------------------------------------------------
    DISABLED = 0
    STANDARD = 1
    VERBOSE = 2
    MORE_VERBOSE = 3


    #----------------------------------------------------------------------
    @staticmethod
    def configure(LogOut = None, LogError = None, logLevel = 0):

        if LogOut:
            IOConsole.__logout = LogOut

        if LogError:
            IOConsole.__logerror = LogError

        if logLevel >= 0 and logLevel <= 3:
            IOConsole.__loglevel = logLevel



    #----------------------------------------------------------------------
    @staticmethod
    def __log(message):
        """
        Write a message into log

        :param message: message to write
        :type message: str
        """
        try:
            if message:
                IOConsole.__logout.writelines(message)
        except Exception,e:
            print "[!] Error while writen into log file or console: %s" % e.message

    #----------------------------------------------------------------------
    @staticmethod
    def log(message):
        """
        Write a message into log

        :param message: message to write
        :type message: str
        """
        if IOConsole.__loglevel == IOConsole.STANDARD:
            IOConsole.__log(message)

    #----------------------------------------------------------------------
    @staticmethod
    def log_more_verbose(self, message):
        """
        Write a message into log with even more verbosity

        :param message: message to write
        :type message: str
        """
        if IOConsole.__loglevel == IOConsole.MORE_VERBOSE:
            IOConsole.__log(message)


    #----------------------------------------------------------------------
    @staticmethod
    def log_verbose(self, message):
        """
        Write a message into log with more verbosity

        :param message: message to write
        :type message: str
        """
        if IOConsole.__loglevel == IOConsole.VERBOSE:
            IOConsole.__log(message)





    #----------------------------------------------------------------------
    @staticmethod
    def __log_error(message):
        """
        Write a error message into log

        :param message: message to write
        :type message: str"""
        try:
            if message:
                IOConsole.__logerror.writelines(message)
        except Exception,e:
            print "[!] Error while writen into log file or console: %s" % e.message


    #----------------------------------------------------------------------
    @staticmethod
    def log_error(message):
        """
        Write a error message into log

        :param message: message to write
        :type message: str"""
        if IOConsole.__logerror == IOConsole.STANDARD:
            IOConsole.__logerror(message)

    #----------------------------------------------------------------------
    @staticmethod
    def log_error_verbose(message):
        """
        Write a error message into log with more verbosity

        :param message: message to write
        :type message: str
        """
        if IOConsole.__logerror == IOConsole.VERBOSE:
            IOConsole.__logerror(message)


    #----------------------------------------------------------------------
    @staticmethod
    def log_error_more_verbose(message):
        """
        Write a error message into log with even more verbosity

        :param message: message to write
        :type message: str
        """
        if IOConsole.__logerror == IOConsole.MORE_VERBOSE:
            IOConsole.__logerror(message)
