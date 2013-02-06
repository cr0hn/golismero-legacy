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




def enum(*sequential, **named):
    """Virtual enumeration"""
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)




# Metaclase que verifica que las interfases se cumplan.
class _interface(type):
    def __init__(cls, name, bases, namespace):

        # Llama a la superclase.
        type.__init__(cls, name, bases, namespace)

        # Los metodos definidos en esta clase.
        current = set( [x for x in cls.__dict__.keys() if not x.startswith("_")] )

        # Buscamos las interfases.
        interfases = []
        for clazz in bases:

            # Si la clase base a su vez deriva *directamente* de Interface...
            if len(clazz.__bases__) and clazz.__bases__[0] == Interface:

                # Entonces la guardo para la comprobacion posterior.
                interfases.append(clazz)

        # Averiguamos que metodos deben implementar estas interfases.
        metodos = set()
        for clazz in interfases:
            metodos.update( [x for x in clazz.__dict__.keys() if not x.startswith("_")] )

        # Verificamos que no falte ninguno.
        metodos.difference_update(current)

        # Si falta alguno...
        if metodos:
            # Lanzamos excepcion.
            raise TypeError("Missing methods: %s" % ", ".join(sorted(metodos)))

class Interface (object):
    __metaclass__ = _interface



#--------------------------------------------------------------------------
class GlobalParams:
    """
    Global parameters fro program
    """


    # Run modes enumerators
    RUN_MODE = enum('standalone', 'cloudclient', 'cloudserver')
    # User interface
    USER_INTERFACE = enum('console')

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        self.Target = ""
        self.RunMode = GlobalParams.RUN_MODE.standalone
        self.UserInterface = GlobalParams.USER_INTERFACE.console

        # Audit name
        self.AuditName = ""

        # Enabled plugins
        self.Plugins = ["all"]