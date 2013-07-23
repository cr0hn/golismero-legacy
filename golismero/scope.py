#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Audit scope checking.
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

__all__ = ["AuditScope"]

from .api.data.resource.domain import Domain
from .api.data.resource.ip import IP
from .api.data.resource.url import Url
from .api.net.dns import DNS
from .api.net.web_utils import DecomposedURL, split_hostname

from netaddr import IPAddress, IPNetwork
from netaddr.core import AddrFormatError

import re


#------------------------------------------------------------------------------
class AuditScope (Singleton):
    """
    Audit scope.

    Example:

        >>> from golismero.api.config import Config
        >>> 'www.example.com' in Config.audit_scope
        True
        >>> 'www.google.com' in Config.audit_scope
        False
    """

    _re_is_domain = re.compile(r"^[A-Za-z][A-Za-z0-9\_\-\.]*[A-Za-z0-9]$")


    #--------------------------------------------------------------------------
    def __init__(self, audit_config):
        """
        :param audit_config: Audit configuration.
        :type audit_config: AuditConfig
        """

        # This is where we'll keep the parsed targets.
        self.__domains   = set()   # Domain names.
        self.__addresses = set()   # IP addresses.
        self.__web_pages = set()   # URLs.

        # Remember if subdomains are allowed.
        self.__include_subdomains = audit_config.include_subdomains

        # For each user-supplied target string...
        for target in audit_config.targets:

            # If it's a domain name...
            if self._re_is_domain.match(target):

                # Convert it to lowercase.
                target = target.lower()

                # Keep the domain name.
                self.__domains.add(target)

                # Guess an URL from it.
                # FIXME: this should be smarter and use port scanning!
                self.__web_pages.add("http://%s/" % target)

            # If it's an IP address...
            else:
                try:
                    IPAddress(target)
                    address = target
                except AddrFormatError:
                    address = None
                if address is not None:

                    # Keep the IP address.
                    self.__addresses.add(address)

                    # Guess an URL from it.
                    # FIXME: this should be smarter and use port scanning!
                    self.__web_pages.add("http://%s/" % address)

                # If it's an IP network...
                else:
                    try:
                        network = IPNetwork(target)
                    except AddrFormatError:
                        network = None
                    if network is not None:

                        # For each host IP address in range...
                        for address in network.iter_hosts():
                            address = str(address)

                            # Keep the IP address.
                            self.__addresses.add(address)

                            # Guess an URL from it.
                            # FIXME: this should be smarter and use port scanning!
                            self.__web_pages.add("http://%s/" % address)

                    # If it's an URL...
                    else:
                        try:
                            parsed_url = DecomposedURL(target)
                            url = parsed_url.url
                        except Exception:
                            url = None
                        if url is not None:

                            # Keep the URL.
                            self.__web_pages.add(url)

                            # Extract the domain or IP address.
                            host = parsed_url.host
                            try:
                                IPAddress(host)
                                self.__addresses.add(host)
                            except AddrFormatError:
                                self.__domains.add( host.lower() )

        # If subdomains are allowed, we must include the parent domains.
        if self.__include_subdomains:
            for hostname in self.__domains.copy():
                subdomain, domain, suffix = split_hostname(hostname)
                if subdomain:
                    prefix = ".".join( (domain, suffix) )
                    for part in reversed(subdomain.split(".")):
                        self.__domains.add(prefix)
                        prefix = ".".join( (part, prefix) )

        # For each domain name...
        for domain in self.__domains:

            # Resolve the IPv4 addresses.
            for register in DNS.get_a(domain):
                self.__addresses.add(register.target)

            # Resolve the IPv6 addresses.
            for register in DNS.get_aaaa(domain):
                self.__addresses.add(register.target)


    #--------------------------------------------------------------------------
    def get_targets(self):
        """
        Get the audit targets as Data objects.

        :returns: Data objects.
        :rtype: list(Data)
        """
        result = []
        result.extend( IP(address) for address in self.__addresses )
        result.extend( Domain(domain) for domain in self.__domains )
        result.extend( Url(url) for url in self.__web_pages )
        return result


    #--------------------------------------------------------------------------
    def __contains__(self, target):
        """
        Tests if the given target is included in the current audit scope.

        :param target: Target. May be an URL, a hostname or an IP address.
        :type target: str

        :returns: True if the target is in scope, False otherwise.
        :rtype: bool
        """

        # Trivial case.
        if not target:
            return False

        # If it's an URL...
        try:
            parsed_url = DecomposedURL(target)
        except Exception:
            parsed_url = None
        if parsed_url is not None:

            # Extract the host and use it as target.
            target = parsed_url.host

        # If it's a domain name...
        if self._re_is_domain.match(target):

            # Convert the target to lowercase.
            target = target.lower()

            # Test if the domain is one of the targets. If subdomains are
            # allowed, check if it's a subdomain of a target domain.
            return target in self.__domains or (
                self.__include_subdomains and
                any(target.endswith("." + domain) for domain in self.__domains)
            )

        # If it's an IP address...
        try:
            IPAddress(target)
            address = target
        except AddrFormatError:
            address = None
        if address is not None:

            # Test if it's one of the target IP addresses.
            return address in self.__addresses

        # We don't know what this is, so we'll consider it out of scope.
        return False
