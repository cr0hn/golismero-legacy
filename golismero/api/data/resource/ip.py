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
from netaddr import IPAddress
from netaddr.core import AddrFormatError

#------------------------------------------------------------------------------
class IP(Resource):
    """
    IPv4 address.
    """

    resource_type = Resource.RESOURCE_IP


    #----------------------------------------------------------------------
    def __init__(self, address, version="auto"):
        """
        :param address: IPv4 address.
        :type address: str

        :param version: version of IP protocolo: 4, 6 or auto to detect the version.
        :param type: str(4|6|auto)
        """
        if isinstance(version, basestring):
            if version == "auto":
                try:
                    self.__version =  IPAddress(address).version
                except AddrFormatError:
                    raise ValueError("Wrong IP address")
            elif version not in ("4", "6"):
                raise ValueError("Valid versions for IP are: 4 or 6")
            else:
                self.__version = version
        else:
            raise TypeError("Expected basestring, got '%s'" % type(version))


        # IP address.
        self.__address = address

        # Parent constructor.
        super(IP, self).__init__()


    #----------------------------------------------------------------------
    def __str__(self):
        return self.address


    #----------------------------------------------------------------------
    def __repr__(self):
        return "<IP address=%r>" % self.address

    #----------------------------------------------------------------------
    @property
    def version(self):
        """
        :return: version of IP protocolo: 4 or 6.
        :rtype: str(4|6)
        """
        return self.__version

    #----------------------------------------------------------------------
    @identity
    def address(self):
        """
        :return: IPv4 address.
        :rtype: str
        """
        return self.__address