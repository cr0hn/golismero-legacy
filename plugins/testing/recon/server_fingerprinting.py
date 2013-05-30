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
from golismero.api.text.matching_analyzer import get_matching_level
from golismero.api.net.web_utils import is_in_scope, DecomposedURL
from golismero.api.net.scraper import extract_from_html
from golismero.api.data.information.webserver_fingerprint import WebServerFingerprint
from repoze.lru import lru_cache
from ping import *

from collections import Counter, OrderedDict
from urlparse import urljoin
from re import compile

SERVER_PATTERN = compile("([\w\W\s\d]+)[\s\/]+([\d\w\.]+)")


__doc__="""

Fingerprint techniques are based on the fantastic paper of httprecon project, and their databases:

- Doc: http://www.computec.ch/projekte/httprecon/?s=documentation
- Project page: http://www.computec.ch/projekte/httprecon


This plugin try to a fingerprinting over web servers.

Step 1
------

Define the methods used:

1 Check de Banner.
2 Check de order headers in HTTP response.
3 Check the rest of headers.


Step 2
------

Then assigns a weight to each method:

1. -> 50%
2. -> 20%
3. -> 30% (divided by the number of test for each header)


Step 3
------

We have 9 request with:

1. GET / HTTP/1.1
2. GET /index.php HTTP/1.1
3. GET /404_file.html HTTP/1.1
4. HEAD / HTTP/1.1
5. OPTIONS / HTTP/1.1
6. DELETE / HTTP/1.1
7. TEST / HTTP/1.1
8. GET / 9.8
9. GET /<SCRIPT>alert</script> HTTP/1.1 -> Any web attack.

Step 4
------

For each type of response analyze the HTTP headers trying to find matches and
multiply for their weight.

Step 5
------

Sum de values obtained in step 4, for each test in step 3.

Step 6
------

Get the 3 highter values os matching.


For example
-----------

For an Apache 1.3.26 we will have these results for a normal GET:

- Banner (any of these options):

 + Apache/1.3.26 (Linux/SuSE) mod_ssl/2.8.10 OpenSSL/0.9.6g PHP/4.2.2
 + Apache/1.3.26 (UnitedLinux) mod_python/2.7.8 Python/2.2.1 PHP/4.2.2 mod_perl/1.27
 + Apache/1.3.26 (Unix)
 + Apache/1.3.26 (Unix) Debian GNU/Linux mod_ssl/2.8.9 OpenSSL/0.9.6g PHP/4.1.2 mod_webapp/1.2.0-dev
 + Apache/1.3.26 (Unix) Debian GNU/Linux PHP/4.1.2
 + Apache/1.3.26 (Unix) mod_gzip/1.3.19.1a PHP/4.3.11 mod_ssl/2.8.9 OpenSSL/0.9.6
 + MIT Web Server Apache/1.3.26 Mark/1.5 (Unix) mod_ssl/2.8.9 OpenSSL/0.9.7c

- A specific order for the rest of HTTP headers (any of these options):

 + Date,Server,Accept-Ranges,Content-Type,Content-Length,Via
 + Date,Server,Connection,Content-Type
 + Date,Server,Keep-Alive,Connection,Transfer-Encoding,Content-Type
 + Date,Server,Last-Modified,ETag,Accept-Ranges,Content-Length,Connection,Content-Type
 + Date,Server,Last-Modified,ETag,Accept-Ranges,Content-Length,Keep-Alive,Connection,Content-Type
 + Date,Server,Set-Cookie,Content-Type,Set-Cookie,Keep-Alive,Connection,Transfer-Encoding
 + Date,Server,X-Powered-By,Keep-Alive,Connection,Transfer-Encoding,Content-Type
 + Date,Server,X-Powered-By,Set-Cookie,Expires,Cache-Control,Pragma,Set-Cookie,Set-Cookie,Keep-Alive,Connection,Transfer-Encoding,Content-Type
 + Date,Server,X-Powered-By,Set-Cookie,Set-Cookie,Expires,Last-Modified,Cache-Control,Pragma,Keep-Alive,Connection,Transfer-Encoding,Content-Type

- The value of the rest of headers must be:

 * Content-Type (any of these options):

  + text/html
  + text/html; charset=iso-8859-1
  + text/html;charset=ISO-8859-1

 * Cache-Control (any of these options):

  + no-store, no-cache, must-revalidate, post-check=0, pre-check=0
  + post-check=0, pre-check=0

 * Connection (any of these options):

  + close
  + Keep-Alive

 * Quotes types must be double for ETag field:

  + ETag: "0", instead of ETag: '0'

 * E-Tag length (any of these options):

  + 0
  + 20
  + 21
  + 23

 * Pragma (any of these options):

  + no-cache

 * Format of headers. After a bash, the letter is uncapitalized, for http headers. For example:

  + Content-type, instead of Content-\*\*T\*\*ype.

 * Has spaces between names and values. For example:

  + E-Tag:0; instead of: E-Tag:0

 * Protocol name used in request is 'HTTP'. For example:

  + GET / HTTP/1.1

 * The status text for a response of HTTP.

   GET / HTTP/1.1
   Host: misite.com

   HTTP/1.1 200 \*\*OK\*\*
   \.\.\.\.

 * X-Powered-By (any of these options):

  + PHP/4.1.2
  + PHP/4.2.2
  + PHP/4.3.11
"""

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

		return main_server_fingerprint(info)




#----------------------------------------------------------------------
def main_server_fingerprint(base_url):
	"""
	Main function for server fingerprint. Get an URL and return the fingerprint results.

	:param base_url: Domain resource instance.
	:type base_url: Domain

	:return: Fingerprint type
	"""
	#return
	m_main_url = base_url.url

	Logger.log_more_verbose("Starting fingerprinting plugin for site: %s" % m_main_url)

	# Get a connection pool
	m_conn = NetworkAPI.get_connection()

	#
	# Detect the platform: Windows or *NIX
	#
	#basic_platform_detection(m_main_url, m_conn)
	m_platform = ttl_platform_detection(DecomposedURL(m_main_url).hostname)
	if m_platform:
		Logger.log_more_verbose("Fingerprint - Plaform: %s" % ','.join(m_platform.keys()))

	#
	# Analyze HTTP protocol
	#
	m_server_name, m_server_version, m_webserver_complete_desc, m_others = http_analyzers(m_main_url, m_conn)

	Logger.log_more_verbose("Fingerprint - Server: %s | Version: %s" % (m_server_name, m_server_version))

	m_return = WebServerFingerprint(m_server_name, m_server_version, m_webserver_complete_desc, m_others)

	# Associate resource
	m_return.add_resource(base_url)

	return [m_return]


#----------------------------------------------------------------------
def basic_platform_detection(main_url, conn):
	"""
	Detect if platform is Windows or \*NIX. To do this, get the first link, in scope, and
	does two resquest. If are the same response, then, platform are Windows. Else are \*NIX.

	:returns: Name of platforms: Windows, \*NIX or unknown.
	:rtype: str
	"""
	m_forbidden = (
		"logout",
		"logoff",
		"exit",
		"sigout",
		"signout",
	)

	# Get the main web page
	m_r     = conn.get(main_url, follow_redirect=True)

	# Get the first link
	m_links = extract_from_html(m_r.information.raw_data, main_url)

	if not m_links:
		return "unknown"

	# Get the first link of page
	m_first_link = None
	for u in m_links:
		if is_in_scope(u) and not any(x in u for x in m_forbidden):
			m_first_link = u
			break

	if not m_first_link:
		return "unknown"

	# Now get two request to the links. One to the original URL and other
	# as upper URL.

	# Original
	m_response_orig  = conn.get(m_first_link)
	# Upper
	m_response_upper = conn.get(m_first_link.upper())
	# Comparte it
	m_match_level    = get_matching_level(m_response_orig.raw_content, m_response_upper.raw_content)

	# If the responses are equals at 90%, two URL are the same => Windows; else => *NIX
	m_return = None
	if m_match_level > 0.95:
		m_return = "Windows"
	else:
		m_return = "*NIX"


	return m_return

#----------------------------------------------------------------------
def http_analyzers(main_url, conn, number_of_entries=4):
	"""
	Analyze HTTP headers for detect the web server. Return a list with most possible web servers.

	:param main_url: Base url to test.
	:type main_url: str

	:param conn: Instance of connection.
	:type conn: Web type connection

	:param number_of_entries: number of resutls tu return for most probable web servers detected.
	:type number_of_entries: int

	:return: Web server family, Web server version, Web server complete description, others web server with their probabilities like: dict(CONCRETE_WEB_SERVER, PROBABILITY)
	"""

	if not isinstance(conn, Web):
		return


	# Load wordlist directly related with a HTTP fields.
	# { HTTP_HEADER_FIELD : [wordlists] }
	m_wordlists_HTTP_fields = {
        "Accept-Ranges"              : "accept-range",
        "Server"                     : "banner",
        "Cache-Control"              : "cache-control",
        "Connection"                 : "connection",
        "Content-Type"               : "content-type",
        "WWW-Authenticate"           : "htaccess-realm",
        "Pragma"                     : "pragma",
        "X-Powered-By"               : "x-powered-by"
    }

	m_actions = {
		'GET'        : { 'wordlist' : 'Wordlist_get'            , 'weight' : 1 , 'protocol' : 'HTTP/1.1', 'method' : 'GET'      , 'payload': '/' },
		'LONG_GET'   : { 'wordlist' : 'Wordlist_get_long'       , 'weight' : 1 , 'protocol' : 'HTTP/1.1', 'method' : 'GET'      , 'payload': '/%s' % ('a' * 200) },
		'NOT_FOUND'  : { 'wordlist' : 'Wordlist_get_notfound'   , 'weight' : 2 , 'protocol' : 'HTTP/1.1', 'method' : 'GET'      , 'payload': '/404_NOFOUND__X02KAS' },
		'HEAD'       : { 'wordlist' : 'Wordlist_head'           , 'weight' : 3 , 'protocol' : 'HTTP/1.1', 'method' : 'HEAD'     , 'payload': '/' },
		'OPTIONS'    : { 'wordlist' : 'Wordlist_options'        , 'weight' : 2 , 'protocol' : 'HTTP/1.1', 'method' : 'OPTIONS'  , 'payload': '/' },
		'DELETE'     : { 'wordlist' : 'Wordlist_delete'         , 'weight' : 5 , 'protocol' : 'HTTP/1.1', 'method' : 'DELETE'   , 'payload': '/' },
		'TEST'       : { 'wordlist' : 'Wordlist_attack'         , 'weight' : 5 , 'protocol' : 'HTTP/1.1', 'method' : 'TEST'     , 'payload': '/' },
		'INVALID'    : { 'wordlist' : 'Wordlist_wrong_method'   , 'weight' : 5 , 'protocol' : 'HTTP/9.8', 'method' : 'GET'      , 'payload': '/' },
		'ATTACK'     : { 'wordlist' : 'Wordlist_wrong_version'  , 'weight' : 2 , 'protocol' : 'HTTP/1.1', 'method' : 'GET'      , 'payload': "/etc/passwd?format=%%%%&xss=\x22><script>alert('xss');</script>&traversal=../../&sql='%20OR%201;"}
	}


	# Store results for others HTTP params
	m_results_http_others = {}
	m_d                   = DecomposedURL(main_url)
	m_hostname            = m_d.hostname
	m_port                = m_d.port
	m_debug               = False # Only for develop

	# Score counter
	m_counters = HTTPAnalyzer(debug=m_debug)

	for l_action, v in m_actions.iteritems():
		if m_debug:
			print "###########"
		l_method      = v["method"]
		l_payload     = v["payload"]
		l_proto       = v["protocol"]
		l_wordlist    = v["wordlist"]

		# Each type of probe hast different weight.
		#
		# Weights go from 0 - 5
		#
		l_weight      = v["weight"]

		# Make the URL
		l_url         = urljoin(main_url, l_payload)

		# Make the raw request
		#l_raw_request = "%(method)s %(payload)s %(protocol)s\r\nHost: %(host)s:%(port)s\r\nConnection: Close\r\n\r\n" % (
		l_raw_request = "%(method)s %(payload)s %(protocol)s\r\nHost: %(host)s\r\n\r\n" % (
			{
				"method"     : l_method,
				"payload"    : l_payload,
				"protocol"   : l_proto,
				"host"       : m_hostname,
				"port"       : m_port
			}
		)
		if m_debug:
			print "REQUEST"
			print l_raw_request

		# Do the connection
		l_response = None
		try:
			# PONER AQUI LA PETICION CON GET_RAW
			l_response = conn.get_raw( host            = m_hostname,
						               port            = m_port,
						               request_content = l_raw_request,
						               cache           = True)
		except NetworkException,e:
			Logger.log_error_more_verbose("Server-Fingerprint plugin: No response for URL (%s) '%s'. Message: %s" % (l_method, l_url, e.message))
			continue

		if not l_response:
			Logger.log_error_more_verbose("No response for URL '%s'." % l_url)
			continue
		l_original_headers = {v.split(":")[0]:v.split(":")[1] for v in l_response.http_headers_raw.splitlines()}


		if m_debug:
			print "RESPONSE"
			print l_response.http_headers_raw

		# Analyze for each wordlist
		#

		#
		# =====================
		# HTTP directly related
		# =====================
		#
		#
		for l_http_header_name, l_header_wordlist in m_wordlists_HTTP_fields.iteritems():

			# Check if HTTP header field is in response
			if l_http_header_name not in l_response.http_headers:
				continue

			l_curr_header_value = l_response.http_headers.get(l_http_header_name)

			# Generate concrete wordlist name
			l_wordlist_path     = Config.plugin_extra_config[l_wordlist][l_header_wordlist]

			# Load words for the wordlist
			l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(l_wordlist_path)
			# Looking for matches
			l_matches           = l_wordlist_instance.matches_by_value(l_curr_header_value)

			m_counters.inc(l_matches, l_action, l_weight, l_http_header_name, message="HTTP field: " + l_curr_header_value)

		#
		# =======================
		# HTTP INdirectly related
		# =======================
		#
		#

		#
		# Status code
		# ===========
		#
		l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["statuscode"])
		# Looking for matches
		l_matches           = l_wordlist_instance.matches_by_value(l_response.http_response_code)

		m_counters.inc(l_matches, l_action, l_weight, "statuscode", message="Status code: " + str(l_response.http_response_code))


		#
		# Status text
		# ===========
		#
		l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["statustext"])
		# Looking for matches
		l_matches           = l_wordlist_instance.matches_by_value(l_response.http_response_reason)

		m_counters.inc(l_matches, l_action, l_weight, "statustext", message="Status text: " + l_response.http_response_reason)


		#
		# Header space
		# ============
		#
		# Count the number of spaces between HTTP field name and their value, for example:
		# -> Server: Apache 1
		# The number of spaces are: 1
		#
		# -> Server:Apache 1
		# The number of spaces are: 0
		#
		l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["header-space"])
		# Looking for matches
		try:
			l_http_value        = l_response.http_headers_raw.splitlines()[0].split(":")[1] # get the value of first HTTP field
			l_spaces_num        = str(abs(len(l_http_value) - len(l_http_value.lstrip())))
			l_matches           = l_wordlist_instance.matches_by_value(l_spaces_num)

			m_counters.inc(l_matches, l_action, l_weight, "header-space", message="Header space: " + l_spaces_num)

		except IndexError:
			print "index error header space"
			pass


		#
		# Header capitalafterdash
		# =======================
		#
		# Look for non capitalized first letter of field name, for example:
		# -> Content-type: ....
		# Instead of:
		# -> Content-Type: ....
		#
		l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["header-capitalafterdash"])
		# Looking for matches
		l_original_headers = {v.split(":")[0]:v.split(":")[1] for v in l_response.http_headers_raw.splitlines()}
		l_valid_fields     = [x for x in l_original_headers if "-" in x]

		if l_valid_fields:

			l_h = l_valid_fields[0]

			l_value = l_h.split("-")[1] # Get the second value: Content-type => type
			l_dush  = None

			if l_value[0].isupper(): # Check first letter is lower
				l_dush = 1
			else:
				l_dush = 0

			l_matches           = l_wordlist_instance.matches_by_value(l_dush)
			m_counters.inc(l_matches, l_action, l_weight, "header-capitalizedafterdush", message="Capital after dash: %s" % str(l_dush))

		#
		# Header order
		# ============
		#
		l_header_order  = ','.join(v.split(":")[0] for v in l_response.http_headers_raw.splitlines())

		l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["header-order"])
		l_matches           = l_wordlist_instance.matches_by_value(l_header_order)

		m_counters.inc(l_matches, l_action, l_weight, "header-order", message="Header order: " + l_header_order)


		#
		# Protocol name
		# ============
		#
		# For a response like:
		# -> HTTP/1.0 200 OK
		#    ....
		#
		# Get the 'HTTP' value.
		#
		try:
			l_proto             = l_response.raw_response.splitlines()[0][:4] # Get de 'HTTP' text from response, if available
			if l_proto:
				l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["protocol-name"])
				l_matches           = l_wordlist_instance.matches_by_value(l_proto)

				m_counters.inc(l_matches, l_action, l_weight, "proto-name", message="Proto name: " + l_proto)

		except IndexError:
			print "index error protocol name"
			pass


		#
		# Protocol version
		# ================
		#
		# For a response like:
		# -> HTTP/1.0 200 OK
		#    ....
		#
		# Get the '1.0' value.
		#
		try:
			l_version           = l_response.raw_response.splitlines()[0][5:8] # Get de '1.0' text from response, if available
			if l_version:
				l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["protocol-version"])
				l_matches           = l_wordlist_instance.matches_by_value(l_version)

				m_counters.inc(l_matches, l_action, l_weight, "proto-version", message="Proto version: " + l_version)

		except IndexError:
			print "index error protocol version"
			pass



		if "ETag" in l_response.http_headers:
			l_etag_header       = l_response.http_headers.get("ETag")
			#
			# ETag length
			# ================
			#
			l_etag_len          = len(l_etag_header)
			l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["etag-legth"])
			l_matches           = l_wordlist_instance.matches_by_value(l_etag_len)

			m_counters.inc(l_matches, l_action, l_weight, "etag-length", message="ETag length: " + str(l_etag_len))


			#
			# ETag Quotes
			# ================
			#
			l_etag_striped          = l_etag_header.strip()
			if l_etag_striped.startswith("\"") or l_etag_striped.startswith("'"):
				l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["etag-quotes"])
				l_matches           = l_wordlist_instance.matches_by_value(l_etag_striped[0])

				m_counters.inc(l_matches, l_action, l_weight, "etag-qoutes", message="Etag quotes: " + l_etag_striped[0])

		if "Vary" in l_response.http_headers:
			l_vary_header       = l_response.http_headers.get("Vary")
			#
			# Vary delimiter
			# ================
			#
			# Checks if Vary header delimiter is something like this:
			# -> Vary: Accept-Encoding,User-Agent
			# Or this:
			# -> Vary: Accept-Encoding, User-Agent
			#
			l_var_delimiter     = ", " if l_vary_header.find(", ") else ","
			l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["vary-delimiter"])
			l_matches           = l_wordlist_instance.matches_by_value(l_var_delimiter)

			m_counters.inc(l_matches, l_action, l_weight, "vary-delimiter", message="Vary delimiter: " + l_var_delimiter)

			#
			# Vary capitalizer
			# ================
			#
			# Checks if Vary header delimiter is something like this:
			# -> Vary: Accept-Encoding,user-Agent
			# Or this:
			# -> Vary: accept-encoding,user-agent
			#
			l_vary_capitalizer  = str(0 if l_vary_header == l_vary_header.lower() else 1)
			l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["vary-capitalize"])
			l_matches           = l_wordlist_instance.matches_by_value(l_vary_capitalizer)

			m_counters.inc(l_matches, l_action, l_weight, "vary-capitalize", message="Vary capitalizer: " + l_vary_capitalizer)


			#
			# Vary order
			# ================
			#
			# Checks order between vary values:
			# -> Vary: Accept-Encoding,user-Agent
			# Or this:
			# -> Vary: User-Agent,Accept-Encoding
			#
			l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["vary-order"])
			l_matches           = l_wordlist_instance.matches_by_value(l_vary_header)

			m_counters.inc(l_matches, l_action, l_weight, "vary-order", message="Vary order: " + l_vary_header)


		#
		# =====================
		# HTTP specific options
		# =====================
		#
		#
		if l_action == "HEAD":
			#
			# HEAD Options
			# ============
			#
			l_option            = l_response.http_headers.get("Allow")
			if l_option:
				l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["options-public"])
				# Looking for matches
				l_matches           = l_wordlist_instance.matches_by_value(l_option)

				m_counters.inc(l_matches, l_action, l_weight, "options-allow", message="HEAD option: " + l_option)


		if l_action == "OPTIONS" or l_action == "INVALID" or l_action == "DELETE":
			if "Allow" in l_response.http_headers:
				#
				# Options allow
				# =============
				#
				l_option            = l_response.http_headers.get("Allow")
				if l_option:
					l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["options-public"])
					# Looking for matches
					l_matches           = l_wordlist_instance.matches_by_value(l_option)

					m_counters.inc(l_matches, l_action, l_weight, "options-allow", message="OPTIONS allow: "  + l_action + " # " + l_option)


				#
				# Allow delimiter
				# ===============
				#
				l_option            = l_response.http_headers.get("Allow")
				if l_option:
					l_var_delimiter     = ", " if l_option.find(", ") else ","
					l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["options-delimited"])
					# Looking for matches
					l_matches           = l_wordlist_instance.matches_by_value(l_var_delimiter)

					m_counters.inc(l_matches, l_action, l_weight, "options-delimiter", message="OPTION allow delimiter " + l_action + " # " + l_option)


			if "Public" in l_response.http_headers:
				#
				# Public response
				# ===============
				#
				l_option            = l_response.http_headers.get("Public")
				if l_option:
					l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["options-public"])
					# Looking for matches
					l_matches           = l_wordlist_instance.matches_by_value(l_option)

					m_counters.inc(l_matches, l_action, l_weight, "options-public", message="Public response: " + l_action + " # " + l_option)


	if m_debug:
		print "Common score"
		print m_counters.results_score.most_common(10)
		print "Common score complete"
		print m_counters.results_score_complete.most_common(10)
		print "Common count"
		print m_counters.results_count.most_common(10)
		print "Common count complete"
		print m_counters.results_count_complete.most_common(10)
		print "Determinators"
		print "============="
		for a in m_counters.results_score_complete.most_common(10):
		#for k,v in m_counters.results_determinator_complete.iteritems():
			k = a[0]
			print ""
			print k
			print "-" * len(k)
			for l,v in m_counters.results_determinator_complete[k].iteritems():
				print "   %s (%s  [ %s ] )" % (l, ','.join(v), str(len(v)))


	#
	# Filter the results
	#
	m_other_servers_prob = OrderedDict() # { WEB_SERVER, PROBABILITY }

	# Get web server family. F.E: Apache

	m_web_server      = None
	m_server_family   = None
	m_server_version  = None
	m_server_complete = None

	# If fingerprint found
	if m_counters.results_score.most_common():

		m_web_server      = m_counters.results_score.most_common(1)[0][0]
		m_server_family   = m_web_server.split("-")[0]
		m_server_version  = m_web_server.split("-")[1]

		# Get concrete versions and the probability
		m_base_percent = m_counters.results_score_complete.most_common(1)[0][1] # base value used for calculate percents
		for v in m_counters.results_score_complete.most_common(40):
			l_server_name    = v[0]
			l_server_prob    = v[1]

			if not l_server_name.startswith(m_server_family):
				continue

			# Asociate complete web server info with most probable result
			if not m_server_complete and m_server_version in l_server_name:
				m_server_complete = l_server_name

			m_other_servers_prob[l_server_name] = '{:0.2f}'.format((float(l_server_prob)/float(m_base_percent)) * 100.0)

			# Get only 4 results
			if len(m_other_servers_prob) >= number_of_entries:
				break
	else:

		m_web_server      = "Unknown"
		m_server_family   = "Unknown"
		m_server_version  = "Unknown web server"
		m_server_complete = []


	return m_server_family, m_server_version, m_server_complete, m_other_servers_prob





#----------------------------------------------------------------------
def ttl_platform_detection(main_url):
	"""
	This function try to recognize the remote platform doing a ping and analyzing the
	TTL of IP header response.

	:param main_url: Base url to test.
	:type main_url: str

	:return: a list with posibles platforms
	:rtype: dict(OS, version)
	"""

	# Do a ping
	try:
		m_ttl               = do_ping_and_receive_ttl(DecomposedURL(main_url).hostname, 2)

		# Load words for the wordlist
		l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config["Wordlist_ttl"]["ttl"])
		# Looking for matches
		l_matches           = l_wordlist_instance.matches_by_value(m_ttl)

		if l_matches:
			m_ret = {}
			for v in l_matches:
				sp = v.split("|")
				k = sp[0].strip()
				v = sp[1].strip()
				m_ret[k] = v

			return m_ret
		else:
			return {}
	except EnvironmentError,e:
		Logger.log_error("! You can't make the platform detection if you're not root.")
		return {}
	except Exception, e:
		return {}



@lru_cache(maxsize=100)
def calculate_server_track(server_name):
	# from nginx/1.5.1-r2 -> ("nginx", "1.5.1")
	l_server_track = None
	l_server       = None
	try:
		l_server = transform_name(server_name)
	except ValueError:
		return server_name


	# Name -> nginx
	l_server_name    = l_server[0]
	l_server_version = None
	try:

		# if version has format: 6.0v1 or 2.0
		if l_server[1].count(".") == 1:
			l_server_version = l_server[1]
		else:
			# Major version: 1.5.1 -> 1.5
			l_i = nindex(l_server[1], ".", 2)

			if l_i != -1:
				l_server_version = l_server[1][:l_i]
			else:
				l_server_version = l_server[1]

	except ValueError:
		l_server_version = "generic"

	l_server_track = "%s-%s" % (l_server_name, l_server_version)

	return l_server_track


#----------------------------------------------------------------------
@lru_cache(maxsize=100)
def nindex(str_in, substr, nth):
	"""
	From and string get nth ocurrence of substr
	"""

	m_slice  = str_in
	n        = 0
	m_return = None
	while nth:
		try:
			n += m_slice.index(substr) + len(substr)
			m_slice = str_in[n:]
			nth -= 1
		except ValueError:
			break
	try:
		m_return = n - 1
	except ValueError:
		m_return = 0

	return m_return

#----------------------------------------------------------------------
@lru_cache(maxsize=100)
def transform_name(name):
	"""
	Transforme strings like:

	nginx/1.5.1    -> (nginx, 1.5)

	nginx 1.5.1-r2 -> (nginx, 1.5)

	nginx/1.5.1v5  -> (nginx, 1.5)

	Microsoft IIS 6.0 -> (Microsoft IIS, 6.0)

	:return: a tuple as forme: (SERVER_NAME, VERSION)
	:rtype: tuple
	"""
	if not name:
		raise ValueError("Empty value")

	m_results = SERVER_PATTERN.search(name)

	if not m_results:
		raise ValueError("Incorrect format of name: '%s'" % name)

	return (m_results.group(1), m_results.group(2))


#------------------------------------------------------------------------------
class HTTPAnalyzer:
	""""""

	#----------------------------------------------------------------------
	def __init__(self, debug = False):
		"""Constructor"""

		self.__HTTP_fields_weight = {
			"accept-ranges"                : 1,
			"server"                       : 4,
			"cache-control"                : 2,
			"connection"                   : 2,
			"content-type"                 : 1,
			"etag-length"                  : 5,
			"etag-qoutes"                  : 2,
			"header-capitalizedafterdush"  : 2,
			"header-order"                 : 10,
			"header-space"                 : 2,
			"www-authenticate"             : 3,
			"pragma"                       : 2,
			"proto-name"                   : 1,
			"proto-version"                : 2,
			"statuscode"                   : 4,
			"statustext"                   : 4,
			"vary-capitalize"              : 2,
			"vary-delimiter"               : 2,
			"vary-order"                   : 3,
			"x-powered-by"                 : 3,
			"options-allow"                : 1,
			"options-public"               : 2,
		}

		self.__debug = debug

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

		# Scores:
		#
		# Count server + major version: nginx-1.5.1-r2 -> nginx-1.5
		self.__results_score          = Counter()
		# Count server + all revision: nginx-1.5.1-r2
		self.__results_score_complete = Counter()

		# Simple counters:
		#
		# Count server + major version: nginx-1.5.1-r2 -> nginx-1.5
		self.__results_count          = Counter()
		# Count server + all revision: nginx-1.5.1-r2
		self.__results_count_complete = Counter()

		#
		# Parameters determinator for each server
		self.__determinator = {}
		self.__determinator_complete = {}

	#----------------------------------------------------------------------
	def inc(self, test_lists, method, method_weight, types,  message = ""):
		""""""
		if test_lists:
			l_types = types.lower()

			# Debug info
			if self.__debug:
				print "%s: %s" % (message, l_types)

			# Get parsed web server list
			l_server_splited = set([calculate_server_track(server) for server in test_lists])

			# Count only one time of each web server
			for u in l_server_splited:
				self.__results_count[u] += 1 * method_weight
				self.__results_score[u] += self.__HTTP_fields_weight[l_types] * method_weight

				# Store determinators
				try:
					self.__determinator[u][l_types].add(method)
				except KeyError:
					self.__determinator[u] = {}
					self.__determinator[u][l_types] = set()
					self.__determinator[u][l_types].add(method)

			# Count all info
			for l_full_server_name in test_lists:

				#m_results_http_fields[server] += 1 * l_weight
				self.__results_count_complete[l_full_server_name] += 1 * method_weight
				self.__results_score_complete[l_full_server_name] += self.__HTTP_fields_weight[l_types] * method_weight

				# Store determinators
				try:
					a = self.__determinator_complete[l_full_server_name]
				except KeyError:
					self.__determinator_complete[l_full_server_name] = {}

				try:
					self.__determinator_complete[l_full_server_name][l_types].add(method)
				except KeyError:
					self.__determinator_complete[l_full_server_name][l_types] = set()
					self.__determinator_complete[l_full_server_name][l_types].add(method)


	#----------------------------------------------------------------------
	@property
	def results_score(self):
		""""""
		return self.__results_score

	#----------------------------------------------------------------------
	@property
	def results_score_complete(self):
		""""""
		return self.__results_score_complete

	#----------------------------------------------------------------------
	@property
	def results_count(self):
		""""""
		return self.__results_count

	#----------------------------------------------------------------------
	@property
	def results_count_complete(self):
		""""""
		return self.__results_count_complete


	#----------------------------------------------------------------------
	@property
	def results_determinator(self):
		""""""
		return self.__determinator


	#----------------------------------------------------------------------
	@property
	def results_determinator_complete(self):
		""""""
		return self.__determinator_complete