#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
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


# Fix the module path for the tests.
import sys
import os
from os import path
try:
    _FIXED_PATH_
except NameError:
    here = path.split(path.abspath(__file__))[0]
    if not here:  # if it fails use cwd instead
        here = path.abspath(os.getcwd())
    golismero = path.join(here, "..")
    thirdparty_libs = path.join(golismero, "thirdparty_libs")
    if path.exists(thirdparty_libs):
        sys.path.insert(0, thirdparty_libs)
        sys.path.insert(0, golismero)
    _FIXED_PATH_ = True


# Imports
from golismero.api.net.web_utils import DecomposedURL

# Simple test cases.
simple = (

    # Full http url.
    {
        'url'              : 'http://user:pass@www.site.com/folder/index.php?param=value#anchor',
        'request_uri'      : '/folder/index.php?param=value',
        'scheme'           : 'http',
        'host'             : 'www.site.com',
        'port'             : 80,
        'username'         : 'user',
        'password'         : 'pass',
        'auth'             : 'user:pass',
        'netloc'           : 'user:pass@www.site.com',
        'path'             : '/folder/index.php',
        'directory'        : '/folder',
        'filename'         : 'index.php',
        'filebase'         : 'index',
        'minimal_filebase' : 'index',
        'extension'        : '.php',
        'all_extensions'   : '.php',
        'query'            : 'param=value',
        'query_char'       : '?',
        'query_params'     : { 'param' : 'value' },
    },

    # Simple http url with double extension.
    {
        'url'              : 'http://www.google.com@www.example.com:8080/malware.pdf.exe',
        'request_uri'      : '/malware.pdf.exe',
        'scheme'           : 'http',
        'host'             : 'www.example.com',
        'port'             : 8080,
        'username'         : 'www.google.com',
        'password'         : '',
        'auth'             : 'www.google.com',
        'netloc'           : 'www.google.com@www.example.com:8080',
        'path'             : '/malware.pdf.exe',
        'directory'        : '/',
        'filename'         : 'malware.pdf.exe',
        'filebase'         : 'malware.pdf',
        'minimal_filebase' : 'malware',
        'extension'        : '.exe',
        'all_extensions'   : '.pdf.exe',
        'query'            : '',
        'query_char'       : '?',
        'query_params'     : {},
    },

    # Simple https url.
    {
        'url'              : 'https://www.example.com/',
        'request_uri'      : '/',
        'scheme'           : 'https',
        'host'             : 'www.example.com',
        'port'             : 443,
        'username'         : '',
        'password'         : '',
        'auth'             : '',
        'netloc'           : 'www.example.com',
        'path'             : '/',
        'directory'        : '/',
        'filename'         : '',
        'filebase'         : '',
        'minimal_filebase' : '',
        'extension'        : '',
        'all_extensions'   : '',
        'query'            : '',
        'query_char'       : '?',
        'query_params'     : {},
    },

    # Simple ftp url.
    {
        'url'              : 'ftp://ftp.example.com/file.txt',
        'request_uri'      : '/file.txt',
        'scheme'           : 'ftp',
        'host'             : 'ftp.example.com',
        'port'             : 21,
        'username'         : '',
        'password'         : '',
        'auth'             : '',
        'netloc'           : 'ftp.example.com',
        'path'             : '/file.txt',
        'directory'        : '/',
        'filename'         : 'file.txt',
        'filebase'         : 'file',
        'minimal_filebase' : 'file',
        'extension'        : '.txt',
        'all_extensions'   : '.txt',
        'query'            : '',
        'query_char'       : '?',
        'query_params'     : {},
    },

    # Simple mailto url.
    {
        'url'              : 'mailto://user@example.com?subject=Hi%21',
        'request_uri'      : '?subject=Hi%21',
        'scheme'           : 'mailto',
        'host'             : 'example.com',
        'port'             : 25,
        'username'         : 'user',
        'password'         : '',
        'auth'             : 'user',
        'netloc'           : 'user@example.com',
        'path'             : '',
        'directory'        : '',
        'filename'         : '',
        'filebase'         : '',
        'minimal_filebase' : '',
        'extension'        : '',
        'all_extensions'   : '',
        'query'            : 'subject=Hi%21',
        'query_char'       : '?',
        'query_params'     : { 'subject' : 'Hi!' },
    },
)

# Test of the URL parser.
def test_url_parser():
    for case in simple:
        url = case['url']
        d = DecomposedURL(url)
        for key, value in case.iteritems():
            try:
                assert getattr(d, key) == value
            except AssertionError:
                print "-" * 79
                print "Failed test case: %r" % url
                print "Attribute name: %r" % key
                print "Expected value: %r" % value
                print "Got instead:    %r" % getattr(d, key)
                print "-" * 79
                raise


# Run all tests from the command line.
if __name__ == "__main__":
    test_url_parser()
