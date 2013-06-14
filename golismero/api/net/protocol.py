#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Network protocols API.
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

__all__ = ['NetworkAPI', 'NetworkException', 'Web']

from .cache import NetworkCache
from .http import HTTP_Request, HTTP_Response
from .web_utils import *
from ..config import Config
from ..data.resource.url import Url
from ..logger import Logger
from ...messaging.codes import MessageCode

from httpparser.httpparser import *
from requests import *
from requests.exceptions import RequestException
from time import time
from mimetools import Message
import socket

# Use StringIO instead of cStringIO because cStringIO can't be pickled,
# and mimetools.Message tries to store a copy of the "file descriptor".
# FIXME: this may be fixed by tweaking mimetools instead.
from StringIO import StringIO


#------------------------------------------------------------------------------
class NetworkException(Exception):
    """
    Network connection errors.
    """
    pass


#------------------------------------------------------------------------------
class NetworkOutOfScope(Exception):
    """
    Resource is out of audit scope.
    """
    pass


#------------------------------------------------------------------------------
class NetworkAPI (object):
    """
    Network protocols API.
    """

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

        :param protocol: Connection to receive. Must be one of the TYPE_* constants.
        :type protocol: int
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
                auth, _ = detect_auth_method(m_proxy_addr)

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
class ConnectionSlot (object):
    """
    Connection slot context manager.
    """

    @property
    def hostname(self):
        return self.__host

    def __init__(self, hostname):
        self.__host = hostname

    def __enter__(self):
        self.__token = Config._context.remote_call(
            MessageCode.MSG_RPC_REQUEST_SLOT, self.hostname, 1
        )
        if not self.__token:
            # XXX FIXME
            # This should block, not throw an error...
            raise IOError("Connection slots limit exceeded, try again later")

    def __exit__(self, type, value, tb):
        Config._context.remote_call(
            MessageCode.MSG_RPC_RELEASE_SLOT, self.__token
        )


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
    def clear(self):
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
    def clear(self):
        self.__http_pool_manager.clear()


    #----------------------------------------------------------------------
    def get(self, URL, method = "GET", timeout = 5, post_data = None, follow_redirect = None, cache = True):
        """
        Get response for an input URL.
        The URL parameter can be a string or an Url instance.

        .. note::
           Most plugins will only use this method.
           However, there are also more advanced
           methods for customized HTTP requests.

        Example with string:

        >>> from golismero.api.net.protocol import NetworkAPI
        >>> con = NetworkAPI.get_connection()
        >>> response = con.get("www.mysite.com", timeout=2, follow_redirect=True)
        >>> response.http_headers_raw
        HTTP/1.0 200 OK
        Date: Wed, 29 May 2013 18:44:54 GMT
        Server: Apache 2.2
        Content-Type: text/html; charset=utf-8
        >>> response.lines_count
        4

        Example with Url instance:

        >>> from golismero.api.net.protocol import NetworkAPI
        >>> from golismero.api.data.resource.url import Url
        >>> con = NetworkAPI.get_connection()
        >>> u = Url("www.mysite.com")
        >>> response = con.get(u)
        >>> response.request_time
        0.2
        >>> response.content_type
        "text/html"

        :param URL: string with URL or Url instance
        :type URL: str | Url

        :param cache: True to enable the network cache.
        :type cache: bool

        :param redirect: True to follow HTTP redirects.
        :type redirect: bool

        :param timeout: Timeout in seconds.
        :type timeout: int

        :returns: HTTP response object.
        :rtype: HTTP_Response

        :raises NetworkException: A network error has occurred.
        :raises NetworkOutOfScope: The requested URL is out of scope for this audit.
        """

        # Extract the raw URL when applicable
        m_referer = None
        try:
            if isinstance(URL, Url):
                URL       = URL.url
                m_referer = URL.referer
            elif isinstance(URL, basestring):
                URL       = URL
                # Parse, verify and canonicalize the URL
                parsed = DecomposedURL(URL)
                if not parsed.host or not parsed.scheme:
                    raise ValueError("Only absolute URLs must be used!")

        except AttributeError:
            pass

        # Check for host matching
        if not is_in_scope(URL):
            Logger.log_verbose("[!] Url '%s' is out of scope. Skipping it." % URL)
            raise NetworkOutOfScope("'%s' is out of scope." % URL)

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
        if m_referer:
            m_request.referer = m_referer

        return self.get_custom(m_request, timeout= timeout)


    #----------------------------------------------------------------------
    def get_custom(self, request, timeout = 5):
        """
        Get an HTTP response from a custom HTTP Request object.

        The HTTP Request object can be customized to do advanced requests.

        .. note::
           For more info about HTTP Request objects you can read :py:class:`HTTP_Request`

        Example:

        >>> from golismero.api.net.protocol import NetworkAPI
        >>> from golismero.api.net.http import HTTP_Request
        >>> conn = NetworkAPI.get_connection()
        >>> request = HTTP_Request("www.mysite.com")
        >>> request.accept = "application/x-javascript"
        >>> request.post_data = {'param1': 'value1', 'param2': 'value2'}
        >>> request.add_file_from_file("PATH_TO_MY_FILE")
        >>> response = conn.get_custom(request)
        >>> response.http_headers_raw
        HTTP/1.0 200 OK
        Date: Wed, 29 May 2013 18:44:54 GMT
        Server: Apache 2.2
        Content-Type: text/html; charset=utf-8

        :param request: HTTP request object.
        :type request: HTTP_Request

        :param timeout: Timeout in seconds.
        :type timeout: int

        :returns: HTTP response object.
        :rtype: HTTP_Response

        :raises NetworkException: A network error has occurred.
        :raises NetworkOutOfScope: The requested URL is out of scope for this audit.
        """
        if not isinstance(request, HTTP_Request):
            raise TypeError("Expected HTTP_Request, got %s instead" % type(request))

        # Check if the URL is within scope of the audit.
        if not is_in_scope(request.url):
            Logger.log_verbose("Url '%s' is out of scope. Skipping it." % request.url)
            raise NetworkOutOfScope("'%s' is out of scope." % request.url)

        # If the URL is cached, return the cached contents.
        if request.is_cacheable and self._cache.exists(request.request_id, protocol=request.parsed_url.scheme):
            return self._cache.get(request.request_id, protocol=request.parsed_url.scheme)

        #
        # Get URL
        #
        with ConnectionSlot(request.parsed_url.hostname):

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
                #'timeout' : timeout
            }

            # HTTP method
            m_method = request.method.upper()

            # Set files data, if available
            if m_method == "POST" or (m_method == "PUT" and request.files_attached):
                # Add files
                for fname, fvalue in request.files_attached.iteritems():
                    m_request_params["files"] = { 'file': (fname, fvalue) } # overloaded operator!

            # Select request type
            #
            # Fix URL: www.site.com -> http://www.site.com
            m_parsed_url = DecomposedURL(request.url)
            m_url = m_parsed_url.url

            if m_method not in ("GET", "POST", "HEAD", "OPTIONS", "PUT", "PATCH", "DELETE"):
                raise NotImplementedError("Method '%s' not allowed." % m_method)

            # Start timing the request
            t1 = time()

            # Issue the request
            try:
                m_response = getattr(self.__http_pool_manager, m_method.lower())(m_url, timeout = timeout, **m_request_params)
            except RequestException, e:
                raise NetworkException(e.message)

            # Stop timing the request
            t2 = time()

            # Calculate the request time
            m_time = t2 - t1

            # Parse the response
            #m_response = HTTP_Response(m_time)
            m_response = HTTP_Response.from_custom_request(m_response, m_time)

            # Cache the response if enabled
            if request.is_cacheable:
                self._cache.set(request.request_id, m_response,
                                protocol  = request.parsed_url.scheme,
                                timestamp = t1)

        # Return the response
        return m_response


    #----------------------------------------------------------------------
    def get_raw(self, host, request_content, timeout=2.0, port=80, proto="HTTP"):
        """
        This method allow you to make raw connections to a host.

        You must to provide the data that you want to send to the server.

        .. warning::
           This method only returns the HTTP response headers, **NOT THE CONTENT**.
           Also this method doesn't use the cache.

        Example:

        >>> from golismero.api.net.protocol import NetworkAPI
        >>> request = "GET / HTTP/1.1\\r\\nHost: www.mysite.com\\r\\n\\r\\n\"
        >>> con = NetworkAPI.get_connection()
        >>> response = con.get_raw(request)
        >>> response.http_headers_raw
        HTTP/1.0 200 OK
        Date: Wed, 29 May 2013 18:44:54 GMT
        Server: Apache 2.2
        Content-Type: text/html; charset=utf-8
        >>> response.lines_count
        4

        :param host: Host name to connect to.
        :type host: str

        :param request_content: Raw request to send.
        :type request_content: str

        :param timeout: Timeout in seconds.
        :type timeout: float

        :param port: TCP port to connect to.
        :type port: int

        :param proto: Network protocol.
        :type proto: str

        :return: HTTP response. Only the headers are parsed, not the contents.
        :rtype: HTTPResponse

        :raises NetworkException: A network error has occurred.
        :raises NetworkOutOfScope: The requested URL is out of scope for this audit.
        """

        # Check if the URL is within scope of the audit.
        if not is_in_scope(host):
            Logger.log_verbose("Url '%s' out of scope. Skipping it." % host)
            raise NetworkOutOfScope("'%s' is out of scope." % host)

        # Get a connection slot.
        with ConnectionSlot(host):

            # Start timing the request.
            t1 = time()

            # Connect to the server.
            try:
                s = socket.socket()        # XXX FIXME: this fails for IPv6!
                try:
                    s.settimeout(timeout)
                    s.connect((host, port))
                    try:

                        # Send the HTTP request.
                        s.sendall(request_content)

                        # Get the HTTP response headers.
                        raw_response = StringIO()
                        while True:
                            data = s.recv(1)
                            if not data:
                                raise NetworkException("Server has closed the connection")
                            raw_response.write(data)
                            if raw_response.getvalue().endswith("\r\n\r\n"):
                                break   # full HTTP headers received
                            if len(raw_response.getvalue()) > 65536:
                                raise NetworkException("Response headers too long")

                        # TODO: add support for reading the data as well,
                        #       this could mean having to parse HTTP for real
                        #       and automatically storing large files on disk

                    # Close the connection and clean up the socket.
                    finally:
                        try:
                            s.shutdown(2)
                        except Exception:
                            pass
                finally:
                    try:
                        s.close()
                    except Exception:
                        pass

                # Stop timing the request.
                t2 = time()

                # Build the response dictionary.
                try:
                    m_response = {}

                    # Store the raw response data.
                    raw_content = raw_response.getvalue()
                    m_response["raw_content"] = raw_content

                    # Split the response line from the headers.
                    request_line, raw_headers = raw_content.split("\r\n", 1)

                    # Parse the response line.
                    # FIXME: use a proper HTTP parser here!
                    protocol, statuscode, statustext = request_line.strip().split(" ", 2)
                    protocol, version = protocol.split("/", 1)

                    # Store the parsed response line.
                    m_response["protocol"]   = protocol.strip().upper()
                    m_response["version"]    = version.strip()
                    m_response["statuscode"] = statuscode.strip()
                    m_response["statustext"] = statustext.strip()

                    # Parse and store the response headers.
                    m_response["headers"] = Message(StringIO(raw_headers))

                    # XXX HACK: store an empty content to keep HTTP_Response from crashing.
                    m_response["content"] = ""

                # On parse error, send an exception.
                except Exception, e:
                    raise NetworkException("Error parsing the response: %s" % str(e))

            # On socket errors, send an exception.
            except socket.error, e:
                raise NetworkException(e.message)

        # Calculate the request time.
        m_time = t2 - t1

        # Return an HTTP response object.
        return HTTP_Response.from_raw_request(m_response, m_time)
