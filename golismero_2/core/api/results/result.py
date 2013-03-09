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

from ...main.commonstructures import get_unique_id

#------------------------------------------------------------------------------
class Result(object):
    """
    Base class for plugin results.
    """

    #--------------------------------------------------------------------------
    #
    # Types of results
    #
    #--------------------------------------------------------------------------

    TYPE_ANY = 0      # not a real type! only used in get_accepted_info()

    TYPE_INFORMATION           = 1
    TYPE_VULNERABILITY         = 2

    TYPE_FIRST   = TYPE_INFORMATION    # constant for the first valid type
    TYPE_LAST    = TYPE_VULNERABILITY  # constant for the last valid type


    #----------------------------------------------------------------------
    def __init__(self):
        self.__result_type = Result.TYPE_ANY


    #----------------------------------------------------------------------
    def __get_result_type(self):
        """
        Get the result type.

        :returns: int -- The result type.
        """
        return self.__result_type

    def __set_result_type(self, result_type):
        """
        Set the result type.

        :param result_type: The type of result
        :type result_type: int
        """
        if result_type == self.TYPE_ANY:
            raise ValueError("Results can't be of the TYPE_ANY type")
        if not self.TYPE_FIRST <= result_type <= self.TYPE_LAST:
            raise ValueError("Unknown result type: %d" % result_type)
        self.__result_type = result_type

    result_type = property(__get_result_type, __set_result_type)

    #----------------------------------------------------------------------
    @property
    def hash_sum(self):
        """
        Get the hash of this object.
        """
        # NOTE:
        #   This can't be cached, because we have no way of knowing if
        #   the internal state of the object has changed.
        return get_unique_id(self)
