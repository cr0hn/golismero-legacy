#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Folder URL type.
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

__all__ = ["FolderUrl"]

from . import Resource
from .domain import Domain
from .. import identity
from ...config import Config
from ...net.web_utils import DecomposedURL


#------------------------------------------------------------------------------
class FolderUrl(Resource):
    """
    Folder URL.

    Unlike the Url type, which refers to an URL that's linked or somehow found
    to be valid, the FolderUrl type refers to inferred URLs to folders detected
    within another URL.

    This makes it semantically different, since there's no guarantee that the
    URL actually points to a valid resource, nor that it belongs to the normal
    web access flow.

    For example, a plugin receiving both FolderUrl and Url may get this input:

    - Url("http://www.my_site.com/wp-content/uploads/2013/06/attachment.pdf")
    - FolderUrl("http://www.my_site.com/wp-content/uploads/2013/06/")
    - FolderUrl("http://www.my_site.com/wp-content/uploads/2013/")
    - FolderUrl("http://www.my_site.com/wp-content/uploads/")
    - FolderUrl("http://www.my_site.com/wp-content/")

    Note that the folder URLs may or may not be sent again as an Url object.
    For example, for a site that has a link to the "incoming" directory in its
    index page, we may get something like this:

    - Url("http://www.my_site.com/index.html")
    - Url("http://www.my_site.com/incoming/")
    - FolderUrl("http://www.my_site.com/incoming/")

    FolderUrl objects are never sent for the root folder of a web site.
    For that, see the BaseUrl data type.
    """

    resource_type = Resource.RESOURCE_FOLDER_URL


    #----------------------------------------------------------------------
    def __init__(self, url):
        """
        :param url: Absolute URL to a folder.
        :type url: str

        :raises ValueError: The URL wasn't absolute or didn't point to a folder.
        """

        # Parse, verify and canonicalize the URL.
        parsed = DecomposedURL(url)
        if not parsed.host or not parsed.scheme:
            raise ValueError("Only absolute URLs must be used!")
        if not parsed.path.endswith("/"):
            raise ValueError("URL does not point to a folder!")

        # Store the URL.
        self.__url = url
        self.__parsed_url = parsed

        # Call the parent constructor.
        super(FolderUrl, self).__init__()


    #----------------------------------------------------------------------
    @staticmethod
    def from_url(url):
        """
        :param url: Any **absolute** URL. The folder will be extracted from it.
        :type url: str

        :returns: Inferred folder URLs.
        :rtype: list(FolderUrl)

        :raises ValueError: Only absolute URLs must be used.
        """
        assert isinstance(url, basestring)

        # Parse, verify and canonicalize the URL.
        parsed = DecomposedURL(url)
        if not parsed.host or not parsed.scheme:
            raise ValueError("Only absolute URLs must be used!")

        # Extract the folders from the path.
        path = parsed.path
        folders = path.split("/")
        if not path.endswith("/"):
            folders.pop()

        # Convert the URL to a base URL.
        parsed.auth = None
        parsed.path = "/"
        parsed.fragment = None
        parsed.query = None
        parsed.query_char = None

        # Generate a new folder URL for each folder.
        folder_urls = {parsed.url}
        for folder in folders:
            if folder:
                parsed.path += folder + "/"
                folder_urls.add(parsed.url)

        # Return the generated URLs.
        return [FolderUrl(x) for x in folder_urls]


    #----------------------------------------------------------------------
    def __str__(self):
        return self.url


    #----------------------------------------------------------------------
    def __repr__(self):
        return "<FolderUrl url=%r>" % self.url


    #----------------------------------------------------------------------
    def is_in_scope(self):
        return self.url in Config.audit_scope


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
    def path(self):
        """
        :return: Path component of the URL.
        :rtype: str
        """
        return self.__parsed_url.path


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
        if self.is_in_scope():
            return [Domain(self.hostname)]
        return []
