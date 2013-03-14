#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------
# Network protocols API
#-----------------------------------------------------------------------

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

__all__ = ['NetworkAPI', 'NetworkException', 'Web']

from .cache import NetworkCache
from ..config import Config
from ..data.information.http import HTTP_Request, HTTP_Response
from ..data.resource.url import Url
from ..logger import Logger
from .web_utils import *

from re import compile, match, IGNORECASE
from requests import *
from requests.exceptions import RequestException as NetworkException
from time import time


#------------------------------------------------------------------------------
class NetworkAPI (object):
    """"""

    TYPE_WEB = 0
    TYPE_FTP = 1

    TYPE_FIRST = TYPE_WEB
    TYPE_LAST  = TYPE_FTP

    # Pool manager. One pool per target.
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
        if NetworkAPI.__http_pool_manager is None:

            # Set pool
            NetworkAPI.__http_pool_manager = Session()

            # If proxy
            m_proxy_addr = Config.audit_config.proxy_addr
            if m_proxy_addr:
                m_auth_user = Config.audit_config.proxy_user
                m_auth_pass = Config.audit_config.proxy_pass

                # Detect auth method
                auth, realm = detect_auth_method(m_proxy_addr, m_auth_user, m_auth_pass)

                # Set auth and proxy
                NetworkAPI.__http_pool_manager.auth = get_auth_obj(auth, m_auth_user, m_auth_pass)
                NetworkAPI.__http_pool_manager.proxies = {'http': m_proxy_addr}



            # Set cookie
            m_cookies = Config.audit_config.cookie
            if m_cookies:
                NetworkAPI.__http_pool_manager.cookies = m_cookies

        if protocol is NetworkAPI.TYPE_WEB:
            return Web(NetworkAPI.__http_pool_manager, Config.audit_config)

        else:
            raise ValueError("Unknown protocol type, value: %d" % protocol)


#------------------------------------------------------------------------------
class Protocol (object):
    """
    Superclass for networks protocols.
    """


    #----------------------------------------------------------------------
    def __init__(self):

        # Network cache API.
        self._cache = NetworkCache()


    #----------------------------------------------------------------------
    def state(self):
        pass


    #----------------------------------------------------------------------
    def close(self):
        """
        Release all resources associated with this object.
        """
        pass


    #----------------------------------------------------------------------
    def get(self, URL, cache = True):
        """
        Fetch a resource, optionally specifying if it must be stored
        in the cache.

        :param URL: URL to get.
        :type URL: str

        :param cache: True if response must be cached, False if it must not, None if it's indifferent.
        :type cache: bool
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


#------------------------------------------------------------------------------
#
# Web protocols.
#
#------------------------------------------------------------------------------
class Web (Protocol):
    """
    Web protocols handler (HTTP, HTTPS).
    """


    #----------------------------------------------------------------------
    def __init__(self, http_pool, config):
        super(Web, self).__init__()

        self.__http_pool_manager = http_pool
        self.__config = config

        # Global option for redirects
        self.__follow_redirects = config.follow_redirects


    #----------------------------------------------------------------------
    def state(self):
        pass


    #----------------------------------------------------------------------
    def close(self):
        self.__http_pool_manager.clear()


    #----------------------------------------------------------------------
    def get_custom(self, request):
        """Get an HTTP response from a custom HTTP Request object.

        :param request: An HTTP request object.
        :type request: HTTP_request

        :returns: HTTP_Response -- HTTP response object | None
        """
        if not isinstance(request, HTTP_Request):
            raise TypeError("Expected HTTP_Request, got %s instead" % type(URL))

        # Check if the URL is within scope of the audit.
        if not is_in_scope(request.url):
            Logger.log_verbose("Url '%s' out of scope. Skipping it." % request.url)
            return

        m_response = None
        m_time = None

        # URL is cached?
        if request.is_cacheable and self._cache.exists(request.request_id):
            m_response = self._cache[request.request_id]
        else:
            #
            # Get URL
            #

            # Set redirect option
            request.follow_redirects = request.follow_redirects or self.__follow_redirects


            # allow_redirects
            # headers
            #
            # files = {'file': open('report.xls', 'rb')}
            # r = requests.post(url, files=files)
            #
            #  GET, OPTIONS, HEAD, POST, PUT, PATCH and DELETE.



            # Set options
            m_request_params = {
                'allow_redirects' : request.follow_redirects,
                'headers' : request.raw_headers,
            }

            # HTTP method
            m_method = request.method.upper()

            # Set files data, if available
            if m_method == "POST" or (m_method == "PUT" and request.files_attached):
                # Add files
                for fname, fvalue in request.files_attached.iteritems():
                    m_request_params["files"] = { 'file': (fname, fvalue) } # overloaded operator!

            # Select request type
            m_url = request.url
            if m_method not in ("GET", "POST", "HEAD", "OPTIONS", "PUT", "PATCH", "DELETE"):
                raise NotImplementedError("Method '%s' not allowed." % m_method)

            # Start timing the request
            t1 = time()

            # Issue the request
            m_response = getattr(self.__http_pool_manager, m_method.lower())(m_url, **m_request_params)

            # Stop timing the request
            t2 = time()

            # Calculate the request time
            m_time = t2 - t1

            # Parse the response
            m_response = HTTP_Response(m_response, m_time, request)

            # Cache the response if enabled
            if request.is_cacheable:
                self._cache.set(request.request_id, m_response,
                                protocol  = request.parsed_url.scheme,
                                timestamp = t1)

        # Return the response
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
        m_referer = None
        try:
            URL = URL.url

            # Set referer option
            m_referer = URL.referer if URL.referer else ''

        except AttributeError:
            pass

        # Check for host matching
        if not is_in_scope(URL):
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

        # Set referer
        m_request.referer = m_referer

        return self.get_custom(m_request)
