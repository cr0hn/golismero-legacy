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

__all__ = ["AuditBridge", "ExceptionAuditNotFound", "ExceptionAudit", "ExceptionAuditUnknown"]

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


class ExceptionAuditUnknown(Exception):
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
		config["command"]     = "scan"
		# Set BBDD store location
		config["db_location"] = data.store_path

		if not BRIDGE.SIMULATE:
			BRIDGE.RPC.call("audit/create", config)



	#----------------------------------------------------------------------
	@staticmethod
	def stop(audit_id):
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

		:raises: ExceptionAuditNotFound, ExceptionAuditUnknown
		"""
		pass

	#----------------------------------------------------------------------
	#
	# Getters methods
	#
	#----------------------------------------------------------------------
	@staticmethod
	def get_log(audit_id):
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

		if not BRIDGE.SIMULATE:
			rpc_response = BRIDGE.RPC.call("audit/log", audit_id)

			return [
			          {
			              'plugin_id'     : r[0],
			              'text'          : r[1],
			              'verbosity'     : r[2],
			              'is_error'      : r[3],
			              'timestamp'     : r[4]
			          }

			          for r in rpc_response
			]

	#----------------------------------------------------------------------
	#@staticmethod
	#def get_results(audit_info): #
		#"""
		#Get audit results

		#:param audit_id: string with audit ID.
		#:type audit_id: str
		#"""

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
	def get_state(audit_id):
		"""
		Call to GoLismero core and returns the state, as a string.

		:param audit_id: string with audit ID.
		:type audit_id: str

		:return: a string with audit state.
		:type: str

		:raises: ExceptionAuditNotFound
		"""
		if not BRIDGE.SIMULATE:
			rpc_response = BRIDGE.RPC.call("audit/state", audit_id)

			if not rpc_response:
				return "finished"

			return rpc_response[0][1]
		return "running"





	#----------------------------------------------------------------------
	@staticmethod
	def get_progress(audit_id):
		"""
		Call to GoLismero core and returns the state, as a string.

		:param audit_id: string with audit ID.
		:type audit_id: str

        :return: GoLismeroAuditProgress object
        :rtype: GoLismeroAuditProgress

		:raises: ExceptionAuditNotFound
		"""
		m_return = None

		if not BRIDGE.SIMULATE:
			rpc_response = BRIDGE.RPC.call("audit/state", audit_id)

			if not rpc_response:
				raise ExceptionAuditNotFound()

			steps         = rpc_response[0][0]
			current_state = rpc_response[0][1]
			tests_remain  = 0
			tests_done    = 0
			for t in rpc_response[2]:
				l_progress = t[2] # Value between 0.0 - 100.0

				if l_progress == 100.0:
					tests_done   += 1
				else:
					tests_remain +=1

			m_return = {
		      'current_stage' : current_state,
		      'steps'         : int(steps),
		      'tests_remain'  : tests_remain,
		      'tests_done'    : tests_done
		    }

		else:

			m_return = {
			  'current_stage' : "recon",
			  'steps'         : 1,
			  'tests_remain'  : 21,
			  'tests_done'     : 5
			}
		return GoLismeroAuditProgress(m_return)




