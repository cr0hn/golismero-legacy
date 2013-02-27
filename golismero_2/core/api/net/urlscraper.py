#!/usr/bin/env python
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

__all__ = ['URLScraper']

from thirdparty_libs.urllib3.util import parse_url
from thirdparty_libs.bs3.BeautifulSoup import BeautifulSoup


#------------------------------------------------------------------------------
class URLScraper (object):
    """
    URL scraping API.
    """


    TYPE_LINK        = 0  # Anchors and other links
    TYPE_FORM_ACTION = 1  # Form actions
    TYPE_IMAGE       = 2  # Images
    TYPE_CSS         = 3  # CSS stylesheets
    TYPE_SCRIPT      = 4  # JavaScript and other scripts
    TYPE_OBJECT      = 5  # Java applets, Flash, etc.

    # TODO: look at the HTML5 specs for new link types it may have

    TYPE_FIRST = TYPE_LINK
    TYPE_LAST  = TYPE_OBJECT


    #----------------------------------------------------------------------
    @classmethod
    def parse_html(cls, data):
        """
        Parse raw HTML data looking for URLs.

        URLs are returned as-is, no processing is made of them whatsoever.

        :param data: Raw HTML data.
        :type data: str

        :returns: set(tuple(str, int)) -- Set of tuples with the URL and the URL type constant.
        """

        # Set of results found.
        found = set()

        # Parse the HTML data using BeautifulSoup.
        bs = BeautifulSoup(data)

        # Iterate through all the tags in the HTML document.
        for tag in bs.findAll(True):

            # Get the name of the tag.
            try:
                name = str(tag.name).lower()
            except Exception:
                name = tag.name.lower()

            # Anchor tags.
            if name == "a":
                try:
                    url = tag.href
                    url = str(url)
                except AttributeError:
                    continue
                except UnicodeError:
                    pass
                url_type = cls.TYPE_LINK

            # Image tags.
            elif name == "img":
                try:
                    url = tag.src
                    url = str(url)
                except AttributeError:
                    continue
                except UnicodeError:
                    pass
                url_type = cls.TYPE_IMAGE

            # Form tags.
            if name == "form":
                try:
                    url = tag.action
                    url = str(url)
                except AttributeError:
                    continue
                except UnicodeError:
                    pass
                url_type = cls.TYPE_FORM_ACTION

            # Script tags.
            elif name == "script":
                try:
                    url = tag.src
                    url = str(url)
                except AttributeError:
                    continue
                except UnicodeError:
                    pass
                url_type = cls.TYPE_SCRIPT

            # CSS linked stylesheet tags.
            elif name == "link":
                try:
                    url = tag.href
                    url = str(url)
                except AttributeError:
                    continue
                except UnicodeError:
                    pass
                try:
                    if "stylesheet" in tag.rel.lower():
                        url_type = cls.TYPE_CSS
                    else:
                        url_type = cls.TYPE_LINK
                except Exception:
                    url_type = cls.TYPE_LINK


            # Plugin object tags.
            elif name == "object":


            # Embedded object tags.
            elif name == "embed":


            # Java applet tags.
            elif name == "applet":


            # Generic heuristics for unknown tags.
            else:


            found.add( (url, url_type) )



    # TODO: support more formats (for example txt, csv, json, maybe more complex formats too)
