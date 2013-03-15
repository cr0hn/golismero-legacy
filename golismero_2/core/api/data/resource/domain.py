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

__all__ = ["Domain"]

from .resource import Resource


#------------------------------------------------------------------------------
class Domain(Resource):
    """
    Domain name resource.
    """

    resource_type = Resource.RESOURCE_DOMAIN


    #----------------------------------------------------------------------
    def __init__(self, name, *addresses):
        """
        Construct a domain name resource.

        :param name: Domain name
        :type name: str

        :param addresses: List of IP addresses
        :type addresses: list
        """

        # Domain name
        self.__name = name

        # List of IP addresses
        self.__addresses = tuple(addresses)


    #----------------------------------------------------------------------
    def __str__(self):
        if self.addresses:
            return "%s (%s)" % (
                self.name,
                ", ".join(self.addresses),
            )
        return self.name


    #----------------------------------------------------------------------
    def __repr__(self):
        s = "<Domain name=%r, addresses=%r>"
        s %= (self.name, self.addresses)
        return s


    #----------------------------------------------------------------------
    @property
    def name(self):
        """
        str -- Domain name
        """
        return self.__name

    @property
    def addresses(self):
        """
        tuple(str) -- IP addresses
        """
        return self.__addresses
