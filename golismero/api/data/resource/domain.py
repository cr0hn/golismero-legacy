#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Domain name.
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

__all__ = ["Domain"]

from . import Resource
from .ip import IP
from .. import identity, merge
from ...net.web_utils import is_in_scope, split_hostname


#------------------------------------------------------------------------------
class Domain(Resource):
    """
    Domain name.

    This data type maps the domain names to the IP addresses they resolve to.
    """

    resource_type = Resource.RESOURCE_DOMAIN


    #----------------------------------------------------------------------
    def __init__(self, name, *addresses):
        """
        :param name: Domain name.
        :type name: str

        :param addresses: IP address or addresses it resolves to.
        :type addresses: tuple(str)
        """

        # Domain name.
        self.__name = name

        # IP addresses.
        self.__addresses = addresses

        # Parent constructor.
        super(Domain, self).__init__()


    #----------------------------------------------------------------------
    def __str__(self):
        if self.addresses:
            return "(Domain) %s (%s)" % (
                self.name,
                ", ".join(self.addresses),
            )
        return "(Domain) %s" % self.name


    #----------------------------------------------------------------------
    def __repr__(self):
        s = "<Domain name=%r, addresses=%r>"
        s %= (self.name, self.addresses)
        return s


    #----------------------------------------------------------------------
    def is_in_scope(self):
        return is_in_scope("http://%s" % self.__name)


    #----------------------------------------------------------------------
    @identity
    def name(self):
        """
        :return: Domain name.
        :rtype: str
        """
        return self.__name


    #----------------------------------------------------------------------
    @merge
    def addresses(self):
        """
        :return: IP address or addresses this domain name resolves to.
        :rtype: tuple(str)
        """
        return self.__addresses

    #----------------------------------------------------------------------
    @property
    def hostname(self):
        """
        :return: the hostname of domain. i.e: www.mysite.com -> mysite.com
        :rtype: str
        """
        subdomain, domain, suffix = split_hostname(self.name)
        return "%s.%s" % (domain, suffix)


    #----------------------------------------------------------------------

    @property
    def discovered(self):
        # TODO: check the IPs for scope too
        domain = self.name
        result = [ IP(address) for address in self.addresses ]
        subdomain, domain, suffix = split_hostname(domain)
        if subdomain:
            prefix = ".".join( (domain, suffix) )
            for part in reversed(subdomain.split(".")):
                if is_in_scope(prefix):
                    result.append( Domain(prefix) )
                prefix = ".".join( (part, prefix) )
        return result
