#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com
  Mario Vilas | mvilas@gmail.com

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

__all__ = ["HTML", "HTMLElement"]

from ..data import identity
from .information import Information

from bs3.BeautifulSoup import BeautifulSoup


#------------------------------------------------------------------------------
class HTMLElement (object):
    """"""


    #----------------------------------------------------------------------
    def __init__(self, tag_name, attrs, content):
        """
        Constructor.

        :param attr: dict with parameters of HTML element.
        :type attr: dict

        :param childrens: raw HTML with sub elements of this HTML element
        :type childrens: str
        """
        self.__tag_name = tag_name
        self.__attrs = attrs
        self.__content = HTML(content)


    #----------------------------------------------------------------------
    def __str__(self):
        """"""
        return "%s:%s" % (self.__tag_name, str(self.__attrs))


    #----------------------------------------------------------------------

    @property
    def tag_name(self):
        return self.__tag_name

    @property
    def attrs(self):
        return self.__attrs

    @property
    def content(self):
        """Returns an HTML object nested into this HTML element.

        :returns: and HTML object
        """
        return self.__content


#------------------------------------------------------------------------------
class HTML(Information):
    """"""

    information_type = Information.INFORMATION_HTML


    #----------------------------------------------------------------------
    def __init__(self, data):
        """Constructor

        :param data: raw HTML data.
        :type data: str
        """

        # Initialize the BeautifulSoup parser
        self.__html_parser = HTMLBeautifulSoup(data)


    #----------------------------------------------------------------------

    @identity
    def raw_data(self):
        """Get raw HTML code"""
        return self.__html_parser.raw_data

    #----------------------------------------------------------------------

    @property
    def elements(self):
        """Get all HTML elements"""
        return self.__html_parser.elements

    @property
    def forms(self):
        """Get forms from HTML"""
        return self.__html_parser.forms

    @property
    def images(self):
        """Get images from HTML"""
        return self.__html_parser.images

    @property
    def links(self):
        """Get links of HTML"""
        return self.__html_parser.links

    @property
    def css_links(self):
        """Get CSS links from HTML"""
        return self.__html_parser.css_links

    @property
    def javascript_links(self):
        """Get JavaScript links from HTML"""
        return self.__html_parser.javascript_links

    @property
    def css_embedded(self):
        """Get embedded CSS from HTML"""
        return self.__html_parser.css_embedded

    @property
    def javascript_embedded(self):
        """Get embedded JavaScript from HTML"""
        return self.__html_parser.javascript_embedded

    @property
    def objects(self):
        """Get object tags from HTML"""
        return self.__html_parser.objects

    @property
    def metas(self):
        """Get meta tags from HTML"""
        return self.__html_parser.metas

    @property
    def title(self):
        """Get title from HTML"""
        return self.__html_parser.title


#------------------------------------------------------------------------------
class HTMLBeautifulSoup(object):
    """
    Wrapper for the BeautifulSoup HTML parser.
    """


    #----------------------------------------------------------------------
    def __init__(self, data):
        """Constructor.

        :param data: raw HTML content
        :type data: str
        """

        # Raw HTML content
        self.__raw_data = data

        # Init parser
        self.__html_parser = BeautifulSoup(data)

        #
        # Parsed HTML elementes
        #

        # All elements
        self.__all_elements = None

        # HTML forms
        self.__html_forms = None

        # Images in HTML
        self.__html_images = None

        # Links in HTML
        self.__html_links = None

        # CSS links
        self.__html_css = None

        # CSS embedded
        self.__html_css_embedded = None

        # Javascript
        self.__html_javascript = None

        # Javascript embedded
        self.__html_javascript_embedded = None

        # Objects
        self.__html_objects = None

        # Metas
        self.__html_metas = None

        # Title
        self.__html_title = None


    #----------------------------------------------------------------------
    def __convert_to_HTMLElements(self, data):
        """
        Convert parser format to list of HTML Elements.

        :return: list of HTMLElements
        """
        return [
            HTMLElement(
                x.name.encode("utf-8"),
                { v[0].encode("utf-8"): v[1].encode("utf-8") for v in x.attrs},
                "".join(( str(item) for item in x.contents if item != "\n"))
                ) for x in data
        ]


    #----------------------------------------------------------------------
    @property
    def raw_data(self):
        """Get raw HTML code"""
        return self.__raw_data


    #----------------------------------------------------------------------
    @property
    def elements(self):
        """Get all HTML elements"""
        if self.__all_elements is None:
            m_result = self.__html_parser.findAll()
            self.__all_elements = self.__convert_to_HTMLElements(m_result)
        return self.__all_elements


    #----------------------------------------------------------------------
    @property
    def forms(self):
        """Get forms from HTML"""
        if self.__html_forms is None:
            m_elem = self.__html_parser.findAll("form")
            self.__html_forms = self.__convert_to_HTMLElements(m_elem)
        return self.__html_forms


    #----------------------------------------------------------------------
    @property
    def images(self):
        """Get images from HTML"""
        if self.__html_images is None:
            m_elem = self.__html_parser.findAll("img")
            self.__html_images = self.__convert_to_HTMLElements(m_elem)
        return self.__html_images


    #----------------------------------------------------------------------
    @property
    def links(self):
        """Get links from HTML"""
        if self.__html_links is None:
            m_elem = self.__html_parser.findAll("a")
            self.__html_links = self.__convert_to_HTMLElements(m_elem)
        return self.__html_links


    #----------------------------------------------------------------------
    @property
    def css_links(self):
        """Get CSS links from HTML"""
        if self.__html_css is None:
            m_elem = self.__html_parser.findAll(name="link", attrs={"rel":"stylesheet"})
            self.__html_css = self.__convert_to_HTMLElements(m_elem)
        return self.__html_css


    #----------------------------------------------------------------------
    @property
    def javascript_links(self):
        """Get JavaScript links from HTML"""
        if self.__html_javascript is None:
            m_elem = self.__html_parser.findAll(name="script", attrs={"src": True})
            self.__html_javascript = self.__convert_to_HTMLElements(m_elem)
        return self.__html_javascript


    #----------------------------------------------------------------------
    @property
    def css_embedded(self):
        """Get embedded CSS from HTML"""
        if self.__html_css_embedded is None:
            m_elem = self.__html_parser.findAll("style")
            self.__html_css_embedded = self.__convert_to_HTMLElements(m_elem)
        return self.__html_css_embedded


    #----------------------------------------------------------------------
    @property
    def javascript_embedded(self):
        """Get embedded JavaScript from HTML"""
        if self.__html_javascript_embedded is None:
            m_elem = self.__html_parser.findAll(name="script", attrs={"src": False})
            self.__html_javascript_embedded = self.__convert_to_HTMLElements(m_elem)
        return self.__html_javascript_embedded


    #----------------------------------------------------------------------
    @property
    def metas(self):
        """Get meta tags from HTML"""
        if self.__html_metas is None:
            m_elem = self.__html_parser.findAll(name="meta")
            self.__html_metas = self.__convert_to_HTMLElements(m_elem)
        return self.__html_metas


    #----------------------------------------------------------------------
    @property
    def title(self):
        """Get title from HTML"""
        if self.__html_title is None:
            m_elem = self.__html_parser.findAll(name="title", recursive=False, limit=1)
            self.__html_title = m_elem.name.encode("utf-8")
        return self.__html_title


    #----------------------------------------------------------------------
    @property
    def objects(self):
        """Get object tags from HTML"""

        if self.__html_objects is None:
            m_elem = self.__html_parser.findAll(name="object")

            m_result = []
            m_result_append_bind = m_result.append

            for obj in m_elem:

                # Get attrs
                m_ojb_attr = { v[0].encode("utf-8"): v[1].encode("utf-8") for v in obj.attrs }

                # Add param attr
                m_ojb_attr["param"] = {}

                # Add value for params
                apply(m_ojb_attr["param"].update,
                    (
                        { k[0].encode("utf-8"): k[1].encode("utf-8") for k in param.attrs}
                        for param in obj.findAllNext("param")
                    )
                )

                m_raw_content = "".join((str(item) for item in obj.contents if item != "\n"))

                m_result_append_bind(HTMLElement(obj.name.encode("utf-8"), m_ojb_attr, m_raw_content))

            self.__html_objects = m_result

        return self.__html_objects
