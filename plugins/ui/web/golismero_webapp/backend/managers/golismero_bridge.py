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
	def new_audit(data): #
		"""
		Creates and start a new audit.

		:param data: GoLismeroAuditData with audit info.
		:type data: GoLismeroAuditData

		:raises: ExceptionAudit
		"""
		if not isinstance(data, GoLismeroAuditData):
			raise TypeError("Expected GoLismeroAuditData, got '%s' instead" % type(data))



	#----------------------------------------------------------------------
	@staticmethod
	def stop(audit_id): #
		"""
		Stops and audit.

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

		[
		  {
		     'plugin_id'     : str,
			 'text'          : str,
			 'verbosity'     : int,
			 'is_error'      : bool,
			 'timestamp'     : float
		  }
		]

		:param audit_id: string with audit ID.
		:type audit_id: str

		:raises: ExceptionAuditNotFound
		"""
		return [
		    {
		       'plugin_id'     : 'spider',
		       'text'          : 'spider demo',
		       'verbosity'     : 1,
		       'is_error'      : False,
		       'timestamp'     : 1383390392.95667
		    }
		]

	#----------------------------------------------------------------------
	@staticmethod
	def get_results(audit_id): #
		"""


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
		return "new"



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
			return Audits.objects.get(pk)
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
		return "new"


	#----------------------------------------------------------------------
	@staticmethod
	def get_progress(audit_id): #
		"""
		Call to GoLismero core and returns the state, as a string.

		:param audit_id: string with audit ID.
		:type audit_id: str

		:return: a string with audit state.
		:type: str

		:raises: ExceptionAuditNotFound
		"""
		return "new"



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
			return BRIDGE.RCP.call("do_audit_det")
		except ObjectDoesNotExist:
			return None



