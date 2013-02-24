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

from ..result import Result


#------------------------------------------------------------------------------
class Injection(Result):
    """
    Base class for control channel injections.
    """


    #--------------------------------------------------------------------------
    #
    # Types of Infomation injections
    #
    #--------------------------------------------------------------------------

    INJECTION_ANY = 0
    XSS_REFLECTED = 1

    INJECTION_FIRST = INJECTION_ANY
    INJECTION_LAST  = XSS_REFLECTED


    #----------------------------------------------------------------------
    def __init__(self, injection_type = XSS_REFLECTED):
        """Constructor."""
        super(Injection, self).__init__()

        self.result_type = self.TYPE_INJECTION
        self.__result_subtype = self.INJECTION_ANY


    #----------------------------------------------------------------------
    def __get_result_subtype(self):
        """
        Get the injection type.

        :returns: int -- The injection type.
        """
        return self.__result_subtype

    def __set_result_subtype(self, result_subtype = XSS_REFLECTED):
        """
        Set the injection type.

        :param injection_type: The type of injection
        :type injection_type: int
        """
        if result_subtype is None:
            result_subtype = Injection.XSS_REFLECTED
        elif result_subtype < self.INJECTION_FIRST or result_subtype > self.INJECTION_LAST:
            raise ValueError("Unknown injection type, value: %d" % result_subtype)
        self.__result_subtype = result_subtype

    result_subtype = property(__get_result_subtype, __set_result_subtype)
