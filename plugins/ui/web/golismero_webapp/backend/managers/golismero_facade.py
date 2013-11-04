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

__doc__ = """

This file contains data, classes and methods to manage GoLismero engine.

Classes in this file acts as facade pattern.

Scheme of process is:

+------+      +--------+           +------------------+
| REST | <--> | Facade | <-->|<--> | GoLismero Bridge |
+------+      +--------+     |     +------------------+
                             |
                             |     +------+
                             |<--> | BBDD |
                                   +------+

"""

__all__ = ["GoLismeroFacadeAudit", "GoLismeroFacadeAuditNotFoundException", "GoLismeroFacadeAuditStoppedException", "GoLismeroFacadeAuditRunningException"]

from backend.managers.golismero_bridge import *
from backend.managers import *
from backend.models import *


from django.db.models import ObjectDoesNotExist



#----------------------------------------------------------------------
#
# Exceptions
#
#----------------------------------------------------------------------
class GoLismeroFacadeAuditNotFoundException(Exception):
    """Audit not found"""

class GoLismeroFacadeAuditStoppedException(Exception):
    """Audit is stopped"""

class GoLismeroFacadeAuditRunningException(Exception):
    """Audit is currently running."""




#------------------------------------------------------------------------------
class GoLismeroFacadeAudit(object):
    """
    This class acts as Facade between REST API and GoLismero Backend.
    """


    #----------------------------------------------------------------------
    #
    # Aux methods
    #
    #----------------------------------------------------------------------
    @staticmethod
    def audit2json(audits):
        """
        From an Audit list gets json list like:

        [
           {
                'id'     : str,
                'name'   : str,
                'user'   : str,
                'state'  : str
           }
        ]

        :param audits: Audit list
        :type audits: list(Audits)

        :return: A json with list of audit info.
        :rtype: list(dict)
        """
        m_info = []
        for l_audit in audits:
            m_info.append({
                'id'     : l_audit.id,
                'name'   : l_audit.audit_name,
                'user'   : l_audit.user.username,
                'state'  : l_audit.audit_state
            })

        return m_info


    #----------------------------------------------------------------------
    #
    # Getters
    #
    #----------------------------------------------------------------------
    @staticmethod
    def get_audit(audit_id):
        """
        Get an Audit structure.

        :param audit_id: string with audit ID.
        :type audit_id: str

        :return: Audits instance, if Audit exits. None otherwise.
        :type: Audits | None
        """
        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        m_return = None
        try:

            m_audit = Audits.objects.get(audit_id)

            # Checks GoLismero state:
            #
            # TODO
            m_new_state = GoLismeroFacadeAudit.get_audit_state(audit_id)

            #  Update audit state into BBDD
            if m_audit.audit_state != m_new_state:
                m_audit.audit_state = m_new_state
                m_audit.save()

            return m_audit
        except ObjectDoesNotExist:
            return None

    #----------------------------------------------------------------------
    @staticmethod
    def get_state(audit_id):
        """
        Get audit state.

        :param audit_id: audit ID.
        :type audit_id: str

        :return: an string with the progress
        :rtype: str
        """
        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        # Call to GoLismero
        try:
            return "new"
            #return AuditBridge.get_state(audit_id)
        except ExceptionAuditNotRunning:
            pass

    #----------------------------------------------------------------------
    @staticmethod
    def get_progress(audit_id): #
        """
        Get audit state.

        :param audit_id: audit ID.
        :type audit_id: str

        :return: an AuditProgress object.
        :rtype: AuditProgress
        """
        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        return AuditProgress({
              'current_stage' : "recon",
              'steps'         : 2,
              'tests_remain'  : 4,
              'tests_done'     : 25
        })

        # Call to GoLismero
        try:
            #m_state = AuditBridge.get_progress(audit_id)
            m_state = AuditProgress({
                  'current_stage' : "recon",
                  'steps'         : 2,
                  'tests_remain'  : 4,
                  'tests_done'     : 25
            })

            return m_state
        except Exception,e:
            return str(e)



    #----------------------------------------------------------------------
    @staticmethod
    def get_list(audit_id):
        """
        Get audit list
        """

    #----------------------------------------------------------------------
    @staticmethod
    def get_details(audit_id):
        """"""

    #----------------------------------------------------------------------
    @staticmethod
    def get_log(audit_id):
        """"""


    #----------------------------------------------------------------------
    @staticmethod
    def get_results(audit_id):
        """"""


    #----------------------------------------------------------------------
    @staticmethod
    def get_detail(audit_id):
        """"""

    #----------------------------------------------------------------------
    #
    # Binary actions
    #
    #----------------------------------------------------------------------
    @staticmethod
    def create(data):
        """"""
        return "asdfasfsf"

    #----------------------------------------------------------------------
    @staticmethod
    def delete(audit_id):
        """"""


    #----------------------------------------------------------------------
    @staticmethod
    def start(audit_id):
        """"""

    #----------------------------------------------------------------------
    @staticmethod
    def stop(audit_id):
        """"""

    #----------------------------------------------------------------------
    @staticmethod
    def pause(audit_id):
        """"""

    #----------------------------------------------------------------------
    @staticmethod
    def resume(audit_id):
        """"""

    #----------------------------------------------------------------------
    @staticmethod
    def search(audit_id):
        """"""
