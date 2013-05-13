#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------
# Network protocols API
#-----------------------------------------------------------------------

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

__all__ = ['NetworkAPI', 'NetworkException', 'Web']

from .cache import NetworkCache
from .http import HTTP_Request, HTTP_Response
from .web_utils import *
from ..config import Config
from ..data.resource.url import Url
from ..logger import Logger
from ...messaging.codes import MessageCode

from re import compile, match, IGNORECASE
from httpparser.httpparser import *
from requests import *
from requests.exceptions import RequestException
from time import time
from StringIO import StringIO # Use StringIO instead of cStringIO because cStringIO can't be pickled
from mimetools import Message
import socket, select
import hashlib


#------------------------------------------------------------------------------
class NetworkException(Exception):
	"""
	Exception for net connections
	"""
	pass

#------------------------------------------------------------------------------
class NetworkOutOfScope(Exception):
	"""
	Exception for net connections
	"""
	pass


#------------------------------------------------------------------------------
class NetworkAPI (object):
	""""""

	TYPE_WEB = 0
	TYPE_FTP = 1

	TYPE_FIRST = TYPE_WEB
	TYPE_LAST  = TYPE_FTP

	# Pool manager. One pool per target.
	__http_pool_manager = None


	#----------------------------------------------------------------------
	@staticmethod
	def get_connection(protocol = TYPE_WEB):
		"""
		Get a connection of for an specific protocol.

		:param protocol: Connection to receive: HTTP, FTP...
		:type protocol: int

		:raises: ValueError
		"""
		if NetworkAPI.__http_pool_manager is None:

			# Set pool
			NetworkAPI.__http_pool_manager = Session()

			# If proxy
			m_proxy_addr = Config.audit_config.proxy_addr
			if m_proxy_addr:
				m_auth_user = Config.audit_config.proxy_user
				m_auth_pass = Config.audit_config.proxy_pass

				# Detect auth method
				auth, realm = detect_auth_method(m_proxy_addr, m_auth_user, m_auth_pass)

				# Set auth and proxy
				NetworkAPI.__http_pool_manager.auth = get_auth_obj(auth, m_auth_user, m_auth_pass)
				NetworkAPI.__http_pool_manager.proxies = {'http': m_proxy_addr}



			# Set cookie
			m_cookies = Config.audit_config.cookie
			if m_cookies:
				NetworkAPI.__http_pool_manager.cookies = m_cookies

		if protocol is NetworkAPI.TYPE_WEB:
			return Web(NetworkAPI.__http_pool_manager, Config.audit_config)

		else:
			raise ValueError("Unknown protocol type, value: %d" % protocol)


#------------------------------------------------------------------------------
class ConnectionSlot (object):
	"""
	Connection slot context manager.
	"""

	@property
	def hostname(self):
		return self.__host

	def __init__(self, hostname):
		self.__host = hostname

	def __enter__(self):
		self.__token = Config._context.remote_call(
		    MessageCode.MSG_RPC_REQUEST_SLOT, self.hostname, 1
		)
		if not self.__token:
			# XXX FIXME
			# This should block, not throw an error...
			raise IOError("Connection slots limit exceeded, try again later")

	def __exit__(self, type, value, tb):
		Config._context.remote_call(
		    MessageCode.MSG_RPC_RELEASE_SLOT, self.__token
		)


#------------------------------------------------------------------------------
class Protocol (object):
	"""
	Superclass for networks protocols.
	"""


	#----------------------------------------------------------------------
	def __init__(self):

		# Network cache API.
		self._cache = NetworkCache()


	#----------------------------------------------------------------------
	def state(self):
		pass


	#----------------------------------------------------------------------
	def close(self):
		"""
		Release all resources associated with this object.
		"""
		pass


	#----------------------------------------------------------------------
	def get(self, URL, cache = True):
		"""
		Fetch a resource, optionally specifying if it must be stored
		in the cache.

		:param URL: URL to get.
		:type URL: str

		:param cache: True if response must be cached, False if it must not, None if it's indifferent.
		:type cache: bool
		"""
		raise NotImplementedError("Subclasses MUST implement this method!")


#------------------------------------------------------------------------------
#
# Web protocols.
#
#------------------------------------------------------------------------------
class Web (Protocol):
	"""
	Web protocols handler (HTTP, HTTPS).
	"""


	#----------------------------------------------------------------------
	def __init__(self, http_pool, config):
		super(Web, self).__init__()

		self.__http_pool_manager = http_pool
		self.__config = config

		# Global option for redirects
		self.__follow_redirects = config.follow_redirects


	#----------------------------------------------------------------------
	def state(self):
		pass


	#----------------------------------------------------------------------
	def close(self):
		self.__http_pool_manager.clear()


	#----------------------------------------------------------------------
	def get_custom(self, request, timeout = 5):
		"""Get an HTTP response from a custom HTTP Request object.

		:param request: An HTTP request object.
		:type request: HTTP_request

		:param timeout: timeout in seconds.
		:type timeout: int

		:returns: HTTP_Response -- HTTP response object | None
		"""
		if not isinstance(request, HTTP_Request):
			raise TypeError("Expected HTTP_Request, got %s instead" % type(URL))

		# Check if the URL is within scope of the audit.
		if not is_in_scope(request.url):
			Logger.log_verbose("Url '%s' out of scope. Skipping it." % request.url)
			raise NetworkOutOfScope("'%s' is out of the scope." % URL)

		# If the URL is cached, return the cached contents.
		if request.is_cacheable and self._cache.exists(request.request_id, protocol=request.parsed_url.scheme):
			return self._cache.get(request.request_id, protocol=request.parsed_url.scheme)

		#
		# Get URL
		#
		with ConnectionSlot(request.parsed_url.hostname):

			# Set redirect option
			request.follow_redirects = request.follow_redirects or self.__follow_redirects


			# allow_redirects
			# headers
			#
			# files = {'file': open('report.xls', 'rb')}
			# r = requests.post(url, files=files)
			#
			#  GET, OPTIONS, HEAD, POST, PUT, PATCH and DELETE.



			# Set options
			m_request_params = {
			    'allow_redirects' : request.follow_redirects,
			    'headers' : request.raw_headers,
			    #'timeout' : timeout
			}

			# HTTP method
			m_method = request.method.upper()

			# Set files data, if available
			if m_method == "POST" or (m_method == "PUT" and request.files_attached):
				# Add files
				for fname, fvalue in request.files_attached.iteritems():
					m_request_params["files"] = { 'file': (fname, fvalue) } # overloaded operator!

			# Select request type
			#
			# Fix URL: www.site.com -> http://www.site.com
			m_parsed_url = DecomposedURL(request.url)
			m_url = m_parsed_url.url

			if m_method not in ("GET", "POST", "HEAD", "OPTIONS", "PUT", "PATCH", "DELETE"):
				raise NotImplementedError("Method '%s' not allowed." % m_method)

			# Start timing the request
			t1 = time()

			# Issue the request
			try:
				m_response = getattr(self.__http_pool_manager, m_method.lower())(m_url, timeout = timeout, **m_request_params)
			except RequestException, e:
				raise NetworkException(e.message)

			# Stop timing the request
			t2 = time()

			# Calculate the request time
			m_time = t2 - t1

			# Parse the response
			#m_response = HTTP_Response(m_time)
			m_response = HTTP_Response.from_custom_request(m_response, m_time)

			# Cache the response if enabled
			if request.is_cacheable:
				self._cache.set(request.request_id, m_response,
				                protocol  = request.parsed_url.scheme,
				                timestamp = t1)

		# Return the response
		return m_response


	#----------------------------------------------------------------------
	def get(self, URL, method = "GET", timeout = 5, post_data = None, follow_redirect = None, cache = True):
		"""
		Get response for an input URL.

		:param URL: string with URL or Url instance
		:type URL: str or Url

		:param cache: cache response?
		:type cache: bool

		:param redirect: If you want to follow HTTP redirect.
		:type redirect: bool

		:param timeout: timeout in seconds.
		:type timeout: int

		:returns: HTTPResponse instance or None if any error or URL out of scope.

		:raises: TypeError
		"""


		# Extract the raw URL when applicable
		m_referer = None
		try:
			if isinstance(URL, Url):
				URL       = URL.url
				m_referer = URL.referer
			elif isinstance(URL, basestring):
				URL       = URL
				# Parse, verify and canonicalize the URL
				parsed = DecomposedURL(URL)
				if not parsed.host or not parsed.scheme:
					raise ValueError("Only absolute URLs must be used!")

		except AttributeError:
			pass

		# Check for host matching
		if not is_in_scope(URL):
			Logger.log_verbose("[!] Url '%s' out of scope. Skipping it." % URL)
			raise NetworkOutOfScope("'%s' is out of the scope." % URL)

		# Set redirect
		m_follow_redirects = follow_redirect if follow_redirect else self.__follow_redirects

		# Make HTTP_Request object
		m_request = HTTP_Request(
		    url = URL,
		    method = method,
		    post_data = post_data,
		    follow_redirects = m_follow_redirects,
		    cache = cache
		)

		# Set referer
		if m_referer:
			m_request.referer = m_referer

		return self.get_custom(m_request, timeout= timeout)


	#----------------------------------------------------------------------
	def get_raw(self, host, request_content, timeout = 2, port=80, proto="HTTP", cache = True):
		"""
		This method allow you to make raw connections to a host.

		You need to provide the data that you want to send to the server. You're the responsible to manage the
		data that will be send to the server.

		:param timeout: timeout in seconds.
		:type timeout: int

		:return: dict as format: {'protocol' : "HTTP", "version": "x.x", "statuscode": "XXX", "statustext": "XXXXX", 'headers': Message()}

		"""
		# Check if the URL is within scope of the audit.
		if not is_in_scope(host):
			Logger.log_verbose("Url '%s' out of scope. Skipping it." % host)
			raise NetworkOutOfScope("'%s' is out of the scope." % host)

		# Create data for key
		m_string = "%s|%s" % (host, ''.join(( "%s:%s" % (v.split(":")[0], v.split(":")[1]) if ":" in v else '' for v in request_content.splitlines() ) if request_content else ''))

		# Make the hash
		m_request_id = hashlib.md5(m_string).hexdigest()

		# If the URL is cached, return the cached contents.
		if cache and self._cache.exists(m_request_id, protocol=proto):
			return self._cache.get(m_request_id, protocol=proto)

		with ConnectionSlot(host):

			# Start timing the request

			#
			# Get URL
			#
			t1 = time()

			# Issue the request
			try:
				# Connect to the server
				s = socket.socket()
				s.settimeout(timeout)
				s.connect((host, port))

				# Send an HTTP request
				s.send(request_content)
				m_temp_response = StringIO()

				buffer          = s.recv(1)
				m_temp_response.write( buffer )

				m_counter       = 0
				if buffer == '\n' or buffer == '\r':
					m_counter += 1

				# Get HTTP header
				while True:
					buffer = s.recv(1)
					m_temp_response.write( buffer )
					m_counter = m_counter + 1 if buffer == '\n' or buffer == '\r' else 0
					if m_counter == 4: # End of HTTP header
						break

				s.close()

				# Parse the HTTP header and get the Content-Length
				#if "Content-Length" in m_parser.response_http_headers:
					#m_body_length = int(m_parser.response_http_headers.get("Content-Length"))


				m_response = {}
				m_response["raw_content"]  = m_temp_response.getvalue() # TODO: Add complete response!!!!!!

				# Read headers
				request_line, headers_alone = m_response["raw_content"].split('\n', 1)

				# Parse first line
				m_response["protocol"]      = request_line[0:4]
				m_response["version"]       = request_line[5:8]
				m_response["statuscode"]    = request_line[9:12]
				m_response["statustext"]    = request_line[13:]
				m_response["content"]       = "" # TODO: Add complete response!!!!!!

				# Build headers
				m_response["headers"]     = Message(StringIO(headers_alone))


				#
				#
				# TODO!!!!!
				#
				# When response of HEAD, with "Content-Length" header, but without data
				# is received, then the connection is locked.
				#
				#m_response.write(s.recv(m_body_length))


			except socket.error, e:
				raise NetworkException(e.message)

			# Stop timing the request
			t2 = time()

		# Calculate the request time
		m_time = t2 - t1

		# Parse the response
		m_response     = HTTP_Response.from_raw_request(m_response, m_time)

		# Cache the response if enabled
		if cache:
			self._cache.set(m_request_id, m_response,
			                protocol  = proto,
			                timestamp = t1)

		# Return the response
		return m_response