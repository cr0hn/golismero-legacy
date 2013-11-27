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

__all__ = ["AuditBridge", "ExceptionAuditNotFound", "ExceptionAudit", "ExceptionAuditUnknown", "ExceptionAuditNotStarted"]

__doc__ = """This file has data structures and method to access to GoLismero engine."""

from django.conf import settings as BRIDGE
from backend.managers import *
from os.path import join


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
class ExceptionAuditNotStarted(Exception):
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
    Audit bridge between GoLismero <-> GUI
    """


    #----------------------------------------------------------------------
    #
    # Unidirectional methods
    #
    #----------------------------------------------------------------------


    #----------------------------------------------------------------------
    @staticmethod
    def import_audit(data, imports):
        """
        Create a new audit from imported data

        :param data: GoLismeroAuditData with audit info.
        :type data: GoLismeroAuditData

        :param imports: list of files to import.
        :type imports: list(str)

        :raises: ExceptionAudit
        """
        if not isinstance(data, GoLismeroAuditData):
            raise TypeError("Expected GoLismeroAuditData, got '%s' instead" % type(data))

        config = data.to_json_console
        print config

        # Set command
        config["command"]        = "IMPORT"
        # Set BBDD store location
        config["audit_db"]       = "%s.db" % join(data.store_path,config['audit_name'])

        # Config the plu
        config["enable_plugins"] += ",import" # Add import plugins
        config["disable_plugins"] = ['all']

        print "-" * 90
        print config
        # Config the file imports
        config["imports"]        = imports

        if not BRIDGE.SIMULATE:
            try:
                BRIDGE.RPC.call("audit/create", config)
            except Exception,e:
                raise ExceptionAudit(e)



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
        config["audit_db"] = "%s.db" % join(data.store_path,config['audit_name'])
        print config
        if not BRIDGE.SIMULATE:
            try:
                BRIDGE.RPC.call("audit/create", config)
            except:
                raise ExceptionAudit()


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
            try:
                BRIDGE.RPC.call("audit/cancel", audit_id)
            except:
                raise ExceptionAuditNotFound()


    #----------------------------------------------------------------------
    #
    # Getter methods
    #
    #----------------------------------------------------------------------


    #----------------------------------------------------------------------
    @staticmethod
    def get_log(audit_id):
        """
        Get log for and audit as format:

        :param audit_id: string with audit ID.
        :type audit_id: str

        :returns: a list with info, as format:
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

        :raises: ExceptionAuditNotFound, ExceptionAuditNotStarted
        """

        if not BRIDGE.SIMULATE:
            try:
                rpc_response = BRIDGE.RPC.call("audit/log", audit_id)
            except:
                raise ExceptionAuditNotFound()


            if rpc_response == "error":
                raise ExceptionAuditNotStarted()

            if not rpc_response:
                raise ExceptionAuditNotFound()
            r = [
                GoLismeroAuditLog({
                    #'plugin_id'     : r[0],
                    'level'         : r[1],
                    'text'          : r[2],
                    'verbosity'     : r[3],
                    'is_error'      : r[4],
                    'timestamp'     : r[5]
                })

                for r in rpc_response
            ]

            return r


    #----------------------------------------------------------------------
    @staticmethod
    def get_summary(audit_id):
        """
        Get results summary for an audit.

        :param audit_id: GoLismeroAuditSummary object
        :type audit_id: GoLismeroAuditSummary

        :raises: ExceptionAuditNotFound, ExceptionAuditNotStarted
        """
        if not BRIDGE.SIMULATE:
            try:
                rpc_response = BRIDGE.RPC.call("audit/summary", audit_id)
            except:
                raise ExceptionAuditNotFound()


            # If info not found -> audit not found
            if not rpc_response:
                raise ExceptionAuditNotFound()

            if rpc_response == "error":
                raise ExceptionAuditNotStarted()

            return GoLismeroAuditSummary(rpc_response)
        else:
            return GoLismeroAuditSummary({
                'vulns_number'            : '10',
                'discovered_hosts'        : '4',
                'total_hosts'             : '6',
                'vulns_by_level'          : {
                    'info'     : '4',
                    'low'      : '2',
                    'medium'   : '2',
                    'high'     : '1',
                    'critical' : '1',
                }
            })


    #----------------------------------------------------------------------
    @staticmethod
    def get_state(audit_id):
        """
        Call to GoLismero core and returns the state, as a string.

        :param audit_id: string with audit ID.
        :type audit_id: str

        :returns: a string with audit state.
        :type: str

        :raises: ExceptionAuditNotFound, ExceptionAuditNotStarted
        """
        if not BRIDGE.SIMULATE:
            try:
                r = BRIDGE.RPC.call("audit/state", audit_id)
            except:
                raise ExceptionAuditNotFound()


            if not r:
                raise ExceptionAuditNotFound("Audit not found")

            if r == "error":
                raise ExceptionAuditNotStarted()

            return r

        return "running"


    #----------------------------------------------------------------------
    @staticmethod
    def get_progress(audit_id):
        """
        Call to GoLismero core and returns the state, as a string.

        :param audit_id: string with audit ID.
        :type audit_id: str

        :returns: GoLismeroAuditProgress object
        :rtype: GoLismeroAuditProgress | None

        :raises: ExceptionAuditNotFound, ExceptionAuditNotStarted
        """
        m_return = None

        if not BRIDGE.SIMULATE:
            try:
                rpc_response = BRIDGE.RPC.call("audit/progress", audit_id)
            except:
                raise ExceptionAuditNotFound()

            if not rpc_response:
                raise ExceptionAuditNotFound()

            if rpc_response == "error":
                raise ExceptionAuditNotStarted()

            try:
                steps = rpc_response[0]
                stage = rpc_response[1]

                if stage == "start":
                    current_state = "start"
                elif stage in ("finish", "cancel"):
                    current_state = "cleanup"
                else:
                    current_state = "running"

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

                return GoLismeroAuditProgress(m_return)

            except IndexError:
                return None
        return None
