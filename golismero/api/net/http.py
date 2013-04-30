#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

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

__all__ = ["HTTP_Request", "HTTP_Response"]

from .web_utils import DecomposedURL
from ..data.information.html import HTML
from ..data.resource.url import Url
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
        """Return a random user agent string"""
        return self.__user_agents[random.randint(0, len(self.__user_agents) - 1)]


    #----------------------------------------------------------------------
    def add_file_from_file(self, path_to_file, alt_filename=None):
        """Add file from path

        :param path_to_file: path to file to load.
        :type path_to_file: str

        :param alt_filename: if you set it, filename used for http post will be set to this.
        :type alt_filename: str
        """
        if path_to_file and param_name:
            self.add_file_from_object(basename(path_to_file), open(path_to_file, "rb").read(), alt_filename)


    #----------------------------------------------------------------------
    def add_file_from_object(self, param_name, obj, alt_filename=None):
        """Add file from a binary object.

        :param param_name: name of parameter in resquest
        :type param_name: str

        :param obj: binary object to send
        :type obj: binary data

        :param alt_filename: if you set it, filename used for http post will be set to this.
        :type alt_filename: str
        """
        if param_name and obj:

            # Create dict, if not exits
            if not self.__files_attached:
                self.__files_attached = {}

            # Fix method, if it's GET
            if self.__method == "GET":
                self.__method = "POST"

            # Add data with true filename or alt filename
            if alt_filename:
                self.__files_attached[file_name] = obj
            else:
                self.__files_attached[param_name] = obj


    #----------------------------------------------------------------------
    #
    # Private functions
    #
    #----------------------------------------------------------------------

    def __get_accept_type(self, accept_type=None):
        """Get accepted types.

        :param accept_type: One of the following: "html", "text", "all"
        :type accept_type: str

        :returns: str -- Value to use on the Accept: HTTP header.
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
        "'Host' HTTP header"
        return self.__headers.get('Host')

    @hostname.setter
    def hostname(self, value):
        assert isinstance(value, basestring)
        self.__headers['Host'] = value
        self.__parsed_url.hostname = self.__headers['Host']

    @property
    def user_agent(self):
        "'User-Agent' HTTP header"
        return self.__headers.get('User-Agent')

    @user_agent.setter
    def user_agent(self, value):
        assert isinstance(value, basestring)
        self.__headers['User-Agent'] = value

    @property
    def accept_language(self):
        "'Accept-Language' HTTP header"
        return self.__headers.get('Accept-Language')

    @accept_language.setter
    def accept_language(self, value):
        assert isinstance(value, basestring)
        self.__headers['Accept-Language'] = value

    @property
    def accept(self):
        "'Accept' HTTP header"
        return self.__headers.get('Accept')

    @accept.setter
    def accept(self, value):
        assert isinstance(value, basestring)
        self.__headers['Accept'] = value

    @property
    def referer(self):
        "'Referer' HTTP header"
        return self.__headers.get('Referer')

    @referer.setter
    def referer(self, value):
        assert isinstance(value, basestring)
        self.__headers['Referer'] = value

    @property
    def cookie(self):
        "'Cookie' HTTP header"
        return self.__headers.get('Cookie')

    @cookie.setter
    def cookie(self, value):
        assert isinstance(value, basestring)
        self.__headers['Cookie'] = value

    @property
    def content_type(self):
        "'Content-Type' HTTP header"
        return self.__headers.get('Content-Type')

    @content_type.setter
    def content_type(self, value):
        assert isinstance(value, basestring)
        self.__headers['Content-Type'] = value

    @property
    def post_data(self):
        "HTTP POST data"
        return self.__post_data

    @post_data.setter
    def post_data(self, value):
        if self.__post_data:
            self.__post_data.update(value)
        else:
            self.__post_data = value
        self.content_type = "application/x-www-form-urlencoded; charset=UTF-8"

    @property
    def raw_headers(self):
        "Raw HTTP headers"
        return self.__headers

    @raw_headers.setter
    def raw_headers(self, value):
        assert isinstance(value, dict)
        self.__headers.update(value)

    @property
    def follow_redirects(self):
        """
        Redirect options for the request (True to follow redirects, False otherwise).

        :returns: None | bool. None if not set. Bool otherwise.
        """
        return self.__follow_redirects

    @follow_redirects.setter
    def follow_redirects(self, value):
        self.__follow_redirects = value


    #----------------------------------------------------------------------
    #
    # Read-only properties
    #
    #----------------------------------------------------------------------
    @property
    def url(self):
        """
        String with URL of the request.

        :returns: str
        """
        return self.__url

    @property
    def parsed_url(self):
        """
        Returns the URL split to its components.

        :returns: DecomposedURL
        """
        return self.__parsed_url

    @property
    def method(self):
        """
        HTTP method used for this request.

        :returns: str
        """
        return self.__method

    @property
    def is_cacheable(self):
        """
        If request is marked as cacheable return True, else False.

        :returns: bool
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

        :returns: int
        """
        return self.__type

    @property
    def files_attached(self):
        """
        Get a dictionary with filenames attached, in the following format:
        {
          'file_name_1' : raw_object_1,
          'file_name_2' : raw_object_2,
        }

        :returns: dict
        """
        return self.__files_attached

    @property
    def request_id(self):
        """
        Get a unique ID for this request.

        :returns: str
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


    #----------------------------------------------------------------------
    def __init__(self, raw_response, request_time, request):

        # Request that produced this response
        self.__request = request

        # HTML code of response
        self.__raw_data = raw_response.content if raw_response.content else ""

        # HTTP response code
        self.__http_response_code = raw_response.status_code

        # HTTP response reason
        self.__http_response_code_reason = raw_response.reason

        # HTTP headers
        self.__http_headers = raw_response.headers

        # HTTP headers in raw format
        self.__http_headers_raw = None

        # Request time
        self.__request_time = request_time

        # Information object
        self.__information = None

        # Wrapper for cookie
        self.__cookie = raw_response.cookies.get_dict()

        # Content type
        self.__content_type = None

        #
        # Counters
        #

        # Total number of words of body response
        self.__word_count = None

        # Total number of lines of body response
        self.__lines_count = None

        # Total number of characters of body response
        self.__char_count = None

        #
        # Parent constructor
        #
        super(HTTP_Response, self).__init__()


    #----------------------------------------------------------------------
    def __extract_information(self, headers, data):
        """
        Get an information object from a raw response.
        """
        m_return_content = None
        if headers:
            m_content_type = headers.get("content-type", "text/html")

            # Parse HTML
            if m_content_type.startswith('text/html'):
                self.__content_type = "html"
                m_return_content = HTML(data)
            elif m_content_type.startswith('text/plain'):
                self.__content_type = "text"
                #m_return_content = data
            else:
                self.__content_type = "unknown"
                #m_return_content = data
        return m_return_content


    #----------------------------------------------------------------------
    @property
    def request_from(self):
        """
        Original request that generated this response.

        :returns: An HTTP_Request object.
        """
        return self.__request

    @property
    def raw(self):
        """
        Get raw information from the HTTP response.

        :returns: str
        """
        return self.__raw_data

    @property
    def content_length(self):
        """
        Integer value of the 'Content-Length' header.

        If the value can't be obtained, None is returned.

        :returns: int | None
        """
        if self.__http_headers and 'Content-Length' in self.__http_headers:
            return int(self.__http_headers['Content-Length'])
        return None

    @property
    def cookie(self):
        """
        Value of the 'Cookie' header.

        :returns: str
        """
        return self.__request.cookie

    @property
    def http_response_code(self):
        """
        HTTP response code.

        :returns: int
        """
        return self.__http_response_code

    @property
    def http_response_reason(self):
        """
        Descriptive text for the HTTP response code.

        :returns: str
        """
        return self.__http_response_code_reason

    @property
    def http_headers(self):
        """
        HTTP response headers.

        :returns: dict
        """
        return self.__http_headers

    @property
    def http_raw_headers(self):
        """
        Raw HTTP response headers.

        :returns: str
        """
        if not self.__http_headers_raw:
            self.__http_headers_raw = ''.join(("%s: %s\n" % (k,v) for k,v in raw_response.headers.iteritems()))
        return self.__http_headers_raw

    @property
    def request_time(self):
        """
        Get the response time, in seconds.

        :retuns: float
        """
        return self.__request_time

    @property
    def information(self):
        """
        Information object extracted from this HTTP response.

        :returns: Information
        """
        if self.__information is None:
            self.__information = self.__extract_information(self.__http_headers, self.__raw_data)
        return self.__information

    @property
    def content_type(self):
        """
        Simplified content type identifier.

        This is not the same as the MIME type.

        Available types are:
        - html
        - text
        """
        return self.__content_type


    #----------------------------------------------------------------------
    @property
    def char_count(self):
        """Number of chars in response body"""
        if self.__char_count is None:
            self.__char_count = len(self.__raw_data)
        return self.__char_count

    @property
    def lines_count(self):
        """Number of lines in response body"""
        if self.__lines_count is None:
            self.__lines_count = len(findall("\S+", self.__raw_data))
        return self.__lines_count

    @property
    def words_count(self):
        """Number of words in response body"""
        if not self.__word_count:
            self.__word_count = self.__raw_data.count('\n')
        return self.__word_count
