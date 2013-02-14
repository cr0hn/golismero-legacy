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

import hashlib
from core.main.commonstructures import Singleton, HashSum
from thirdparty_libs.urllib3.util import parse_url
from thirdparty_libs.urllib3 import connection_from_url, HTTPResponse
from time import time


#------------------------------------------------------------------------------
class NetManager():
    """"""

    TYPE_WEB = 0
    TYPE_FTP = 1

    # init?
    __is_initialized = None

    # Pool manager. A pool for target
    __http_pool_manager = None

    # Config
    __config = None

    #----------------------------------------------------------------------
    @staticmethod
    def config(config):
        """Constructor"""
        NetManager.__config = config

        # Set pool manager
        m_add_subdomains = '*' if NetManager.__config.include_subdomains else ''
        m_hosts = "%s%s" % (m_add_subdomains, NetManager.__config.target[0])
        NetManager.__http_pool_manager = connection_from_url(m_hosts, maxsize = NetManager.__config.max_connections, block = True)

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
            return Web(NetManager.__http_pool_manager)

        else:
            raise ValueError("Unknown protocol type, value: %d" % protocol)

#------------------------------------------------------------------------------
class Protocol(object):
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
        m_key = hashlib.md5(URL).hexdigest()

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
        m_key = hashlib.md5(URL).hexdigest()

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
            m_key = hashlib.md5(m_tmp_values).hexdigest()
            self.__cache[m_key] = data



#------------------------------------------------------------------------------
#
# Web methods and data structures
#
#------------------------------------------------------------------------------
class Web(Protocol):
    """
    Class for manager web protocols, like HTTP or HTTPs
    """

    #----------------------------------------------------------------------
    def __init__(self, http_pool):
        """Constructor"""
        super(Web, self).__init__()

        self.__http_pool_manager = http_pool

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
    def get(self, URL, method= "GET", cache = True):
        """
        Get response for an input URL.

        :param URL: string with URL.
        :type URL: str

        :returns: HTTPResponse instance.

        :raises: TypeError
        """

        # None or not str?
        if not isinstance(URL, basestring):
            raise TypeError("Expected string, got %s instead" % type(URL))

        m_response = None

        # URL is cached?
        if cache and self.is_cached(URL):
            m_response = self.get_cache(URL)
        else:
            # Get URL
            try:
                # timing init
                t1 = time()
                # Get resquest
                m_response = self.__http_pool_manager.request(method, URL)
                # timin end
                t2 = time()

                # Cache are enabled?
                if cache:
                    self.set_cache(URL, t1 - t2)
            except Exception, e:
                print e.message


        return HTTP_Response(m_response)



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
class HTTP_Request:
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""





#------------------------------------------------------------------------------
class HTTP_Response(object):
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
        self.__http_headers_raw = ""
        for k, v in self.__http_headers.items():
            self.__http_headers_raw.join("%s\t%s\n" % (k, v))
        # Request time
        self.__request_time = request_time
        # Generate information object
        self.__information = None


    #----------------------------------------------------------------------
    def __get_html_body(self):
        """"""
        return self.__body
    raw_data = property(__get_html_body)

    #----------------------------------------------------------------------
    def __get_http_response_code(self):
        """"""
        return self.__http_response_code
    http_code = property(__get_http_response_code)

    #----------------------------------------------------------------------
    def __get_http_response_reason(self):
        """"""
        return self.__body
    http_reason = property(__get_http_response_reason)

    #----------------------------------------------------------------------
    def __get_http_headers(self):
        """"""
        return self.__http_headers
    http_headers = property(__get_http_headers)

    #----------------------------------------------------------------------
    def __get_http_raw_headers(self):
        """"""
        return self.__body
    http_headers_raw = property(__get_http_raw_headers)

    #----------------------------------------------------------------------
    def __get_request_time(self):
        """"""
        return self.__request_time
    request_time = property(__get_request_time)

    #----------------------------------------------------------------------
    def __get_information(self):
        """"""
        self.__information

    information = property(__get_information)

