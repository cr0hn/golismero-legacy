#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: http://golismero-project.com
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


#----------------------------------------------------------------------
#
# Data structures
#
#----------------------------------------------------------------------
class AuditProgress(object):
	"""

	Get the audit state. This class acts as java POJO, having these attributes:

	- current_stage :: str
	- steps         :: int
	- tests_remain  :: int
	- tests_done     :: int

	"""

	PROPERTIES = ["current_stage", "steps", "tests_remain", "tests_done"]

	#----------------------------------------------------------------------
	def __init__(self, data):
		"""
		Load data from JSON, in format:

		{
		  'current_stage' : str,
		  'steps'         : int,
		  'tests_remain'  : int,
		  'tests_done'     : str
		}

		:param data: dict with info.
		:type data: dict
		"""
		if not isinstance(data, dict):
			raise TypeError("Expected dict, got '%s' instead" % type(data))

		for p in AuditProgress.PROPERTIES:
			try:
				setattr(self, p, data[p])
			except KeyError:
				raise ValueError("Invalid JSON format.")

		# Store original json
		self.__json             = data

	#----------------------------------------------------------------------
	def to_json(self):
		"""
		Return the JSON object
		"""
		return self.__json




class GoLismeroAuditData(object):
	"""Audit info"""

	PROPERTIES = [
	    "id",
	    "audit_name",
	    "only_vulns",
	    "include_subdomains",
	    "subdomain_regex",
	    "depth",
	    "max_links",
	    "follow_redirects",
	    "follow_first_redirect",
	    "proxy_addr",
	    "proxy_user",
	    "proxy_pass",
	    "cookie",
	    "user_agent",
	    "start_date",
	    "end_date",
	    "audit_state",
	    "results_type",
	    "results_location",
	    "user",
	]


	#----------------------------------------------------------------------
	def __init__(self):
		for v in GoLismeroAudit.PROPERTIES:
			setattr(self, v, None)

		# Set list properties
		self.targets         = []
		self.enabled_plugins = []


	#----------------------------------------------------------------------
	@classmethod
	def from_json(cls, data):
		"""
		Load from json model.

		:param data: json object as a dict
		:type data: dict

		:retrun: GoLismeroAuditData instance
		:rtype: GoLismeroAuditData
		"""
		if not isinstance(data, dict):
			raise TypeError("Expected basestring, got '%s' instead" % type(data))

		# Set PK
		c = cls()
		for k, v in data.iteritems():
			setattr(c, k, v, None)

		return c




	#----------------------------------------------------------------------
	def to_json(self):
		"""
		Returns a JSON with all info.

		:return: JSON with info.
		"""
		return { k : v for k, v in self.__dict__.iteritems() }

	#----------------------------------------------------------------------
	def to_json_brief(self):
		"""
		Returns only a json with:
		- audit name
		- user
		- state
		"""
		return {
		    'audit_name'   : self.audit_name,
		    'user'         : self.user,
		    'state'        : self.audit_state
		}
