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
from warnings import catch_warnings


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
        'subdomain'        : 'www',
        'domain'           : 'site',
        'tld'              : 'com',
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
        'subdomain'        : 'www',
        'domain'           : 'example',
        'tld'              : 'com',
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
        'subdomain'        : 'www',
        'domain'           : 'example',
        'tld'              : 'com',
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
        'subdomain'        : 'ftp',
        'domain'           : 'example',
        'tld'              : 'com',
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
        'subdomain'        : '',
        'domain'           : 'example',
        'tld'              : 'com',
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

    # Localhost url.
    {
        'url'              : 'http://localhost:1234/',
        'request_uri'      : '/',
        'scheme'           : 'http',
        'host'             : 'localhost',
        'port'             : 1234,
        'username'         : '',
        'password'         : '',
        'auth'             : '',
        'netloc'           : 'localhost:1234',
        'subdomain'        : '',
        'domain'           : 'localhost',
        'tld'              : '',
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


# Some manual testing.
def test_url_parser_custom():

    # Relative URLs.
    assert DecomposedURL("/index.html", base_url="http://www.example.com").url == "http://www.example.com/index.html"
    assert DecomposedURL("index.html", base_url="http://www.example.com/folder/").url == "http://www.example.com/folder/index.html"
    assert DecomposedURL("index.html", base_url="http://www.example.com/folder").url == "http://www.example.com/index.html"

    # Setters.
    d = DecomposedURL("http://www.example.com")
    assert d.path == "/"
    d.path = "/index.html"
    assert d.url == "http://www.example.com/index.html"
    assert d.path == "/index.html"
    assert d.port == 80
    d.scheme = "https"
    assert d.url == "https://www.example.com/index.html"
    assert d.port == 443
    d.port = 8080
    assert d.port == 8080
    assert d.url == "https://www.example.com:8080/index.html"
    d.scheme = "http://"
    assert d.port == 8080
    assert d.url == "http://www.example.com:8080/index.html"
    d.port = None
    assert d.port == 80
    assert d.url == "http://www.example.com/index.html"
    d.path = "index.html"
    assert d.path == "/index.html"
    assert d.url == "http://www.example.com/index.html"
    d.host = "www.site.com"
    assert d.url == "http://www.site.com/index.html"
    d.netloc = "user:pass@www.site.com"
    assert d.url == "http://user:pass@www.site.com/index.html"
    assert d.username == "user"
    assert d.password == "pass"
    d.username = "someone"
    assert d.url == "http://someone:pass@www.site.com/index.html"
    assert d.netloc == "someone:pass@www.site.com"
    d.password = "secret"
    assert d.url == "http://someone:secret@www.site.com/index.html"
    assert d.netloc == "someone:secret@www.site.com"
    assert d.auth == "someone:secret"
    d.password = None
    assert d.url == "http://someone@www.site.com/index.html"
    assert d.netloc == "someone@www.site.com"
    assert d.auth == "someone"
    d.password = "secret"
    assert d.url == "http://someone:secret@www.site.com/index.html"
    assert d.netloc == "someone:secret@www.site.com"
    assert d.auth == "someone:secret"
    d.username = None
    assert d.url == "http://:secret@www.site.com/index.html"
    assert d.netloc == ":secret@www.site.com"
    assert d.auth == ":secret"
    d.auth = "test:key"
    assert d.url == "http://test:key@www.site.com/index.html"
    assert d.netloc == "test:key@www.site.com"
    assert d.username == "test"
    assert d.password == "key"
    d.auth = None
    assert d.url == "http://www.site.com/index.html"
    assert d.netloc == "www.site.com"
    assert d.username == ""
    assert d.password == ""
    d.fragment = "fragment"
    assert d.url == "http://www.site.com/index.html#fragment"
    assert d.fragment == "fragment"
    d.fragment = None
    assert d.url == "http://www.site.com/index.html"
    assert d.fragment == ""
    d.query = "key=value&param=data"
    assert d.url == "http://www.site.com/index.html?key=value&param=data"
    assert d.query_char == "?"
    assert d.query == "key=value&param=data"
    assert d.query_params == { "key": "value", "param": "data" }
    d.query_params["test"] = "me"
    assert d.url == "http://www.site.com/index.html?key=value&param=data&test=me"
    assert d.query == "key=value&param=data&test=me"
    assert d.query_params == { "key": "value", "param": "data", "test": "me" }
    d.query_params = { "some": "thing" }
    assert d.url == "http://www.site.com/index.html?some=thing"
    assert d.query == "some=thing"
    assert d.query_params == { "some": "thing" }
    d.query = "a=b&c"
    assert d.url == "http://www.site.com/index.html?a=b&c="
    assert d.query == "a=b&c="
    assert d.query_params == { "a": "b", "c": "" }
    d.query = "teststring".encode("rot13")
    assert d.url == "http://www.site.com/index.html?" + "teststring".encode("rot13")
    assert d.query == "teststring".encode("rot13")
    assert d.query_params == {}
    d.query = "test string".encode("base64")[:-1]
    assert d.url == "http://www.site.com/index.html?" + "test string".encode("base64")[:-1]
    assert d.query == "test string".encode("base64")[:-1]
    assert d.query_params == {}
    d.query = "test string".encode("base64")
    assert d.url == "http://www.site.com/index.html?" + "test string".encode("base64")[:-1] + "%0A"
    assert d.query == "test string".encode("base64")[:-1] + "%0A"
    assert d.query_params == {"test string".encode("base64")[:-2]: "\n"}
    d.query = "test=me"
    d.query_char = "/"
    assert d.url == "http://www.site.com/index.html/test=me"
    assert d.query_char == "/"
    assert d.query == "test=me"
    assert d.query_params == { "test": "me" }
    d.fragment = "frag"
    assert d.url == "http://www.site.com/index.html/test=me#frag"

    # Methods.
    d.hostname = "this.is.a.subdomain.of.example.co.uk"
    assert ".".join(d.split_hostname()) == d.host
    assert d.split_hostname() == ("this.is.a.subdomain.of", "example", "co.uk")
    d.path = "/folder.with.extensions/file.pdf.exe"
    assert d.get_all_extensions(directory_allowed = False, double_allowed = True)  == [".pdf", ".exe"]
    assert d.get_all_extensions(directory_allowed = True,  double_allowed = True)  == [".with", ".extensions", ".pdf", ".exe"]
    assert d.get_all_extensions(directory_allowed = False, double_allowed = False) == [".exe"]
    assert d.get_all_extensions(directory_allowed = True,  double_allowed = False) == [".extensions", ".exe"]
    assert d.get_all_extensions(directory_allowed = False                        ) == [".pdf", ".exe"]
    assert d.get_all_extensions(                           double_allowed = False) == [".extensions", ".exe"]
    assert d.get_all_extensions(                                                 ) == [".with", ".extensions", ".pdf", ".exe"]

    # Exceptions.
    last_url = d.url
    try:
        d.query_char = "*"
        assert False
    except ValueError:
        pass
    try:
        d.scheme = "fake://"
        assert False
    except ValueError:
        pass
    try:
        d.port = "fake"
        assert False
    except ValueError:
        pass
    try:
        d.port = -1
        assert False
    except ValueError:
        pass
    try:
        d.port = 80000
        assert False
    except ValueError:
        pass
    assert d.url == last_url

    # Warnings.
    with catch_warnings(record=True) as w:
        d.fragment = "#test"
        d.query = "?test=me"
    assert len(w) == 2


# Run all tests from the command line.
if __name__ == "__main__":
    test_url_parser()
    test_url_parser_custom()
