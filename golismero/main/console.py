#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

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

__all__ = ["Console"]

from ..api.logger import Logger

# do not use the "from sys import" form, or coloring won't work on Windows
import sys

from colorizer import colored


#----------------------------------------------------------------------
# Map of colors
m_colors = {

    # String log levels to color names
    'info': 'green',
    'low': 'cyan',
    'middle': 'white',
    'high' :'red',
    'critical' : 'yellow',

    # Integer log levels to color names
    0: 'green',
    1: 'cyan',
    2: 'magenta',
    3: 'red',
    4: 'yellow',

    # Color names mapped to themselves
    'green': 'green',
    'cyan': 'cyan',
    'magenta': 'magenta',
    'red': 'red',
    'yellow': 'yellow',
}


#----------------------------------------------------------------------
def colorize_substring(text, substring, level_or_color):
    """
    Colorize a substring in a text depends of type of alert:
    - Information
    - Low
    - Middle
    - Hight
    - Critical

    :param text: orginal text
    :type text: str

    :param text: subtext to colorize.
    :type text: int with level (0-4) or string with values: info, low, middle, high, critical.

    :param level_or_color: color name or integer with level selected.
    :type level_or_color: str or integer (0-4).

    :returns: str -- string with information to print.
    """

    #
    # XXX TODO:
    #
    # We also probably need to parse existing ANSI escape codes
    # to know what's the color of the surrounding text, otherwise
    # we'll only properly colorize substrings in non colored text.
    #
    # Maybe we can settle with this: indicate a color for the text
    # and a color for the substring. Should work in all situations
    # we _currently_ need to handle.
    #

    # Check for trivial cases.
    if text and substring and Console.use_colors:

        # XXX HACK
        # Instead of calling colorize() it's faster
        # to call colored() directly. That means we'll
        # have to convert level_or_color to the value
        # that colored() expects.
        color = m_colors[level_or_color]

        # Loop for each occurrence of the substring.
        m_pos = 0
        while 1:

            # Find the substring in the text.
            m_pos = text.find(substring, m_pos)

            # If not found, break out of the loop.
            if m_pos < 0:
                break

            # Split the text where the substring was found.
            m_prefix  = text[:m_pos]
            m_content = text[m_pos: m_pos + len(substring)]
            m_suffix  = text[m_pos + len(substring):]

            # Patch the text to colorize the substring.
            ##m_content = colorize(m_content, level_or_color) # XXX HACK
            m_content = colored(m_content, color)             # See above
            text = "%s%s%s" % (m_prefix, m_content, m_suffix)

            # Update the current position and keep searching.
            m_pos = len(m_prefix) + len(m_content)

    # Return the patched text.
    return text


#----------------------------------------------------------------------
def colorize(text, level_or_color):
    """
    Colorize a text depends of type of alert:
    - Information
    - Low
    - Middle
    - High
    - Critical

    :param text: text to colorize.
    :type text: int with level (0-4) or string with values: info, low, middle, high, critical.

    :param level_or_color: color name or integer with level selected.
    :type level_or_color: str or integer (0-4).

    :returns: str -- string with information to print.
    """
    if Console.use_colors:
        return colored(text, m_colors[level_or_color])
    else:
        return text


#----------------------------------------------------------------------
class Console (object):
    """
    Console I/O wrapper.
    """


    #----------------------------------------------------------------------
    # Verbose levels

    DISABLED     = Logger.DISABLED
    STANDARD     = Logger.STANDARD
    VERBOSE      = Logger.VERBOSE
    MORE_VERBOSE = Logger.MORE_VERBOSE

    # Current verbose level
    level = STANDARD

    # Use colors?
    use_colors = True


    #----------------------------------------------------------------------
    @classmethod
    def _display(cls, message):
        """
        Write a message into output

        :param message: message to write
        :type message: str
        """
        try:
            if message:
                sys.stdout.write("%s\n" % message)
                sys.stdout.flush()
        except Exception,e:
            print "[!] Error while writing to output onsole: %s" % e.message


    #----------------------------------------------------------------------
    @classmethod
    def display(cls, message):
        """
        Write a message into output

        :param message: message to write
        :type message: str
        """
        if  cls.level >= cls.STANDARD:
            cls._display(message)


    #----------------------------------------------------------------------
    @classmethod
    def display_verbose(cls, message):
        """
        Write a message into output with more verbosity

        :param message: message to write
        :type message: str
        """
        if cls.level >= cls.VERBOSE:
            cls._display(message)


    #----------------------------------------------------------------------
    @classmethod
    def display_more_verbose(cls, message):
        """
        Write a message into output with even more verbosity

        :param message: message to write
        :type message: str
        """
        if cls.level >= cls.MORE_VERBOSE:
            cls._display(message)


    #----------------------------------------------------------------------
    @classmethod
    def _display_error(cls, message):
        """
        Write a error message into output

        :param message: message to write
        :type message: str
        """
        try:
            if message:
                sys.stderr.write("%s\n" % message)
                sys.stderr.flush()
        except Exception,e:
            print "[!] Error while writing to error console: %s" % e.message


    #----------------------------------------------------------------------
    @classmethod
    def display_error(cls, message):
        """
        Write a error message into output

        :param message: message to write
        :type message: str
        """
        if cls.level >= cls.STANDARD:
            cls._display_error(message)


    #----------------------------------------------------------------------
    @classmethod
    def display_error_verbose(cls, message):
        """
        Write a error message into output with more verbosity

        :param message: message to write
        :type message: str
        """
        if cls.level >= cls.VERBOSE:
            cls._display_error(message)


    #----------------------------------------------------------------------
    @classmethod
    def display_error_more_verbose(cls, message):
        """
        Write a error message into output with more verbosity

        :param message: message to write
        :type message: str
        """
        if cls.level >= cls.MORE_VERBOSE:
            cls._display_error(message)
