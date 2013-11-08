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

__all__ = ["AuditBridge", "ExceptionAuditNotFound", "ExceptionAudit"]

__doc__ = """This file has data structures and method to access to GoLismero engine."""

from django.conf import settings as BRIDGE
from backend.managers import *



#----------------------------------------------------------------------
#
# Exceptions
#
#----------------------------------------------------------------------
class ExceptionAuditNotFound(Exception):
	"""Audit not found."""
	pass


class ExceptionAudit(Exception):
	pass

#----------------------------------------------------------------------
#
# Managers
#
#----------------------------------------------------------------------
class AuditBridge(object):
	"""
	Audit bridge between GoLismero <-> Django
	"""

	#----------------------------------------------------------------------
	#
	# Unidirectional methods
	#
	#----------------------------------------------------------------------

	@staticmethod
	def new_audit(data):
		"""
		Creates and start a new audit.

		:param data: GoLismeroAuditData with audit info.
		:type data: GoLismeroAuditData

		:raises: ExceptionAudit
		"""
		if not isinstance(data, GoLismeroAuditData):
			raise TypeError("Expected GoLismeroAuditData, got '%s' instead" % type(data))

		config = data.to_json_console

		# Set command
		config["command"] = "scan"

		if not BRIDGE.SIMULATE:
			BRIDGE.RPC.call("audit/create", config)



	#----------------------------------------------------------------------
	@staticmethod
	def stop(audit_id): #
		"""
		Stops and audit.

		:param audit_id: string with audit ID.
		:type audit_id: str

		:raises: ExceptionAuditNotFound
		"""
		if not BRIDGE.SIMULATE:
			BRIDGE.RPC.call("audit/cancel", audit_id)



	#----------------------------------------------------------------------
	@staticmethod
	def resume(audit_id): #
		"""
		Resumes and audit.

		:param audit_id: string with audit ID.
		:type audit_id: str

		:raises: ExceptionAuditNotFound
		"""
		pass

	#----------------------------------------------------------------------
	#
	# Getters methods
	#
	#----------------------------------------------------------------------
	@staticmethod
	def get_log(audit_id): #
		"""
		Get log for and audit as format:

		:param audit_id: string with audit ID.
		:type audit_id: str

		:return: a list with info, as format:
		[
		  {
		     'plugin_id'     : str,
			 'text'          : str,
			 'verbosity'     : int,
			 'is_error'      : bool,
			 'timestamp'     : float
		  }
		]
		:rtype: list(dict)

		:raises: ExceptionAuditNotFound
		"""
		return [
		    {
		        'plugin_id' : '',
		        'text' : 'Added 4 new targets to the database.',
		        'verbosity' : '2',
		        'is_error' : '0',
		        'timestamp' : '1383390392.95667'
		    },
		    {
		        'plugin_id' : '',
		        'text' : '''Audit scope:

		    IP addresses:
		        208.84.244.10

		    Domains:
		        *.terra.es
		        terra.es
		        www.terra.es

		    Web pages:
		        http://www.terra.es/
		    ''',
		        'verbosity' : '3',
		        'is_error' : '0',
		        'timestamp' : '1383390392.95934'
		    },
		    {
		        'plugin_id' : '1',
		        'text' : 'Spidering URL: "http://www.terra.es/"',
		        'verbosity' : '2',
		        'is_error' : '0',
		        'timestamp' : '1383390393.02968'
		    }
		]

	#----------------------------------------------------------------------
	@staticmethod
	def get_results(audit_info): #
		"""
		Get audit results

		:param audit_id: string with audit ID.
		:type audit_id: str
		"""

	#----------------------------------------------------------------------
	def get_summary(audit_id): #
		"""
		Get results summary for an audit.

		:param audit_id: string with audit ID.
		:type audit_id: str

		:raises: ExceptionAuditNotFound
		"""
		pass

	#----------------------------------------------------------------------
	@staticmethod
	def get_state(audit_id): #
		"""
		Call to GoLismero core and returns the state, as a string.

		:param audit_id: string with audit ID.
		:type audit_id: str

		:return: a string with audit state.
		:type: str

		:raises: ExceptionAuditNotFound
		"""
		if not BRIDGE.SIMULATE:
			BRIDGE.RPC.call("audit/state", audit_id)



	#----------------------------------------------------------------------
	@staticmethod
	def get_details(audit_id): #
		"""
		Checks if audit details

		:param audit_id: string with audit ID.
		:type audit_id: str

		:return: Audits instance, if Audit exits. None otherwise.
		:type: Audits | None

		:raises: ExceptionAuditNotFound
		"""
		try:
			return Audit.objects.get(pk)
		except ObjectDoesNotExist:
			return None


	#----------------------------------------------------------------------
	@staticmethod
	def get_state(audit_id): #
		"""
		Call to GoLismero core and returns the state, as a string.

		:param audit_id: string with audit ID.
		:type audit_id: str

		:return: a string with audit state.
		:type: str

		:raises: ExceptionAuditNotFound
		"""
		return "running"


	#----------------------------------------------------------------------
	@staticmethod
	def get_progress(audit_id): #
		"""
		Call to GoLismero core and returns the state, as a string.

		:param audit_id: string with audit ID.
		:type audit_id: str

        :return: GoLismeroAuditProgress object
        :rtype: GoLismeroAuditProgress

		:raises: ExceptionAuditNotFound
		"""
		a = {
		  'current_stage' : "recom",
		  'steps'         : 1,
		  'tests_remain'  : 21,
		  'tests_done'     : 5
		}
		return GoLismeroAuditProgress(a)



	#----------------------------------------------------------------------
	@staticmethod
	def get_details(audit_id): #
		"""
		Get audit details.

		:param audit_id: string with audit ID.
		:type audit_id: str

		:return: GoLismeroAuditData instance, if Audit exits. None otherwise.
		:type: GoLismeroAuditData | None

		:raises: ExceptionAuditNotFound
		"""
		try:
			if not BRIDGE.SIMULATE:
				return BRIDGE.RPC.call("audit/details")
		except ObjectDoesNotExist:
			return None



