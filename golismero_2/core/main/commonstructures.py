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


#--------------------------------------------------------------------------
#
# INTERNAL DEVELOP STRUCTURES
#
#--------------------------------------------------------------------------
def enum(*sequential, **named):
    "Enumerated type"
    values = dict(zip(sequential, range(len(sequential))), **named)
    values['_values'] = values
    return type('Enum', (), values)



#--------------------------------------------------------------------------
# Metaclass to define abstract interfaces in Python.
class _interface(type):
    def __init__(cls, name, bases, namespace):

        # Call the superclass.
        type.__init__(cls, name, bases, namespace)

        # Get the methods defined in this class, rather than inherited.
        current = set( [x for x in cls.__dict__.keys() if not x.startswith("_")] )

        # Look for the interfaces implemented by this class.
        # That is, the base classes that derive *directly* from Interface.
        interfaces = []
        for clazz in bases:
            if len(clazz.__bases__) and clazz.__bases__[0] == Interface:
                interfaces.append(clazz)

        # Find out which methods are required by the interfaces.
        methods = set()
        for clazz in interfaces:
            methods.update( [x for x in clazz.__dict__.keys() if not x.startswith("_")] )

        # Check none of them are missing.
        methods.difference_update(current)

        # If one or more are missing...
        if methods:

            # Raise an exception.
            raise TypeError("Missing methods: %s" % ", ".join(sorted(methods)))

#--------------------------------------------------------------------------
class Interface (object):
    __metaclass__ = _interface

#--------------------------------------------------------------------------
class Singleton (object):
    """
    Implementation of the Singleton pattern.
    """

    # Variable where we keep the instance.
    _instance = None

    def __new__(cls, *args, **kwargs):

        # If the singleton has already been instanced, return it.
        if cls._instance is not None:
            return cls._instance

        # Create the singleton's instance.
        cls._instance = super(Singleton, cls).__new__(cls)

        # Call the constructor.
        cls._instance.__init__(*args, **kwargs)

        # Delete the constructor so it won't be called again.
        cls._instance.__init__ = object.__init__
        cls.__init__ = object.__init__

        # Return the instance.
        return cls._instance

#--------------------------------------------------------------------------
#
# GLOBAL CONFIGURATION PARAMETER
#
#--------------------------------------------------------------------------
class GlobalParams:
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
        self.target = [""]
        # Run mode
        self.run_mode = GlobalParams.RUN_MODE.standalone
        # UI mode
        self.user_interface = GlobalParams.USER_INTERFACE.console
        # Set verbose mode
        self.verbose = False
        # Set more verbose mode
        self.verbose = False

        #
        # Audit options
        #
        # Audit name
        self.audit_name = ""
        # Maximum number of processes for execute plugins
        self.max_process = 4

        #
        # Plugins options
        #
        # Enabled plugins
        self.plugins = ["all"]

        #
        # Networks options
        #
        # Maximum number of connection, by host
        self.max_connections = 3
        # Include subdomains?
        self.include_subdomains = True

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
        cmdParams.target = args.target
        # Set verbose mode
        cmdParams.verbose = args.verbose
        # Set more verbose mode
        cmdParams.verbose = args.verbose_more

        #
        # Plugins options
        #
        # Get the list of enabled plugins
        cmdParams.plugins = args.plugins

        #
        # Audit options
        #
        # Get the name of the audit
        cmdParams.audit_name = args.audit_name
        # Maximum number of processes for execute plugins
        cmdParams.max_process = args.max_process

        #
        # Network options
        #
        # Maximum number of connection, by host
        cmdParams.max_connections = args.max_connections
        # Include subdomains?
        cmdParams.include_subdomains = args.include_subdomains

        # Check params

        GlobalParams.check_params(cmdParams)

        return cmdParams


    #----------------------------------------------------------------------
    @staticmethod
    def check_params(params):
        """
        Check if parameters are valid. Raises an exception otherwise.

        :raises: ValueError
        """
        if not isinstance(params, GlobalParams):
            return

        # Check max connections
        if params.max_connections < 1:
            raise ValueError("Number of connections must be greater than 0, got %s." % params.max_connections)

        # Check max process
        if params.max_process< 1:
            raise ValueError("Number of process must be greater than 0, got %s." % params.max_process)

        # Check plugins selected
        if not params.plugins and "all" not in map(str.lower, params.plugins):
            raise ValueError("Some plugin must be selected.")



#--------------------------------------------------------------------------
#
# MESSAGING STRUCTURES
#
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
class IReceiver(Interface):
    """
    This class acts as an interface.

    It must be imported for al classes that wants receive messages from
    the messaging system.

    """
    #----------------------------------------------------------------------
    def recv_msg(self, message):
        """Receive method for messages"""
        pass



#--------------------------------------------------------------------------
class IObserver(Interface):
    """
    This class acts as an interface.

    It must be imported for al classes that wants send messages to the
    messaging system.

    """


    #----------------------------------------------------------------------
    def send(self, Message):
        """Send method for messages"""
        pass


