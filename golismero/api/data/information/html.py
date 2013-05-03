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

from .information import Information
from ..data import identity
from ...net.web_utils import HTMLParser


#------------------------------------------------------------------------------
class HTML(Information):
    """
    HTML document.
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
        """Get raw HTML code"""
        return self.__raw_data


    #----------------------------------------------------------------------
    @property
    def elements(self):
        """Get all HTML elements"""
        return HTMLParser(self.raw_data).elements


    #----------------------------------------------------------------------
    @property
    def forms(self):
        """Get forms from HTML"""
        return HTMLParser(self.raw_data).forms


    #----------------------------------------------------------------------
    @property
    def images(self):
        """Get images from HTML"""
        return HTMLParser(self.raw_data).images


    #----------------------------------------------------------------------
    @property
    def links(self):
        """Get links from HTML"""
        return HTMLParser(self.raw_data).links


    #----------------------------------------------------------------------
    @property
    def css_links(self):
        """Get CSS links from HTML"""
        return HTMLParser(self.raw_data).css_links


    #----------------------------------------------------------------------
    @property
    def javascript_links(self):
        """Get JavaScript links from HTML"""
        return HTMLParser(self.raw_data).javascript_links


    #----------------------------------------------------------------------
    @property
    def css_embedded(self):
        """Get embedded CSS from HTML"""
        return HTMLParser(self.raw_data).css_embedded


    #----------------------------------------------------------------------
    @property
    def javascript_embedded(self):
        """Get embedded JavaScript from HTML"""
        return HTMLParser(self.raw_data).javascript_embedded


    #----------------------------------------------------------------------
    @property
    def metas(self):
        """Get meta tags from HTML"""
        return HTMLParser(self.raw_data).metas


    #----------------------------------------------------------------------
    @property
    def title(self):
        """Get title from HTML"""
        return HTMLParser(self.raw_data).title


    #----------------------------------------------------------------------
    @property
    def objects(self):
        """Get object tags from HTML"""
        return HTMLParser(self.raw_data).objects
