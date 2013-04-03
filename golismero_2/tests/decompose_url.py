#!/usr/bin/env python
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

# Fix the module load path.
if __name__ == "__main__":
    import os, sys
    from os import path
    root = path.split(path.abspath(__file__))[0]
    if not root:  # if it fails use cwd instead
        root = path.abspath(os.getcwd())
    root = path.abspath(path.join(root, ".."))
    thirdparty_libs = path.join(root, "thirdparty_libs")
    if not path.exists(path.join(root, "golismero")):
        raise RuntimeError("Can't find GoLismero!")
    sys.path.insert(0, thirdparty_libs)
    sys.path.insert(0, root)

from golismero.api.net.web_utils import DecomposedURL

from pprint import pprint
from unittest import TestCase, main


#--------------------------------------------------------------------------
class Test_DecomposedURL (TestCase):


    #--------------------------------------------------------------------------
    # Test case for "normal" URLs.

    # Canonicalized URLs.
    __normal = (
        'http://example.com/',
        'https://example.com/',
        'ftp://asmith@ftp.example.org/',
        'http://username:password@example.com:1234/path?query_string#fragment_id',
        'http://username:password@example.com:1234/path?query=string#fragment_id',
        'http://example.com/very/long/path/query=string',
        'http://example.com/shorter/path/query=string',
        'http://example.com/path/query=string',
        'http://example.com/query=string',
    )

    def test_normal(self):
        for url in self.__normal:
            ##pprint(DecomposedURL(url).url)
            self.assertEqual(DecomposedURL(url).url, url)


    #--------------------------------------------------------------------------
    # Test case for URL canonicalization.

    __equivalent = (

        # Case insensitive scheme and hostname, automatically add the trailing slash.
        (
            'http://example.com',
            'http://example.com/',
            'HTTP://EXAMPLE.COM',
            'HTTP://EXAMPLE.COM/',
        ),

        # Default port number.
        (
            'http://example.com',
            'http://example.com:80',
        ),
        (
            'https://example.com',
            'https://example.com:443',
        ),
        (
            'ftp://example.com',
            'ftp://example.com:21',
        ),

        # Sorting of query parameters, handling of missing values.
        (
            'http://example.com/path?query=string&param=value&orphan',
            'http://example.com/path?query=string&param=value&orphan=',
            'http://example.com/path?orphan&query=string&param=value',
            'http://example.com/path?orphan=&query=string&param=value',
        ),
        (
            'http://example.com/path?query=string&param=value&orphan#fragment_id',
            'http://example.com/path?query=string&param=value&orphan=#fragment_id',
            'http://example.com/path?orphan&query=string&param=value#fragment_id',
            'http://example.com/path?orphan=&query=string&param=value#fragment_id',
        ),
    )

    def test_equivalent(self):
        for url_list in self.__equivalent:
            normalized = set()
            for url in url_list:
                normalized.add(DecomposedURL(url).url)
            ##pprint(normalized)
            self.assertEqual(len(normalized), 1)


#--------------------------------------------------------------------------
if __name__ == "__main__":

    # Lauch the unit tests.
    main()
