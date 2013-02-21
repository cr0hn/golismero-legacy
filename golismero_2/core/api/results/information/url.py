#!/usr/bin/python
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

from core.api.results.information.information import Information


#------------------------------------------------------------------------------
class Url(Information):
	"""
	URL results.
	"""

	CONTENT_HTTP      = 0
	CONTENT_JSON      = 1
	CONTENT_VIEWSTATE = 2
	CONTENT_SOAP      = 3


	#----------------------------------------------------------------------
	def __init__(self, url, method = "GET", url_params = None, post_params= None, content_type = 0):
		"""
		Construct a URL result.

		:param url: URL to manage
		:type url: str

		:param method: HTTP method to get URL
		:type method: str

		:param url_params: params inside URL
		:type url_params: dict

		:param post_params: params inside post
		:type post_params: dict
		"""
		super(Url, self).__init__(Information.INFORMATION_URL)

		# URL
		self.__url = url

		# Method
		self.__method = 'GET' if not method else method.upper()

		# Params in URL
		self.__url_params = url_params if url_params else {}

		# Params as post
		self.__post_params = post_params if post_params else {}

		# HTTPs?
		self.__is_https = True if url.lower().find("https") else False

		# Len counts
		self.__has_url_params = None
		self.__has_post_params = None

		# Content type
		self.__content_type = content_type


	#----------------------------------------------------------------------
	def __str__(self):
		return "[%s] %s (%s)" % (
			self.__method,
			self.__url,
			''.join(["%s = %s | " % (k, v) for k, v in (self.__url_params.items() if self.__method != 'POST' else self.__post_params.items())])[:-2]
		)


	#----------------------------------------------------------------------
	def __get_url(self):
		"""
		Get raw info of URL.
		"""
		return self.__url
	url = property(__get_url)

	def __get_method(self):
		"""
		Get method to get URL
		"""
		return self.__method
	method = property(__get_method)

	def __get_url_params(self):
		"""
		Get raw info of URL.
		"""
		return self.__url_params
	url_params = property(__get_url_params)

	def __get_post_params(self):
		"""
		Get raw info of URL.
		"""
		return self.__post_params
	post_params = property(__get_post_params)

	#----------------------------------------------------------------------
	def __get_is_http(self):
		""""""
		return self.__is_https
	is_https = property(__get_is_http)

	#----------------------------------------------------------------------
	def __get_has_url_param(self):
		""""""
		if self.__has_url_params:
			self.__has_url_params = True
	has_url_params = property(__get_has_url_param)

	#----------------------------------------------------------------------
	def __get_has_post_param(self):
		""""""
		if self.__has_post_params:
			self.__has_post_params = True
	has_post_params = property(__get_has_post_param)


	#----------------------------------------------------------------------
	def __get_content_type(self):
		""""""
		return self.__content_type
	content_type = property(__get_content_type)




