#!/usr/bin/python

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


from core.api.results.information.information import Information

__all__ = ["HTML", "HTMLElement"]

#------------------------------------------------------------------------------
class HTMLElement(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, tag_name, attrs, content):
 	"""
	Constructor

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
	"""Return HTML an object nested into this HTML element.

	:returns: and HTML object
	"""
	return self.__content
    content = property(__get_content)


    #----------------------------------------------------------------------
    def __str__(self):
	""""""
	return str(self.__attrs)




#------------------------------------------------------------------------------
class HTML(Information):
    """"""


    __PARSER_BEAUTYFULL_SOAP = 0


    #----------------------------------------------------------------------
    def __init__(self, data):
        """Constructor

        :param data: raw HTML data.
        :type data: str
        """
        super(Information, self).__init__(Information.INFORMATION_HTML)

	# Init and store type of HTML parser
	self.__html_parser_type, self.__html_parser = self.__init_parser(data)


    def __get_raw(self):
	"""Get raw HTML code"""
	return self.__html_parser.raw_data
    raw_data = property(__get_raw)

    #----------------------------------------------------------------------
    def __get_forms(self):
        """Get forms of HTML"""
	return self.__html_parser.forms
    forms = property(__get_forms)
    """Forms in HTML"""

    #----------------------------------------------------------------------
    def __get_images(self):
        """Get forms of HTML"""
	return self.__html_parser.images

    images = property(__get_images)
    """Images in HTML"""

    #----------------------------------------------------------------------
    def __get_links(self):
        """Get forms of HTML"""
	return self.__html_parser.links

    links = property(__get_links)
    """Links in HTML"""

    #----------------------------------------------------------------------
    def __get_css(self):
        """Get forms of HTML"""
	return self.__html_parser.css_links

    css_links = property(__get_css)
    """CSS links in HTML"""

    #----------------------------------------------------------------------
    def __get_javascript(self):
        """Get forms of HTML"""
	return self.__html_parser.javascripts_links

    javascript_links = property(__get_javascript)
    """Javascript links in HTML"""

    #----------------------------------------------------------------------
    def __get_css_embeded(self):
	""""""
	return self.__html_parser.css_embeded

    css_embeded = property(__get_css_embeded)
    """Get css embeded in HTML"""

    #----------------------------------------------------------------------
    def __get_javascript_embeded(self):
	""""""
	return self.__html_parser.javascript_embeded

    javascript_embeded = property(__get_javascript_embeded)
    """Get javascripts embeded in HTML"""

    #----------------------------------------------------------------------
    def __get_object_embeded(self):
	""""""
	return self.__html_parser.objects

    objects = property(__get_object_embeded)
    """Get objects tags in HTML"""

    #----------------------------------------------------------------------
    def __get_metas(self):
	""""""
	return self.__html_parser.metas

    metas = property(__get_metas)
    """Get metas tags in HTML"""

    #----------------------------------------------------------------------
    def __get_title(self):
	""""""
	return self.__html_parser.title

    title = property(__get_title)
    """Get title of HTML"""


    #----------------------------------------------------------------------
    def __init_parser(self, data):
        """Initializes the HTML parser

	:return: Type and instance of parser, as tupple: (type, instance)
	"""

	m_return_parser = HTMLBeautifullSoap(data)
	m_return_type = HTML.__PARSER_BEAUTYFULL_SOAP

	return m_return_type, m_return_parser





#------------------------------------------------------------------------------
class HTMLBeautifullSoap(object):
    """
    Specify paser for Beautifull Soap parser
    """


    #----------------------------------------------------------------------
    def __init__(self, data):
	"""Constructor

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
	# CSS embeded
	self.__html_css_embeded = []
	# Javascript
	self.__html_javascript = []
	# Javascript embeded
	self.__html_javascript_embeded = []
	# Objects
	self.__html_objects = []
	# Metas
	self.__html_metas = []
	# Title
	self.__html_title = ""



    def __get_raw(self):
	"""Get raw HTML code"""
	return self.__raw_data
    raw_data = property(__get_raw)
    """Raw HTML content"""

    #----------------------------------------------------------------------
    def __get_forms(self):
	"""Get forms of HTML"""
	if not self.__html_forms:
	    m_elem = self.__html_parser.findAll("form")
	    # Get, and parte to UTF, info
	    self.__html_forms.extend(self.__converto_to_HTMLElements(m_elem))
	return self.__html_forms

    forms = property(__get_forms)
    """Forms in HTML"""

    #----------------------------------------------------------------------
    def __get_images(self):
	"""Get forms of HTML"""
	if not self.__html_images:
	    m_elem = self.__html_parser.findAll("img")
	    # Get the list of dicts
	    self.__html_images.extend(self.__converto_to_HTMLElements(m_elem))

	return self.__html_images

    images = property(__get_images)
    """Images in HTML"""

    #----------------------------------------------------------------------
    def __get_links(self):
	"""Get forms of HTML"""
	if not self.__html_links:
	    m_elem = self.__html_parser.findAll("form")
	    # Get the list of dicts
	    self.__html_links.extend(self.__converto_to_HTMLElements(m_elem))

	return self.__html_links

    links = property(__get_links)
    """Links in HTML"""

    def __get_css(self):
	"""Get forms of HTML"""
	if not self.__html_css:
	    m_elem = self.__html_parser.findAll(name="link", attrs={"rel":"stylesheet"})
	    # Get the list of dicts
	    self.__html_css.extend(self.__converto_to_HTMLElements(m_elem))

	return self.__html_css

    css_links = property(__get_css)
    """CSS links in HTML"""

    def __get_javascript(self):
	"""Get forms of HTML"""
	if not self.__html_javascript:
	    m_elem = self.__html_parser.findAll(name="script", attrs={"src": True})
	    # Get the list of dicts
	    self.__html_javascript.extend(self.__converto_to_HTMLElements(m_elem))

	return self.__html_javascript

    javascripts_links = property(__get_javascript)
    """Javascripts links in HTML"""

    #----------------------------------------------------------------------
    def __get_css_embeded(self):
	""""""
	if not self.__html_css_embeded:
	    m_elem = self.__html_parser.findAll("style")
	    # Get the list of dicts
	    self.__html_css_embeded.extend(self.__converto_to_HTMLElements(m_elem))

	return self.__html_css_embeded

    css_embeded = property(__get_css_embeded)
    """Get css embeded in HTML"""

    #----------------------------------------------------------------------
    def __get_javascript_embeded(self):
	""""""
	if not self.__html_javascript_embeded:
	    m_elem = self.__html_parser.findAll(name="script", attrs={"src": False})
	    # Get the list of dicts
	    self.__html_javascript_embeded.extend(self.__converto_to_HTMLElements(m_elem))

	return self.__html_javascript_embeded

    javascript_embeded = property(__get_javascript_embeded)
    """Get javascript embeded in HTML"""

    #----------------------------------------------------------------------
    def __get_metas(self):
	""""""
	if not self.__html_metas:
	    m_elem = self.__html_parser.findAll(name="meta")
	    # Get the list of dicts
	    self.__html_metas.extend(self.__converto_to_HTMLElements(m_elem))

	return self.__html_metas

    metas = property(__get_metas)
    """Get javascript embeded in HTML"""

    #----------------------------------------------------------------------
    def __get_title(self):
	""""""
	if not self.__html_title:
	    m_elem = self.__html_parser.findAll(name="title", recursive=False, limit=1)
	    # Get the list of dicts
	    self.__html_title = m_elem.name.encode("utf-8") if len(m_elem) > 0 else ""

	return self.__html_title

    title = property(__get_title)
    """Get title of HTML"""

    #----------------------------------------------------------------------
    def __get_object_embeded(self):
	""""""
	if not self.__html_objects:
	    m_elem = self.__html_parser.findAll(name="object")

	    m_result = list()

	    for obj in m_elem:
		# Get attrs
		m_ojb_attr = { k.encode("utf-8"): v.encode("utf-8") for k,v in obj.attrs.items()}

		# Add param attr
		m_ojb_attr["param"] = dict()

		# Add value for params
		for param in obj.findAllNext("param"):
		    m_ojb_attr["param"].update({ k.encode("utf-8"): v.encode("utf-8") for k,v in param.attrs.items()})

		m_raw_content = "".join([str(item.encode("utf-8")) for item in obj.contents if item != "\n"])

		m_result.append(HTMLElement(obj.name.encode("utf-8"), m_ojb_attr, m_raw_content))

	    self.__html_objects = m_result

	return self.__html_objects

    objects = property(__get_object_embeded)
    """Get objects embeded in HTML"""




    #----------------------------------------------------------------------
    def __converto_to_HTMLElements(self, data):
	"""
	Convert parser format to list of HTML Elements

	:return: list of HTMLElements
	"""
	return [
	    HTMLElement(
	        x.name.encode("utf-8"),
	        { k.encode("utf-8"): v.encode("utf-8") for k,v in x.attrs.items()},
	        "".join([str(item.encode("utf-8")) for item in x.contents if item != "\n"])
	        ) for x in data
	]


    #----------------------------------------------------------------------
    def __init_parser(self, data):
        """Initializes the HTML parser

	:return: Type and instance of parser
	"""
	from thirdparty_libs.bs4 import BeautifulSoup

	return BeautifulSoup(data)
