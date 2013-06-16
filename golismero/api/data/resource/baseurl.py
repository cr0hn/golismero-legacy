#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base URL type.
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

__all__ = ["BaseUrl"]

from . import Resource
from .domain import Domain
from .. import identity
from ...net.web_utils import DecomposedURL, is_in_scope


#------------------------------------------------------------------------------
class BaseUrl(Resource):
    """
    Base URL.

    Unlike the Url type, which refers to any URL, this type is strictly for
    root level URLs in a web server. Plugins that only run once per web server
    should probably receive this data type.

    For example, a plugin receiving both BaseUrl and Url may get this input:

    - BaseUrl("http://www.my_site.com/")
    - Url("http://www.my_site.com/")
    - Url("http://www.my_site.com/index.php")
    - Url("http://www.my_site.com/admin.php")
    - Url("http://www.my_site.com/login.php")

    Notice how the root level URL is sent twice,
    once as BaseUrl and again the more generic Url.
    """

    resource_type = Resource.RESOURCE_BASE_URL


    #----------------------------------------------------------------------
    def __init__(self, url):
        """
        :param url: Any **absolute** URL. The base will be extracted from it.
        :type url: str

        :raises ValueError: Only absolute URLs must be used.
        """
        assert isinstance(url, basestring)

        # Parse, verify and canonicalize the URL.
        parsed = DecomposedURL(url)
        if not parsed.host or not parsed.scheme:
            raise ValueError("Only absolute URLs must be used!")

        # Convert it into a base URL.
        parsed.auth = None
        parsed.path = "/"
        parsed.fragment = None
        parsed.query = None
        parsed.query_char = None
        url = parsed.url

        # Raw base URL.
        self.__url = url

        # Parsed base URL.
        self.__parsed_url = parsed

        # Parent constructor.
        super(BaseUrl, self).__init__()


    #----------------------------------------------------------------------
    def __str__(self):
        return self.url


    #----------------------------------------------------------------------
    def __repr__(self):
        return "<BaseUrl url=%r>" % self.url


    #----------------------------------------------------------------------
    def is_in_scope(self):
        return is_in_scope(self.url)


    #----------------------------------------------------------------------
    @identity
    def url(self):
        """
        :return: Raw URL.
        :rtype: str
        """
        return self.__url


    #----------------------------------------------------------------------
    @property
    def parsed_url(self):
        """
        :return: Parsed URL.
        :rtype: DecomposedURL
        """
        return self.__parsed_url


    #----------------------------------------------------------------------
    @property
    def hostname(self):
        """
        :return: Hostname this URL points to.
        :rtype: str
        """
        return self.__parsed_url.hostname


    #----------------------------------------------------------------------
    @property
    def is_https(self):
        """
        :return: True if it's HTTPS, False otherwise.
        :rtype: bool
        """
        return self.__parsed_url.scheme == "https"


    #----------------------------------------------------------------------
    @property
    def discovered(self):
        return [Domain(self.hostname)]
