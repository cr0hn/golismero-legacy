#!/usr/bin/python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------
# Web utilities API
#-----------------------------------------------------------------------

__license__="""
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

__all__ = ["fix_url", "is_in_scope", "convert_to_absolute_url",
           "convert_to_absolute_urls", "detect_auth_method",
           "get_auth_obj", "check_auth", "parse_url",
           "HTMLParser", "HTMLElement"]

from ..config import Config

from collections import namedtuple

from BeautifulSoup import BeautifulSoup
from repoze_lru import lru_cache
from requests import *
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from requests_ntlm import HttpNtlmAuth

#----------------------------------------------------------------------
# Cached version of the parse_url() function from urllib3

try:
    from requests.packages.urllib3.util import parse_url as original_parse_url
except ImportError:
    from urllib3.util import parse_url as original_parse_url

@lru_cache(maxsize=50)
def parse_url(url):
    return original_parse_url(url)


#----------------------------------------------------------------------
def fix_url(url):
    """
    Fix selected URL adding neccesary info to be complete URL, like:
    www.site.com -> http://www.site.com

    :param url: an URL
    :type url: str
    """
    m_tmp_url = parse_url(url)

    return url if m_tmp_url.scheme and m_tmp_url.scheme != "None" else "http://%s" % url


#----------------------------------------------------------------------
def check_auth(url, user, password):
    """
    Check the auth for and specified url.

    :param url: String with url.
    :type url: str

    :param user: string with user text
    :type user: str

    :param password: string with password text
    :type password: str

    :return: True if authentication is successful. False otherwise.
    """
    if not url:
        return False

    # Get auth method
    auth, realm = detect_auth_method(url)

    if auth:
        # Get authentication object
        m_auth_obj = get_auth_obj(auth, user,password)

        # Try the request
        req = Request(url=url, auth=m_auth_obj)
        p = req.prepare()

        s = Session()
        r = s.send(p)

        if r.status_code == codes.ok:
            return True
        else:
            return False


#----------------------------------------------------------------------
def get_auth_obj(method, user, password):
    """Generates an authentication code

    :param method: Auth method: basic, digest, ntlm.
    :type method: str

    :param user: string with user text
    :type user: str

    :param password: string with password text
    :type password: str

    :return: an object with authentication or None if error/problem.
    """
    m_auth_obj = None

    if method:

        m_method = method.lower()
        if m_method == "basic":
            m_auth_obj = HTTPBasicAuth(user, password)
        elif m_method == "digest":
            m_auth_obj = HTTPDigestAuth(user, password)
        elif m_method == "ntlm":
            m_auth_obj = HttpNtlmAuth(user, password)

    return m_auth_obj


#------------------------------------------------------------------------------
def detect_auth_method(url):
    """
    Detects authentication method.

    :param url: url to test authentication.
    :type url: str.

    :return: (scheme, realm) if auth required. None otherwise.
    """
    req = Request(url=url)
    p = req.prepare()

    s = Session()
    r = s.send(p)

    if 'www-authenticate' in r.headers:
        authline = r.headers['www-authenticate']
        authobj = compile(r'''(?:\s*www-authenticate\s*:)?\s*(\w*)\s+realm=['"]([^'"]+)['"]''',IGNORECASE)
        matchobj = authobj.match(authline)
        if not matchobj:
            return None, None
        scheme = matchobj.group(1)
        realm = matchobj.group(2)

    return scheme, realm


#----------------------------------------------------------------------
def is_in_scope(url):
    """
    Checks if an URL is ins scope of an audit

    :param url: string with url to check.
    :type url: str

    :returns: bool -- True if is in scope. False otherwise.
    """
    if not url:
        return False

    # Scope options
    m_include_subdomains = Config.audit_config.include_subdomains

    # Set of domain names we're allowed to connect to
    m_audit_scope = set(parse_url(x).hostname.lower() for x in Config.audit_config.targets)

    hostname = parse_url(url).hostname.lower()
    return hostname in m_audit_scope or (
        m_include_subdomains and
        any(hostname.endswith("." + domain) for domain in m_audit_scope)
    )


#----------------------------------------------------------------------
def convert_to_absolute_url(base_url, relative_url):
    """
    Convert 'relative_url' in absolute URL. 'base_url' is the base site
    for the relative url.

    :param base_url: base url.
    :type base_url: str

    :param relative_urls: URL to convert
    :type relative_urls: str

    :returns: str -- converted URL
    """

    m_return = convert_to_absolute_urls(base_url, (relative_url,))
    return m_return.pop() if m_return else None


#----------------------------------------------------------------------
def convert_to_absolute_urls(base_url, relative_urls):
    """
    Convert URLs in the 'relative_urls' in absolute URL list and remove duplicates. 'base_url' is the base site
    for the relative urls.

    :param base_url: base url.
    :type base_url: str

    :param relative_urls: list with urls to remove duplicates
    :type relative_urls: iterable

    :returns: iterable with URLs, as string format.
    """
    if not base_url or not relative_urls:
        return None


    # Parsed base url
    m_parsed_url = parse_url(base_url)


    # Remove duplicates and fix URL
    m_return = set()
    m_bind_add = m_return.add
    for u in relative_urls:
        try:
            l_parsed = parse_url(u)
        except ValueError:
            # Error while parsing URL
            continue

        if u == '':
            continue

        # Fix hostname
        m_hostname = ""
        if l_parsed.hostname is None:
            m_hostname = m_parsed_url.hostname
        else:
            m_hostname = l_parsed.hostname

        # Fix scheme
        m_scheme = 'http' if not m_parsed_url.scheme else m_parsed_url.scheme if l_parsed.scheme is None else l_parsed.scheme

        # Fix path
        m_path = ""
        if l_parsed.path:
            m_path = '' if len(l_parsed.path) == 1 and l_parsed.path == "/" else l_parsed.path

        # Fix params of query
        m_query = l_parsed.query if l_parsed.query else ''

        # Add complete URL
        m_bind_add("%s://%s%s%s" % (
            m_scheme,
            m_hostname,
            m_path,
            m_query
        ))

    return m_return


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
        """Name of HTML tag."""
        return self.__tag_name

    @property
    def attrs(self):
        """Attributes of HTML tag."""
        return self.__attrs

    @property
    def content(self):
        """Returns an HTML object nested into this HTML element.

        :returns: and HTML object
        """
        return self.__content


#------------------------------------------------------------------------------
class HTMLParser(object):
    """
    HTML parser.
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
                update = m_ojb_attr["param"].update
                for param in obj.findAllNext("param"):
                    update({ k[0].encode("utf-8"): k[1].encode("utf-8") for k in param.attrs})

                m_raw_content = "".join((str(item) for item in obj.contents if item != "\n"))

                m_result_append_bind(HTMLElement(obj.name.encode("utf-8"), m_ojb_attr, m_raw_content))

            self.__html_objects = m_result

        return self.__html_objects
