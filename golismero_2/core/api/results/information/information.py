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
    INFORMATION_UNKNOWN       = 0    # Placeholder value, not a real type!
    INFORMATION_URL           = 1    # URLs
    INFORMATION_DOMAIN        = 2    # Domain names
    INFORMATION_DOCUMENT      = 3    # Documents in a recognized format
    INFORMATION_BINARY        = 4    # Binary files in an unsupported format
    INFORMATION_IMAGE         = 5    # Pictures and photos
    INFORMATION_MAIL          = 6    # Emails
    INFORMATION_HTML          = 7    # HTML documents
    INFORMATION_HTTP_REQUEST  = 8    # HTTP requests sent to the server
    INFORMATION_HTTP_RESPONSE = 9    # HTTP responses received from the server

    INFORMATION_FIRST = INFORMATION_UNKNOWN
    INFORMATION_LAST  = INFORMATION_HTTP_RESPONSE


    #----------------------------------------------------------------------
    def __init__(self):
        super(Information, self).__init__()
        self.result_type      = self.TYPE_INFORMATION
        self.information_type = self.INFORMATION_UNKNOWN


    #----------------------------------------------------------------------
    def __get_information_type(self):
        """
        Get the result subtype.

        :returns: int -- The result type.
        """
        return self.__information_type

    def __set_information_type(self, information_type):
        """
        Set the result subtype.

        :param result_type: Result subtype.
        :type result_type: int
        """
        if not self.INFORMATION_FIRST <= information_type <= self.INFORMATION_LAST:
            raise ValueError("Unknown result subtype: %d" % information_type)
        self.__information_type = information_type

    information_type = property(__get_information_type, __set_information_type)
