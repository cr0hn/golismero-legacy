#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
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

__all__ = ["Url"]

from . import Resource
from .baseurl import BaseUrl
from .domain import Domain
from .. import identity
from ...net.web_utils import DecomposedURL, is_in_scope


#------------------------------------------------------------------------------
class Url(Resource):
    """
    URL information type.

    This resource referer to a complete URL, like:

    - http://www.my_site.com/index.php?param1=value1
    - site.com/users/

    It has the properties of an Url:

    - Domain name.
    - Get parameters.
    - Post parameters.
    - ...

    """

    resource_type = Resource.RESOURCE_URL


    #----------------------------------------------------------------------
    def __init__(self, url, method = "GET", url_params = None, post_params = None, content_type = None, depth = 0, request_type = 0, referer = ""):
        """
        Construct a URL information type.

        :param url: URL to manage
        :type url: str


        :param method: HTTP method to get URL
        :type method: str

        :param url_params: params inside URL
        :type url_params: dict

        :param post_params: params inside post
        :type post_params: dict

        :param deep: The deep of URL in relation with main site.
        :type deep: int
        """
        assert isinstance(referer, basestring)

        # Parse, verify and canonicalize the URL
        parsed = DecomposedURL(url)
        if not parsed.host or not parsed.scheme:
            raise ValueError("Only absolute URLs must be used!")
        url = parsed.url

        # URL
        self.__url = url

        # Parsed URL
        self.__parsed_url = parsed

        # Method
        self.__method = method.strip().upper() if method else "GET"

        # GET params
        self.__url_params = url_params if url_params else {}

        # POST params
        self.__post_params = post_params if post_params else {}

        # Encrypted?
        self.__is_https = url.lower().startswith("https://")

        # Content type
        self.__content_type = content_type

        # Request type
        self.__request_type = request_type

        # Depth
        assert type(depth) == int
        self.__depth = depth

        # Referer
        assert isinstance(referer, basestring)
        self.__referer = referer

        # Discovered resources
        self.__discovered_resources = None

        # Parent constructor
        super(Url, self).__init__()


    #----------------------------------------------------------------------
    def __str__(self):
        return "(%s) %s" % (
            self.method,
            self.url,
        )


    #----------------------------------------------------------------------
    def __repr__(self):
        s = "<Url url=%r, method=%r, params=%r, referer=%r>"
        s %= (self.url, self.method, self.post_params, self.referer)
        return s


    #----------------------------------------------------------------------
    def is_in_scope(self):
        return is_in_scope(self.url)


    #----------------------------------------------------------------------

    @identity
    def url(self):
        """
        str -- Raw URL.
        """
        return self.__url

    @identity
    def method(self):
        """
        str -- HTTP method.
        """
        return self.__method

    @identity
    def post_params(self):
        """
        dict(str) -- POST parameters.
        """
        return self.__post_params


    #----------------------------------------------------------------------

    @property
    def parsed_url(self):
        """
        DecomposedURL -- Parsed URL.
        """
        return self.__parsed_url

    @property
    def url_params(self):
        """
        dict(str) -- URL parameters.
        """
        return self.__url_params

    @property
    def is_https(self):
        """
        bool -- True if it's HTTPS, False otherwise.
        """
        return self.__is_https

    @property
    def has_url_param(self):
        """
        bool - True if there are URL params, False otherwise.
        """
        return bool(self.url_params)

    @property
    def has_post_param(self):
        """
        bool - True if there are POST params, False otherwise.
        """
        return bool(self.post_params)

    @property
    def content_type(self):
        """
        str - MIME content type.
        """
        return self.__content_type

    @property
    def request_type(self):
        """
        int - One of the HTML.TYPE_* constants.
        """
        return self.__request_type

    @property
    def depth(self):
        """
        int - The recursion depth reached to find this URL.
        """
        return self.__depth

    @property
    def referer(self):
        """
        str -- Referer for this URL.
        """
        return self.__referer


    #----------------------------------------------------------------------

    @property
    def discovered_resources(self):
        return [Domain(self.parsed_url.hostname), BaseUrl(self.url)]
