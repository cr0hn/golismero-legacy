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

__all__ = ["Information"]

#------------------------------------------------------------------------------
class Information(Result):
    """
    Base class for informational results.
    """

    #--------------------------------------------------------------------------
    #
    # Types of Infomation results
    #
    #--------------------------------------------------------------------------
    INFORMATION_UNKNOWN       = 0
    INFORMATION_IMAGE         = 1
    INFORMATION_URL           = 2
    INFORMATION_DOCUMENT      = 3
    INFORMATION_BINARY        = 4
    INFORMATION_MAIL          = 5
    INFORMATION_HTML          = 6
    INFORMATION_HTTP_REQUEST  = 7
    INFORMATION_HTTP_RESPONSE = 8

    INFORMATION_FIRST = INFORMATION_UNKNOWN
    INFORMATION_LAST  = INFORMATION_HTTP_RESPONSE


    #----------------------------------------------------------------------
    def __init__(self):
        super(Information, self).__init__()
        self.result_type    = self.TYPE_INFORMATION
        self.result_subtype = self.INFORMATION_UNKNOWN


    #----------------------------------------------------------------------
    def __get_result_subtype(self):
        """
        Get the result subtype.

        :returns: int -- The result type.
        """
        return self.__result_subtype

    def __set_result_subtype(self, result_subtype):
        """
        Set the result subtype.

        :param result_type: Result subtype.
        :type result_type: int
        """
        if not self.INFORMATION_FIRST <= result_subtype <= self.INFORMATION_LAST:
            raise ValueError("Unknown result subtype: %d" % result_subtype)
        self.__result_subtype = result_subtype

    result_subtype = property(__get_result_subtype, __set_result_subtype)
