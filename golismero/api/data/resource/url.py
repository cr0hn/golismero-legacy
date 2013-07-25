#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Universal Resource Locator (URL).
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

__all__ = ["Url"]

from . import Resource
from .baseurl import BaseUrl
from .domain import Domain
from .folderurl import FolderUrl
from .ip import IP
from .. import identity
from ...config import Config
from ...net.web_utils import DecomposedURL


#------------------------------------------------------------------------------
class Url(Resource):
    """
    Universal Resource Locator (URL).

    You can get the URL in canonical form:

    - url

    In deconstructed form:

    - parsed_url

    The current crawling depth level:

    - depth

    And some extra information needed to build an HTTP request:

    - method
    - url_params
    - post_params
    - referer
    """

    resource_type = Resource.RESOURCE_URL


    #----------------------------------------------------------------------
    def __init__(self, url, method = "GET", post_params = None, depth = 0, referer = None):
        """
        :param url: Absolute URL.
        :type url: str

        :param method: HTTP method.
        :type method: str

        :param post_params: POST parameters.
        :type post_params: dict(str -> str)

        :param depth: Crawling depth.
        :type depth: int

        :param referer: Referrer URL.
        :type referer: str

        :raises ValueError: Currently, relative URLs are not allowed.
        """

        if not isinstance(url, basestring):
            raise TypeError("Expected string, got %s instead" % type(url))
        url = str(url)

        if not isinstance(method, str):
            raise TypeError("Expected string, got %s instead" % type(method))

        if post_params is not None and not isinstance(post_params, dict):
            raise TypeError("Expected dict, got %s instead" % type(post_params))

        if not depth:
            depth = 0
        elif not isinstance(depth, int):
            raise TypeError("Expected int, got %s instead" % type(depth))

        if referer is not None and not isinstance(referer, str):
            raise TypeError("Expected string, got %s instead" % type(referer))

        # Parse, verify and canonicalize the URL.
        # TODO: if relative, make it absolute using the referer when available.
        parsed = DecomposedURL(url)
        if not parsed.host or not parsed.scheme:
            raise ValueError("Only absolute URLs must be used!")
        url = parsed.url

        # URL.
        self.__url = url

        # Parsed URL.
        self.__parsed_url = parsed

        # Method.
        self.__method = method.strip().upper() if method else "GET"

        # POST params.
        self.__post_params = post_params if post_params else {}

        # Encrypted?
        self.__is_https = url.lower().startswith("https://")

        # Depth.
        assert type(depth) == int
        self.__depth = depth

        # Referer.
        if referer is not None:
            assert isinstance(referer, basestring)
        self.__referer = referer

        # Discovered resources.
        self.__discovered = None

        # Parent constructor.
        super(Url, self).__init__()


    #----------------------------------------------------------------------
    def __str__(self):
        return self.url


    #----------------------------------------------------------------------
    def __repr__(self):
        s = "<Url url=%r, method=%r, params=%r, referer=%r, depth=%r>"
        s %= (self.url, self.method, self.post_params, self.referer, self.depth)
        return s


    #----------------------------------------------------------------------
    def is_in_scope(self):
        return self.url in Config.audit_scope


    #----------------------------------------------------------------------

    @identity
    def url(self):
        """
        :return: URL in canonical form.
        :rtype: str
        """
        return self.__url

    @identity
    def method(self):
        """
        :return: HTTP method.
        :rtype: str
        """
        return self.__method

    @identity
    def post_params(self):
        """
        :return: POST parameters.
        :rtype: dict(str)
        """
        return self.__post_params


    #----------------------------------------------------------------------

    @property
    def parsed_url(self):
        """
        :return: URL in decomposed form.
        :rtype: DecomposedURL
        """
        return self.__parsed_url

    @property
    def hostname(self):
        """
        :return: Hostname this URL points to.
        :rtype: str
        """
        return self.__parsed_url.hostname

    @property
    def url_params(self):
        """
        :return: GET parameters.
        :rtype: dict(str -> str)
        """
        query = self.__parsed_url.query
        if type(query) not in (str, unicode):
            return query
        return {}

    @property
    def is_https(self):
        """
        :return: True if it's HTTPS, False otherwise.
        :rtype: bool
        """
        return self.__is_https

    @property
    def has_url_param(self):
        """
        :return: True if there are GET parameters, False otherwise.
        :rtype: bool
        """
        return bool(self.url_params)

    @property
    def has_post_param(self):
        """
        :return: True if there are POST parameters, False otherwise.
        :rtype: bool
        """
        return bool(self.post_params)

    @property
    def depth(self):
        """
        :return: The recursion depth reached to find this URL.
        :rtype: int
        """
        return self.__depth

    @property
    def referer(self):
        """
        :return: Referer for this URL.
        :rtype: str
        """
        return self.__referer


    #----------------------------------------------------------------------
    @property
    def discovered(self):
        if self.is_in_scope():
            result = FolderUrl.from_url(self.url)
            result.append( BaseUrl(self.url) )
            try:
                result.append( IP(self.hostname) )
            except ValueError:
                result.append( Domain(self.hostname) )
            return result
        return []
