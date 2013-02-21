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

__all__ = ["Logger"]

from sys import stdout, stderr

class Logger (object):
    """
    Simple logging mechanism.
    """


    #----------------------------------------------------------------------
    #
    # Verbose levels
    #
    #----------------------------------------------------------------------
    DISABLED     = 0
    STANDARD     = 1
    VERBOSE      = 2
    MORE_VERBOSE = 3

    _f_out   = stdout
    _f_error = stderr
    _level   = STANDARD


    #----------------------------------------------------------------------
    def __new__(cls, *argv, **argd):
        """
        This is a static class!
        """
        raise NotImplementedError("This is a static class!")


    #----------------------------------------------------------------------
    @classmethod
    def configure(cls, stdout   = None,
                       stderror = None,
                       level    = None):
        if stdout   is not None: cls._f_out   = stdout
        if stderror is not None: cls._f_error = stderror
        if level    is not None: cls._level   = level


    #----------------------------------------------------------------------
    @classmethod
    def _log(cls, message):
        """
        Write a message into output

        :param message: message to write
        :type message: str
        """
        try:
            if message:
                cls._f_out.write("%s\n" % message)
                cls._f_out.flush()
        except Exception,e:
            print "[!] Error while writing to output onsole: %s" % e.message


    #----------------------------------------------------------------------
    @classmethod
    def log(cls, message):
        """
        Write a message into output

        :param message: message to write
        :type message: str
        """
        if  cls._level != cls.DISABLED:
            cls._log(message)


    #----------------------------------------------------------------------
    @classmethod
    def log_verbose(cls, message):
        """
        Write a message into output with more verbosity

        :param message: message to write
        :type message: str
        """
        if cls._level >= cls.VERBOSE:
            cls._log(message)


    #----------------------------------------------------------------------
    @classmethod
    def log_more_verbose(cls, message):
        """
        Write a message into output with even more verbosity

        :param message: message to write
        :type message: str
        """
        if cls._level >= cls.MORE_VERBOSE:
            cls._log(message)


    #----------------------------------------------------------------------
    @classmethod
    def _log_error(cls, message):
        """
        Write a error message into output

        :param message: message to write
        :type message: str
        """
        try:
            if message:
                cls._f_error.write("%s\n" % message)
                cls._f_error.flush()
        except Exception,e:
            print "[!] Error while writing to error console: %s" % e.message


    #----------------------------------------------------------------------
    @classmethod
    def log_error(cls, message):
        """
        Write a error message into output

        :param message: message to write
        :type message: str
        """
        if cls._level != cls.DISABLED:
            cls._log_error(message)


    #----------------------------------------------------------------------
    @classmethod
    def log_error_verbose(cls, message):
        """
        Write a error message into output with more verbosity

        :param message: message to write
        :type message: str
        """
        if cls._level >= cls.VERBOSE:
            cls._log_error(message)


    #----------------------------------------------------------------------
    @classmethod
    def log_error_more_verbose(cls, message):
        """
        Write a error message into output with more verbosity

        :param message: message to write
        :type message: str
        """
        if cls._level >= cls.MORE_VERBOSE:
            cls._log_error(message)
