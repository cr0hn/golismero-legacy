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

__all__ = [
    "get_unique_id", "enum",
    "Singleton",
    "ConfigFileParseError", "GlobalParams"
]

try:
    import cPickle as pickle
except ImportError:
    import pickle

# Lazy import
json_decode = None

from os import path

import hashlib


#--------------------------------------------------------------------------
def get_unique_id(obj):
    """
    Get a unique ID for this object.
    """

    # Pickle the object with the compatibility protocol.
    # This produces always the same result for the same input data.
    data = pickle.dumps(obj, protocol=0)

    # Calculate the MD5 hash of the pickled data.
    hash_sum = hashlib.md5(data)

    # Return the hexadecimal digest of the hash.
    return hash_sum.hexdigest()


#--------------------------------------------------------------------------
def enum(*sequential, **named):
    "Enumerated type"
    values = dict(zip(sequential, range(len(sequential))), **named)
    values['_values'] = values
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
#
# AUDIT CONFIGURATION
#
#--------------------------------------------------------------------------
class ConfigFileParseError (RuntimeError):
    pass

class GlobalParams (object):
    """
    Global parameters for the program.
    """

    # Run modes
    RUN_MODE = enum('standalone', 'cloudclient', 'cloudserver')

    # User interface
    USER_INTERFACE = enum('console')


    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor."""

        #
        # Main options
        #

        # Targets
        self.targets = []

        # Run mode
        self.run_mode = GlobalParams.RUN_MODE.standalone

        # UI mode
        self.user_interface = GlobalParams.USER_INTERFACE.console

        # Set verbosity level
        self.verbose = 1

        # Colorize console?
        self.colorize = True

        #
        # Report options
        #
        self.output_file = None
        self.output_formats = []


        #
        # Audit options
        #

        # Audit name
        self.audit_name = ""

        # Audit database
        self.audit_db = "memory://"

        # Maximum number of processes to execute plugins
        self.max_process = 10

        #
        # Plugins options
        #

        # Enabled plugins
        self.plugins = None

        # Plugins folder
        self.plugins_folder = None

        #
        # Networks options
        #

        # Maximum number of connection, by host
        self.max_connections = 50

        # Include subdomains?
        self.include_subdomains = True

        # Subdomains as regex expresion
        self.subdomain_regex = ""

        # Recursivity level for spider
        self.recursivity = 0

        # Follow redirects
        self.follow_redirects = False

        # Follow only first redirect
        self.follow_first_redirect = True


    #----------------------------------------------------------------------
    def check_params(self):
        """
        Check if parameters are valid. Raises an exception otherwise.

        :raises: ValueError
        """

        # Check max connections
        if self.max_connections < 1:
            raise ValueError("Number of connections must be greater than 0, got %i." % params.max_connections)

        # Check max process
        if self.max_process < 0:
            raise ValueError("Number of processes cannot be a negative number, got %i." % params.max_process)

        # Check plugins selected
        if not self.targets:
            raise ValueError("No targets selected for execution.")

        # Check plugins selected
        if self.plugins is not None and not self.plugins:
            raise ValueError("No plugins selected for execution.")

        # Check regular expresion
        if self.subdomain_regex:
            from re import compile, error

            try:
                compile(self.subdomain_regex)
            except error, e:
                raise ValueError("Regular expression not valid: %s." % e.message)

        # Check for outputs restrictions
        if (not self.output_file and self.output_formats) \
           or (self.output_file and not self.output_formats):
            raise ValueError("When you specify '-o' also need to set format option '-of'.")


    #----------------------------------------------------------------------
    def from_dictionary(self, args):
        """
        Get the settings from a Python dictionary.

        :param args: Settings.
        :type args: dict
        """

        #
        # Main options
        #

        # Get the run mode
        if "run_mode" in args:
            self.run_mode = getattr(self.RUN_MODE,
                                    args["run_mode"].lower())

        # Get the user interface mode
        if "user_interface" in args:
            self.user_interface = getattr(self.USER_INTERFACE,
                                          args["user_interface"].lower())

        # Get the list of targets
        self.targets = args.get("targets", self.targets)

        # Set verbosity level
        self.verbose = args.get("verbose", self.verbose)

        # Colorize console?
        self.colorize = args.get("colorize", self.colorize)

        #
        # Report options
        #
        self.output_file    = args.get("output_file", self.output_file)
        self.output_formats = args.get("output_formats", self.output_formats)

        #
        # Plugins options
        #

        # Get the list of enabled plugins
        self.plugins = args.get("plugins", self.plugins)

        # Get the plugins folder
        self.plugins_folder = args.get("plugins_folder", self.plugins_folder)

        #
        # Audit options
        #

        # Get the name of the audit
        self.audit_name = args.get("audit_name", self.audit_name)

        # Audit database
        self.audit_db = args.get("audit_db", self.audit_db)

        # Maximum number of processes to execute plugins
        self.max_process = args.get("max_process", self.max_process)

        #
        # Network options
        #

        # Maximum number of connection, by host
        self.max_connections = args.get("max_connections", self.max_connections)

        # Include subdomains?
        self.include_subdomains = args.get("include_subdomains", self.include_subdomains)

        # Subdomains as regex expresion
        self.subdomain_regex = args.get("subdomain_regex", self.subdomain_regex)

        # Recursivity level for spider
        self.recursivity = args.get("recursivity", self.recursivity)

        # Follow redirects
        self.follow_redirects = args.get("follow_redirects", self.follow_redirects)

        # Follow only first redirect
        self.follow_first_redirect = args.get("follow_first_redirect", self.follow_first_redirect)


    #----------------------------------------------------------------------
    def from_cmdline(self, args):
        """
        Get the settings from the command line arguments.

        :param args: Command line arguments parsed by argparse.
        :type args: object
        """

        # Converts the argparse result into a dictionary and parses it.
        self.from_dictionary(dict( (k, getattr(args, k)) for k in dir(args) ))


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

        # Converts the JSON into a dictionary and parses it.
        args = json_decode(json_raw_data)
        if not isinstance(args, dict):
            raise TypeError("Invalid JSON data")
        self.from_dictionary(args)


    #----------------------------------------------------------------------
    def from_file(self, filename, file_history = None):
        """
        Get the settings from a configuration file.

        :param filename: Configuration file name.
        :type filename: str
        """

        # Get the absolute pathname
        filename = path.abspath(filename)

        # Keep track of included files history
        if file_history is None:
            file_history = [filename]

        # Keep track of duplicated options
        opt_history = set()

        # Regular expression to split the command and the arguments
        regexp = re.compile(r'(\S+)\s+(.*)')

        # Open the config file
        with open(filename, 'rU') as fd:
            number = 0
            while 1:

                # Read a line
                line = fd.readline()
                if not line: break
                number += 1

                # Strip the extra whitespace
                line = line.strip()

                # If it's a comment line or a blank line, discard it
                if not line or line.startswith('#'):
                    continue

                # Split the option and its arguments
                match = regexp.match(line)
                if not match:
                    msg = "cannot parse line %d of config file %s"
                    msg = msg % (number, filename)
                    raise ConfigFileParseError(msg)
                key, value = match.groups()

                # Populate the list of targets
                if key == "target":
                    if value and value not in self.targets:
                        self.targets.append(value)

                # Include other config files
                elif key == "include":
                    if value in file_history:
                        found_loop = file_history[ file_history.index(filename) : ]
                        found_loop.append(value)
                        msg = "error parsing line %d of config file %s\ncircular includes in config files:\n\t%s\n"
                        msg %= (number, filename, ",\n\t".join(found_loop))
                        raise ConfigFileParseError(msg)

                else:

                    # Warn about duplicated options
                    if key in opt_history:
                        print "Warning: duplicated option %s in line %d" \
                              " of config file %s" % (key, number, filename)
                        print
                    else:
                        opt_history.add(key)

                    try:

                        # Get the run mode
                        if key == "run_mode":
                            self.run_mode = getattr(self.RUN_MODE,
                                                    value.lower())

                        # Get verbosity level
                        elif key == "verbose":
                            self.verbose = int(value)

                        # Colorize console?
                        elif key == "colorize":
                            self.colorize = self._parse_boolean(value)

                        # Report base filename
                        elif key == "output_file":
                            self.output_file = value

                        # Report formats
                        elif key == "output_formats":
                            output_formats = self._parse_list(value)
                            self.output_formats = []
                            for token in output_formats:
                                token = token.lower()
                                if token in self.output_formats:
                                    continue
                                if token not in ('text', 'grepable', 'html'):
                                    msg = "invalid output_formats at line %d of config file %s"
                                    msg = msg % (number, filename)
                                    raise ConfigFileParseError(msg)
                                self.output_formats.append(token)

                        # Get the list of enabled plugins
                        elif key == "plugins":
                            if value.lower() == "all":
                                self.plugins = None
                            else:
                                self.plugins = self._parse_list(value)

                        # Get the plugins folder
                        elif key == "plugins_folder":
                            self.plugins_folder = value

                        # Get the name of the audit
                        elif key == "audit_name":
                            self.audit_name = value

                        # Audit database
                        elif key == "audit_db":
                            self.audit_db = value

                        # Maximum number of processes to execute plugins
                        elif key == "max_process":
                            self.max_process = int(value)

                        # Maximum number of connection, by host
                        elif key == "max_connections":
                            self.max_connections = int(value)

                        # Include subdomains?
                        elif key == "include_subdomains":
                            self.include_subdomains = self._parse_boolean(value)

                        # Subdomains as regex expresion
                        elif key == "subdomain_regex":
                            self.subdomain_regex = value

                        # Recursivity level for spider
                        elif key == "recursivity":
                            self.recursivity = int(value)

                        # Follow redirects
                        elif key == "follow_redirects":
                            self.follow_redirects = self._parse_boolean(value)

                        # Follow only first redirect
                        elif key == "follow_first_redirect":
                            self.follow_first_redirect = self._parse_boolean(value)

                        # Unknown option
                        else:
                            msg = ("unknown option %r in line %d"
                                   " of config file %s") % (key, number, config)
                            raise ConfigFileParseError(msg)

                    # On error raise an exception
                    except ConfigFileParseError:
                        raise
                    except Exception:
                        msg = "invalid value for %r at line %d of config file %s"
                        msg = msg % (key, number, filename)
                        raise ConfigFileParseError(msg)

    def _parse_list(self, value):
        tokens = set()
        for token in value.lower().split(','):
            token = token.strip()
            tokens.add(token)
        return tokens

    def _parse_boolean(self, value):
        value = value.strip().lower()
        if value == 'true' or value == 'yes' or value == 'y':
            return True
        if value == 'false' or value == 'no' or value == 'n':
            return False
        return bool(int(value))
