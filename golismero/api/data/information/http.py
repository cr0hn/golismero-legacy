#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTTP requests and responses.
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

__all__ = ["HTTP_Request", "HTTP_Response"]

from . import Information
from .html import HTML
from .. import identity
from ...net.web_utils import DecomposedURL

import httplib
import mimetools


#------------------------------------------------------------------------------
class HTTP_Headers (object):
    """
    HTTP headers.

    Unlike other methods of storing HTTP headers in Python this class preserves
    the original order of the headers, doesn't remove duplicated headers,
    preserves the original case but still letting your access them in a
    case-insensitive manner, and is read-only.
    """

    # Also see: https://en.wikipedia.org/wiki/List_of_HTTP_header_fields


    #----------------------------------------------------------------------
    def __init__(self, headers):
        """
        :param headers: Parsed headers to store.
        :type headers: tuple( tuple(str, str) )
        """

        # Headers in original form.
        self.__headers = tuple( [ (name, value) for name, value in headers ] )

        # Headers parsed as a dictionary of lowercase keys.
        strip = self.__strip_value
        self.__cache = { name.strip().lower() : strip(value) for name, value in headers }

    @staticmethod
    def __strip_value(value):
        lines = value.split("\r\n")
        lines[0] = strip()
        for i in xrange(1, len(lines)):
            lines[i] = " " + lines[i].strip()
        return "\r\n".join(lines)


    #----------------------------------------------------------------------
    def __repr__(self):
        return "<HTTP_Headers headers=%r>" % self.__headers


    #----------------------------------------------------------------------
    def to_tuple(self):
        """
        Convert the headers to Python tuples of strings.

        :returns: Headers.
        :rtype: tuple( tuple(str, str) )
        """
        return self.__headers   # well, that one was easy ;)


    #----------------------------------------------------------------------
    def __iter__(self):
        """
        When iterated, whole header lines are returned.
        To iterate header names and values use iterkeys(), itervalues()
        or iteritems().

        :returns: Iterator of header lines.
        :rtype: iter(str)
        """
        return ("%s: %s\r\n" % item for item in self.__headers)


    #----------------------------------------------------------------------
    def iteritems(self):
        """
        When iterating, the original case and order of the headers
        is preserved. This means some headers may be repeated.

        :returns: Iterator of header names and values.
        :rtype: iter( tuple(str, str) )
        """
        return self.__headers.__iter__()


    #----------------------------------------------------------------------
    def iterkeys(self):
        """
        When iterating, the original case and order of the headers
        is preserved. This means some headers may be repeated.

        :returns: Iterator of header names.
        :rtype: iter(str)
        """
        return (name for name, _ in self.__headers)


    #----------------------------------------------------------------------
    def itervalues(self):
        """
        When iterating, the original case and order of the headers
        is preserved. This means some headers may be repeated.

        :returns: Iterator of header values.
        :rtype: iter(str)
        """
        return (value for _, value in self.__headers)


    #----------------------------------------------------------------------
    def __getitem__(self, key):
        """
        The [] operator works both for index lookups and key lookups.

        When provided with an index, the whole header line is returned.

        When provided with a header name, the value is looked up.
        Only the first header of that name is returned. Comparisons
        are case-insensitive.

        :param key: Index or header name.
        :type key: int | str

        :returns: Header line (for indices) or value (for names).
        :rtype: str
        """
        if type(key) in (int, long):
            return "%s: %s\r\n" % self.__headers[key]
        return self.__cache[ key.lower() ]


    #----------------------------------------------------------------------
    def get(self, name, default = None):
        """
        Get a header by name.

        Comparisons are case-insensitive. When more than one header has
        the requested name, only the first one is returned.

        :param name: Header name.
        :type name: str

        :returns: Header value.
        :rtype: str
        """
        try:
            return self.__cache[ name.lower() ]
        except KeyError:
            return default


    #----------------------------------------------------------------------
    def __getslice__(self, start = None, end = None):
        """
        When sliced, whole header lines are returned in a single string.

        :param start: Start of the slice.
        :type start: int | None

        :param end: End of the slice.
        :type end: int | None

        :returns: The requested header lines merged into a single string.
        :rtype: str
        """
        return "".join("%s: %s\r\n" % item for item in self.__headers[start:end])


    #----------------------------------------------------------------------
    def __str__(self):
        """
        When converted into a string, all header lines are merged, and an
        empty line is appended.

        :returns: All header lines, followed by an empty line.
        :rtype: str
        """
        return "".join("%s: %s\r\n" % item for item in self.__headers) + "\r\n"


#------------------------------------------------------------------------------
class HTTP_Request (Information):
    """
    HTTP request information.
    """

    information_type = INFORMATION_HTTP_REQUEST

    DEFAULT_HEADERS = (
        ("User-Agent", "Mozilla/5.0 (compatible, GoLismero/2.0 The Web Knife; +https://github.com/cr0hn/golismero)"),
        ("Accept-Language", "en-US"),
        ("Accept", "*/*"),
        ("Cache-Control", "no-store"),
        ("Pragma", "no-cache"),
        ("Expires", "0"),
    )


    #----------------------------------------------------------------------
    def __init__(self, url, headers = None, post_data = None, method = "GET", protocol = "HTTP", version = "1.1"):
        """
        :param url: Absolute URL to connect to.
        :type url: str

        :param headers: HTTP headers. Defaults to DEFAULT_HEADERS.
        :type headers: HTTP_Headers | dict(str -> str) | tuple( tuple(str, str) )

        :param post_data: POST data.
        :type post_data: str | None

        :param method: HTTP method.
        :type method: str

        :param protocol: Protocol name.
        :type protocol: str

        :param version: Protocol version.
        :type version: str
        """

        # HTTP method.
        self.__method = method.upper()

        # URL.
        self.__parsed_url = DecomposedURL(url)
        self.__url = self.__parsed_url.url

        # HTTP headers.
        if headers is None:
            headers = self.DEFAULT_HEADERS
            if version == "1.1":
                headers = ("Host", self.__parsed_url.host) + headers
            headers = HTTP_Headers(headers)
        elif not isinstance(headers, HTTP_Headers):
            if hasattr(headers, "items"):
                headers = HTTP_Headers(sorted(headers.items()))
            else:
                headers = HTTP_Headers(sorted(headers))
        self.__headers = headers

        # POST data.
        self.__post_data = post_data

        # Call the parent constructor.
        super(HTTP_Request, self).__init__()


    #----------------------------------------------------------------------

    @identity
    def method(self):
        """
        :returns: HTTP method.
        :rtype: str
        """
        return self.__method

    @identity
    def url(self):
        """
        :returns: URL.
        :rtype: str
        """
        return self.__url

    @identity
    def protocol(self):
        """
        :returns: Protocol name.
        :rtype: str
        """
        return self.__protocol

    @identity
    def version(self):
        """
        :returns: Protocol version.
        :rtype: str
        """
        return self.__version

    @identity
    def headers(self):
        """
        :return: HTTP headers.
        :rtype: HTTP_Headers
        """
        return self.__headers

    @identity
    def post_data(self):
        """
        :return: POST data.
        :rtype: str | None
        """
        return self.__post_data


    #----------------------------------------------------------------------

    @property
    def parsed_url(self):
        """
        :returns: URL split to its components.
        :rtype: DecomposedURL
        """
        return self.__parsed_url

    @property
    def hostname(self):
        """
        :return: 'Host' HTTP header.
        :rtype: str
        """
        return self.__headers.get('Host')

    @property
    def user_agent(self):
        """
        :return: 'User-Agent' HTTP header.
        :rtype: str
        """
        return self.__headers.get('User-Agent')

    @property
    def accept_language(self):
        """
        :return: 'Accept-Language' HTTP header.
        :rtype: str
        """
        return self.__headers.get('Accept-Language')

    @property
    def accept(self):
        """
        :return: 'Accept' HTTP header.
        :rtype: str
        """
        return self.__headers.get('Accept')

    @property
    def referer(self):
        """
        :return: 'Referer' HTTP header.
        :rtype: str
        """
        return self.__headers.get('Referer')

    @property
    def cookie(self):
        """
        :return: 'Cookie' HTTP header.
        :rtype: str
        """
        return self.__headers.get('Cookie')

    @property
    def content_type(self):
        """
        :return: 'Content-Type' HTTP header.
        :rtype: str
        """
        return self.__headers.get('Content-Type')

    @property
    def content_length(self):
        """
        :return: 'Content-Length' HTTP header.
        :rtype: str
        """
        return self.__headers.get('Content-Length')


#------------------------------------------------------------------------------
class HTTP_Response (Information):
    """
    HTTP response information.
    """

    information_type = INFORMATION_HTTP_RESPONSE


    #----------------------------------------------------------------------
    def __init__(self, request, **kwargs):
        """
        All optional arguments must be passed as keywords.

        :param request: HTTP request that originated this response.
        :type request: HTTP_Request

        :param raw_response: (Optional) Raw bytes received from the server.
        :type raw_response: str

        :param status: (Optional) HTTP status code. Defaults to "200".
        :type status: str

        :param reason: (Optional) HTTP reason message.
        :type reason: str

        :param protocol: (Optional) Protocol name. Defaults to "HTTP".
        :type protocol: str

        :param version: (Optional) Protocol version. Defaults to "1.1".
        :type version: str

        :param raw_headers: (Optional) Raw HTTP headers.
        :type raw_headers: str

        :param headers: (Optional) Parsed HTTP headers.
        :type headers: HTTP_Headers | dict(str -> str) | tuple( tuple(str, str) )

        :param data: (Optional) Raw data that followed the response headers.
        :type data: str
        """

        # Initialize everything.
        self.__raw_response = None
        self.__raw_headers  = None
        self.__status       = "200"
        self.__reason       = None
        self.__protocol     = "HTTP"
        self.__version      = "1.1"
        self.__headers      = None
        self.__data         = None

        # Raw response bytes.
        self.__raw_response = kwargs.get("raw_response", None)
        if self.__raw_response:
            self.__parse_raw_response()

        # Status line.
        self.__status   = kwargs.get("status",   self.__status)
        self.__reason   = kwargs.get("reason",   self.__reason)
        self.__protocol = kwargs.get("protocol", self.__protocol)
        self.__version  = kwargs.get("version",  self.__version)
        if self.__status and not self.__reason:
            try:
                self.__reason = httplib.responses[self.__status]
            except Exception:
                pass
        elif not self.__status and self.__reason:
            lower_reason = self.__reason.strip().lower()
            for code, text in httplib.responses.iteritems():
                if text.lower() == lower_reason:
                    self.__status = str(code)
                    break

        # HTTP headers.
        self.__raw_headers = kwargs.get("raw_headers", self.__raw_headers)
        self.__headers = kwargs.get("headers", self.__headers)
        if self.__headers:
            if not isinstance(self.__headers, HTTP_Headers):
                if hasattr(headers, "items"):
                    self.__headers = HTTP_Headers(sorted(self.__headers.items()))
                else:
                    self.__headers = HTTP_Headers(sorted(self.__headers))
            if not self.__raw_headers:
                self.__reconstruct_raw_headers()
        elif self.__raw_headers and not self.__headers:
            self.__parse_raw_headers()

        # Data.
        self.__data = kwargs.get("data",  self.__data)

        # Reconstruct the raw response if needed.
        if not self.__raw_response:
            self.__reconstruct_raw_response()

        # Call the parent constructor.
        super(HTTP_Response, self).__init__()

        # Link this response to the request that originated it.
        self.add_link(request)


    #----------------------------------------------------------------------

    @identity
    def raw_response(self):
        """
        :returns: Raw HTTP response.
        :rtype: str | None
        """
        return self.__raw_response


    #----------------------------------------------------------------------

    @property
    def status(self):
        """
        :returns: HTTP status code.
        :rtype: str | None
        """
        return self.__status

    @property
    def reason(self):
        """
        :returns: HTTP reason message.
        :rtype: str | None
        """
        return self.__reason

    @property
    def protocol(self):
        """
        :returns: Protocol name.
        :rtype: str | None
        """
        return self.__protocol

    @property
    def version(self):
        """
        :returns: Protocol version.
        :rtype: str | None
        """
        return self.__version

    @property
    def headers(self):
        """
        :return: HTTP headers.
        :rtype: dict(str -> str) | None
        """
        return self.__headers

    @property
    def raw_headers(self):
        """
        :returns: HTTP method used for this request.
        :rtype: str | None
        """
        return self.__raw_headers

    @property
    def data(self):
        """
        :return: Response data.
        :rtype: str | None
        """
        return self.__data

    @property
    def content_length(self):
        """
        :return: 'Content-Length' HTTP header.
        :rtype: str | None
        """
        if self.__headers:
            return self.__headers.get('Content-Length')

    @property
    def content_disposition(self):
        """
        :return: 'Content-Disposition' HTTP header.
        :rtype: str | None
        """
        if self.__headers:
            return self.__headers.get('Content-Disposition')

    @property
    def transport_encoding(self):
        """
        :return: 'Transport-Encoding' HTTP header.
        :rtype: str | None
        """
        if self.__headers:
            return self.__headers.get('Transport-Encoding')

    @property
    def cookie(self):
        """
        :return: 'Set-Cookie' HTTP header.
        :rtype: str | None
        """
        if self.__headers:
            return self.__headers.get('Set-Cookie')

    set_cookie = cookie

    @property
    def server(self):
        """
        :return: 'Server' HTTP header.
        :rtype: str | None
        """
        if self.__headers:
            return self.__headers.get('Server')


    #----------------------------------------------------------------------
    def __parse_raw_response(self):

        # TODO

        pass


    #----------------------------------------------------------------------
    def __reconstruct_raw_response(self):

        # TODO

        pass

##        # FIXME: now sure how Requests handles content encoding,
##        # it may be possible to generate broken raw responses if
##        # the content is decoded automatically behind our backs
##
##        if self.__protocol and self.__version:
##            proto_ver = "%s/%s " % (self.__protocol, self.__version)
##        elif self.__protocol:
##            proto_ver = self.__protocol + " "
##        elif self.__version:
##            proto_ver = self.__version + " "
##        else:
##            proto_ver = ""
##        if self.__status and self.__reason:
##            status_line = "%s%s %s\r\n" % (proto_ver, self.__status, self.__reason)
##        elif self.__status:
##            status_line = "%s%s\r\n" % (proto_ver, self.__status)
##        elif self.__reason:
##            status_line = "%s%s\r\n" % (proto_ver, self.__reason)
##        return "%s%s%s" % (status_line, self.__raw_headers, self.__data)


    #----------------------------------------------------------------------
    def __parse_raw_headers(self):

        # TODO

        pass


    #----------------------------------------------------------------------
    def __reconstruct_raw_headers(self):
        self.__raw_headers = str(self.__headers)
