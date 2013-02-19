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


__all__ = ["NetManager", "Web", "HTTP_Response"]

from core.main.commonstructures import get_unique_id
from thirdparty_libs.urllib3.util import parse_url
from thirdparty_libs.urllib3 import PoolManager
from core.api.results.information.html import *
from time import time
from core.api.results.information.url import Url
from core.api.logger import Logger
from re import match, compile

#------------------------------------------------------------------------------
class NetManager (object):
    """"""

    TYPE_WEB = 0
    TYPE_FTP = 1

    # init?
    __is_initialized = None

    # Pool manager. A pool for target
    __http_pool_manager = None
    __config = None

    #----------------------------------------------------------------------
    @staticmethod
    def config(config):
        """Constructor"""
        NetManager.__config = config

        # Set pool manager
        NetManager.__http_pool_manager = PoolManager(NetManager.__config.max_connections)


    #----------------------------------------------------------------------
    @staticmethod
    def get_connection(protocol = TYPE_WEB):
        """
        Get a connection of for an specific protocol.

        :param protocol: Connection to receive: HTTP, FTP...
        :type protocol: int

        :raises: ValueError
        """
        if protocol is NetManager.TYPE_WEB:
            return Web(NetManager.__http_pool_manager, NetManager.__config)

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
    def get_cache(self, URL):
        """
        Get URL from cache

        :returns: object cached | None
        """
        # None or empty?
        if not URL:
            return None

        # get key
        m_key = get_unique_id(URL)

        m_return = None
        try:
            # if cached
            m_return = self.__cache[URL]
        except KeyError:
            # Not cached
            m_return = None

        return m_return

    #----------------------------------------------------------------------
    def is_cached(self, URL):
        """
        Indicates if URL is cached

        :returns: bool -- True if URL has cached. False otherwise.
        """
        # get key
        m_key = get_unique_id(URL)

        return m_key in self.__cache

    #----------------------------------------------------------------------
    def set_cache(self, URL, data):
        """
        Include and URL, and their data, into cache.

        :param URL: String with URL
        :type URL: str

        :param data: data with information
        :type data: object
        """
        # None or empty?
        if URL and data:
            m_key = get_unique_id(URL)
            self.__cache[m_key] = data



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
            self.matcher = compile("%s%s" % (self.__config.suddomains_regex, self.__config.target[0]))
        else:
            self.matcher = compile(".*%s" % self.__config.target[0] if self.__config.include_subdomains else None)


    #----------------------------------------------------------------------
    def state(self):
        """"""
        pass

    #----------------------------------------------------------------------
    def close(self):
        """"""
        self.__http_pool_manager.clear()

    #----------------------------------------------------------------------
    def get_custom(self, request):
        """"""
        pass


    #----------------------------------------------------------------------
    def get(self, URL, method= "GET", cache = True, redirect=False):
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
        m_url = None
        if isinstance(URL, basestring):
            m_url = URL
        elif isinstance(URL, Url):
            m_url = URL.url_raw
        else:
            raise TypeError("Expected string or Url, got %s instead" % type(URL))

        # Check for host matching
        m_parser = parse_url(m_url)
        if m_parser.hostname and not self.matcher.match(m_parser.hostname):
            Logger.log_verbose("[!] Url '%s' out of scope. Skiping it." % m_url)
            return None

        m_response = None
        m_time = None

        # URL is cached?
        if cache and self.is_cached(m_url):
            m_response = self.get_cache(m_url)
        else:
            # Get URL
            try:
                # timing init
                t1 = time()
                # Get resquest
                m_response = self.__http_pool_manager.request(method, m_url, redirect=False)
                # timin end
                t2 = time()

                m_time = t2 - t1

                m_response = HTTP_Response(m_response, m_time)

                # Cache are enabled?
                if cache:
                    self.set_cache(URL, m_response)
            except Exception, e:
                Logger.log_error_verbose("[!] Unknown error: '%s'." % e.message)


        return m_response



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



#------------------------------------------------------------------------------
class HTTP_Request (object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""





#------------------------------------------------------------------------------
class HTTP_Response (object):
    """
    This class contain all info fo HTTP response
    """

    #----------------------------------------------------------------------
    def __init__(self, response, request_time):
        """Constructor"""

        # HTML code of response
        self.__raw_data = response.data
        # HTTP response code
        self.__http_response_code = response.status
        # HTTP response reason
        self.__http_response_code_reason = response.reason
        # HTTP headers
        self.__http_headers = dict(response.headers)
        # HTTP headers in raw format
        self.__http_headers_raw = ''.join(["%s: %s\n" % (k,v) for k,v in response.headers.items()])
        # Request time
        self.__request_time = request_time
        # Generate information object
        self.__information = self.__get_type_by_raw(self.__http_headers, self.__raw_data)


    #----------------------------------------------------------------------
    def __get_raw(self):
        """"""
        return self.__raw_data
    raw_data = property(__get_raw)

    #----------------------------------------------------------------------
    def __get_http_response_code(self):
        """"""
        return self.__http_response_code
    http_code = property(__get_http_response_code)

    #----------------------------------------------------------------------
    def __get_http_response_reason(self):
        """"""
        return self.__http_response_code_reason
    http_reason = property(__get_http_response_reason)

    #----------------------------------------------------------------------
    def __get_http_headers(self):
        """"""
        return self.__http_headers
    http_headers = property(__get_http_headers)

    #----------------------------------------------------------------------
    def __get_http_raw_headers(self):
        """"""
        return self.__http_headers_raw
    http_headers_raw = property(__get_http_raw_headers)

    #----------------------------------------------------------------------
    def __get_request_time(self):
        """"""
        return self.__request_time
    request_time = property(__get_request_time)

    #----------------------------------------------------------------------
    def __get_information(self):
        """"""
        return self.__information
    information = property(__get_information)

    #----------------------------------------------------------------------
    def __get_type_by_raw(self, headers, data):
        """
        Get an information type from a raw object
        """
        m_return_content = None
        if headers:
            if "content-type" in headers.keys():
                m_content_type = headers["content-type"]

                # Select the type
                if m_content_type.startswith('text/html'):
                    m_return_content = HTML(data)

        return m_return_content

