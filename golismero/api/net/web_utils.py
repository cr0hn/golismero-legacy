#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------
# Web utilities API
#-----------------------------------------------------------------------

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

__all__ = [
    "is_method_allowed", "fix_url",
    "check_auth", "get_auth_obj", "detect_auth_method",
    "is_in_scope", "generate_error_page_url",
    "DecomposedURL", "HTMLElement", "HTMLParser",
]



from ..config import Config
from ..text.text_utils import generate_random_string, split_first

from BeautifulSoup import BeautifulSoup
from copy import deepcopy
from posixpath import join, splitext, split
from repoze.lru import lru_cache
from requests import Request, Session, codes
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from requests_ntlm import HttpNtlmAuth
from urllib import quote, quote_plus, unquote, unquote_plus
from urlparse import urldefrag, urljoin
from warnings import warn

import re


#----------------------------------------------------------------------
# Cached version of the parse_url() function from urllib3,
# and Url class renamed as Urllib3_Url to avoid confusion.

try:
    from requests.packages.urllib3.util import parse_url as original_parse_url
    from requests.packages.urllib3.util import Url as Urllib3_Url
except ImportError:
    from urllib3.util import parse_url as original_parse_url
    from urllib3.util import Url as Urllib3_Url

@lru_cache(maxsize=50)
def parse_url(url):
    """
    .. warning:
       This method is only a wrapper of the original urllib3 function with de particularity that the **result will be cached for improve the performance**.

    Given a url, return a parsed :class:`.Url` namedtuple. Best-effort is
    performed to parse incomplete urls. Fields not provided will be None.

    Partly backwards-compatible with :mod:`urlparse`.

    Example: ::

        >>> parse_url('http://google.com/mail/')
        Url(scheme='http', host='google.com', port=None, path='/', ...)
        >>> parse_url('google.com:80')
        Url(scheme=None, host='google.com', port=80, path=None, ...)
        >>> parse_url('/foo?bar')
        Url(scheme=None, host=None, port=None, path='/foo', query='bar', ...)
    """
    return original_parse_url(url)


#----------------------------------------------------------------------
def is_method_allowed(method, url, network_conn):
    """
    Checks if method as parameter is allowed for this url.

    if method is supported return True. False otherwise.

    Example:

    >>> from golismero.net.web_utils import is_method_allowed
    >>> is_method_allowed("GET", "www.site.com", connection_object)
    True
    >>> is_method_allowed("OPTIONS", "www.site.com", connection_object)
    False

    :param method: string with method to check
    :type method: str

    :param url: URL to test methods.
    :type url: str.

    :param network_conn: network connection.
    :type network_conn: Protocol (Web).

    :returns: bool -- True if method is allowed. False otherwise.
    :rtype: bool
    """
    if not url or not network_conn or not method:
        return False

    try:
        p = network_conn.get(url, method=method)
    except:
        return False

    if p.http_response_code == 200: # and 'Content-Length' in p.http_headers:
        return True
    else:
        return False


#----------------------------------------------------------------------
def fix_url(url, base_url=None):
    """
    Fix selected URL adding neccesary info to be complete URL, like:

    * www.site.com -> http://www.site.com/

    Example:

    >>> from golismero.net.web_utils import fix_url
    >>> fix_url("www.site.com")
    http://www.site.com

    If base_url is provided, then a canonized and fixed url will return:

    * in  -> (url=/contact, base_url=www.site.com)
    * out -> http://www.site.com/contact

    Example:

    >>> from golismero.net.web_utils import fix_url
    >>> fix_url(url="/contact", base_url="www.site.com")
    http://www.site.com/contact

    :param url: URL
    :type url: str

    :param base_url: base url for canonize process.
    :type base_url: str

    :return: fixed and canonized url.
    :rtype: str

    """
    parsed = DecomposedURL(url)
    if not parsed.scheme:
        parsed.scheme = 'http://'

    if base_url:
        # Remove the fragment from the base URL.
        base_url = urldefrag(base_url)[0]
        # Canonicalize the URL.
        return urljoin(base_url, parsed.url.strip())
    else:
        return parsed.url


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
    """
    Generates an authentication code object depending of method as parameter:

    * "basic"
    * "digest"
    * "ntlm"

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
    Detects authentication method/type for an URL.

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
        authobj = re.compile(r'''(?:\s*www-authenticate\s*:)?\s*(\w*)\s+realm=['"]([^'"]+)['"]''',re.IGNORECASE)
        matchobj = authobj.match(authline)
        if not matchobj:
            return None, None
        scheme = matchobj.group(1)
        realm = matchobj.group(2)

    return scheme, realm


#----------------------------------------------------------------------
@lru_cache(maxsize=100, timeout=1*60*60)
# The "audit_name" parameter is required for the cache.
# No matter what PyLint says, don't remove it!
def get_audit_scope(audit_name):
    """
    Gets the scope for the audit that are executing. In practice, get all of hosts included to scan.

    **For improve the performance, all the check are cached**

    :param audit_name: Name of the current audit.
    :type audit_name: str

    :return: Domain names we're allowed to connect to.
    :rtype: set(str)
    """
    return {parse_url(x).hostname.lower() for x in Config.audit_config.targets}


#----------------------------------------------------------------------
def is_in_scope(url):
    """
    Checks if an URL is ins scope of an audit

    Example:

    If you're auditing the site: www.mysite.com:

    >>> from golismero.api.web_utils import is_in_scope
    >>> url_to_check="www.other_site.com"
    >>> is_in_scope(url_to_check)
    False

    :param url: string with url to check.
    :type url: str

    :returns: bool -- True if is in scope. False otherwise.
    """

    # Trivial case.
    if not url:
        return False

    # Use parse_url instead of DecomposedURL because it's faster and good enough for this.
    try:
        p_url = parse_url(url)
    except Exception, e:
        warn("Error parsing URL (%s): %s" % (url, e.message))
        return False

    # Set of domain names we're allowed to connect to.
    m_audit_scope = get_audit_scope(Config.audit_name)

    # Check domains, and subdomains too when requested.
    # FIXME: IPv4 and IPv6 addresses are not handled!
    m_include_subdomains = Config.audit_config.include_subdomains
    hostname = p_url.hostname.lower()
    return hostname in m_audit_scope or (
        m_include_subdomains and
        any(hostname.endswith("." + domain) for domain in m_audit_scope)
    )


#----------------------------------------------------------------------
def generate_error_page_url(url):
    """
    Generates a random error page for selected URL:

    Example:

    >>> from golismero.api.web_utils import generate_error_page_url
    >>> original_url = "http://www.site.com/index.php"
    >>> generate_error_page_url(original_url)
    'http://www.site.com/index.php.19ds_8vjX'

    :param url: original URL
    :type  url: str

    :return: error page generated.
    :rtype: str
    """
    m_parsed_url = DecomposedURL(url)
    m_parsed_url.path = m_parsed_url.path + generate_random_string()
    return m_parsed_url.url


#----------------------------------------------------------------------
class DecomposedURL(object):
    """
    Decomposed URL, that is, broken down to its parts.

    For example, the following URL:

    http://user:pass@www.site.com/folder/index.php?param1=val1&b#anchor

    Is broken down to the following properties:

    + url          = 'http://user:pass@www.site.com/folder/index.php?param1=val1&b#anchor'
    + request_uri  = '/folder/index.php?param1=val1&b#anchor'
    + scheme       = 'http'
    + host         = 'www.site.com'
    + port         = 80
    + username     = 'user'
    + password     = 'pass'
    + auth         = 'user:pass'
    + netloc       = 'user:pass@www.site.com'
    + path         = '/folder/index.php'
    + directory    = '/folder/'
    + filename     = 'index.php'
    + filebase     = 'index'
    + extension    = '.php'
    + query        = 'param1=val1&b'
    + query_params = { 'param1' : 'val1', 'b' : '' }

    The url property contains the normalized form of the URL, mostly
    preserving semantics (the query parameters may be sorted, and empty
    URL components are removed).
    For more details see: https://en.wikipedia.org/wiki/URL_normalization

    Changes to the values of these properties will be reflected in all
    other relevant properties. The url and request_uri properties are
    read-only, however.

    **Missing properties are returned as empty strings**, except for the port
    and query_params properties: port is an integer from 1 to 65535 when
    found, or None when it's missing and can't be guessed; query_params is
    a dictionary that may be empty when missing, or None when the query
    string could not be parsed as standard key/value pairs.

    Rebuilding the URL may result in a slightly different, but
    equivalent URL, if the URL that was parsed originally had
    unnecessary delimiters (for example, a ? with an empty query;
    the RFC states that these are equivalent).

    Example:

    >>> from golismero.api.web_utils import DecomposedURL
    >>> url="http://user:pass@www.site.com/folder/index.php?param1=val1&b#anchor"
    >>> r = DecomposedURL(url)
    >>> r.scheme
    'http'
    >>> r.filename
    'index.php'
    >>> r.hostname
    'www.site.com'


    .. warning::
       The url, request_uri, query, netloc and auth properties are URL-encoded. All other properties are URL-decoded.

    .. warning::
       Unicode is currently NOT supported.
    """

    #----------------------------------------------------------------------
    # TODO: for the time being we're using the buggy quote and unquote
    # implementations from urllib, but we'll have to roll our own to
    # properly support Unicode (urllib does a mess of it!).
    #----------------------------------------------------------------------


    #----------------------------------------------------------------------
    # Dictionary of default port numbers per each supported scheme.
    # The keys of this dictionary are also used to check if a given
    # scheme is supported by this class.

    default_ports = {
        'http'      : 80,        # http://www.example.com/
        'https'     : 443,       # https://secure.example.com/
        'ftp'       : 21,        # ftp://ftp.example.com/file.txt
        'mailto'    : 25,        # mailto://user@example.com?subject=Hi!
        ##'file'      : None,      # file://C:\Windows\System32\calc.exe
        ##'data'      : None,      # data:data:image/png;base64,iVBORw0KGgoA...
        ##'javascript': None,      # javascript:alert('XSS')
        ##'vbscript'  : None,      # vbscript:alert('XSS')
        ##'magnet'    : None,      # magnet:?xt=urn:sha1:YNCKHTQCWBTRNJIV4WN...
    }


    #----------------------------------------------------------------------
    # The constructor has code borrowed from the urllib3 project, then
    # adapted and expanded to fit the needs of GoLismero.
    #
    # Urllib3 is copyright 2008-2012 Andrey Petrov and contributors (see
    # CONTRIBUTORS.txt) and is released under the MIT License:
    # http://www.opensource.org/licenses/mit-license.php
    # http://raw.github.com/shazow/urllib3/master/CONTRIBUTORS.txt
    #
    def __init__(self, url, base_url = None):
        """
        :param url: URL to parse.
        :type url: str

        :param base_url: Optional base URL.
        :type base_url: str
        """

        original_url = url

        self.__query_char = '?'

        scheme = ''
        auth = ''
        host = ''
        port = None
        path = ''
        query = ''
        fragment = ''

        if base_url:
            url = urljoin(base_url, url, allow_fragments=True)

        # Scheme
        if ':' in url:
            if '://' in url:
                scheme, url = url.split('://', 1)
            else:
                scheme, url = url.split(':', 1)

            # we sanitize it here to prevent errors down below
            scheme = scheme.strip().lower()
            if '%' in scheme or '+' in scheme:
                scheme = unquote_plus(scheme)
            if scheme not in self.default_ports:
                raise ValueError("Failed to parse: %s" % original_url)

        # Find the earliest Authority Terminator
        # (http://tools.ietf.org/html/rfc3986#section-3.2)
        url, path_, delim = split_first(url, ['/', '?', '#'])

        if delim:
            # Reassemble the path
            path = delim + path_

        # Auth
        if '@' in url:
            auth, url = url.split('@', 1)

        # IPv6
        if url and url[0] == '[':
            host, url = url[1:].split(']', 1)
            host = "[%s]" % host  # we need to remember it's IPv6

        # Port
        if ':' in url:
            _host, port = url.split(':', 1)

            if not host:
                host = _host

            if '%' in port:
                port = unquote(port)

            if not port.isdigit():
                raise ValueError("Failed to parse: %s" % original_url)

            port = int(port)

        elif not host and url:
            host = url

        if path:

            # Fragment
            if '#' in path:
                path, fragment = path.split('#', 1)

            # Query
            if '?' in path:
                path, query = path.split('?', 1)
            else:
                # Fix path for values like:
                # http://www.site.com/folder/value_id=0
                p = path.rfind('/') + 1
                if p > 0:
                    _path = path[:p]
                    _query = path[p:]
                else:
                    _path = '/'
                    _query = path
                if '=' in _query:
                    path, query = _path, _query
                    self.__query_char = '/'

        if auth:
            auth = unquote_plus(auth)
        if host:
            host = unquote_plus(host)
        if path:
            path = unquote_plus(path)
        if fragment:
            fragment = unquote_plus(fragment)

        self.__scheme = scheme  # already sanitized
        self.auth = auth
        self.host = host
        self.port = port
        self.path = path
        self.query = query
        self.fragment = fragment


    #----------------------------------------------------------------------
    def __str__(self):
        return self.url


    #----------------------------------------------------------------------
    def copy(self):
        """
        :returns: DecomposedURL -- A copy of this object.
        """
        return deepcopy(self)


    #----------------------------------------------------------------------
    def to_urlsplit(self):
        """
        Convert to a tuple that can be passed to urlparse.urlunstrip().
        """
        return (self.__scheme, self.netloc, self.__path, self.query, self.__fragment)


    #----------------------------------------------------------------------
    def to_urlparse(self):
        """
        Convert to a tuple that can be passed to urlparse.urlunparse().
        """
        return (self.__scheme, self.netloc, self.__path, None, self.query, self.__fragment)


    #----------------------------------------------------------------------
    def to_urllib3(self):
        """
        Convert to a named tuple as returned by urllib3.parse_url().
        """
        return Urllib3_Url(self.__scheme, self.auth, self.__host, self.port,
                           self.__path, self.query, self.__fragment)


    #----------------------------------------------------------------------
    # Read-only properties.

    @property
    def url(self):
        scheme = self.__scheme
        fragment = self.__fragment
        request_uri = self.request_uri
        if scheme:
            scheme = scheme + "://"
        if fragment:
            request_uri = "%s#%s" % (request_uri, quote(fragment, safe=''))
        return "%s%s%s" % (scheme, self.netloc, request_uri)

    @property
    def request_uri(self):
        path = quote_plus(self.__path, safe='/')
        query = self.query
        if query:
            char = self.__query_char
            if path.endswith(char):
                path = path + query
            else:
                path = "%s%s%s" % (path, char, query)
        return path


    #----------------------------------------------------------------------
    # Read-write properties.

    @property
    def scheme(self):
        return self.__scheme

    @scheme.setter
    def scheme(self, scheme):
        if scheme:
            scheme = scheme.strip().lower()
            if scheme.endswith('://'):
                scheme = scheme[:-3].strip()
            if scheme and scheme not in self.default_ports:
                raise ValueError("URL scheme not supported: %s" % scheme)
        else:
            scheme = ''
        self.__scheme = scheme

    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, host):
        if not host:
            host = ''
        elif host.startswith('[') and host.endswith(']'):
            host = host.upper()
        else:
            host = host.strip().lower()
        self.__host = host

    @property
    def query_char(self):
        return self.__query_char

    @query_char.setter
    def query_char(self, query_char):
        if not query_char:
            query_char = '?'
        elif query_char not in ('?', '/'):
            raise ValueError("Invalid query separator character: %r" % query_char)
        self.__query_char = query_char

    @property
    def port(self):
        port = self.__port
        if not port:
            port = self.default_ports.get(self.__scheme, None)
        return port

    @port.setter
    def port(self, port):
        if not port:
            port = None
        elif not 1 <= port <= 65535:
            raise ValueError("Bad port number: %r" % port)
        self.__port = port

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path):
        if not path:
            path = '/'
        self.__path = path

    @property
    def fragment(self):
        return self.__fragment

    @fragment.setter
    def fragment(self, fragment):
        if not fragment:
            fragment = ''
        self.__fragment = fragment

    @property
    def query(self):
        # TODO: according to this: https://en.wikipedia.org/wiki/URL_normalization
        # sorting the query parameters may break semantics. To fix this we may want
        # to try to preserve the original order when possible. The problem then is
        # we'll "see" URLs with the same parameters in different order as different.
        if self.__query is not None:  # when it can't be parsed
            return self.__query
        if not self.__query_params:
            return ''
        return '&'.join( '%s=%s' % ( quote(k, safe=''), quote(v, safe='') )
                         for (k, v) in sorted(self.__query_params.iteritems()) )

    @query.setter
    def query(self, query):
        if not query:
            query_params = {}
        else:
            try:
                # much faster than parse_qsl()
                query_params = dict(( map(unquote_plus, (token + '=').split('=', 2)[:2])
                                      for token in query.split('&') ))
                if len(query_params) == 1 and not query_params.values()[0]:
                    query_params = None
                else:
                    query = None
            except Exception:
                ##raise   # XXX DEBUG
                query_params = None
        self.__query, self.__query_params = query, query_params


    #----------------------------------------------------------------------
    # Aliases.

    @property
    def directory(self):
        return split(self.__path)[0]

    @directory.setter
    def directory(self, directory):
        self.path = join(directory, self.filename)

    hostname = host
    folder = directory

    @property
    def filename(self):
        return split(self.__path)[1]

    @filename.setter
    def filename(self, filename):
        self.path = join(self.directory, filename)

    @property
    def filebase(self):
        return splitext(self.filename)[0]

    @filebase.setter
    def filebase(self, filebase):
        self.path = join(self.directory, filebase + self.extension)

    @property
    def extension(self):
        return splitext(self.filename)[1]

    @extension.setter
    def extension(self, extension):
        self.path = join(self.directory, self.filebase + extension)

    @property
    def netloc(self):
        host = self.__host
        if not (host.startswith('[') and host.endswith(']')):
            host = quote(host, safe='.')
        port = self.port
        auth = self.auth
        if port and port in self.default_ports.values():
            port = None
        if auth:
            host = "%s@%s" % (auth, host)
        if port:
            host = "%s:%s" % (host, port)
        return host

    @netloc.setter
    def netloc(self, netloc):
        if '@' in netloc:
            auth, host = netloc.split('@', 1)
        else:
            auth, host = None, netloc
        if host and host[0] == '[':
            host, port = host[1:].split(']', 1)
            if ':' in port:
                _host, port = port.split(':', 1)
                if not host:
                    host = _host
        elif ':' in host:
            host, port = host.split(':', 1)
        if '%' in port:
            port = unquote(port)
        if port:
            port = int(port)
        if host:
            host = unquote_plus(host)
        self.auth = auth  # TODO: roll back changes if it fails
        self.host = host
        self.port = port

    @property
    def auth(self):
        auth = ''
        username = self.__username
        password = self.__password
        if username:
            if password:
                auth = "%s:%s" % (quote(username, safe=''), quote(password, safe=''))
            else:
                auth = quote(username, safe='')
        elif password:
            auth = ":%s" % quote(password, safe='')
        return auth

    @auth.setter
    def auth(self, auth):
        if auth:
            if ':' in auth:
                username, password = auth.split(':', 1)
                self.__username = unquote_plus(username)
                self.__password = unquote_plus(password)
            else:
                self.__username = unquote_plus(auth)
                self.__password = ''
        else:
            self.__username = ''
            self.__password = ''


#------------------------------------------------------------------------------
class HTMLElement (object):


    #----------------------------------------------------------------------
    def __init__(self, tag_name, attrs, content):
        """
        Constructor.

        :param attr: dict with parameters of HTML element.
        :type attr: dict

        :param content: raw HTML with sub elements of this HTML element
        :type content: str
        """
        self.__tag_name = tag_name
        self.__attrs = attrs
        self.__content = content


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

        :returns: an HTML object
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
