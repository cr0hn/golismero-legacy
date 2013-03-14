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

#-----------------------------------------------------------------------
# Remote logging API
#-----------------------------------------------------------------------

__all__ = ["Logger"]

from .config import Config
from ..messaging.message import Message


class Logger (object):
    """
    Simple logging mechanism.
    """


    #----------------------------------------------------------------------
    # Verbose levels

    DISABLED     = 0
    STANDARD     = 1
    VERBOSE      = 2
    MORE_VERBOSE = 3

    _level = STANDARD


    #----------------------------------------------------------------------
    def __new__(cls, *argv, **argd):
        """
        This is a static class!
        """
        raise NotImplementedError("This is a static class!")


    #----------------------------------------------------------------------
    @classmethod
    def set_level(cls, level = STANDARD):
        """
        Set the current log level.

        :param level: One of the log level constants defined in this class.
        :type level: int
        """
        cls._level = level


    #----------------------------------------------------------------------
    @classmethod
    def get_level(cls):
        """
        Get the current log level.

        :returns: int -- Current log level.
        """
        return cls._level


    #----------------------------------------------------------------------
    @classmethod
    def check_level(cls, level):
        """
        Determine if the current log level is at least the one given.

        :returns: bool - True if the log level is at least the one given.
        """
        return cls._level >= level


    #----------------------------------------------------------------------
    @classmethod
    def _log(cls, message, is_error = False):
        """
        Write a message into output

        :param message: message to write
        :type message: str
        """
        try:
            if message:
                if is_error:
                    message_code = Message.MSG_CONTROL_LOG_ERROR
                else:
                    message_code = Message.MSG_CONTROL_LOG_MESSAGE
                Config()._get_context().send_msg(
                    message_type = Message.MSG_TYPE_CONTROL,
                    message_code = message_code,
                    message_info = message)
        except Exception, e:
            if is_error:
                print "[!] Error while writing to error console: %s" % e.message
            else:
                print "[!] Error while writing to output console: %s" % e.message


    #----------------------------------------------------------------------
    @classmethod
    def log(cls, message):
        """
        Write a message into output

        :param message: message to write
        :type message: str
        """
        if  cls._level >= cls.STANDARD:
            cls._log(message, is_error = False)


    #----------------------------------------------------------------------
    @classmethod
    def log_verbose(cls, message):
        """
        Write a message into output with more verbosity

        :param message: message to write
        :type message: str
        """
        if cls._level >= cls.VERBOSE:
            cls._log(message, is_error = False)


    #----------------------------------------------------------------------
    @classmethod
    def log_more_verbose(cls, message):
        """
        Write a message into output with even more verbosity

        :param message: message to write
        :type message: str
        """
        if cls._level >= cls.MORE_VERBOSE:
            cls._log(message, is_error = False)


    #----------------------------------------------------------------------
    @classmethod
    def log_error(cls, message):
        """
        Write a error message into output

        :param message: message to write
        :type message: str
        """
        if cls._level >= cls.STANDARD:
            cls._log(message, is_error = True)


    #----------------------------------------------------------------------
    @classmethod
    def log_error_verbose(cls, message):
        """
        Write a error message into output with more verbosity

        :param message: message to write
        :type message: str
        """
        if cls._level >= cls.VERBOSE:
            cls._log(message, is_error = True)


    #----------------------------------------------------------------------
    @classmethod
    def log_error_more_verbose(cls, message):
        """
        Write a error message into output with more verbosity

        :param message: message to write
        :type message: str
        """
        if cls._level >= cls.MORE_VERBOSE:
            cls._log(message, is_error = True)
