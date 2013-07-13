#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
IPv4 address type.
"""

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: https://github.com/cr0hn/golismero/
Golismero project mail: golismero.project<@>gmail.com

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

__all__ = ["IP"]

from . import Resource
from .. import identity
from ...net.web_utils import is_in_scope


#------------------------------------------------------------------------------
class IP(Resource):
    """
    IPv4 address.
    """

    resource_type = Resource.RESOURCE_IP


    #----------------------------------------------------------------------
    def __init__(self, address, domain):
        """
        :param address: IPv4 address.
        :type address: str

        :param domain: Domain associated to this IP address. Used to determine scope.
        :type domain: str
        """

        # IPv4 address.
        # TODO: sanitize the IP addresses
        self.__address = address

        # Domain name.
        self.__domain = domain

        # Parent constructor.
        super(IP, self).__init__()


    #----------------------------------------------------------------------
    def __str__(self):
        return self.address


    #----------------------------------------------------------------------
    def __repr__(self):
        return "<IP address=%r>" % self.address


    #----------------------------------------------------------------------
    def is_in_scope(self):
        return self.domain and is_in_scope(self.domain)


    #----------------------------------------------------------------------
    @identity
    def address(self):
        """
        :return: IPv4 address.
        :rtype: str
        """
        return self.__address


    #----------------------------------------------------------------------
    @identity
    def domain(self):
        """
        :return: Domain name associated to this IP address. Used to determine scope.
        :rtype: str
        """
        return self.__domain
