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

__all__ = ["HTML"]

from . import Information
from .. import identity
from ...net.web_utils import HTMLParser


#------------------------------------------------------------------------------
class HTML(Information):
    """
    HTML document.

    This type contains all of relevant tags of a HTML document:

    - CSS links
    - CSS embeded
    - Javascript links
    - Metas
    - Links
    - Forms
    - Images
    - Title
    - Object

    Also contains a generic property for access to other tags:

    - Elements

    You can also access to raw HTML code.

    - raw_data

    .. note::
       The HTML parser used is dinamically selected internally, depends of your installed libraries.

    Use if is very simple:

    >>> from golismero.api.data.information.html import HTML
    >>> html_info=\"\"\"<html>
    <head>
      <title>My sample page</title>
    </head>
    <body>
      <a href="http://www.mywebsitelink.com">Link 1</a>
      <p>
        <img src="/images/my_image.png" />
      </p>
    </body>
    </html>\"\"\"
    >>> html_parsed=HTML(html_info)
    >>> html_parsed.links
    [<golismero.api.net.web_utils.HTMLElement object at 0x109ca8b50>]
    >>> html_parsed.links[0].tag_name
    'a'
    >>> html_parsed.links[0].tag_content
    'Link 1'
    >>> html_parsed.links[0].attrs
    {'href': 'http://www.mywebsitelink.com'}
    >>> html_parsed.images[0].tag_name
    'img'
    >>> html_parsed.images[0].tag_content
    ''
    """

    information_type = Information.INFORMATION_HTML


    #----------------------------------------------------------------------
    def __init__(self, data):
        """Constructor.

        :param data: Raw HTML content
        :type data: str
        """

        # Raw HTML content
        self.__raw_data = data

        # Parent constructor
        super(HTML, self).__init__()


    #----------------------------------------------------------------------
    @identity
    def raw_data(self):
        """
        :return: Get raw HTML code
        :rtype: str
        """
        return self.__raw_data


    #----------------------------------------------------------------------
    @property
    def elements(self):
        """
        :return: All HTML elements as a list of HTMLElement objects
        :rtype: list(HTMLElement)
        """
        return HTMLParser(self.raw_data).elements


    #----------------------------------------------------------------------
    @property
    def forms(self):
        """
        :return: HTML form tags as a list of HTMLElement objects
        :rtype: list(HTMLElement)
        """
        return HTMLParser(self.raw_data).forms


    #----------------------------------------------------------------------
    @property
    def images(self):
        """
        :return: Image tags as a list of HTMLElement objects
        :rtype: list(HTMLElement)
        """
        return HTMLParser(self.raw_data).images


    #----------------------------------------------------------------------
    @property
    def links(self):
        """
        :return: Links tags as a list of HTMLElement objects
        :rtype: list(HTMLElement)
        """
        return HTMLParser(self.raw_data).links


    #----------------------------------------------------------------------
    @property
    def css_links(self):
        """
        :return: CSS links as a list of HTMLElement objects
        :rtype: list(HTMLElement)
        """
        return HTMLParser(self.raw_data).css_links


    #----------------------------------------------------------------------
    @property
    def javascript_links(self):
        """
        :return: JavaScript links as a list of HTMLElement objects
        :rtype: list(HTMLElement)
        """
        return HTMLParser(self.raw_data).javascript_links


    #----------------------------------------------------------------------
    @property
    def css_embedded(self):
        """
        :return: Embedded CSS as a list of HTMLElement objects
        :rtype: list(HTMLElement)
        """
        return HTMLParser(self.raw_data).css_embedded


    #----------------------------------------------------------------------
    @property
    def javascript_embedded(self):
        """
        :return: Embedded JavaScript as a list of HTMLElement objects
        :rtype: list(HTMLElement)
        """
        return HTMLParser(self.raw_data).javascript_embedded


    #----------------------------------------------------------------------
    @property
    def metas(self):
        """
        :return: Meta tags as a list of HTMLElement objects
        :rtype: list(HTMLElement)
        """
        return HTMLParser(self.raw_data).metas


    #----------------------------------------------------------------------
    @property
    def title(self):
        """
        :return: Document title as a HTMLElement object
        :rtype: HTMLElement
        """
        return HTMLParser(self.raw_data).title


    #----------------------------------------------------------------------
    @property
    def objects(self):
        """
        :return: Object tags as a list of HTMLElement objects
        :rtype: list(HTMLElement)
        """
        return HTMLParser(self.raw_data).objects
