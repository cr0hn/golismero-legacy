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


# Imports.
from golismero.api.data.information.http import HTTP_Headers, HTTP_Request, HTTP_Response


# Test cases for HTTP headers.
cases_http_headers = (

    ("normal HTTP headers",
     ("Host: www.example.com\r\n"
      "Connection: keep-alive\r\n"
      "Content-Length: 0\r\n"
      "Content-Encoding: plain\r\n"
      "Transport-Encoding: plain\r\n"
      "Pragma: no-cache\r\n"
      "\r\n"),
     (("Host", "www.example.com"),
      ("Connection", "keep-alive"),
      ("Content-Length", "0"),
      ("Content-Encoding", "plain"),
      ("Transport-Encoding", "plain"),
      ("Pragma", "no-cache")),
     {"host": "www.example.com",
      "connection": "keep-alive",
      "content-length": "0",
      "content-encoding": "plain",
      "transport-encoding": "plain",
      "pragma": "no-cache"}
    ),

    ("multiline HTTP headers",
     ("Host: www.example.com\r\n"
      "Set-Cookie: example=true,\r\n"
      "            multiline=true\r\n"
      "Location: http://www.example.com/index.php\r\n"
      "\r\n"),
     (("Host", "www.example.com"),
      ("Set-Cookie", "example=true, multiline=true"),
      ("Location", "http://www.example.com/index.php")),
     {"host": "www.example.com",
      "set-cookie": "example=true, multiline=true",
      "location": "http://www.example.com/index.php"}
    ),

    ("duplicated HTTP headers",
     ("Host: www.example.com\r\n"
      "Set-Cookie: example=true\r\n"
      "Set-Cookie: duplicated=true\r\n"
      "Location: http://www.example.com/index.php\r\n"
      "\r\n"),
     (("Host", "www.example.com"),
      ("Set-Cookie", "example=true"),
      ("Set-Cookie", "duplicated=true"),
      ("Location", "http://www.example.com/index.php")),
     {"host": "www.example.com",
      "set-cookie": "example=true, duplicated=true",
      "location": "http://www.example.com/index.php"}
    ),

    ("broken HTTP headers",
     ("Host: www.example.com\r\n"
      "Set-Cookie: example=true\r\n"
      "\r\n"
      "Location: http://www.example.com/index.php\r\n"
      "\r\n"),
     (("Host", "www.example.com"),
      ("Set-Cookie", "example=true")),
     {"host": "www.example.com",
      "set-cookie": "example=true"}
    ),

    ("HTTP headers with extra whitespace",
     ("Host  \t  :   \t   www.example.com   \t   \r\n"
      "X-Whatever::::: ::::: some data goes here \r\n"
      "\t   and here too   \r\n"
      "Set-Cookie: example=true,   \t   \r\n"
      "     \t        multiline=true  \t  \r\n"
      "Set-Cookie:  \t   duplicated=true  \t \r\n"
      "Pragma: no-cache\r\n"
      "\r\n"),
     (("Host", "www.example.com"),
      ("X-Whatever", ":::: ::::: some data goes here and here too"),
      ("Set-Cookie", "example=true, multiline=true"),
      ("Set-Cookie", "duplicated=true"),
      ("Pragma", "no-cache")),
     {"host": "www.example.com",
      "x-whatever": ":::: ::::: some data goes here and here too",
      "set-cookie": "example=true, multiline=true, duplicated=true",
      "pragma": "no-cache"}
    ),
)


# This tests the HTTP headers parser.
def test_http_headers():
    for title, raw_headers, original, parsed in cases_http_headers:
        print "Testing " + title
        headers = HTTP_Headers(raw_headers)
        assert str(headers) == raw_headers
        assert headers.to_tuple() == original
        assert headers.to_dict() == parsed


# This tests the HTTP request parser.
def test_http_request():

    # TODO

    pass


# This tests the HTTP response parser.
def test_http_response():

    # TODO

    pass


# Run all tests from the command line.
if __name__ == "__main__":
    test_http_headers()
    test_http_request()
    test_http_response()
