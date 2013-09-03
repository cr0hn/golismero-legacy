#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Text manipulation utilities.
"""

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: https://github.com/golismero
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

__all__ = [ "char_count", "line_count", "word_count",
            "generate_random_string", "split_first",
            "extract_vuln_ids", ]

from random import choice
from re import findall, finditer
from string import ascii_letters, digits


#------------------------------------------------------------------------------
def char_count(text):
    """
    :param text: Text.
    :type text: str

    :returns: Number of printable characters in text.
    :rtype: int
    """
    return sum(1 for _ in finditer(r"\w", text))


#------------------------------------------------------------------------------
def line_count(text):
    """
    :param text: Text.
    :type text: str

    :returns: Number of lines in text.
    :rtype: int
    """
    count = text.count("\n")
    if not text.endswith("\n"):
        count += 1
    return count


#------------------------------------------------------------------------------
def word_count(text):
    """
    :param text: Text.
    :type text: str

    :returns: Number of words in text.
    :rtype: int
    """
    return sum(1 for _ in finditer(r"\w+", text))


#------------------------------------------------------------------------------
def generate_random_string(length = 30):
    """
    Generates a random string of the specified length.

    The key space used to generate random strings are:

    - ASCII letters (both lowercase and uppercase).
    - Digits (0-9).

    >>> from golismero.text.text_utils import generate_random_string
    >>> generate_random_string(10)
    Asi91Ujsn5
    >>> generate_random_string(30)
    8KNLs981jc0h1ls8b2ks01bc7slgu2

    :param length: Desired string length.
    :type length: int
    """

    m_available_chars = ascii_letters + digits

    return "".join(choice(m_available_chars) for _ in xrange(length))


#------------------------------------------------------------------------------
def extract_vuln_ids(text):
    """
    Extract vulnerability IDs from plain text using regular expressions.
    Currently CVE, CWE and OSVDB are supported.

    Example::
        >>> extract_vuln_ids(\"\"\"
        ... Here we have CVE-1234-1234 and CVE-4321-4321.
        ... We also have a CWE, namely CWE-1234-1234.
        ... However we're only mentioning OSVDB, not using it.
        ... \"\"\")
        {'cve': ['CVE-1234-1234', 'CVE-4321-4321'], 'cwe': ['CWE-1234-1234']}
        >>> extract_vuln_ids("There is nothing here!")
        {}

    This can be useful when instancing Vulnerability objects::
        >>> from golismero.api.data.vulnerability import GenericVulnerability
        >>> description = "This vulnerability is CVE-1234-4321."
        >>> kwargs = extract_vuln_ids(description)
        >>> kwargs['description'] = description
        >>> vuln = GenericVulnerability( **kwargs )
        >>> vuln.description
        'This vulnerability is CVE-1234-4321.'
        >>> vuln.cve
        ['CVE-1234-4321']
        >>> vuln.cwe
        ()

    :param text: Plain text to search.
    :type text: str

    :returns: Map of ID type ("cve", "cwe", "osvdb") to lists containing one
        or more strings, each string being a vulnerability ID of that type.
        Vulnerability types not found will not be present in the dictionary. If
        no vulnerability IDs were found at all, the dictionary will be empty.
    :rtype: dict( str -> list(str, ...) )
    """
    d = {}
    found = findall(r"\b(OSVDB\-[0-9]+)\b", text)
    if found:
        d["osvdb"] = found
    found = findall(
        r"\b(CVE\-[0-9][0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9][0-9]?)\b", text)
    if found:
        d["cve"] = found
    found = findall(
        r"\b(CWE\-[0-9][0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9])\b", text)
    if found:
        d["cwe"] = found
    return d


#------------------------------------------------------------------------------
# This function was borrowed from the urllib3 project.
#
# Urllib3 is copyright 2008-2012 Andrey Petrov and contributors (see
# CONTRIBUTORS.txt) and is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php
# http://raw.github.com/shazow/urllib3/master/CONTRIBUTORS.txt
#
def split_first(s, delims):
    """
    Given a string and an iterable of delimiters, split on the first found
    delimiter. Return the two split parts and the matched delimiter.

    If not found, then the first part is the full input string.

    Example: ::

        >>> split_first('foo/bar?baz', '?/=')
        ('foo', 'bar?baz', '/')
        >>> split_first('foo/bar?baz', '123')
        ('foo/bar?baz', '', None)

    Scales linearly with number of delimiters.
    Not ideal for a large number of delimiters.

    .. warning: This function was borrowed from the urllib3 project.
                It may be removed in future versions of GoLismero.
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
