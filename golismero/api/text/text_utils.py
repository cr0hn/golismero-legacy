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

__all__ = [
    "char_count", "line_count", "word_count", "generate_random_string",
    "uncamelcase", "extract_vuln_ids",  "convert_references_to_vuln_ids",
    "convert_vuln_ids_to_references", "split_first",
]

import re

from random import choice
from re import finditer
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
# Adapted from: http://stackoverflow.com/a/2560017/426293
__uncamelcase_re = re.compile("%s|%s|%s" % (
    r"(?<=[A-Z])(?=[A-Z][a-z])",
    r"(?<=[^A-Z])(?=[A-Z])",
    r"(?<=[A-Za-z])(?=[^A-Za-z])",
))
def uncamelcase(string):
    """
    Converts a CamelCase string into a human-readable string.

    Examples::
        >>> uncamelcase("lowercase")
        'lowercase'
        >>> uncamelcase("Class")
        'Class'
        >>> uncamelcase("MyClass")
        'My Class'
        >>> uncamelcase("HTML")
        'HTML'
        >>> uncamelcase("PDFLoader")
        'PDF Loader'
        >>> uncamelcase("AString")
        'A String'
        >>> uncamelcase("SimpleXMLParser")
        'Simple XML Parser'
        >>> uncamelcase("GL11Version")
        'GL 11 Version'
        >>> uncamelcase("99Bottles")
        '99 Bottles'
        >>> uncamelcase("May5")
        'May 5'
        >>> uncamelcase("BFG9000")
        'BFG 9000'

    :param string: CamelCase string.
    :type string: str

    :returns: Human-readable string.
    :rtype: str
    """
    return __uncamelcase_re.sub(" ", string)


#------------------------------------------------------------------------------
# Vulnerability ID processing utilities.

# ID extraction from plain text.
_vuln_id_regex = {
    "bid": [
        re.compile(
            r"\b(?:BID\-|BID\: ?|BUGTRAQ\-|BUGTRAQ\: ?|BUGTRAQ ID: ?)"
            r"([0-9]+)\b"),
    ],
    "capec": [
        re.compile(r"\bCAPEC(?:\-|\: ?)([0-9]+)\b"),
    ],
    "cve": [
        re.compile(
            r"\bCVE\-([0-9][0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9][0-9]?)\b"),
    ],
    "cwe": [
        re.compile(r"\bCWE(?:\-|\: ?)([0-9]+)\b"),
    ],
    "osvdb": [
        re.compile(r"\b(?:OSVDB\-|OSVDB\: ?|OSVDB ID\: ?)([0-9]+)\b"),
    ],
    "sa": [
        re.compile(r"\b(?:SECUNIA|SA)(?:\-|\: ?)([0-9]+)\b"),
        re.compile(r"\bSA([0-9]+)\b"),
    ],
    "sectrack": [
        re.compile(r"\b(?:SECTRACK\-|SECTRACK\: ?|SECTRACK ID\: ?)([0-9]+)\b"),
    ],
    "xf": [
        re.compile(r"\bXF\: ?[a-z0-9\-]* ?\(([0-9]+)\)(?:[^\w]|$)"),
        re.compile(r"\bXF\-([0-9]+)\b"),
    ],
}

# ID extraction from URLs.
_vuln_ref_regex = {
    "bid": [
        re.compile(
            r"^https?\:\/\/(?:www\.)?securityfocus\.com\/bid\/([0-9]+)$"),
    ],
    "capec": [
        re.compile(
            r"^https?\:\/\/capec\.mitre\.org\/data\/definitions\/"
            r"([0-9]+)\.html$"),
    ],
    "cve": [
        re.compile(
            r"^https?\:\/\/cve\.mitre\.org\/cgi\-bin\/cvename\.cgi\?name\="
            r"CVE\-([0-9][0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9][0-9]?)$"),
        re.compile(
            r"^https?\:\/\/nvd\.nist\.gov\/nvd\.cfm\?cvename\="
            r"CVE\-([0-9][0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9][0-9]?)$"),
        re.compile(
            r"^https?\:\/\/web\.nvd\.nist\.gov\/view\/vuln\/detail\?vulnId\="
            r"CVE\-([0-9][0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9][0-9]?)$"),
    ],
    "cwe": [
        re.compile(
        r"^https?\:\/\/cwe\.mitre\.org\/data\/definitions\/([0-9]+)\.html$"),
    ],
    "osvdb": [
        re.compile(
            r"^https?\:\/\/(?:www\.)?osvdb\.org\/show\/osvdb\/([0-9]+)$"),
    ],
    "sa": [
        re.compile(
            r"^https?\:\/\/(?:www\.)?secunia\.com\/advisories\/([0-9]+)$"),
    ],
    "sectrack": [
        re.compile(
            r"^https?\:\/\/(?:www\.)?securitytracker\.com\/id\?([0-9]+)$"),
        re.compile(
            r"^https?\:\/\/(?:www\.)?securitytracker\.com\/alerts"
            r"\/[0-9]+\/[A-Za-z]+\/([0-9]+)\.html$"),
    ],
    "xf": [
        re.compile(
            r"^https?\:\/\/xforce\.iss\.net\/xforce\/xfdb\/([0-9]+)$"),
    ],
}

# URL templates for references.
_vuln_ref_tpl = {
    "bid":      "http://www.securityfocus.com/bid/%s",
    "capec":    "https://capec.mitre.org/data/definitions/%s.html",
    "cve":      "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-%s",
    "cwe":      "https://cwe.mitre.org/data/definitions/%s.html",
    "osvdb":    "http://osvdb.org/show/osvdb/%s",
    "sa":       "http://www.secunia.com/advisories/%s",
    "sectrack": "http://www.securitytracker.com/id?%s",
    "xf":       "http://xforce.iss.net/xforce/xfdb/%s",
}

def extract_vuln_ids(text):
    """
    Extract vulnerability IDs from plain text using regular expressions.

    Currently the following ID types are supported: Bugtraq ID, CAPEC, CVE,
    CWE, OSVDB, Secunia, Security Tracker and ISS X-Force.

    Example::
        >>> extract_vuln_ids(\"\"\"
        ... Here we have CVE-1234-1234 and CVE-4321-4321.
        ... We also have a CWE, namely CWE-1234.
        ... However we're only mentioning OSVDB, not using it.
        ... \"\"\")
        {'cve': ['CVE-1234-1234', 'CVE-4321-4321'], 'cwe': ['CWE-1234']}
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
        ('CVE-1234-4321',)
        >>> vuln.cwe
        ()

    :param text: Plain text to search.
    :type text: str

    :returns: Map of ID type ("bid", "capec", "cve", "cwe", "osvdb", "sa",
        "sectrack", "xf") to lists of one or more strings, each string being a
        vulnerability ID of that type. Vulnerability types not found will not
        be present in the dictionary. If no vulnerability IDs were found at
        all, the dictionary will be empty.
    :rtype: dict( str -> list(str, ...) )
    """
    d = {}
    for vuln_type, vuln_re_list in _vuln_id_regex.iteritems():
        found = set()
        for vuln_re in vuln_re_list:
            found.update(vuln_re.findall(text))
        if found:
            prefix = vuln_type.upper() + "-"
            d[vuln_type] = sorted(
                prefix + vuln_id
                for vuln_id in found
            )
    return d

def convert_references_to_vuln_ids(urls):
    """
    Convert reference URLs to the vulnerability IDs they point to.

    Currently the following websites are supported: MITRE, NIST, OSVDB,
    Secunia, SecurityFocus, Security Tracker and ISS X-Force.

    :param urls: List of URLs to parse. URLs not pointing to one of the
        supported websites are silently ignored.
    :type urls: list(str)

    """ # docstring completed later!
    d = {}
    for vuln_type, vuln_re_list in _vuln_ref_regex.iteritems():
        found = set()
        for vuln_re in vuln_re_list:
            for url in urls:
                found.update(vuln_re.findall(url))
        if found:
            prefix = vuln_type.upper() + "-"
            d[vuln_type] = sorted(
                prefix + vuln_id
                for vuln_id in found
            )
    return d

# Fix the docstring.
convert_references_to_vuln_ids.__doc__ += \
    extract_vuln_ids.__doc__[extract_vuln_ids.__doc__.rfind(":returns:")]

def convert_vuln_ids_to_references(vuln_ids):
    """
    Convert vulnerability IDs to reference URLs.

    Currently the following ID types are supported: Bugtraq ID, CAPEC, CVE,
    CWE, OSVDB, Secunia, Security Tracker and ISS X-Force.

    :param vuln_ids: Vulnerability IDs.
    :type vuln_ids: list(str)

    :returns: Reference URLs.
    :rtype: list(str)
    """
    return [
        _vuln_ref_tpl[ vuln_type.lower() ] % vuln_id
        for vuln_type, vuln_id
        in [v.split("-", 1) for v in vuln_ids]
    ]


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
