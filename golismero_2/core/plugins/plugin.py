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

__author__ = "Daniel Garcia Garcia a.k.a cr0hn - dani@iniqua.com"
__copyright__ = "Copyright 2011-2013 - GoLismero project"
__credits__ = ["Daniel Garcia Garcia a.k.a cr0hn"]
__maintainer__ = "cr0hn"
__email__ = "golismero.project@gmail.com"
__status__ = "Develop"
__license__ = "GPL"
__version__ = "0.0.1"

#-----------------------------------------------------------------------
#
#
# This file contain interfaces an abstract classes for plugins
#
#
#-----------------------------------------------------------------------

from core.data.commonstructures import Interface
from core.main.orchester import Orchestrator

class IPlugin(Interface):
    """
    Plugin interface.

    All plugins will inherit indirectly from it.    
    """

    
    #----------------------------------------------------------------------
    def run(self):
        """Execution code for a plugin must be write here"""
        pass

    #----------------------------------------------------------------------    
    def check_input_params(self, inputParams):
        """
        Comprueba las comprobaciones de los parametros introducidos por el
        usuario.
        
        Los parametros seran pasados en la instancia del tipo 'GlobalParams'.
        
        Si algun parametro no es correcto o hay algun error, sera lanzada
        una excepcion del tipo 'ValueError'.
        
        :param inputParams: Parametros de entrada a comprobar
        :type inputParams: GlobalParam
        """
        pass
      
    #----------------------------------------------------------------------    
    def display_help(self):
        """This method display help for a plugin"""
        pass
    
    #----------------------------------------------------------------------
    def recv_msg(self):
        """Method for receive messages. All plugin will overrite it."""
        pass

    #----------------------------------------------------------------------
    def send_msg(self, message):
        """Method for send messages. Plugins can't override it."""
        pass    
        
    
#---------------------------------------------------------------------------
class Plugin(IPlugin):
    """
    This class provides an abstract class for plugins, implementing some common
    methods and facilities for all plugins.

    All plugins will inherit directly from it.

    """
    
    #----------------------------------------------------------------------
    def __init__(self, observer):
        """
        Prepare common structures
        """
        if not isinstance(observer, Orchestrator):
            raise ValueError("observer parameter must be an instance of Observer")
        
        self.__observer_ref = observer
        
    #----------------------------------------------------------------------
    def send_msg(self, message):
        """Send a message to observer"""
        self.__observer_ref.recv_msg(message)
        
        
    
    
    