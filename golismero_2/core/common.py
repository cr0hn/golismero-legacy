#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com
  Mario Vilas | mvilas@gmail.com

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

__all__ = [
    "get_user_settings_folder",
    "Singleton", "enum", "decorator", "pickle",
    "ConfigFileParseError", "GlobalParams"
]

try:
    import cPickle as pickle
except ImportError:
    import pickle

# Lazy import
json_decode = None

from keyword import iskeyword
from os import path

import os
import hashlib

try:
    from decorator import decorator
except ImportError:
    import functools
    def decorator(w):
        """
        The decorator module was not found. You can install it from:
        http://pypi.python.org/pypi/decorator/
        """
        def d(fn):
            @functools.wraps(fn)
            def x(*argv, **argd):
                return w(fn, *argv, **argd)
            return x
        return d


#--------------------------------------------------------------------------
_user_settings_folder = None
def get_user_settings_folder():
    """
    Get the current user's GoLismero settings folder.

    This folder will be used to store the various caches
    and the user-defined plugins.
    """

    # TODO: on Windows, use the roaming data folder instead.

    # Return the cached value if available.
    global _user_settings_folder
    if _user_settings_folder:
        return _user_settings_folder

    # Get the user's home folder.
    home = os.getenv("HOME")              # Unix
    if not home:
        home = os.getenv("USERPROFILE")   # Windows

        # If all else fails, use the current directory.
        if not home:
            home = os.getcwd()

    # Get the user settings folder.
    folder = path.join(home, ".golismero")

    # Make sure it ends with a slash.
    if not folder.endswith(path.sep):
        folder += path.sep

    # Make sure it exists.
    try:
        os.makedirs(folder)
    except Exception:
        pass

    # Cache the folder.
    _user_settings_folder = folder

    # Return the folder.
    return folder


#--------------------------------------------------------------------------
def enum(*sequential, **named):
    "Enumerated type"
    values = dict(zip(sequential, range(len(sequential))), **named)
    numbers = values.values()
    values['_values'] = values
    values['_first']  = min(numbers)
    values['_last']   = max(numbers)
    return type('Enum', (), values)


#--------------------------------------------------------------------------
class Singleton (object):
    """
    Implementation of the Singleton pattern.
    """

    # Variable where we keep the instance.
    _instance = None

    def __new__(cls):

        # If the singleton has already been instanced, return it.
        if cls._instance is not None:
            return cls._instance

        # Create the singleton's instance.
        cls._instance = super(Singleton, cls).__new__(cls)

        # Call the constructor.
        cls.__init__(cls._instance)

        # Delete the constructor so it won't be called again.
        cls._instance.__init__ = object.__init__
        cls.__init__ = object.__init__

        # Return the instance.
        return cls._instance


#--------------------------------------------------------------------------
class Configuration (object):
    """
    Generic configuration class.
    """

    # Here's where subclasses define the options.
    #
    # It's a list of tuples of the following format:
    #
    #   ( name, parser, default )
    #
    # Where "name" is the option name, "parser" is an optional
    # callback to parse the input values, and "default" is an
    # optional default value.
    #
    # If no parser is given, the values are preserved when set.
    #
    # Example:
    #    class MySettings(Configuration):
    #        _settings_  = (
    #            ("verbose", int, 0),   # A complete definition.
    #            ("output_file", str),  # Omitting the default value (None is used).
    #            "data",                # Omitting the parser too (values won't be filtered).
    #        )
    #
    _settings_ = ()


    #----------------------------------------------------------------------
    def __init__(self):
        self.__setter = dict()
        history = set()
        for option in self._settings_:
            if isinstance(option, str):
                option = (option,)
            if option[0] in history:
                raise SyntaxError("Duplicated option name: %r" % option[0])
            history.add(option[0])
            self.__init_option(*option)


    #----------------------------------------------------------------------
    def __init_option(self, name, parser = None, default = None):
        if name.endswith("_") or not name.replace("_", "").isalnum():
            msg = "Option name %r is not a valid Python identifier"
            raise SyntaxError(msg % name)
        if iskeyword(name):
            msg = "Option name %r is a Python reserved keyword"
            raise SyntaxError(msg % name)
        if name.startswith("__"):
            msg = "Option name %r is a private Python identifier"
            raise SyntaxError(msg % name)
        if name.startswith("_"):
            msg = "Option name %r is a protected Python identifier"
            raise SyntaxError(msg % name)
        if parser is not None:
            self.__setter[name] = parser
        setattr(self, name, default)


    #----------------------------------------------------------------------
    def __setattr__(self, name, value):
        try:
            parser = self.__setter.get(name, None)
        except AttributeError:
            parser = None
        if parser is not None:
            value = parser(value)
        object.__setattr__(self, name, value)


    #----------------------------------------------------------------------
    def from_dictionary(self, args):
        """
        Get the settings from a Python dictionary.

        :param args: Settings.
        :type args: dict
        """
        for option in self._settings_:
            if isinstance(option, str):
                option = (option,)
            name = option[0]
            default = getattr(self, name)
            value = args.get(name, default)
            setattr(self, name, value)


    #----------------------------------------------------------------------
    def from_object(self, args):
        """
        Get the settings from the attributes of a Python object.

        :param args: Python object, for example the command line arguments parsed by argparse.
        :type args: object
        """

        # Builds a dictionary with the object's public attributes.
        args = { k : getattr(args, k) for k in dir(args) if not k.startswith("_") }

        # Extract the settings from the dictionary.
        self.from_dictionary(args)


    #----------------------------------------------------------------------
    def from_json(self, json_raw_data):
        """
        Get the settings from a JSON encoded dictionary.

        :param json_raw_data: JSON raw data.
        :type json_raw_data: str
        """

        # Lazy import of the JSON decoder function.
        global json_decode
        if json_decode is None:
            try:
                # The fastest JSON parser available for Python.
                import cjson.decode as json_decode
            except ImportError:
                try:
                    # Faster than the built-in module, usually found.
                    import simplejson.loads as json_decode
                except ImportError:
                    # Built-in module since Python 2.6, very very slow!
                    import json.loads as json_decode

        # Converts the JSON data into a dictionary.
        args = json_decode(json_raw_data)
        if not isinstance(args, dict):
            raise TypeError("Invalid JSON data")

        # Extract the settings from the dictionary.
        self.from_dictionary(args)


#----------------------------------------------------------------------
#
# Global options parser
#
#----------------------------------------------------------------------


#----------------------------------------------------------------------
# The option parsers:

def _parse_string(x):
    return str(x) if x is not None else None

def _parse_trinary(x):
    if x not in (None, True, False):
        raise SyntaxError("Trinary values only accept True, False and None")
    return x

def _parse_run_mode(run_mode):
    run_mode = run_mode.strip().lower()
    if not run_mode in GlobalParams.RUN_MODE._values:
        raise ValueError("Invalid run mode: %s" % run_mode)
    return getattr(GlobalParams.RUN_MODE, run_mode)

def _parse_user_interface(user_interface):
    user_interface = user_interface.strip().lower()
    if not user_interface in GlobalParams.USER_INTERFACE._values:
        raise ValueError("Invalid user interface mode: %s" % user_interface)
    return getattr(GlobalParams.USER_INTERFACE, user_interface)

def _parse_output_formats(output_formats):
    if output_formats:
        try:
            output_formats = [getattr(GlobalParams.REPORT_FORMAT, fmt.strip().lower())
                              for fmt in output_formats]
        except AttributeError:
            raise ValueError("Invalid output format: %s" % fmt)
    else:
        output_formats = []
    return output_formats

def _parse_cookie(cookie):
    if cookie:
        # Parse the cookies argument
        try:
            # Prepare cookie
            m_cookie = cookie.replace(" ", "").replace("=", ":")
            # Remove 'Cookie:' start, if exits
            m_cookie = m_cookie[len("Cookie:"):] if m_cookie.startswith("Cookie:") else m_cookie
            # Split
            m_cookie = m_cookie.split(";")
            # Parse
            self.cookie = { c.split(":")[0]:c.split(":")[1] for c in m_cookie}
        except ValueError:
            raise ValueError("Invalid cookie format specified. Use this format: 'Key=value; key=value'.")
    else:
        cookie = None
    return cookie


#--------------------------------------------------------------------------
class GlobalParams (Configuration):
    """
    Global parameters for the program.
    """

    # The logic in this class is always:
    # - Checking options without fixing them is done in check_params().
    # - Sanitizing (fixing) options is done in setters.
    # - For each source, there's a "from_*" method. They add to the
    #   current options rather than overwriting them completely.
    #   This allows options to be read from multiple sources.


    # Run modes
    RUN_MODE = enum('standalone', 'master', 'slave')

    # User interface
    USER_INTERFACE = enum('console')

    # Report formats
    REPORT_FORMAT = enum('screen', 'text', 'grepable', 'html')


    #----------------------------------------------------------------------
    # The options definitions:
    #
    _settings_ = (

        #
        # Main options
        #

        # Targets
        ("targets", None, []),

        # Run mode
        ("run_mode", _parse_run_mode, "standalone"),

        # UI mode
        ("user_interface", _parse_user_interface, "console"),

        # Verbosity level
        ("verbose", int, 1),

        # Colorize console?
        ("colorize", bool, True),

        #
        # Report options
        #
        ("output_file", _parse_string),
        ("output_formats", _parse_output_formats, ["screen"]),


        #
        # Audit options
        #

        # Audit name
        ("audit_name", _parse_string),

        # Audit database
        ("audit_db", None, "memory://"),

        # Maximum number of processes to execute plugins
        ("max_process", int, 10),

        #
        # Plugins options
        #

        # Enabled plugins
        ("enabled_plugins", list, ["global", "testing", "report", "ui/console"]),

        # Disabled plugins
        ("disabled_plugins", list, ["all"]),

        # Plugins folder
        ("plugins_folder", _parse_string),

        #
        # Networks options
        #

        # Maximum number of connection, by host
        ("max_connections", int, 50),

        # Include subdomains?
        ("include_subdomains", bool, True),

        # Subdomains as regex expresion
        ("subdomain_regex", _parse_string),

        # Depth level for spider
        ("depth", int, 0),

        # Follow redirects
        ("follow_redirects", bool, True),

        # Follow only first redirect
        ("follow_first_redirect", bool, True),

        # Proxy options
        ("proxy_addr", _parse_string),
        ("proxy_user", _parse_string),
        ("proxy_pass", _parse_string),

        # Cookie
        ("cookie", _parse_cookie),

        # Use persistent cache?
        # True: yes
        # False: no
        # None: default for current run mode
        ("use_cache_db", _parse_trinary),
    )

    @property
    def targets(self):
        return self._targets

    @targets.setter
    def targets(self, targets):
        # Always append, never overwrite
        # Fix target URLs if the scheme part is missing
        self._targets = getattr(self, "_targets", [])
        self._targets.extend((x if x.startswith("http://") else "http://" + x) for x in targets)

    @targets.deleter
    def targets(self):
        self._targets = []


    #----------------------------------------------------------------------
    def check_params(self):
        """
        Check if parameters are valid. Raises an exception otherwise.

        This method only checks the validity of the arguments, it won't modify them.

        :raises: ValueError
        """

        # Validate the network connections limit
        if self.max_connections < 1:
            raise ValueError("Number of connections must be greater than 0, got %i." % params.max_connections)

        # Validate the number of concurrent processes
        if self.max_process < 0:
            raise ValueError("Number of processes cannot be a negative number, got %i." % params.max_process)

        # Validate the list of targets
        if not self.targets:
            raise ValueError("No targets selected for execution.")

        # Validate the list of plugins
        if not self.enabled_plugins:
            raise ValueError("No plugins selected for execution.")
        if set(self.enabled_plugins).intersection(self.disabled_plugins):
            raise ValueError("Conflicting plugins selection, aborting execution.")

        # Validate the regular expresion
        if self.subdomain_regex:
            from re import compile, error

            try:
                compile(self.subdomain_regex)
            except error, e:
                raise ValueError("Regular expression not valid: %s." % e.message)

        # Validate the output options
        if not self.output_file and self.REPORT_FORMAT.screen not in self.output_formats:
            raise ValueError("Output format specified, but no output file!")
