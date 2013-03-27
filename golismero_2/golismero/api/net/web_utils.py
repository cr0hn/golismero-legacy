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

__all__ = ["DecomposedURL", "is_method_allowed", "decompose_url", "generate_error_page", "fix_url", "is_in_scope", "convert_to_absolute_url", "convert_to_absolute_urls", 'detect_auth_method', 'get_auth_obj', 'check_auth', 'parse_url']

from requests import *
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from requests_ntlm import HttpNtlmAuth
from ..config import Config
from collections import namedtuple
from repoze_lru import lru_cache
from golismero.api.text.text_utils import generate_random_string

from urlparse import urlparse
from os.path import splitext, split

#----------------------------------------------------------------------
def is_method_allowed(method, url, network_conn):
    """
    Checks if method is allowed for this url.

    if method is supported return True. False otherwise.

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
def fix_url(url):
    """
    Fix selected URL adding neccesary info to be complete URL, like:
    www.site.com -> http://www.site.com

    :param url: an URL
    :type url: str
    """
    m_tmp_url = parse_url(url)

    return url if m_tmp_url.scheme and m_tmp_url.scheme != "NoneType" and m_tmp_url.scheme != "None" else "http://%s" % url

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



#----------------------------------------------------------------------
class DecomposedURL(object):
    """
    Decomposed URL in their parts, like:

    http://www.site.com/folder/index.php?param1=val1&b

    Where properties has the values:
    + scheme                    = 'http'
    + host                      = 'www.site.com'
    + complete_path             = '/folder/index.php?param1=val1'
    + relative_path             = '/folder/'
    + path_filename             = 'index.php'
    + path_filename_ext         = '.php'
    + path_filename_without_ext = 'index'
    + query                     = 'param1=val1&b'
    + query_params              = { 'param1' : 'val1', 'b' : '' }

    ** If any values are not present in URL, empty string are returned **NOT None TYPE**
    """
    #----------------------------------------------------------------------
    def __init__(self):
        """"""
        self.scheme = ''
        self.host = ''
        self.complete_path = ''
        self.relative_path = ''
        self.path_filename = ''
        self.path_filename_ext = ''
        self.path_filename_without_ext = ''
        self.query = ''
        self.query_params = {}

#----------------------------------------------------------------------
@lru_cache(maxsize=50)
def decompose_url(url):
    """
    Decompose URL in their parts and return DecomposedURL Object

    :param url: URL to decompose.
    :type url: str

    :return: DecomposedURL object
    :rtype: DecomposedURL
    """
    if url:

        m_parsed_url = parse_url(url)

        m_o = DecomposedURL()
        m_o.scheme                    = m_parsed_url.scheme if m_parsed_url.scheme else ''
        m_o.host                      = m_parsed_url.host if m_parsed_url.host else ''
        #m_o.complete_path             = m_parsed_url.path if m_parsed_url.path.endswith("/") else m_parsed_url.path + "/" if m_parsed_url.path is not None and m_parsed_url.path != "NoneType" else ''
        m_o.complete_path = None
        if m_parsed_url.path and m_parsed_url.path != "NoneType":
            m_o.complete_path = m_parsed_url.path if m_parsed_url.path.endswith("/") else m_parsed_url.path + "/"
        else:
            m_o.complete_path = ''

        m_o.path_filename_ext         = splitext(m_o.complete_path)[1] if m_o.complete_path else ''
        m_o.path_filename             = split(m_o.complete_path)[1] if m_o.complete_path and m_o.path_filename_ext else ''
        m_o.path_filename_without_ext = splitext(m_o.path_filename)[0] if m_o.complete_path and m_o.path_filename else ''
        m_o.query                     = m_parsed_url.query if m_parsed_url.query else ''



        # Add query params
        for t in m_o.query.split('&'):
            l_sp_t = t.split("=")
            if l_sp_t: # len > 0
                l_key = l_sp_t[0]
                l_val = '' if len(l_sp_t) == 1 else l_sp_t[1]
                # Store
                m_o.query_params[l_key] = l_val

        # Fix path for values like:
        # http://www.site.com/folder/value_id=0
        m_path = m_o.complete_path
        m_prev_folder = m_path[:m_path[:-1].rfind("/") + 1] # /folder/
        m_last = m_path[m_path[:-1].rfind("/") + 1: -1] # value_id=0
        if m_last.find("=") != -1:
            m_o.complete_path = m_prev_folder
        m_o.path_filename_without_ext = '/' if not m_prev_folder else m_prev_folder

        # Partial path
        m_o.relative_path = m_prev_folder

        return m_o

    else:
        raise ValueError("Valid URL string espected; got '%s'" % type(url))


#----------------------------------------------------------------------
def generate_error_page(url):
    """
    Generates a random error page for selected URL:

    http://www.site.com/index.php -> http://www.site.com/index.php.19ds_8vjX


    :param url: original URL
    :type  url: str

    :return: error page generated.
    :rtype: str
    """


    m_parsed_url = decompose_url(url)

    return "%s://%s%s%s.%s%s" % (
        m_parsed_url.scheme,
        m_parsed_url.host,
        m_parsed_url.relative_path if m_parsed_url.relative_path else '/',
        m_parsed_url.path_filename,
        generate_random_string(),
        m_parsed_url.query
    )


#----------------------------------------------------------------------
#
# THIS CODE HAS BEEN BORROWED FROM THE URLLIB3 PROJECT
#
#----------------------------------------------------------------------
class Url(namedtuple('Url', ['scheme', 'auth', 'host', 'port', 'path', 'query', 'fragment'])):
    """
    Datastructure for representing an HTTP URL. Used as a return value for
    :func:`parse_url`.
    """
    slots = ()

    def __new__(cls, scheme=None, auth=None, host=None, port=None, path=None, query=None, fragment=None):
        return super(Url, cls).__new__(cls, scheme, auth, host, port, path, query, fragment)

    @property
    def hostname(self):
        """For backwards-compatibility with urlparse. We're nice like that."""
        return self.host

    @property
    def request_uri(self):
        """Absolute path including the query string."""
        uri = self.path or '/'

        if self.query is not None:
            uri += '?' + self.query

        return uri

def split_first(s, delims):
    """
    Given a string and an iterable of delimiters, split on the first found
    delimiter. Return two split parts and the matched delimiter.

    If not found, then the first part is the full input string.

    Example: ::

        >>> split_first('foo/bar?baz', '?/=')
        ('foo', 'bar?baz', '/')
        >>> split_first('foo/bar?baz', '123')
        ('foo/bar?baz', '', None)

    Scales linearly with number of delims. Not ideal for large number of delims.
    """
    min_idx = None
    min_delim = None
    for d in delims:
        idx = s.find(d)
        if idx < 0:
            continue

        if min_idx is None or idx < min_idx:
            min_idx = idx
            min_delim = d

    if min_idx is None or min_idx < 0:
        return s, '', None

    return s[:min_idx], s[min_idx+1:], min_delim


#----------------------------------------------------------------------
class ParsedURLItem(object):
    """
    Contains a parsed URL. Properties:

    + scheme
    + username
    + password
    + hostname
    + port
    + path
    + query
    + fragment

    Where:

    scheme://username:password@hostname:port/path?query

    """
    pass

# Cache for parse url function
@lru_cache(maxsize=100)
def parse_url_(url):
    """
    Parse and URL and return a ParsedURLItem item

    :param url: URL to parse.
    :type url: str

    :return: ParsedURLItem item
    :rtype: ParsedURLItem
    """
    m_parsed_url = urlparse(url)

    m_robj = ParsedURLItem()
    m_robj.scheme   = m_parsed_url.scheme if m_parsed_url.scheme else None
    m_robj.host     = m_parsed_url.hostname if m_parsed_url.hostname else ''
    m_robj.hostname = m_robj.host # for compatibility and avoid errors.
    m_robj.path     = m_parsed_url.path if m_parsed_url.path else None
    m_robj.query    = m_parsed_url.query if m_parsed_url.query else None
    m_robj.fragment = m_parsed_url.fragment if m_parsed_url.fragment else None
    m_robj.port     = m_parsed_url.port if m_parsed_url.port else None
    m_robj.username = m_parsed_url.username if m_parsed_url.username else None
    m_robj.password = m_parsed_url.password if m_parsed_url.password else None

    return m_robj




@lru_cache(maxsize=100)
def parse_url(url):
    """
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

    # While this code has overlap with stdlib's urlparse, it is much
    # simplified for our needs and less annoying.
    # Additionally, this imeplementations does silly things to be optimal
    # on CPython.

    scheme = None
    auth = None
    host = None
    port = None
    path = None
    fragment = None
    query = None

    # Scheme
    if '://' in url:
        scheme, url = url.split('://', 1)

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

    # Port
    if ':' in url:
        _host, port = url.split(':', 1)

        if not host:
            host = _host

        if not port.isdigit():
            port = 80

        port = int(port)

    elif not host and url:
        host = url

    if not path:
        return Url(scheme, auth, host, port, path, query, fragment)

    # Fragment
    if '#' in path:
        path, fragment = path.split('#', 1)

    # Query
    if '?' in path:
        path, query = path.split('?', 1)

    return Url(scheme, auth, host, port, path, query, fragment)
