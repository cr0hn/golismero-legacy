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

from core.api.injections.injection import injection

#------------------------------------------------------------------------------
class Injection(injection):
    """
    Abstract class for informational injections
    """

    #--------------------------------------------------------------------------
    #
    # Types of Infomation injections
    #
    #--------------------------------------------------------------------------
    XSS_REFLECTED = 0



    #----------------------------------------------------------------------
    def __init__(self, injection_type = None):
        """Constructor"""
        super(Injection, self).__init__(injection.TYPE_INJECTION)

        self.__injection_type = injection_type



    #----------------------------------------------------------------------
    def get_injection_type(self):
        """
        Get the injection type

        :returns: int -- The injection type.
        """
        if self.__injection_type is None:
            return Injection.XSS_REFLECTED
        else:
            return self.__injection_type

    #----------------------------------------------------------------------
    def set_injection_type(self, injection_type):
        """
        Set the injection type.

        :param injection_type: The type of injection
        :type injection_type: int
        """
        if injection_type is not None and injection_type >= 0 and injection_type <= 10:
            self.__injection_type = injection_type

    injection_type = property(get_information_type, set_information_type)


