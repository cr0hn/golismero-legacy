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

try:
    import cPickle as pickle
except ImportError:
    import pickle

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
        self.verbose = 0

        #
        # Audit options
        #

        # Audit name
        self.audit_name = ""

        # Maximum number of processes for execute plugins
        ##self.max_process = 4
        self.max_process = 0

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
        self.max_connections = 15

        # Include subdomains?
        self.include_subdomains = True


    #----------------------------------------------------------------------
    @classmethod
    def from_cmdline(cls, args):
        """Get the settings from the command line arguments."""

        # Instance a settings object.
        cmdParams = cls()

        #
        # Main options
        #

        # Get the run mode
        cmdParams.run_mode = getattr(GlobalParams.RUN_MODE,
                                     args.run_mode.lower())

        # Get the user interface mode
        cmdParams.user_interface = getattr(GlobalParams.USER_INTERFACE,
                                           args.user_interface.lower())

        # Get the list of targets
        cmdParams.targets = args.targets

        # Set verbosity level
        cmdParams.verbose = args.verbose

        #
        # Plugins options
        #

        # Get the list of enabled plugins
        cmdParams.plugins = args.plugins

        # Get the plugins folder
        cmdParams.plugins_folder = args.plugins_folder

        #
        # Audit options
        #

        # Get the name of the audit
        cmdParams.audit_name = args.audit_name

        # Maximum number of processes for execute plugins
        ##cmdParams.max_process = args.max_process

        #
        # Network options
        #

        # Maximum number of connection, by host
        cmdParams.max_connections = args.max_connections

        # Include subdomains?
        cmdParams.include_subdomains = args.include_subdomains

        # Check params
        cmdParams.check_params()

        return cmdParams


    #----------------------------------------------------------------------
    def check_params(self):
        """
        Check if parameters are valid. Raises an exception otherwise.

        :raises: ValueError
        """

        # Check max connections
        if self.max_connections < 1:
            raise ValueError("Number of connections must be greater than 0, got %s." % params.max_connections)

        # Check max process
        if self.max_process < 0:
            raise ValueError("Number of process cannot be a negative number, got %s." % params.max_process)

        # Check plugins selected
        if self.plugins is not None and not self.plugins:
            raise ValueError("No plugins selected for execution.")
