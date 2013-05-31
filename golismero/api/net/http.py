#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This package contains the classes that represent HTTP requests and responses.
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

from .web_utils import DecomposedURL
from ..data.information.html import HTML
from ...common import random

from os.path import basename

import hashlib
from re import findall


#------------------------------------------------------------------------------
class HTTP_Request (object):
    """
    HTTP request.
    """

    TYPE_HTTP      = 0    # No additional parsing
    TYPE_JSON      = 1    # Automatic JSON parsing
    TYPE_SOAP      = 2    # Automatic SOAP parsing
    TYPE_VIEWSTATE = 3    # Automatic Viewstate parsing

    DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible, GoLismero/2.0 The Web Knife; +http://code.google.com/p/golismero)"

    __user_agents = (
        "Opera/9.80 (Windows NT 6.1; U; zh-tw) Presto/2.5.22 Version/10.50",
        "Mozilla/6.0 (Macintosh; U; PPC Mac OS X Mach-O; en-US; rv:2.0.0.0) Gecko/20061028 Firefox/3.0",
        "Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1",
        "Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/13.0.1",
        "Mozilla/5.0 (X11; Linux i686; rv:6.0) Gecko/20100101 Firefox/6.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20120724 Debian Iceweasel/15.0",
        "Mozilla/5.0 (X11; Linux) KHTML/4.9.1 (like Gecko) Konqueror/4.9",
        "Lynx/2.8.8dev.3 libwww-FM/2.14 SSL-MM/1.4.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.6 Safari/537.11",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.2; SV1; .NET CLR 3.3.69573; WOW64; en-US)",
        "Mozilla/4.0(compatible; MSIE 7.0b; Windows NT 6.0)",
        "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; ja-jp) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
        "Mozilla/5.0 (BlackBerry; U; BlackBerry 9900; en) AppleWebKit/534.11+ (KHTML, like Gecko) Version/7.1.0.346 Mobile Safari/534.11+",
        "Mozilla/5.0 (PLAYSTATION 3; 3.55)",
        "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)"
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-us) AppleWebKit/534.16+ (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4",
        "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25"
    )


    #----------------------------------------------------------------------
    def __init__(self, url, method = 'GET', post_data = None, cache = True, follow_redirects = None, cookie = "", random_user_agent = False, request_type = 0):

        # Set method
        self.__method = method.upper() if method else "GET"

        # Set url
        self.__parsed_url = DecomposedURL(url)
        self.__url = self.__parsed_url.url

        # Follow redirects
        self.__follow_redirects = follow_redirects

        # Set headers
        self.__headers = {
            'User-Agent' : self.generate_user_agent() if random_user_agent else self.DEFAULT_USER_AGENT,
            'Accept-Language' : "en-US",
            'Accept' : self.__get_accept_type(),
        }

        # Cache?
        self.__cache = cache
        # Set cache headers
        if not self.__cache:
            self.__headers['Cache-Control'] = 'no-cache'
            self.__headers['Cache-Control'] = 'no-store'
            self.__headers['Pragma'] = 'no-cache'
            self.__headers['Expires'] = '0'

        # Post data
        self.__post_data = post_data

        # Post data
        if self.__post_data:
            self.__headers.update(self.__get_content_type())


        # Get type of request
        self.__type = request_type

        # This vas specify if request has files attached
        self.__files_attached = None

        # Id of request
        self.__request_id = None


    #----------------------------------------------------------------------
    #
    # Public functions
    #
    #----------------------------------------------------------------------

    def generate_user_agent(self):
        """
        :return: Return a random user agent string.
        :rtype: str
        """
        return self.__user_agents[random.randint(0, len(self.__user_agents) - 1)]


    #----------------------------------------------------------------------
    def add_file_from_file(self, path_to_file, alt_filename=None):
        """
        Add file from path

        :param path_to_file: Path to file to load.
        :type path_to_file: str

        :param alt_filename: If you set it, filename used for http post will be set to this.
        :type alt_filename: str
        """
        self.add_file_from_object(basename(path_to_file), open(path_to_file, "rb").read(), alt_filename)


    #----------------------------------------------------------------------
    def add_file_from_object(self, param_name, obj, alt_filename=None):
        """
        Add file from a binary object.

        :param param_name: Name of parameter in request.
        :type param_name: str

        :param obj: Binary object to send.
        :type obj: binary data

        :param alt_filename: If you set it, filename used for http post will be set to this.
        :type alt_filename: str
        """

        # Create dict, if not exits
        if not self.__files_attached:
            self.__files_attached = {}

        # Fix method, if it's GET
        if self.__method == "GET":
            self.__method = "POST"

        # Add data with true filename or alt filename
        if alt_filename:
            self.__files_attached[alt_filename] = obj
        else:
            self.__files_attached[param_name] = obj


    #----------------------------------------------------------------------
    #
    # Private functions
    #
    #----------------------------------------------------------------------

    def __get_accept_type(self, accept_type=None):
        """
        Get accepted types.

        :param accept_type: One of the following: "html", "text", "all".
        :type accept_type: str

        :returns: Value to use on the Accept: HTTP header.
        :rtype: str
        """

        m_types = {
            "html": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "text" : "text/plain",
            "all": "*/*"
        }

        # If type is in list
        if accept_type:
            if accept_type in m_types:
                return m_types[accept_type]

        # Otherwise
        return m_types["all"]


    #----------------------------------------------------------------------
    #
    # Read/write properties
    #
    #----------------------------------------------------------------------

    @property
    def hostname(self):
        """
        :return: 'Host' HTTP header.
        :rtype: str
        """
        return self.__headers.get('Host')

    @hostname.setter
    def hostname(self, value):
        """
        :param value: 'Host' HTTP header.
        :type value: str
        """
        assert isinstance(value, basestring)
        self.__headers['Host'] = value
        self.__parsed_url.hostname = self.__headers['Host']

    @property
    def user_agent(self):
        """
        :return: 'User-Agent' HTTP header.
        :rtype: str
        """
        return self.__headers.get('User-Agent')

    @user_agent.setter
    def user_agent(self, value):
        """
        :param value: 'User-Agent' HTTP header.
        :type value: str
        """
        assert isinstance(value, basestring)
        self.__headers['User-Agent'] = value

    @property
    def accept_language(self):
        """
        :return: 'Accept-Language' HTTP header.
        :rtype: str
        """
        return self.__headers.get('Accept-Language')

    @accept_language.setter
    def accept_language(self, value):
        """
        :param value: 'Accept-Language' HTTP header.
        :type value: str
        """
        assert isinstance(value, basestring)
        self.__headers['Accept-Language'] = value

    @property
    def accept(self):
        """
        :return: 'Accept' HTTP header.
        :rtype: str
        """
        return self.__headers.get('Accept')

    @accept.setter
    def accept(self, value):
        """
        :param value: 'Accept' HTTP header.
        :type value: str
        """
        assert isinstance(value, basestring)
        self.__headers['Accept'] = value

    @property
    def referer(self):
        """
        :return: 'Referer' HTTP header.
        :rtype: str
        """
        return self.__headers.get('Referer')

    @referer.setter
    def referer(self, value):
        """
        :param value: 'Referer' HTTP header.
        :type value: str
        """
        assert isinstance(value, basestring)
        self.__headers['Referer'] = value

    @property
    def cookie(self):
        """
        :return: 'Cookie' HTTP header.
        :rtype: str
        """
        return self.__headers.get('Cookie')

    @cookie.setter
    def cookie(self, value):
        """
        :param value: 'Cookie' HTTP header.
        :type value: str
        """
        assert isinstance(value, basestring)
        self.__headers['Cookie'] = value

    @property
    def content_type(self):
        """
        :return: 'Content-Type' HTTP header.
        :rtype: str
        """
        return self.__headers.get('Content-Type')

    @content_type.setter
    def content_type(self, value):
        """
        :param value: 'Content-Type' HTTP header.
        :type value: str
        """
        assert isinstance(value, basestring)
        self.__headers['Content-Type'] = value

    @property
    def post_data(self):
        """
        :return: HTTP POST data.
        :rtype: str
        """
        return self.__post_data

    @post_data.setter
    def post_data(self, value):
        """
        :param value: HTTP POST data.
        :type value: str
        """
        if self.__post_data:
            self.__post_data.update(value)
        else:
            self.__post_data = value
        self.content_type = "application/x-www-form-urlencoded; charset=UTF-8"

    @property
    def raw_headers(self):
        """
        :return: Raw HTTP headers.
        :rtype: dict(str -> str)
        """
        return self.__headers

    @raw_headers.setter
    def raw_headers(self, value):
        """
        :param value: Raw HTTP headers.
        :type value: dict(str -> str)
        """
        assert isinstance(value, dict)
        self.__headers.update(value)

    @property
    def follow_redirects(self):
        """
        :returns: Redirect options for the request (True to follow redirects, False no follow, None if not set).
        :rtype: None | bool
        """
        return self.__follow_redirects

    @follow_redirects.setter
    def follow_redirects(self, value):
        """
        :param value: Redirect options for the request (True to follow redirects, False no follow, None if not set).
        :type value: None | bool
        """
        self.__follow_redirects = value


    #----------------------------------------------------------------------
    #
    # Read-only properties
    #
    #----------------------------------------------------------------------
    @property
    def url(self):
        """
        :returns: String with URL of the request.
        :rtype: str
        """
        return self.__url

    @property
    def parsed_url(self):
        """
        :returns: URL split to its components.
        :rtype: DecomposedURL
        """
        return self.__parsed_url

    @property
    def method(self):
        """
        :returns: HTTP method used for this request.
        :rtype: str
        """
        return self.__method

    @property
    def is_cacheable(self):
        """
        :returns: True if the request is marked as cacheable, otherwise False.
        :rtype: bool
        """
        return self.__cache

    @property
    def request_type(self):
        """
        Type of HTTP request. Possible values are:
        0 - HTTP
        1 - JSON
        2 - SOAP
        3 - VIEWSTATE

        :returns: Type of HTTP request.
        :rtype: int
        """
        return self.__type

    @property
    def files_attached(self):
        """
        Attached filenames in the following format:

        .. code-block:: python

           {
              'file_name_1' : raw_object_1,
              'file_name_2' : raw_object_2
           }

        :returns: Attached filenames.
        :rtype: dict
        """
        return self.__files_attached

    @property
    def request_id(self):
        """
        :returns: Unique ID for this request.
        :rtype: str
        """
        if not self.__request_id:
            # Create data for key
            m_string = "%s|%s" % (self.__url, ''.join(( "%s:%s" % (k, v) for k,v in self.post_data.iteritems()) if self.post_data else ''))

            # Make the hash
            self.__request_id = hashlib.md5(m_string).hexdigest()
        return self.__request_id


#------------------------------------------------------------------------------
class HTTP_Response (object):
    """
    HTTP response.
    """

    def __init__(self):

        # Content type.
        self.__content_type = None

        # Raw HTTP headers.
        self.__http_headers_raw = None

        # Raw HTTP response.
        self.__raw_response = None

        # Total number of words in response body.
        self.__word_count = None

        # Total number of lines in response body.
        self.__lines_count = None

        # Total number of characters in response body.
        self.__char_count = None

        # Parent constructor.
        super(HTTP_Response, self).__init__()


    #----------------------------------------------------------------------
    @classmethod
    def from_custom_request(cls, raw_response, request_time):
        """
        This method make an HTTP Response object from a Request library.

        Using this method, raw response are not available.

        :param raw_response: HTTPResponse object, from Request library.
        :type raw_response: HTTPResponse

        :param request_time: time that the response was take.
        :type request_time: float

        :param request: The original request for this response.
        :para request: HTTP_Request
        """

        instance = cls()

        # Request time.
        instance.__request_time              = request_time

        # Raw response from server.
        instance.__raw_response              = ""

        # HTML data.
        instance.__raw_data                  = raw_response.content if raw_response.content else ""

        # HTTP response code.
        instance.__http_response_code        = raw_response.status_code

        # HTTP response reason.
        instance.__http_response_code_reason = raw_response.reason

        # HTTP headers.
        instance.__http_headers              = raw_response.headers
        instance.__http_headers_raw          = "".join(raw_response.headers)

        # Wrapper for cookie.
        instance.__cookie                    = raw_response.cookies.get_dict()

        return instance


    #----------------------------------------------------------------------
    @classmethod
    def from_raw_request(cls, raw_response, request_time):
        """
        This method make an HTTP Response object from a raw parse of HTTP response.

        :param raw_response: HttpParser object with the info.
        :type raw_response: HttpParse

        :param request_time: time that the response was take.
        :type request_time: float
        """

        instance = cls()

        # Request time.
        instance.__request_time              = request_time

        # Raw response from server.
        instance.__raw_response              = raw_response["raw_content"]

        # HTML data.
        instance.__raw_data                  = raw_response["content"]

        # HTTP response code.
        instance.__http_response_code        = raw_response["statuscode"]

        # HTTP response reason.
        instance.__http_response_code_reason = raw_response["statustext"]

        # HTTP headers.
        instance.__http_headers              = raw_response["headers"]
        instance.__http_headers_raw          = "".join(raw_response["headers"].headers)

        # Wrapper for cookie.
        instance.__cookie                    = raw_response.get("cookie") if raw_response.get("cookie") else raw_response.get("set-cookie") # Thus, 2 cookie modes are covered.

        return instance


    #----------------------------------------------------------------------

    @property
    def raw_content(self):
        """
        :returns: HTML data.
        :rtype: str
        """
        return self.__raw_data

    @property
    def raw_response(self):
        """
        :returns: Raw HTTP response.
        :rtype: str
        """
        return self.__raw_response

    @property
    def content_length(self):
        """
        :returns: Value of the 'Content-Length' header, or None if not found.
        :rtype: int | None
        """
        if self.__http_headers and 'Content-Length' in self.__http_headers:
            return int(self.__http_headers['Content-Length'])
        return None

    @property
    def cookie(self):
        """
        :returns: Value of the 'Cookie' header.
        :rtype: str
        """
        return self.__cookie

    @property
    def http_response_code(self):
        """
        :returns: HTTP response code.
        :rtype: int
        """
        return self.__http_response_code

    @property
    def http_response_reason(self):
        """
        :returns: Descriptive text for the HTTP response code.
        :rtype: str
        """
        return self.__http_response_code_reason

    @property
    def http_headers(self):
        """
        :returns: HTTP response headers.
        :rtype: dict(str -> str)
        """
        return self.__http_headers

    @property
    def http_headers_raw(self):
        """
        :returns: Raw HTTP response headers.
        :rtype: str
        """
        if not self.__http_headers_raw:
            self.__http_headers_raw = ''.join(("%s:%s\n" % (k,v) for k,v in self.__http_headers.iteritems()))
        return self.__http_headers_raw

    @property
    def request_time(self):
        """
        :returns: Get the response time, in seconds.
        :rtype: float
        """
        return self.__request_time

    @property
    def information(self):
        """
        :returns: Information object extracted from this HTTP response.
        :rtype: Information
        """

        m_return = None

        m_contents = {
            "text/html": HTML,
        }

        if self.content_type == "text/plain" or self.content_type == "unknown":
            m_return = self.raw_content
        else:
            m_return = m_contents[self.content_type](self.raw_content)

        return m_return

    @property
    def content_type(self):
        """
        Simplified content type identifier.

        This is not the same as the MIME type.

        Available types are:
        - html
        - text

        :returns: Simplified content type identifier.
        :rtype: str
        """
        if not self.__content_type:
            self.__content_type = self.http_headers.get("Content-Type").split(";")[0]
            if not self.__content_type:
                self.__content_type = "unknown"
        return self.__content_type


    #----------------------------------------------------------------------

    @property
    def char_count(self):
        """
        :returns: Number of chars in response body.
        :rtype: int
        """
        if self.__char_count is None:
            self.__char_count = len(self.__raw_data)
        return self.__char_count

    @property
    def lines_count(self):
        """
        :returns: Number of lines in response body.
        :rtype: int
        """
        if self.__lines_count is None:
            self.__lines_count = len(findall("\S+", self.__raw_data))
        return self.__lines_count

    @property
    def words_count(self):
        """
        :returns: Number of words in response body.
        :rtype: int
        """
        if not self.__word_count:
            self.__word_count = self.__raw_data.count('\n')
        return self.__word_count
