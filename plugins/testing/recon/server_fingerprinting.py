#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
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

from golismero.api.logger import Logger
from golismero.api.net.protocol import *
from golismero.api.plugin import TestingPlugin
from golismero.api.data.resource.baseurl import BaseUrl
from golismero.api.text.wordlist_api import WordListAPI
from golismero.api.config import Config
from collections import Counter
from urlparse import urljoin

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
        return [BaseUrl.RESOURCE_BASE_URL]


    #----------------------------------------------------------------------
    def recv_info(self, info):
        if not isinstance(info, BaseUrl):
            raise TypeError("Expected Url, got %s instead" % type(info))

        main_server_fingerprint(info)

        return


#----------------------------------------------------------------------
def main_server_fingerprint(base_url):
    """
    Main function for server fingerprint. Get an URL and return the fingerprint results.

    :param base_url: Domain resource instance.
    :type base_url: Domain

    :return: Fingerprint type
    """

    m_main_url = base_url.url

    # Load wordlist directly related with a HTTP fields.
    # { HTTP_HEADER_FIELD : [wordlists] }
    m_wordlists_HTTP_fields = {
        "Accept-Ranges"              : [ "accept-range" ],
        "Server"                     : [ "banner" ],
        "Cache-Control"              : [ "cache-control" ],
        "Connection"                 : [ "connection" ],
        "Content-Type"               : [ "content-type" ],
        "ETag"                       : [ "etag-quotes", "etag-legth" ],
        "WWW-Authenticate"           : [ "htaccess-realm" ],
        "Pragma"                     : [ "pragma" ],
        "Vary"                       : [ "vary-order", "vary-capitalize", "vary-delimiter" ],
        "X-Powered-By"               : [ "x-powered-by" ]
    }

    # Wordlists not directly related with HTTP fields.
    m_wordlists_HTTP_properties = [
        "header-capitalafterdash",
        "header-order",
        "header-space",
        "statuscode",
        "statustext",
        "protocol-name",
        "protocol-version "
    ]


    # Wordlists for each type of action
    m_wordlist_types = [
        "Wordlist_Get"
    ]

    m_actions = {
        'GET'        : { 'method' : 'GET'      , 'payload': '/' },
        'LONG_GET'   : { 'method' : 'GET'      , 'payload': '%s%s' % ('/', 'a' * 200) },
        'NOT_FOUND'  : { 'method' : 'GET'      , 'payload': '/404_NOFOUND__X02KAS' },
        'HEAD'       : { 'method' : 'HEAD'     , 'payload': '/' },
        'OPTIONS'    : { 'method' : 'OPTIONS'  , 'payload': '/' },
        'DELETE'     : { 'method' : 'DELETE'   , 'payload': '/' },
        'TEST'       : { 'method' : 'TEST'     , 'payload': '/' },
        'ATTACK'     : { 'method' : 'GET'      , 'payload': "/etc/passwd?format=%%%%&xss=\x22><script>alert('xss');</script>&traversal=../../&sql='%20OR%201;"}
    }

    # Get a connection pool
    m_conn = NetworkAPI.get_connection()

    #
    # Store structures. Format:
    #
    # { SERVER_NAME: int }
    #
    # Where:
    # - SERVER_NAME -> Discovered server name
    # - int         -> Number of wordlist that matches this server
    #
    # Store results for HTTP directly related fields
    m_results_http_fields = Counter()
    # Store results for others HTTP params
    m_results_http_others = {}

    # start
    # Do the actions
    for m, v in m_actions.iteritems():
        l_method  = v["method"]
        l_payload = v["payload"]

        # Make the URL
        l_url     = urljoin(m_main_url, l_payload)

        # Do the connection
        l_response = None
        try:
            l_response = m_conn.get( l_url,
                                     method=l_method,
                                     follow_redirect=True,
                                     cache=True)
        except NetworkException,e:
            Logger.log_more_verbose("Server-Fingerprint plugin: No response for URL '%s'. Message: " % (l_url, e.message))
            continue

        if not l_response:
            Logger.log_more_verbose("No response for URL '%s'." % l_url)
            continue

        # Analyze for each wordlist
        for w_t in m_wordlist_types:

            #
            # HTTP directly related
            #
            for l_http_header_name, l_wordlists in m_wordlists_HTTP_fields.iteritems():

                # Check if HTTP header field is in response
                if l_http_header_name not in l_response.http_headers:
                    continue

                # Generate concrete wordlist name
                for l_w in l_wordlists:
                    l_wordlist_path     = Config.plugin_extra_config[w_t][l_w]

                    # Load words for the wordlist
                    l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(l_wordlist_path)

                    # Looking for matches
                    l_matches           = l_wordlist_instance.matches_by_value(l_http_header_name)

                    if l_matches:
                        for server in l_matches:
                            m_results_http_fields[server] += 1

            #
            # HTTP INdirectly related
            #
            for l_val in m_wordlists_HTTP_properties:
                pass


