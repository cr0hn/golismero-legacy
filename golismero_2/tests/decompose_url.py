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
from timeit import Timer, default_repeat
from unittest import TestCase, main


#--------------------------------------------------------------------------
class Test_DecomposedURL (TestCase):


    #--------------------------------------------------------------------------
    # Test cases for "normal" URLs.

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
    # Test cases for URL canonicalization.

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

        # Sanitization of pathological cases.
        (
            "http://user:name:password@example.com",    # broken
            "http://user:name%3Apassword@example.com/", # sanitized
        ),
        (
            "http://lala@pepe@example.com",    # broken
            "http://lala@pepe%40example.com/", # sanitized
        ),
        (
            "http://example.com/path%2Ffile", # broken
            "http://example.com/path/file",   # sanitized
        ),
        (
            "http://example%2Ecom/", # broken
            "http://example.com/",   # sanitized
        ),
        (
            "h%74%74p://example.com/", # broken
            "http://example.com/",     # sanitized
        ),
        (
            "http://example.com/file name with spaces", # broken
            "http://example.com/file+name+with+spaces", # sanitized
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
    # Test cases for relative URLs.

    # Relative URLs, base: http://example.com/path/
    __relative = (
        ('/robots.txt', 'http://example.com/robots.txt'),
        ('index.php?query=string', 'http://example.com/path/index.php?query=string'),
        ('#fragment', 'http://example.com/path/#fragment'),
    )

    def test_relative(self):
        for url in self.__normal:
            ##pprint(DecomposedURL(url, 'http://example.com/path/').url)
            self.assertEqual(DecomposedURL(url, 'http://example.com/path/').url, url)


    #--------------------------------------------------------------------------
    # Test cases for URL parsing errors.

    __errors = (

        # Unsupported scheme.
        "bogus://example.com",
        "data:11223344",
        "javascript:alert('xss')",

        # Broken scheme
        "http:/example.com",
        "http:example.com",
    )

    def __decompose_url(self, url):
        return DecomposedURL(url).url

    def test_errors(self):
        for url in self.__errors:
            self.assertRaises(ValueError, self.__decompose_url, url)


#--------------------------------------------------------------------------
def _benchmark():
    return DecomposedURL('http://example.com/path?query=string&param=value&orphan#fragment_id').url

# Some code borrowed from the timeit module.
def benchmark(number = 0, precision = 3, verbose = True):
    repeat = default_repeat
    t = Timer(_benchmark)
    if number == 0:
        # determine number so that 0.2 <= total time < 2.0
        for i in range(1, 10):
            number = 10**i
            try:
                x = t.timeit(number)
            except:
                t.print_exc()
                return 1
            if verbose:
                print "%d loops -> %.*g secs" % (number, precision, x)
            if x >= 0.2:
                break
    try:
        r = t.repeat(repeat, number)
    except:
        t.print_exc()
        return 1
    best = min(r)
    if verbose:
        print "raw times:", " ".join(["%.*g" % (precision, x) for x in r])
    print "%d loops," % number,
    usec = best * 1e6 / number
    if usec < 1000:
        print "best of %d: %.*g usec per loop" % (repeat, precision, usec)
    else:
        msec = usec / 1000
        if msec < 1000:
            print "best of %d: %.*g msec per loop" % (repeat, precision, msec)
        else:
            sec = msec / 1000
            print "best of %d: %.*g sec per loop" % (repeat, precision, sec)
    return None


#--------------------------------------------------------------------------
if __name__ == "__main__":

    # Launch the benchmark tests.
    print "----------------------------------------------------------------------"
    print "Benchmark tests"
    benchmark()

    # Lauch the unit tests.
    print "----------------------------------------------------------------------"
    print "Unit tests"
    main()
