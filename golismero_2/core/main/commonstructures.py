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

    This class can call a virtual init, only one time, when
    object is created. For this, you must to create a method called
    "__vinit__".
    """

    __instance = None
    def __new__(cls, *args, **kargs):

        # If the singleton has already been instanced, return it.
        if cls.__instance is not None:
            return cls.__instance

        # Instance the singleton for the first (and only) time.
        cls.__instance = super(Singleton, cls).__new__(cls, *args, **kargs)

        # Call a virtual init, if it exists.
        if "__vinit__" in cls.__dict__:
            cls.__instance.__vinit__(*args, **kargs)

        # Return the singleton instance.
        return cls.__instance

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

        self.targets = []
        self.run_mode = GlobalParams.RUN_MODE.standalone
        self.user_interface = GlobalParams.USER_INTERFACE.console

        # Audit name
        self.audit_name = ""

        # Enabled plugins
        self.plugins = ["all"]

    @classmethod
    def from_cmdline(cls, args):
        """Get the settings from the command line arguments."""

        # Instance a settings object.
        cmdParams = cls()

        # Get the run mode
        cmdParams.run_mode = getattr(GlobalParams.RUN_MODE,
                                     args.run_mode.lower())

        # Get the user interface mode
        cmdParams.user_interface = getattr(GlobalParams.USER_INTERFACE,
                                           args.user_interface.lower())

        # Get the list of targets
        cmdParams.targets = args.targets

        # Get the list of enabled plugins
        cmdParams.plugins = args.plugins

        # Get the name of the audit
        cmdParams.audit_name = args.audit_name

        return cmdParams
