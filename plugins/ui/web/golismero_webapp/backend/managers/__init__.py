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

from backend.models import *

class GoLismeroAuditProgress(object):
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
		  'tests_done'     : int
		}

		:param data: dict with info.
		:type data: dict
		"""
		if not isinstance(data, dict):
			raise TypeError("Expected dict, got '%s' instead" % type(data))

		for p in GoLismeroAuditProgress.PROPERTIES:
			try:
				setattr(self, p, data[p])
			except KeyError:
				raise ValueError("Invalid JSON format.")

		# Store original json
		self.__json             = data

	#----------------------------------------------------------------------
	@property
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
	    "disable_plugins"
	]


	#----------------------------------------------------------------------
	def __init__(self):
		for v in GoLismeroAuditData.PROPERTIES:
			setattr(self, v, None)

		# Set list properties
		self.targets         = []
		self.enable_plugins  = []

		# store path
		self.__store_path    = None

	#----------------------------------------------------------------------
	@property
	def store_path(self):
		"""
		:return: Folder path to store audit info
		:rtype: str
		"""
		return self.__store_path

	#----------------------------------------------------------------------
	@store_path.setter
	def store_path(self, val):
		"""
		:param val: Folder path to store audit info
		:type val: str
		"""
		if not isinstance(val, basestring):
			raise TypeError("Expected , got '%s'" % type(val))

		self.__store_path = val




	#----------------------------------------------------------------------
	@classmethod
	def from_json(cls, data):
		"""
		Load from json model.

		:param data: json object as a dict
		:type data: dict

		:retrun: GoLismeroAuditData instance
		:rtype: GoLismeroAuditData

		:raises: TypeError
		"""
		if not isinstance(data, dict):
			raise TypeError("Expected basestring, got '%s' instead" % type(data))

		# Set PK
		c = cls()
		for k, v in data.iteritems():
			setattr(c, k, v, None)

		return c

	#----------------------------------------------------------------------
	@classmethod
	def from_django(cls, data):
		"""
		Loads object form Audits django object.

		:param data: Audits instance
		:type data: Audits

		:raises: TypeError
		"""
		if not isinstance(data, Audit):
			raise TypeError("Expected Audits, got '%s' instead" % type(data))

		c = cls()

		for d in GoLismeroAuditData.PROPERTIES:
			setattr(c, d, str(getattr(data, d)))

		#
		# Set relations
		#
		# Targets
		c.targets = []
		for d in data.targets.all():
			c.targets.append(d.target_name)

		# Plugins
		c.enable_plugins = []
		for d in data.enable_plugins.all():
			l_plugin = {}
			l_plugin['plugin_name'] = str(d.plugin_name)
			l_plugin['params'] = []

			for p in d.plugin_params.all():
				l_param = {}
				l_param['param_name']  = str(p.param_name)
				l_param['param_value'] = str(p.param_value)
				l_plugin['params'].append(l_param)

			c.enable_plugins.append(l_plugin)

		# Users
		c.user = str(data.user.username)

		return c

	#----------------------------------------------------------------------
	@property
	def to_json(self):
		"""
		Returns a JSON with all info.

		:return: JSON with info.
		"""
		return { k : v for k, v in self.__dict__.iteritems() }

	#----------------------------------------------------------------------
	@property
	def to_json_brief(self):
		"""
		Returns only a json with:
		- id
		- name
		- user
		- state
		"""
		return {
		    'id'     : self.id,
		    'name'   : self.audit_name,
		    'user'         : self.user,
		    'state'        : self.audit_state
		}
