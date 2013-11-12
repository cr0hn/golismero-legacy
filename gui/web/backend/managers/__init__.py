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
from os.path import join

class GoLismeroAuditProgress(object):
	"""

	Get the audit state. This class acts as java POJO, having these attributes:

	- current_stage :: str
	- steps         :: int
	- tests_remain  :: int
	- tests_done     :: int

	"""

	PROPERTIES     = ["current_stage", "steps", "tests_remain", "tests_done"]
	REPORT_FORMATS = ["html", "text", "rst", "xml"]

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
	    "user",
	    "disable_plugins"
	]

	COMPLEX_PROPERTIES = ["enable_plugins", "user", "targets"]

	#----------------------------------------------------------------------
	def __init__(self):
		for v in GoLismeroAuditData.PROPERTIES:
			setattr(self, v, None)

		# Set list properties
		self.targets         = []
		self.enable_plugins  = []

		# store path
		self.store_path      = None


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
		Returns a JSON with all info in format:

		{
		  "audit_name": "asdfasdf",
		  "targets": [ "127.0.0.1", "mysite.com" ],
		  "enabled_plugins": [
			{
			  "plugin_name": "openvas",
			  "params": [
				{
				  "param_name": "profile",
				  "param_value": "Full and fast"
				},
				{
				  "param_name": "user",
				  "param_value": "admin"
				},
				{
				  "param_name": "password",
				  "param_value": "admin"
				}
			  ]
			}
		  ],
		  "disabled_plugins": ["spider","nikto"]

		:return: JSON with info.
		"""
		return { k : v for k, v in self.__dict__.iteritems() }

	#----------------------------------------------------------------------
	@property
	def to_json_brief(self):
		"""
		Returns only a json in format:

		{
		   'id'    : int,
		   'name'  : str,
		   'user'  : str,
		   'state' : str
		}

		:return: dict
		:rtype: dict
		"""
		return {
		    'id'     : self.id,
		    'name'   : self.audit_name,
		    'user'   : self.user,
		    'state'  : self.audit_state
		}

	#----------------------------------------------------------------------
	@property
	def to_json_console(self):
		"""
		:return: return a JSON formated for GoLismero console:
		{
		  "audit_name": "asdfasdf_1",
		  "targets": ["127.0.0.1", "mysite.com" ],
		  "enabled_plugins": ["openvas"]
		  "disabled_plugins": ["spider","nikto"]

		}
		:rtype: dict
		"""
		# Add simple config
		m_config                    = { k : str(v) for k, v in self.__dict__.iteritems() if k not in GoLismeroAuditData.COMPLEX_PROPERTIES and not isinstance(v, list) and not isinstance(v, dict)}

		# Fix audit name
		m_config['audit_name']      = "%s_%s" % (self.audit_name, str(self.id))

		# Add targets
		m_config['targets']         = self.__dict__["targets"]

		# Add plugins enabled
		m_config['enable_plugins']  = []


		#
		# FIXME in next version:
		#
		# For this version, golismero will generate reports in all possible formats.
		# After, core will choice what to serve.
		#
		m_config['reports']         = [join(self.store_path, "report.%s" % x) for x in GoLismeroAuditProgress.REPORT_FORMATS]

		#
		# Plugins
		#
		m_tmp_plugin_args           = []
		# Add plugins config
		for p in self.enable_plugins:
			l_plugin_name = p["plugin_name"]

			m_config['enable_plugins'].appen(l_plugin_name)

			# Plugins params
			for pp in p.get("params", []):
				m_tmp_plugin_args.append([l_plugin_name, pp["plugin_name"], pp["plugin_value"]])

		# Add plugin args?
		if m_tmp_plugin_args:
			m_config['plugin_args'] = m_tmp_plugin_args

		# No plugins?
		if len(m_config['enable_plugins']) == 0:
			m_config['enable_plugins'] = ["all"]

		return m_config
