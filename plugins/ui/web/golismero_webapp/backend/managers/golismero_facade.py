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

__all__ = ["GoLismeroFacadeAudit", "GoLismeroFacadeAuditNotFoundException", "GoLismeroFacadeAuditStoppedException", "GoLismeroFacadeAuditRunningException", "GoLismeroFacadeAuditStateException", "GoLismeroFacadeAuditUnknownException"]

import os
import os.path as path
import datetime

from backend.managers.golismero_bridge import *
from backend.managers import *
from backend.models import *
from backend.utils import *

from django.contrib.auth.models import User
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




class GoLismeroFacadeAuditStateException(Exception):
    pass
class GoLismeroFacadeAuditUnknownException(Exception):
    pass
#------------------------------------------------------------------------------
class GoLismeroFacadeAudit(object):
    """
    This class acts as Facade between REST API and GoLismero Backend.
    """


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

        :return: GoLismeroAuditData instance, if Audit exits. None otherwise.
        :type: GoLismeroAuditData | None

        :raises: GoLismeroFacadeAuditNotFoundException, TypeError
        """
        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        try:

            a = Audit.objects.get(pk=audit_id)

            return GoLismeroAuditData.from_django(a)

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()


    #----------------------------------------------------------------------
    @staticmethod
    def get_state(audit_id):
        """
        Get audit state. Each call updates the state of provided audit.

        :param audit_id: audit ID.
        :type audit_id: str

        :return: an string with the state
        :rtype: str

        :raises: GoLismeroFacadeAuditNotFoundException, TypeError
        """
        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        # Call to GoLismero
        try:

            m_audit = Audit.objects.get(pk=audit_id)

            # If audit is new, return state
            if m_audit.audit_state == "new":
                return "new"

            m_new_state = None
            try:
                m_new_state = AuditBridge.get_state(audit_id)
            except ExceptionAuditNotFound:
                # Audit not working
                m_new_state = "stopped"

            #  Update audit state into BBDD
            if m_audit.audit_state != m_new_state:
                m_audit.audit_state = m_new_state
                m_audit.save()

            return m_audit.audit_state
        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()

    #----------------------------------------------------------------------
    @staticmethod
    def get_progress(audit_id):
        """
        Get audit state.

        :param audit_id: audit ID.
        :type audit_id: str

        :return: GoLismeroAuditProgress object
        :rtype: GoLismeroAuditProgress

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditRunningException, TypeError
        """
        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        # Call to GoLismero
        try:

            m_audit = Audit.objects.get(pk=audit_id)

            # If audit are not running return error.
            if m_audit.audit_state != "running":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is not running. Can't obtain progress from not running audits." % str(audit_id))

            return AuditBridge.get_progress(audit_id)

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()


    #----------------------------------------------------------------------
    @staticmethod
    def get_log(audit_id):
        """
        Get audit log as string. The format, per line:

        [TIMESTAMP] TEXT

        :param audit_id: audit ID.
        :type audit_id: str

        :return: an string with the log
        :rtype: str

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditStateException, TypeError
        """
        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        # Call to GoLismero
        try:

            m_audit = Audit.objects.get(pk=audit_id)

            # If audit is new, return state
            if m_audit.audit_state == "new":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is not running. Can't obtain log for non started audits." % str(audit_id))

            return ''.join([ "[%s] %s" % (datetime.datetime.fromtimestamp(float(x['timestamp'])).strftime('%Y-%m-%d %H:%M:%S:%s'), x['text']) for x in AuditBridge.get_log(audit_id)])

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()


    #----------------------------------------------------------------------
    @staticmethod
    def get_results(audit_id): #
        """"""


    #----------------------------------------------------------------------
    #
    # Binary actions
    #
    #----------------------------------------------------------------------
    @staticmethod
    def list_audits(state="all"):
        """
        List all audits audits by their state.

        :param state: audit state. All by default.
        :type state: str

        :return: A list of GoLismeroAuditData objects.
        :type: list(GoLismeroAuditData)
        """

        m_audit_list = None
        if state == "all":
            m_audit_list = Audit.objects.all()
        else:
            m_audit_list = Audit.objects.filter(audit_state=state).all()

        m_return = []
        for l_audit in m_audit_list:
            l_audit_id = str(l_audit.id)

            # Update the state for each audit
            GoLismeroFacadeAudit.get_state(l_audit_id)

            # Store audit info
            m_return.append(GoLismeroFacadeAudit.get_audit(l_audit_id))

        return m_return


    @staticmethod
    def create(data):
        """
        Creates an audit instance into BBDD. Dara param must have this format:

		{
		  "audit_name": "asdfasdf",
		  "targets": [
			{
			  "target_name": "127.0.0.1"
			},
			{
			  "target_name": "mysite.com"
			}
		  ],
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
		}

        :param data: A JSON info.
        :type data: dict

        :raises: TypeError, ValueError, GoLismeroFacadeAuditUnknownException
        """
        if not isinstance(data, dict):
            raise TypeError("Expected dict, got '%s' instead" % type(data))

        try:
            #
            # TARGETS
            #
            m_targets  = data.get('targets', None)
            if not m_targets:
                raise ValueError("Wrong format: Targets not found.")

            m_targets_stored = []
            for t in m_targets:
                l_target             = Target()
                l_target.target_name = t['target_name']
                l_target.save()

                # Add to global
                m_targets_stored.append(l_target)



            #
            # PLUGINS
            #
            m_enable_plugins        = data.get('enable_plugins', [])
            m_enable_plugins_stored = []
            for p in m_enable_plugins:

                l_plugin             = Plugins()
                l_plugin.plugin_name = p['plugin_name']
                l_plugin.save()

                # Plugins params
                for pp in p.get("params", []):
                    l_param = PluginParameters()
                    l_param.param_name    = pp['param_name']
                    l_param.param_value   = pp['param_value']
                    l_param.plugin_params = l_plugin
                    l_param.save()

                # Add to total
                m_enable_plugins_stored.append(l_plugin)

            #
            # AUDIT
            #
            # Simple values
            m_audit = Audit()
            for k, v in data.iteritems():
                if not isinstance(v, dict) and not isinstance(v, list):
                    setattr(m_audit, k, v)

            # Set user
            m_audit.user = User.objects.get(pk=5)
            m_audit.save()

            # Relations
            for t in m_targets_stored:
                m_audit.targets.add(t)

            for p in m_enable_plugins_stored:
                m_audit.enable_plugins.add(p)

            # Store
            m_audit.save()

            return m_audit.id
        except ValueError,e:
            raise ValueError(e)
        except Exception,e:
            raise GoLismeroFacadeAuditUnknownException(e)

    #----------------------------------------------------------------------
    @staticmethod
    def delete(audit_id):
        """
        Delete an Audit

        :param audit_id: Audit id
        :type audit_id: str

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditRunningException, TypeError
        """

        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        try:
            a = Audit.objects.get(pk=audit_id)

            # Update the state.
            m_state = GoLismeroFacadeAudit.get_state(audit_id)

            # If audit is running, cant' delete it.
            if m_state == "running":
                raise GoLismeroFacadeAuditRunningException("Audit '%s' is running. Can't delete. Stop it first." % str(audit_id))

            a.delete()

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()


    #----------------------------------------------------------------------
    @staticmethod
    def start(audit_id): # Crear directorio y demas
        """
        Start an audit in state 'new.

        :param audit_id: Audit id.
        :type audit_id: str

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditStateException, TypeError
        """

        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        try:
            a = Audit.objects.get(pk=audit_id)

            # Checks if state is correct
            if a.audit_state != "new":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is '%s'. Only new audits can be started." % (str(a.id), a.audit_state))

            #
            # Create dir to store audit info
            #

            # Create folder: home folder + audit id
            l_path = path.join(get_user_settings_folder(), str(a.id))
            if path.exists(l_path):
                raise GoLismeroFacadeAuditUnknownException("Storage folder for audit already exits: '%s'" % l_path)

            try:
                os.mkdir(l_path)
            except Exception,e:
                print str(e)
                raise GoLismeroFacadeAuditUnknownException("Can't create audit files in: '%s'" % l_path)

            # Configuration
            audit_config            = GoLismeroAuditData.from_django(a)
            audit_config.store_path = l_path


            # Send to GoLismero core
            #AuditBridge.new_audit(audit_config)

            # Change the state
            a.audit_state = "running"
            a.save()

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()

    #----------------------------------------------------------------------
    @staticmethod
    def stop(audit_id):
        """
        Stop an audit in state 'new.

        :param audit_id: Audit id.
        :type audit_id: str

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditStateException, TypeError
        """

        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        try:
            a = Audit.objects.get(pk=audit_id)

            # Checks if state is correct
            if a.audit_state != "running":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is '%s'. Only running audits can be stopped." % (str(a.id), a.audit_state))

            # Send to GoLismero core
            AuditBridge.stop(audit_id)

            # Change the state
            a.audit_state = "stopped"
            a.save()

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()


    #----------------------------------------------------------------------
    @staticmethod
    def pause(audit_id):
        """
        Pause an audit in state 'new.

        :param audit_id: Audit id.
        :type audit_id: str

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditStateException, TypeError
        """

        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        try:
            a = Audit.objects.get(pk=audit_id)

            # Checks if state is correct
            if a.audit_state != "running":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is '%s'. Only running audits can be paused." % (str(a.id), a.audit_state))

            # Send to GoLismero core
            AuditBridge.stop(audit_id)

            # Change the state
            a.audit_state = "paused"
            a.save()

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()

    #----------------------------------------------------------------------
    @staticmethod
    def resume(audit_id):
        """
        Resume an audit in state 'new.

        :param audit_id: Audit id.
        :type audit_id: str

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditStateException, TypeError
        """

        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        try:
            a = Audit.objects.get(pk=audit_id)

            # Checks if state is correct
            if a.audit_state != "paused":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is '%s'. Only paused audits can be resumed." % (str(a.id), a.audit_state))

            # Send to GoLismero core
            AuditBridge.resume(audit_id)

            # Change the state
            a.audit_state = "running"
            a.save()

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()

