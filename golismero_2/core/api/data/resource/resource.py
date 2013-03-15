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

from ..data import Data

#------------------------------------------------------------------------------
class Resource(Data):
    """
    Base class resources.
    """
    #--------------------------------------------------------------------------
    #
    # Types of Infomation results
    #
    #--------------------------------------------------------------------------
    RESOURCE_UNKNOWN       = 0
    RESOURCE_URL           = 1
    RESOURCE_DOMAIN        = 2    # Domain names


    RESOURCE_FIRST = RESOURCE_UNKNOWN
    RESOURCE_LAST  = RESOURCE_DOMAIN

    #----------------------------------------------------------------------
    def __init__(self):
        super(Resource, self).__init__()
        self.__data_type = Data.TYPE_RESOURCE


    #----------------------------------------------------------------------
    def __get_resource_type(self):
        """
        Get the resource type.

        :returns: int -- The resource type.
        """
        return self.__resource_type

    def __set_resource_type(self, resource_type):
        """
        Set the resource type.

        :param resource_type: The type of resource
        :type resource_type: int
        """
        if resource_type == self.TYPE_ANY:
            raise ValueError("Resource can't be of the TYPE_ANY type")
        if not self.TYPE_FIRST <= resource_type <= self.TYPE_LAST:
            raise ValueError("Unknown resource type: %d" % resource_type)
        self.__resource_type = resource_type

    resource_type = property(__get_resource_type, __set_resource_type)

