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


from urllib3.util import parse_url
from core.api.config import Config

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
    m_include_subdomains = Config().audit_config.include_subdomains

    # Set of domain names we're allowed to connect to
    m_audit_scope = set(parse_url(x).hostname.lower() for x in Config().audit_config.targets)

    hostname = parse_url(url).hostname.lower()
    return hostname in m_audit_scope or (
        m_include_subdomains and
        any(hostname.endswith("." + domain) for domain in m_audit_scope)
    )



#----------------------------------------------------------------------
def converto_to_absolute_url(base_url, relative_url):
    """
    Convert 'relative_url' in absolute URL. 'base_url' is the base site
    for the relative url.

    :param base_url: base url.
    :type base_url: str

    :param relative_urls: URL to convert
    :type relative_urls: str

    :returns: str -- converted URL
    """
    m_return = converto_to_absolute_url(base_url, (relative_url))
    return m_return[0] if m_return else None

#----------------------------------------------------------------------
def converto_to_absolute_urls(base_url, relative_urls):
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
    m_return = []
    for u in relative_urls:
        try:
            l_parsed = parse_url(u)
        except LocationParseError:
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
        m_scheme = m_parsed_url.scheme if l_parsed.scheme is None else l_parsed.scheme

        # Fix path
        m_path = ""
        if l_parsed.path:
            m_path = '' if len(l_parsed.path) == 1 and l_parsed.path == "/" else l_parsed.path

        # Fix params of query
        m_query = l_parsed.query if l_parsed.query else ''

        # Add complete URL
        m_return.append("%s://%s%s%s" % (
                m_scheme,
                m_hostname,
                m_path,
                m_query
            ))

    return set(m_return)