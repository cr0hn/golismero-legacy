#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com
  Mario Vilas | mvilas@gmail.com

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

__all__ = ["Information"]

from ..data import Data


#------------------------------------------------------------------------------
class Information(Data):
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
    INFORMATION_DOCUMENT      = 2
    INFORMATION_BINARY        = 3
    INFORMATION_MAIL          = 4
    INFORMATION_HTML          = 5
    INFORMATION_HTTP_REQUEST  = 6
    INFORMATION_HTTP_RESPONSE = 7
    INFORMATION_PLAIN_TEXT    = 8

    INFORMATION_FIRST = INFORMATION_UNKNOWN
    INFORMATION_LAST  = INFORMATION_PLAIN_TEXT


    #----------------------------------------------------------------------

    data_type = Data.TYPE_INFORMATION
    information_type = INFORMATION_UNKNOWN
