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

__all__ = ['NetManager', 'Web']


from ..config import Config
from ..logger import Logger
from ..results.information.url import Url
from ..results.information.http import *
from core.managers.cachemanager import *

from time import time
from urllib3.util import parse_url
from urllib3 import PoolManager



#------------------------------------------------------------------------------
class NetManager (object):
    """"""

    TYPE_WEB = 0
    TYPE_FTP = 1

    # init?
    __is_initialized = None

    # Pool manager. A pool for target
    __http_pool_manager = None


    #----------------------------------------------------------------------
    @staticmethod
    def get_connection(protocol = TYPE_WEB):
        """
        Get a connection of for an specific protocol.

        :param protocol: Connection to receive: HTTP, FTP...
        :type protocol: int

        :raises: ValueError
        """
        if NetManager.__http_pool_manager is None:
            NetManager.__http_pool_manager = PoolManager(Config().audit_config.max_connections)
        if protocol is NetManager.TYPE_WEB:
            return Web(NetManager.__http_pool_manager, Config().audit_config)

        else:
            raise ValueError("Unknown protocol type, value: %d" % protocol)




#------------------------------------------------------------------------------
class Protocol (object):
    """
    Super class for networks protocols.
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor."""

        # Set reference to cache
        self._cache = CacheManager()


    #----------------------------------------------------------------------
    def state(self):
        """"""
        pass

    #----------------------------------------------------------------------
    def close(self):
        """"""
        pass


    #----------------------------------------------------------------------
    def get(self, URL, method = None, cache = True):
        """
        This method obtain the URL passed as parameter with method specified.

        :param URL: URL to get.
        :type URL: str

        :param method: method to get URL
        :type method: str

        :param method: indicates if response must be cached.
        :type cache: bool
        """
        pass

    #----------------------------------------------------------------------
    def custom_request(self, request):
        """"""




#------------------------------------------------------------------------------
#
# Web methods and data structures
#
#------------------------------------------------------------------------------
class Web (Protocol):
    """
    Class for manager web protocols, like HTTP or HTTPs
    """

    #----------------------------------------------------------------------
    def __init__(self, http_pool, config):
        """Constructor"""
        super(Web, self).__init__()

        self.__http_pool_manager = http_pool
        self.__config = config

        # Set of domain names we're allowed to connect to
        self.__audit_scope = set(parse_url(x).hostname.lower() for x in config.targets)

        # Global option for redirects
        self.__follow_redirects = config.follow_redirects

        try:
            self.__audit_scope.remove("")
        except KeyError:
            pass
        try:
            self.__audit_scope.remove(None)
        except KeyError:
            pass


    #----------------------------------------------------------------------
    def is_in_scope(self, url):
        """
        Determines if the given URL is within scope of the audit.

        :param url: URL to test.
        :type url: str

        :returns: True if the URL is within scope of the audit, False otherwise.
        """
        hostname = parse_url(url).hostname.lower()
        return hostname in self.__audit_scope or (
            self.__config.include_subdomains and
            any(hostname.endswith("." + domain) for domain in self.__audit_scope)
        )


    #----------------------------------------------------------------------
    def state(self):
        """"""
        pass

    #----------------------------------------------------------------------
    def close(self):
        """Close and clear pool connections"""
        self.__http_pool_manager.clear()

    #----------------------------------------------------------------------
    def get_custom(self, request):
        """Get an HTTP response from a custom HTTP Request object

        :param request: An instance of HTTP_Request.
        :type request: HTTP_request

        :returns: HTTPResponse instance or None if any error or URL out of scope.

        :raises: TypeError
        """
        if not  isinstance(request, HTTP_Request):
            raise TypeError("Expected HTTP_Request, got %s instead" % type(URL))

        # Check for host matching
        if not self.is_in_scope(request.url):
            Logger.log_verbose("Url '%s' out of scope. Skipping it." % request.url)
            return

        m_response = None
        m_time = None

        # URL is cached?
        if request.is_cacheable and self._cache.is_cached(request):
            m_response = self._cache.get_cache(request)
        else:
            # Get URL
            try:
                # Set redirect options
                request.follow_redirects = request.follow_redirects if request.follow_redirects else self.__follow_redirects

                # timing init
                t1 = time()
                # Select request type
                m_response = None
                if "POST" == request.method or "PUT" == request.method:
                    m_response = self.__http_pool_manager.request(
                        method = request.method,
                        url = request.url,
                        redirect = request.follow_redirects,
                        headers = request.raw_headers,
                        fields = request.post_data,
                        encode_multipart = request.files_attached
                    )
                elif "GET" == request.method:
                    m_response = self.__http_pool_manager.request(
                        method = request.method,
                        url = request.url,
                        redirect = request.follow_redirects,
                        headers = request.raw_headers,
                    )
                else:
                    m_response = self.__http_pool_manager.request(
                        method = request.method,
                        url = request.url,
                        redirect = request.follow_redirects,
                        headers = request.raw_headers,
                        fields = request.post_data,
                    )

                # timin end
                t2 = time()

                # Calculate response time
                m_time = t2 - t1

                m_response = HTTP_Response(m_response, m_time, request)

                # Cache is enabled?
                if request.is_cacheable:
                    self._cache.set_cache(m_response)
            except Exception, e:
                Logger.log_error_verbose("Unknown error: '%s'." % e.message)

        return m_response


    #----------------------------------------------------------------------
    def get(self, URL, method = "GET", post_data = None, follow_redirect = None, cache = True):
        """
        Get response for an input URL.

        :param URL: string with URL or Url instance
        :type URL: str or Url

        :param cache: cache response?
        :type cache: bool

        :param redirect: If you want to follow HTTP redirect.
        :type redirect: bool

        :returns: HTTPResponse instance or None if any error or URL out of scope.

        :raises: TypeError
        """


        # Extract the raw URL when applicable
        try:
            URL = URL.url
        except AttributeError:
            pass

        # Check for host matching
        if not self.is_in_scope(URL):
            Logger.log_verbose("[!] Url '%s' out of scope. Skipping it." % URL)
            return

        # Set redirect
        m_follow_redirects = follow_redirect if follow_redirect else self.__follow_redirects

        # Make HTTP_Request object
        m_request = HTTP_Request(
            url = URL,
            method = method,
            post_data = post_data,
            follow_redirects = m_follow_redirects,
            cache = cache
        )

        return self.get_custom(m_request)



    #----------------------------------------------------------------------
    #
    # Static methods
    #
    #----------------------------------------------------------------------
    @staticmethod
    def get_url_id(url):
        """
        Makes an identifier for a URL.

        :returns: str -- Identifier, using: URL.scheme + URL.host + URL.port
        """
        m_url = parse_url(url)
        return "%s%s%s" % (m_url.scheme, m_url.host, m_url.port)



