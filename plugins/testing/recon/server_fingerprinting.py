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
from ping import *

from collections import Counter
from urlparse import urljoin


"""
 !!!!!!!!!!!!!

 Fingerprint techniques are based on the fantastic paper of httprecon project, and their databases:

 Doc: http://www.computec.ch/projekte/httprecon/?s=documentation
 Project page: http://www.computec.ch/projekte/httprecon

 !!!!!!!!!!!!!


 This plugin try to a fingerprinting over web servers.

 Step 1
 ======
 Define the methods used:
 1 - Check de Banner.
 2 - Check de order headers in HTTP response.
 3 - Check the rest of headers.

 Step 2
 ======
 Then assigns a weight to each method:
 1 -> 50%
 2 -> 20%
 3 -> 30% (divided by the number of test for each header)

 Step 3
 ======
 We have 9 request with:
 1 - GET / HTTP/1.1
 2 - GET /index.php HTTP/1.1
 3 - GET /404_file.html HTTP/1.1
 4 - HEAD / HTTP/1.1
 5 - OPTIONS / HTTP/1.1
 6 - DELETE / HTTP/1.1
 7 - TEST / HTTP/1.1
 8 - GET / 9.8
 9 - GET /<SCRIPT>alert</script> HTTP/1.1 -> Any web attack.

 Step 4
 ======
 For each type of response analyze the HTTP headers trying to find matches and
 multiply for their weight.

 Step 5
 ======
 Sum de values obtained in step 4, for each test in step 3.

 Step 6
 ======
 Get the 3 highter values os matching.


 For example
 ===========
 For an Apache 1.3.26 we will have these results for a normal GET:

 Banner (any of these options):
 ++++ Apache/1.3.26 (Linux/SuSE) mod_ssl/2.8.10 OpenSSL/0.9.6g PHP/4.2.2
 ++++ Apache/1.3.26 (UnitedLinux) mod_python/2.7.8 Python/2.2.1 PHP/4.2.2 mod_perl/1.27
 ++++ Apache/1.3.26 (Unix)
 ++++ Apache/1.3.26 (Unix) Debian GNU/Linux mod_ssl/2.8.9 OpenSSL/0.9.6g PHP/4.1.2 mod_webapp/1.2.0-dev
 ++++ Apache/1.3.26 (Unix) Debian GNU/Linux PHP/4.1.2
 ++++ Apache/1.3.26 (Unix) mod_gzip/1.3.19.1a PHP/4.3.11 mod_ssl/2.8.9 OpenSSL/0.9.6
 ++++ MIT Web Server Apache/1.3.26 Mark/1.5 (Unix) mod_ssl/2.8.9 OpenSSL/0.9.7c

 - A specific order for the rest of HTTP headers (any of these options):
 ++++ Date,Server,Accept-Ranges,Content-Type,Content-Length,Via
 ++++ Date,Server,Connection,Content-Type
 ++++ Date,Server,Keep-Alive,Connection,Transfer-Encoding,Content-Type
 ++++ Date,Server,Last-Modified,ETag,Accept-Ranges,Content-Length,Connection,Content-Type
 ++++ Date,Server,Last-Modified,ETag,Accept-Ranges,Content-Length,Keep-Alive,Connection,Content-Type
 ++++ Date,Server,Set-Cookie,Content-Type,Set-Cookie,Keep-Alive,Connection,Transfer-Encoding
 ++++ Date,Server,X-Powered-By,Keep-Alive,Connection,Transfer-Encoding,Content-Type
 ++++ Date,Server,X-Powered-By,Set-Cookie,Expires,Cache-Control,Pragma,Set-Cookie,Set-Cookie,Keep-Alive,Connection,Transfer-Encoding,Content-Type
 ++++ Date,Server,X-Powered-By,Set-Cookie,Set-Cookie,Expires,Last-Modified,Cache-Control,Pragma,Keep-Alive,Connection,Transfer-Encoding,Content-Type

 - The value of the rest of headers must be:
 ** Content-Type (any of these options):
 +++++ text/html
 +++++ text/html; charset=iso-8859-1
 +++++ text/html;charset=ISO-8859-1

 ** Cache-Control (any of these options):
 ++++ no-store, no-cache, must-revalidate, post-check=0, pre-check=0
 ++++ post-check=0, pre-check=0

 ** Connection (any of these options):
 ++++ close
 ++++ Keep-Alive

 ** Quotes types must be double for ETag field:
 ++++ ETag: "0", instead of ETag: '0'

 ** E-Tag length (any of these options):
 ++++ 0
 ++++ 20
 ++++ 21
 ++++ 23

 ** Pragma (any of these options):
 ++++ no-cache

 ** Format of headers. After a bash, the letter is uncapitalized, for http headers. For example:
 ++++ Content-type, instead of Content-**T**ype.

 ** Has spaces between names and values. For example:
 ++++ E-Tag:0; instead of: E-Tag:0

 ** Protocol name used in request is 'HTTP'. For example:
 ++++ GET / HTTP/1.1

 ** The status text for a response of HTTP.
     GET / HTTP/1.1
     Host: misite.com

     HTTP/1.1 200 **OK**
     ....

 ** X-Powered-By (any of these options):
 ++++ PHP/4.1.2
 ++++ PHP/4.2.2
 ++++ PHP/4.3.11
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

		#main_server_fingerprint(info)

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

	Logger.log_more_verbose("Starting fingerprinting plugin for site: %s" % m_main_url)

	# Get a connection pool
	m_conn = NetworkAPI.get_connection()

	#
	# Detect the platform: Windows or *NIX
	#
	#print basic_platform_detection(m_main_url, m_conn)
	#print ttl_platform_detection(DecomposedURL(m_main_url).hostname)

	#
	# Analyze HTTP protocol
	#
	#a, b = http_analyzers(m_main_url, m_conn)

	#print a
	Logger.log_more_verbose("Fingerprint ends for url: %s" % m_main_url)



#----------------------------------------------------------------------
def basic_platform_detection(main_url, conn):
	"""
	Detect if platform is Windows or *NIX. To do this, get the first link, in scope, and
	does two resquest. If are the same response, then, platform are Windows. Else are *NIX.

	:returns: Name of platforms: Windows, *NIX or unknown.
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


	# Delete created objects
	del m_response_orig
	del m_response_upper
	del m_first_link
	del m_r

	return m_return

#----------------------------------------------------------------------
def http_analyzers(main_url, conn, number_of_entries=10):
	"""
	Analyze HTTP headers for detect the web server. Return a list with most possible web servers.

	:param main_url: Base url to test.
	:type main_url: str

	:param conn: Instance of connection.
	:type conn: Web type connection

	:param number_of_entries: number of resutls tu return for most probable web servers detected.
	:type number_of_entries: int

	:return: a tuple with two lists with: ([Most counts hits], [Highest score])
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

	m_HTTP_fields_weight = {
		"accept-ranges"                : 1,
		"server"                       : 3,
		"cache-control"                : 2,
		"connection"                   : 2,
		"content-type"                 : 1,
		"etag-length"                  : 3,
		"etag-qoutes"                  : 2,
		"header-capitalizedafterdush"  : 2,
		"header-order"                 : 5,
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


	#m_HTTP_fields_weight = {
		#"accept-ranges"                : 1,
		#"server"                       : 1,
		#"cache-control"                : 1,
		#"connection"                   : 1,
		#"content-type"                 : 1,
		#"etag-length"                  : 1,
		#"etag-qoutes"                  : 1,
		#"header-capitalizedafterdush"  : 1,
		#"header-order"                 : 1,
		#"header-space"                 : 1,
		#"www-authenticate"             : 1,
		#"pragma"                       : 1,
		#"proto-name"                   : 1,
		#"proto-version"                : 1,
		#"statuscode"                   : 1,
		#"statustext"                   : 1,
		#"vary-capitalize"              : 1,
		#"vary-delimiter"               : 1,
		#"vary-order"                   : 1,
		#"x-powered-by"                 : 1,
		#"options-allow"                : 1,
		#"options-public"               : 1,
	#}

	m_actions = {
		'GET'        : { 'wordlist' : 'Wordlist_get'            , 'weight' : 1 , 'protocol' : 'HTTP/1.1', 'method' : 'GET'      , 'payload': '/' },
		'LONG_GET'   : { 'wordlist' : 'Wordlist_get_long'       , 'weight' : 1 , 'protocol' : 'HTTP/1.1', 'method' : 'GET'      , 'payload': '/%s' % ('a' * 200) },
		'NOT_FOUND'  : { 'wordlist' : 'Wordlist_get_notfound'   , 'weight' : 3 , 'protocol' : 'HTTP/1.1', 'method' : 'GET'      , 'payload': '/404_NOFOUND__X02KAS' },
		'HEAD'       : { 'wordlist' : 'Wordlist_head'           , 'weight' : 2 , 'protocol' : 'HTTP/1.1', 'method' : 'HEAD'     , 'payload': '/' },
		'OPTIONS'    : { 'wordlist' : 'Wordlist_options'        , 'weight' : 2 , 'protocol' : 'HTTP/1.1', 'method' : 'OPTIONS'  , 'payload': '/' },
		'DELETE'     : { 'wordlist' : 'Wordlist_delete'         , 'weight' : 3 , 'protocol' : 'HTTP/1.1', 'method' : 'DELETE'   , 'payload': '/' },
		'TEST'       : { 'wordlist' : 'Wordlist_attack'         , 'weight' : 3 , 'protocol' : 'HTTP/1.1', 'method' : 'TEST'     , 'payload': '/' },
		'INVALID'    : { 'wordlist' : 'Wordlist_wrong_method'   , 'weight' : 3 , 'protocol' : 'HTTP/9.8', 'method' : 'GET'      , 'payload': '/' },
		'ATTACK'     : { 'wordlist' : 'Wordlist_wrong_version'  , 'weight' : 1 , 'protocol' : 'HTTP/1.1', 'method' : 'GET'      , 'payload': "/etc/passwd?format=%%%%&xss=\x22><script>alert('xss');</script>&traversal=../../&sql='%20OR%201;"}
	}

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
	m_results_count = Counter()
	m_results_score = Counter()
	# Store results for others HTTP params
	m_results_http_others = {}
	m_d                   = DecomposedURL(main_url)
	m_hostname            = m_d.hostname
	m_port                = m_d.port
	_debug                = True

	for l_action, v in m_actions.iteritems():
		if _debug:
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
		if _debug:
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
			Logger.log_more_verbose("Server-Fingerprint plugin: No response for URL '%s'. Message: " % (e.message))
			continue

		if not l_response:
			Logger.log_more_verbose("No response for URL '%s'." % l_url)
			continue

		if _debug:
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

			if l_matches:
				if _debug:
					print "HTTP field: " + l_curr_header_value
				for server in l_matches:
					#m_results_http_fields[server] += 1 * l_weight
					m_results_count[server] += 1
					m_results_score[server] += m_HTTP_fields_weight[l_http_header_name.lower()]

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
		if l_matches:
			if _debug:
				print "Status code: " + str(l_response.http_response_code)
			for server in l_matches:
				#print server + " " + str(l_response.http_response_code)
				#m_results_http_fields[server] += 1 * l_weight
				m_results_count[server] += 1
				m_results_score[server] += m_HTTP_fields_weight["statuscode"]

		#
		# Status text
		# ===========
		#
		l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["statustext"])
		# Looking for matches
		l_matches           = l_wordlist_instance.matches_by_value(l_response.http_response_reason)
		if l_matches:
			if _debug:
				print "Status text: " + l_response.http_response_reason
			for server in l_matches:
				#m_results_http_fields[server] += 1 * l_weight
				m_results_count[server] += 1
				m_results_score[server] += m_HTTP_fields_weight["statustext"]

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
			if l_matches:
				if _debug:
					print "Header space: " + l_spaces_num
				for server in l_matches:
					#m_results_http_fields[server] += 2 * l_weight
					m_results_count[server] += 1
					m_results_score[server] += m_HTTP_fields_weight["header-space"]
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
		l_valid_fields = [x for x in l_response.http_headers if "-" in x]
		if l_valid_fields:
			l_h = l_valid_fields[0]

			l_value = l_h.split("-")[1] # Get the second value: Content-type => type
			if l_value[0].isupper(): # Check first letter is lower
				if _debug:
					print "Capital after dash: 1"
				l_matches           = l_wordlist_instance.matches_by_value(1)
				if l_matches:
					for server in l_matches:
						#m_results_http_fields[server] += 2 * l_weight
						m_results_count[server] += 1
						m_results_score[server] += m_HTTP_fields_weight["header-capitalizedafterdush"]

		#
		# Header order
		# ============
		#
		l_header_order      = ','.join(v.split(":")[0] for v in l_response.http_headers_raw.splitlines())
		l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["header-order"])
		l_matches           = l_wordlist_instance.matches_by_value(l_header_order)
		if l_matches:
			if _debug:
				print "Header order: " + l_header_order
			for server in l_matches:
				#m_results_http_fields[server] += 5 * l_weight
				m_results_count[server] += 1
				m_results_score[server] += m_HTTP_fields_weight["header-order"]

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
			l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["protocol-name"])
			l_matches           = l_wordlist_instance.matches_by_value(l_proto)
			if l_matches:
				if _debug:
					print "Proto name: " + l_proto
				for server in l_matches:
					#m_results_http_fields[server] += 1 * l_weight
					m_results_count[server] += 1
					m_results_score[server] += m_HTTP_fields_weight["proto-name"]
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
			l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["protocol-version"])
			l_matches           = l_wordlist_instance.matches_by_value(l_version)
			if l_matches:
				if _debug:
					print "Proto version: " + l_version
				for server in l_matches:
					#m_results_http_fields[server] += (1 * l_weight)
					m_results_count[server] += 1
					m_results_score[server] += m_HTTP_fields_weight["proto-version"]
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

			if l_matches:
				if _debug:
					print "ETag length: " + str(l_etag_len)
				for server in l_matches:
					#m_results_http_fields[server] += 2 * l_weight
					m_results_count[server] += 1
					m_results_score[server] += m_HTTP_fields_weight["etag-length"]

			#
			# ETag Quotes
			# ================
			#
			l_etag_striped          = l_etag_header.strip()
			if l_etag_striped.startswith("\"") or l_etag_striped.startswith("'"):
				l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["etag-quotes"])
				l_matches           = l_wordlist_instance.matches_by_value(l_etag_striped[0])
				if l_matches:
					if _debug:
						print "Etag quotes: " + l_etag_striped[0]
					for server in l_matches:
						#m_results_http_fields[server] += 2 * l_weight
						m_results_count[server] += 1
						m_results_score[server] += m_HTTP_fields_weight["etag-qoutes"]


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
			if l_matches:
				if _debug:
					print "Vary delimiter: " + l_var_delimiter
				for server in l_matches:
					#m_results_http_fields[server] += 2 * l_weight
					m_results_count[server] += 1
					m_results_score[server] += m_HTTP_fields_weight["vary-delimiter"]

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
			if l_matches:
				if _debug:
					print "Vary capitalizer: " + l_vary_capitalizer
				for server in l_matches:
					#m_results_http_fields[server] += 2 * l_weight
					m_results_count[server] += 1
					m_results_score[server] += m_HTTP_fields_weight["vary-capitalize"]


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
			if l_matches:
				if _debug:
					print "Vary order: " + l_vary_header
				for server in l_matches:
					#m_results_http_fields[server] += 2 * l_weight
					m_results_count[server] += 1
					m_results_score[server] += m_HTTP_fields_weight["vary-order"]


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
			l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["options-public"])
			# Looking for matches
			l_matches           = l_wordlist_instance.matches_by_value(l_option)
			if l_matches:
				if _debug:
					print "HEAD option: " + l_option
				for server in l_matches:
					#m_results_http_fields[server] += 1 * l_weight
					m_results_count[server] += 1
					m_results_score[server] += m_HTTP_fields_weight["options-allow"]


		if l_action == "OPTIONS" or l_action == "INVALID" or l_action == "DELETE":
			if "Allow" in l_response.http_headers:
				#
				# Options allow
				# =============
				#
				l_option            = l_response.http_headers.get("Allow")
				l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["options-public"])
				# Looking for matches
				l_matches           = l_wordlist_instance.matches_by_value(l_option)
				if l_matches:
					if _debug:
						print "OPTIONS allow: "  + l_action + " # " + l_option
					for server in l_matches:
						#m_results_http_fields[server] += 1 * l_weight
						m_results_count[server] += 1
						m_results_score[server] += m_HTTP_fields_weight["options-allow"]


				#
				# Allow delimiter
				# ===============
				#
				l_option            = l_response.http_headers.get("Allow")
				l_var_delimiter     = ", " if l_option.find(", ") else ","
				l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["options-delimited"])
				# Looking for matches
				l_matches           = l_wordlist_instance.matches_by_value(l_var_delimiter)
				if l_matches:
					if _debug:
						print "OPTION allow delimiter " + l_action + " # " + l_option
					for server in l_matches:
						#m_results_http_fields[server] += 1 * l_weight
						m_results_count[server] += 1
						m_results_score[server] += m_HTTP_fields_weight["options-delimiter"]


			if "Public" in l_response.http_headers:
				#
				# Public response
				# ===============
				#
				l_option            = l_response.http_headers.get("Public")
				l_wordlist_instance = WordListAPI().get_advanced_wordlist_as_dict(Config.plugin_extra_config[l_wordlist]["options-public"])
				# Looking for matches
				l_matches           = l_wordlist_instance.matches_by_value(l_option)
				if l_matches:
					if _debug:
						print "Public response: " + l_action + " # " + l_option
					for server in l_matches:
						#m_results_http_fields[server] += 1 * l_weight
						m_results_count[server] += 1
						m_results_score[server] += m_HTTP_fields_weight["options-public"]



		print "Common score"
		print m_results_score.most_common(20)
		print "Common count"
		print m_results_count.most_common(20)
		print

	return m_results_count.most_common(5), m_results_score.most_common(5)





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
		else:
			return {}
	except EnvironmentError,e:
		Logger.log_error("! Yout can't make the platform detection if you're not root.")
		return {}
	except Exception, e:
		print e
		return {}

	print m_ret