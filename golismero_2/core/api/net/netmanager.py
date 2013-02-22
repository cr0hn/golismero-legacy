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

from ..config import Config
from ..results.information.url import Url
from ..results.information.http import *
from ..logger import Logger

from time import time
from re import match, compile

from thirdparty_libs.urllib3.util import parse_url
from thirdparty_libs.urllib3 import PoolManager

__all__ = ['NetManager', 'Web']

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

        # Init the cache
        self.__cache = dict()


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


    #----------------------------------------------------------------------
    def get_cache(self, data):
        """
        Get URL from cache

        :returns: object cached | None
        """
        # None or empty?
        if not data:
            return None

        m_return = None
        try:
            # if cached
            m_return = self.__cache[data.hash_sum]
        except KeyError:
            # Not cached
            m_return = None

        return m_return

    #----------------------------------------------------------------------
    def is_cached(self, data):
        """
        Indicates if URL is cached

        :returns: bool -- True if URL has cached. False otherwise.
        """

        return data.hash_sum in self.__cache.keys()

    #----------------------------------------------------------------------
    def set_cache(self, data):
        """
        Include and URL, and their data, into cache.

        :param URL: String with URL
        :type URL: str

        :param data: data with information
        :type data: object
        """
        # None or empty?
        if data.hash_sum:
            self.__cache[data.hash_sum] = data



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

        # re object with pattern for domain and/or subdomains
        self.macher = None
        if self.__config.subdomain_regex:
            self.matcher = compile("%s%s" % (self.__config.suddomains_regex, self.__config.targets[0]))
        else:
            self.matcher = compile(".*%s" % self.__config.targets[0] if self.__config.include_subdomains else None)


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
        m_parser = parse_url(request.url)
        if all([ m_parser.hostname, not self.matcher.match(m_parser.hostname)]):
            Logger.log_verbose("Url '%s' out of scope. Skiping it." % request.url)
            return None

        m_response = None
        m_time = None

        # URL is cached?
        if request.is_cacheable and self.is_cached(request):
            m_response = self.get_cache(request)
        else:
            # Get URL
            try:
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

                # Cache are enabled?
                if request.is_cacheable:
                    self.set_cache(m_response)
            except Exception, e:
                Logger.log_error_verbose("Unknown error: '%s'." % e.message)

        return m_response


    #----------------------------------------------------------------------
    def get(self, URL, method= "GET", post_data = None, follow_redirect=False, cache = True):
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

        # None or not str?
        if not isinstance(URL, basestring):
            raise TypeError("Expected str, got %s instead" % type(URL))

        # Check for host matching
        m_parser = parse_url(URL)
        if m_parser.hostname and not self.matcher.match(m_parser.hostname):
            Logger.log_verbose("[!] Url '%s' out of scope. Skiping it." % URL)
            return None

        # Make HTTP_Request object
        m_request = HTTP_Request(
            url = URL,
            method = method,
            post_data = post_data,
            follow_redirects = follow_redirect,
            cache = cache
        )

        return  self.get_custom(m_request)



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



