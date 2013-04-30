#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

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

from golismero.api.logger import Logger
from golismero.api.net.protocol import NetworkAPI
from golismero.api.plugin import TestingPlugin
from golismero.api.data.resource.domain import Domain
from golismero.api.data.vulnerability.information_disclosure.url_suspicious import SuspiciousURL
from golismero.api.text.wordlist_api import WordListAPI
from golismero.api.config import Config

#
# !!!!!!!!!!!!!
#
# Fingerprint techniques are based on the fantastic paper of httprecon project, and their databases:
#
# Doc: http://www.computec.ch/projekte/httprecon/?s=documentation
# Project page: http://www.computec.ch/projekte/httprecon
#
# !!!!!!!!!!!!!
#
#
# This plugin try to a fingerprinting over web servers.
#
# Step 1
# ======
# Define the methods used:
# 1 - Check de Banner.
# 2 - Check de order headers in HTTP response.
# 3 - Check the rest of headers.
#
# Step 2
# ======
# Then assigns a weight to each method:
# 1 -> 50%
# 2 -> 20%
# 3 -> 30% (divided by the number of test for each header)
#
# Step 3
# ======
# We have 9 request with:
# 1 - GET / HTTP/1.1
# 2 - GET /index.php HTTP/1.1
# 3 - GET /404_file.html HTTP/1.1
# 4 - HEAD / HTTP/1.1
# 5 - OPTIONS / HTTP/1.1
# 6 - DELETE / HTTP/1.1
# 7 - TEST / HTTP/1.1
# 8 - GET / 9.8
# 9 - GET /<SCRIPT>alert</script> HTTP/1.1 -> Any web attack.
#
# Step 4
# ======
# For each type of response analyze the HTTP headers trying to find matches and
# multiply for their weight.
#
# Step 5
# ======
# Sum de values obtained in step 4, for each test in step 3.
#
# Step 6
# ======
# Get the 3 highter values os matching.
#
#
# For example
# ===========
# For an Apache 1.3.26 we will have these results for a normal GET:
#
# Banner (any of these options):
# ++++ Apache/1.3.26 (Linux/SuSE) mod_ssl/2.8.10 OpenSSL/0.9.6g PHP/4.2.2
# ++++ Apache/1.3.26 (UnitedLinux) mod_python/2.7.8 Python/2.2.1 PHP/4.2.2 mod_perl/1.27
# ++++ Apache/1.3.26 (Unix)
# ++++ Apache/1.3.26 (Unix) Debian GNU/Linux mod_ssl/2.8.9 OpenSSL/0.9.6g PHP/4.1.2 mod_webapp/1.2.0-dev
# ++++ Apache/1.3.26 (Unix) Debian GNU/Linux PHP/4.1.2
# ++++ Apache/1.3.26 (Unix) mod_gzip/1.3.19.1a PHP/4.3.11 mod_ssl/2.8.9 OpenSSL/0.9.6
# ++++ MIT Web Server Apache/1.3.26 Mark/1.5 (Unix) mod_ssl/2.8.9 OpenSSL/0.9.7c
#
# - A specific order for the rest of HTTP headers (any of these options):
# ++++ Date,Server,Accept-Ranges,Content-Type,Content-Length,Via
# ++++ Date,Server,Connection,Content-Type
# ++++ Date,Server,Keep-Alive,Connection,Transfer-Encoding,Content-Type
# ++++ Date,Server,Last-Modified,ETag,Accept-Ranges,Content-Length,Connection,Content-Type
# ++++ Date,Server,Last-Modified,ETag,Accept-Ranges,Content-Length,Keep-Alive,Connection,Content-Type
# ++++ Date,Server,Set-Cookie,Content-Type,Set-Cookie,Keep-Alive,Connection,Transfer-Encoding
# ++++ Date,Server,X-Powered-By,Keep-Alive,Connection,Transfer-Encoding,Content-Type
# ++++ Date,Server,X-Powered-By,Set-Cookie,Expires,Cache-Control,Pragma,Set-Cookie,Set-Cookie,Keep-Alive,Connection,Transfer-Encoding,Content-Type
# ++++ Date,Server,X-Powered-By,Set-Cookie,Set-Cookie,Expires,Last-Modified,Cache-Control,Pragma,Keep-Alive,Connection,Transfer-Encoding,Content-Type
#
# - The value of the rest of headers must be:
# ** Content-Type (any of these options):
# +++++ text/html
# +++++ text/html; charset=iso-8859-1
# +++++ text/html;charset=ISO-8859-1
#
# ** Cache-Control (any of these options):
# ++++ no-store, no-cache, must-revalidate, post-check=0, pre-check=0
# ++++ post-check=0, pre-check=0
#
# ** Connection (any of these options):
# ++++ close
# ++++ Keep-Alive
#
# ** Quotes types must be double for ETag field:
# ++++ ETag: "0", instead of ETag: '0'
#
# ** E-Tag length (any of these options):
# ++++ 0
# ++++ 20
# ++++ 21
# ++++ 23
#
# ** Pragma (any of these options):
# ++++ no-cache
#
# ** Format of headers. After a bash, the letter is uncapitalized, for http headers. For example:
# ++++ Content-type, instead of Content-**T**ype.
#
# ** Has spaces between names and values. For example:
# ++++ E-Tag:0; instead of: E-Tag:0
#
# ** Protocol name used in request is 'HTTP'. For example:
# ++++ GET / HTTP/1.1
#
# ** The status text for a response of HTTP.
#     GET / HTTP/1.1
#     Host: misite.com
#
#     HTTP/1.1 200 **OK**
#     ....
#
# ** X-Powered-By (any of these options):
# ++++ PHP/4.1.2
# ++++ PHP/4.2.2
# ++++ PHP/4.3.11
#

class ServerFingerprinting(TestingPlugin):
    """
    Does fingerprinting tests
    """


    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        pass


    #----------------------------------------------------------------------
    def display_help(self):
        # TODO: this could default to the description found in the metadata.
        return self.__doc__


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [Domain.data_type]


    #----------------------------------------------------------------------
    def recv_info(self, info):

        if not isinstance(info, Domain):
            raise TypeError("Expected Domain, got %s instead" % type(info))

        return
        # Load wordlists
        m_wordlist = WordListAPI().get_wordlist(Config.plugin_config['Wordlists'])

        #

        return