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
    def __get_tag_name(self):
        return self.__tag_name
    tag_name = property(__get_tag_name)


    #----------------------------------------------------------------------
    def __get_attrs(self):
        return self.__attrs
    attrs = property(__get_attrs)


    #----------------------------------------------------------------------
    def __get_content(self):
        """Returns an HTML object nested into this HTML element.

        :returns: and HTML object
        """
        return self.__content
    content = property(__get_content)


    #----------------------------------------------------------------------
    def __str__(self):
        """"""
        return "%s:%s" % (self.__tag_name, str(self.__attrs))


#------------------------------------------------------------------------------
class HTML(Information):
    """"""

    __PARSER_BEAUTIFULSOUP = 0


    #----------------------------------------------------------------------
    def __init__(self, data):
        """Constructor

        :param data: raw HTML data.
        :type data: str
        """
        super(Information, self).__init__()

        self.information_type = self.INFORMATION_HTML

        # Init and store type of HTML parser
        self.__html_parser_type, self.__html_parser = self.__init_parser(data)


    def find_all(self, name=None, attrs={}, recursive=True, text=None, limit=None):
        """
        """
        return self.__html_parser.find_all(name=name, attrs=attrs, recursive=recursive, text=text, limit=limit)


    def __get_raw(self):
        """Get raw HTML code"""
        return self.__html_parser.raw_data
    raw_data = property(__get_raw)


    #----------------------------------------------------------------------
    def __get_forms(self):
        """Get forms from HTML"""
        return self.__html_parser.forms
    forms = property(__get_forms)


    #----------------------------------------------------------------------
    def __get_images(self):
        """Get images from HTML"""
        return self.__html_parser.images
    images = property(__get_images)


    #----------------------------------------------------------------------
    def __get_links(self):
        """Get links of HTML"""
        return self.__html_parser.links
    links = property(__get_links)


    #----------------------------------------------------------------------
    def __get_css(self):
        """Get CSS links from HTML"""
        return self.__html_parser.css_links
    css_links = property(__get_css)


    #----------------------------------------------------------------------
    def __get_javascript(self):
        """Get JavaScript links from HTML"""
        return self.__html_parser.javascripts_links
    javascript_links = property(__get_javascript)


    #----------------------------------------------------------------------
    def __get_css_embedded(self):
        """Get embedded CSS from HTML"""
        return self.__html_parser.css_embedded
    css_embedded = property(__get_css_embedded)


    #----------------------------------------------------------------------
    def __get_javascript_embedded(self):
        """Get embedded JavaScript from HTML"""
        return self.__html_parser.javascript_embedded
    javascript_embedded = property(__get_javascript_embedded)


    #----------------------------------------------------------------------
    def __get_object_embedded(self):
        """Get object tags from HTML"""
        return self.__html_parser.objects
    objects = property(__get_object_embedded)


    #----------------------------------------------------------------------
    def __get_metas(self):
        """Get meta tags from HTML"""
        return self.__html_parser.metas
    metas = property(__get_metas)


    #----------------------------------------------------------------------
    def __get_title(self):
        """Get title from HTML"""
        return self.__html_parser.title
    title = property(__get_title)


    #----------------------------------------------------------------------
    def __init_parser(self, data):
        """Initializes the HTML parser.

        :return: Type and instance of parser, as tuple: (type, instance)
        """

        m_return_parser = HTMLBeautifulSoup(data)
        m_return_type = HTML.__PARSER_BEAUTIFULSOUP

        return m_return_type, m_return_parser


#------------------------------------------------------------------------------
class HTMLBeautifulSoup(object):
    """
    Wrapper for the BeautifulSoup HTML parser.
    """


    #----------------------------------------------------------------------
    def __init__(self, data):
        """Constructor.

        :param data: raw HTML info
        :type data: str
        """

        # Raw HTML content
        self.__raw_data = data

        # Init parser
        self.__html_parser = self.__init_parser(data)

        #
        # Parsed HTML elementes
        #

        # HTML forms
        self.__html_forms = []
        # Images in HTML
        self.__html_images = []
        # Links in HTML
        self.__html_links = []
        # CSS links
        self.__html_css = []
        # CSS embedded
        self.__html_css_embedded = []
        # Javascript
        self.__html_javascript = []
        # Javascript embedded
        self.__html_javascript_embedded = []
        # Objects
        self.__html_objects = []
        # Metas
        self.__html_metas = []
        # Title
        self.__html_title = ""


    #----------------------------------------------------------------------
    #
    # GETTERS
    #
    #----------------------------------------------------------------------
    def __get_raw(self):
        """Get raw HTML code"""
        return self.__raw_data
    raw_data = property(__get_raw)
    """Raw HTML content"""

    #----------------------------------------------------------------------
    def __get_forms(self):
        """Get forms rom HTML"""
        if not self.__html_forms:
            m_elem = self.__html_parser.findAll("form")
            # Get, and parte to UTF, info
            self.__html_forms.extend(self.__converto_to_HTMLElements(m_elem))
        return self.__html_forms

    forms = property(__get_forms)


    #----------------------------------------------------------------------
    def __get_images(self):
        """Get images from HTML"""
        if not self.__html_images:
            m_elem = self.__html_parser.findAll("img")
            # Get the list of dicts
            self.__html_images.extend(self.__converto_to_HTMLElements(m_elem))

        return self.__html_images

    images = property(__get_images)


    #----------------------------------------------------------------------
    def __get_links(self):
        """Get links from HTML"""
        if not self.__html_links:
            m_elem = self.__html_parser.findAll("a")
            # Get the list of dicts
            self.__html_links.extend(self.__converto_to_HTMLElements(m_elem))

        return self.__html_links

    links = property(__get_links)


    #----------------------------------------------------------------------
    def __get_css(self):
        """Get CSS links from HTML"""
        if not self.__html_css:
            m_elem = self.__html_parser.findAll(name="link", attrs={"rel":"stylesheet"})
            # Get the list of dicts
            self.__html_css.extend(self.__converto_to_HTMLElements(m_elem))

        return self.__html_css

    css_links = property(__get_css)


    #----------------------------------------------------------------------
    def __get_javascript(self):
        """Get JavaScript links from HTML"""
        if not self.__html_javascript:
            m_elem = self.__html_parser.findAll(name="script", attrs={"src": True})
            # Get the list of dicts
            self.__html_javascript.extend(self.__converto_to_HTMLElements(m_elem))

        return self.__html_javascript

    javascripts_links = property(__get_javascript)


    #----------------------------------------------------------------------
    def __get_css_embedded(self):
        """Get embedded CSS from HTML"""
        if not self.__html_css_embedded:
            m_elem = self.__html_parser.findAll("style")
            # Get the list of dicts
            self.__html_css_embedded.extend(self.__converto_to_HTMLElements(m_elem))

        return self.__html_css_embedded

    css_embedded = property(__get_css_embedded)


    #----------------------------------------------------------------------
    def __get_javascript_embedded(self):
        """Get embedded JavaScript from HTML"""
        if not self.__html_javascript_embedded:
            m_elem = self.__html_parser.findAll(name="script", attrs={"src": False})
            # Get the list of dicts
            self.__html_javascript_embedded.extend(self.__converto_to_HTMLElements(m_elem))

        return self.__html_javascript_embedded

    javascript_embedded = property(__get_javascript_embedded)


    #----------------------------------------------------------------------
    def __get_metas(self):
        """Get meta tags from HTML"""
        if not self.__html_metas:
            m_elem = self.__html_parser.findAll(name="meta")
            # Get the list of dicts
            self.__html_metas.extend(self.__converto_to_HTMLElements(m_elem))

        return self.__html_metas

    metas = property(__get_metas)


    #----------------------------------------------------------------------
    def __get_title(self):
        """Get title from HTML"""
        if not self.__html_title:
            m_elem = self.__html_parser.findAll(name="title", recursive=False, limit=1)
            # Get the list of dicts
            self.__html_title = m_elem.name.encode("utf-8") if len(m_elem) > 0 else ""

        return self.__html_title

    title = property(__get_title)


    #----------------------------------------------------------------------
    def __get_object_embedded(self):
        """Get object tags from HTML"""
        if not self.__html_objects:
            m_elem = self.__html_parser.findAll(name="object")

            m_result = list()
            m_result_append_bind = m_result.append

            for obj in m_elem:
                # Get attrs
                m_ojb_attr = { v[0].encode("utf-8"): v[1].encode("utf-8") for v in obj.attrs }

                # Add param attr
                m_ojb_attr["param"] = dict()

                # Add value for params
                for param in obj.findAllNext("param"):
                    m_ojb_attr["param"].update({ k[0].encode("utf-8"): k[1].encode("utf-8") for k in param.attrs})

                m_raw_content = "".join((str(item) for item in obj.contents if item != "\n"))

                m_result_append_bind(HTMLElement(obj.name.encode("utf-8"), m_ojb_attr, m_raw_content))

            self.__html_objects = m_result

        return self.__html_objects

    objects = property(__get_object_embedded)


    #----------------------------------------------------------------------
    #
    # PUBLIC FUNCTIONS
    #
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    def find_all(self, name=None, attrs={}, recursive=True, text=None, limit=None):
        """
        Looking for in HTML code by patter.
        """
        m_result = self.__html_parser.findAll(
            name = name,
            attrs = attrs,
            recursive = recursive,
            text = text,
            limit = limit
        )

        # Get the list of HTML Elements
        return self.__converto_to_HTMLElements(m_result)




    #----------------------------------------------------------------------
    #
    # PRIVATE FUNCTIONS
    #
    #----------------------------------------------------------------------
    def __converto_to_HTMLElements(self, data):
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
    def __init_parser(self, data):
        """Initializes the HTML parser.

        :return: Type and instance of parser
        """
        return BeautifulSoup(data)
