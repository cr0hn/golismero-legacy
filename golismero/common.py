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

__all__ = [

    # Dynamically loaded modules, picks the fastest one available.
    "pickle", "random",

    # Helper functions.
    "get_user_settings_folder",

    # Helper classes and decorators.
    "Singleton", "enum", "decorator",

    # Configuration objects.
    "OrchestratorConfig", "AuditConfig"
]

# Load the fast C version of pickle,
# if not available use the pure-Python version.
try:
    import cPickle as pickle
except ImportError:
    import pickle

# Load NumPy's random (faster, written in C) if available,
# otherwise use the built-in but slower random module.
try:
    import numpy.random as random
except ImportError:
    import random

# Lazy import of the JSON decoder.
json_decode = None

# Import @decorator from the decorator module, if available.
# Otherwise define a simple but crude replacement.
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

# Other imports.
from keyword import iskeyword
from os import path

import os
import hashlib


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

    #----------------------------------------------------------------------
    # The logic in configuration classes is always:
    # - Checking options without fixing them is done in check_params().
    # - Sanitizing (fixing) options is done in parsers or in property setters.
    # - For each source, there's a "from_*" method. They add to the
    #   current options rather than overwriting them completely.
    #   This allows options to be read from multiple sources.

    #----------------------------------------------------------------------
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
    #        _settings_  = {
    #            "verbose": (int, 0), # A complete definition.
    #            "output_file": str,  # Omitting the default value (None is used).
    #            "data": None,        # Omitting the parser too.
    #        }
    #
    _settings_ = {}


    #----------------------------------------------------------------------
    # Some helper parsers.

    @staticmethod
    def string(x):
        return str(x) if x is not None else None

    @staticmethod
    def trinary(x):
        if x not in (None, True, False):
            raise SyntaxError("Trinary values only accept True, False and None")
        return x


    #----------------------------------------------------------------------
    def __init__(self):
        history = set()
        for name, definition in self._settings_.iteritems():
            if name in history:
                raise SyntaxError("Duplicated option name: %r" % name)
            history.add(name)
            if type(definition) not in (tuple, list):
                definition = (definition, None)
            self.__init_option(name, *definition)


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
        setattr(self, name, default)


    #----------------------------------------------------------------------
    def __setattr__(self, name, value):
        if not name.startswith("_"):
            definition = self._settings_.get(name, (None, None))
            if type(definition) not in (tuple, list):
                definition = (definition, None)
            parser = definition[0]
            if parser is not None:
                value = parser(value)
        object.__setattr__(self, name, value)


    #----------------------------------------------------------------------
    def check_params(self):
        """
        Check if parameters are valid. Raises an exception otherwise.

        This method only checks the validity of the arguments, it won't modify them.

        :raises: ValueError
        """
        return


    #----------------------------------------------------------------------
    def from_dictionary(self, args):
        """
        Get the settings from a Python dictionary.

        :param args: Settings.
        :type args: dict
        """
        for name, value in args.iteritems():
            if name in self._settings_:
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

class OrchestratorConfig (Configuration):
    """
    Orchestator configuration object.
    """

    # Run modes
    RUN_MODE = enum('standalone', 'master', 'slave')


    #----------------------------------------------------------------------
    # The options definitions:
    #
    _settings_ = {

        #
        # Main options
        #

        # Run mode
        "run_mode": (str, "standalone"),

        # UI mode
        "ui_mode": (str, "console"),

        # Verbosity level
        "verbose": (int, 1),

        # Colorize console?
        "colorize": (bool, True),

        #
        # Plugins options
        #

        # Enabled plugins
        "enabled_plugins": (list, ["global", "testing", "report", "ui/console"]),

        # Disabled plugins
        "disabled_plugins": (list, ["all"]),

        # Plugins folder
        "plugins_folder": Configuration.string,

        # Maximum number of processes to execute plugins
        "max_process": (int, 10),

        #
        # Networks options
        #

        # Maximum number of connections per host
        "max_connections": (int, 50),

        # Use persistent cache?
        # True: yes
        # False: no
        # None: default for current run mode
        "use_cache_db": Configuration.trinary,
    }


    #----------------------------------------------------------------------

    @property
    def run_mode(self):
        return self._run_mode

    @run_mode.setter
    def run_mode(self, run_mode):
        run_mode = run_mode.strip().lower()
        if not run_mode in self.RUN_MODE._values:
            raise ValueError("Invalid run mode: %s" % run_mode)
        self._run_mode = getattr(self.RUN_MODE, run_mode)


    #----------------------------------------------------------------------
    def check_params(self):

        # Validate the network connections limit
        if self.max_connections < 1:
            raise ValueError("Number of connections must be greater than 0, got %i." % params.max_connections)

        # Validate the number of concurrent processes
        if self.max_process < 0:
            raise ValueError("Number of processes cannot be a negative number, got %i." % params.max_process)

        # Validate the list of plugins
        if not self.enabled_plugins:
            raise ValueError("No plugins selected for execution.")
        if set(self.enabled_plugins).intersection(self.disabled_plugins):
            raise ValueError("Conflicting plugins selection, aborting execution.")


#----------------------------------------------------------------------
#
# Audit options parser
#
#----------------------------------------------------------------------

class AuditConfig (Configuration):
    """
    Audit configuration object.
    """


    #----------------------------------------------------------------------
    # The options definitions:
    #
    _settings_ = {

        #
        # Main options
        #

        # Targets
        "targets": (list, []),

        #
        # Report options
        #
        "reports": (list, []),

        #
        # Audit options
        #

        # Audit name
        "audit_name": Configuration.string,

        # Audit database
        "audit_db": (None, "memory://"),

        #
        # Plugins options
        #

        # Enabled plugins
        "enabled_plugins": (list, ["testing", "report"]),

        # Disabled plugins
        "disabled_plugins": (list, ["all"]),

        #
        # Networks options
        #

        # Include subdomains?
        "include_subdomains": (bool, True),

        # Subdomains as regular expression
        "subdomain_regex": Configuration.string,

        # Depth level for spider
        "depth": (int, 0),
        # Limits
        "max_links" : (int, 0), # 0 -> infinite

        # Follow redirects
        "follow_redirects": (bool, True),

        # Follow only first redirect
        "follow_first_redirect": (bool, True),

        # Proxy options
        "proxy_addr": Configuration.string,
        "proxy_user": Configuration.string,
        "proxy_pass": Configuration.string,

        # Cookie
        "cookie": Configuration.string,
    }


    #----------------------------------------------------------------------

    @property
    def targets(self):
        return self._targets

    @targets.setter
    def targets(self, targets):
        # Always append, never overwrite
        # Fix target URLs if the scheme part is missing
        self._targets = getattr(self, "_targets", [])
        if targets:
            self._targets.extend(
                (x if x.startswith("http://") else "http://" + x)
                for x in targets)


    #----------------------------------------------------------------------

    @property
    def reports(self):
        return self._reports

    @reports.setter
    def reports(self, reports):
        # Always append, never overwrite
        self._reports = getattr(self, "_reports", [])
        if reports:
            self._reports.extend(
                (str(x) if x is not None else None) for x in reports)


    #----------------------------------------------------------------------

    @property
    def cookie(self):
        return self._cookie

    @cookie.setter
    def cookie(self, cookie):
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
        self._cookie = cookie


    #----------------------------------------------------------------------
    def check_params(self):

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

        # Validate number
