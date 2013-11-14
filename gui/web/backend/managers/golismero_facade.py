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

__all__ = ["GoLismeroFacadeAudit",
           "GoLismeroFacadeAuditNotAllowedHostException",
           "GoLismeroFacadeAuditNotFoundException",
           "GoLismeroFacadeAuditNotPluginsException",
           "GoLismeroFacadeAuditFinishedException",
           "GoLismeroFacadeAuditStoppedException",
           "GoLismeroFacadeAuditRunningException",
           "GoLismeroFacadeAuditStateException",
           "GoLismeroFacadeAuditUnknownException",
           "GoLismeroFacadeReportUnknownFormatException",
           "GoLismeroFacadeReportNotAvailableException"]

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
class GoLismeroFacadeAuditNotAllowedHostException(Exception):
    """Hosts nos allowed"""
class GoLismeroFacadeAuditNotPluginsException(Exception):
    """Not plugins selected"""
class GoLismeroFacadeAuditNotFoundException(Exception):
    """Audit not found"""
class GoLismeroFacadeAuditFinishedException(Exception):
    """Audit is finished"""
class GoLismeroFacadeAuditStoppedException(Exception):
    """Audit is stopped"""
class GoLismeroFacadeAuditRunningException(Exception):
    """Audit is currently running."""
class GoLismeroFacadeAuditStateException(Exception):
    """Audit state general exception"""
class GoLismeroFacadeAuditUnknownException(Exception):
    """Audit unknown exception"""
class GoLismeroFacadeReportUnknownFormatException(Exception):
    """Unknown format of report requested"""
class GoLismeroFacadeReportNotAvailableException(Exception):
    """Unknown format of report requested"""

#------------------------------------------------------------------------------
class GoLismeroFacadeAudit(object):
    """
    This class acts as Facade between REST API and GoLismero Backend.
    """


    AVAILABLE_REPORT_FORMATS = ["rst", "html", "txt", "xml"]

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

        :returns: GoLismeroAuditData instance, if Audit exits. None otherwise.
        :type: GoLismeroAuditData | None

        :raises: GoLismeroFacadeAuditNotFoundException, TypeError
        """
        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        try:

            m_audit = Audit.objects.get(pk=audit_id)

            return GoLismeroAuditData.from_django(m_audit)

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()


    #----------------------------------------------------------------------
    @staticmethod
    def get_state(audit_id):
        """
        Get audit state. Each call updates the state of provided audit.

        :param audit_id: audit ID.
        :type audit_id: str

        :returns: an string with the state
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
                m_new_state = AuditBridge.get_state(GoLismeroFacadeAudit._get_unique_id(m_audit.id, m_audit.audit_name))
            except ExceptionAuditNotFound:
                # Audit not working
                m_new_state = "finished"

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

        :returns: GoLismeroAuditProgress object
        :rtype: GoLismeroAuditProgress

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditRunningException, TypeError, GoLismeroFacadeAuditFinishedException
        """
        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        # Call to GoLismero
        try:

            m_audit = Audit.objects.get(pk=audit_id)

            # If audit are not running return error.
            if m_audit.audit_state != "running":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is not running. Can't obtain progress from not running audits." % str(audit_id))

            try:
                return AuditBridge.get_progress(GoLismeroFacadeAudit._get_unique_id(m_audit.id, m_audit.audit_name))
            except ExceptionAuditNotFound:
                raise GoLismeroFacadeAuditFinishedException()

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

        :returns: an string with the log
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

            return ''.join([ "[%s] %s" % (datetime.datetime.fromtimestamp(float(x['timestamp'])).strftime('%Y-%m-%d %H:%M:%S:%s'), x['text']) for x in AuditBridge.get_log(GoLismeroFacadeAudit._get_unique_id(m_audit.id, m_audit.audit_name))])

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()


    #----------------------------------------------------------------------
    @staticmethod
    def get_results(audit_id, report_format="html"):
        """
        Get results by format.

        :param audit_id: audit ID.
        :type audit_id: str

        :param report_format: report format. Availables: rst, xml, html, text
        :type report_format: str

        :returns: return file handler ready to read report.
        :rtype: file

        :raises: GoLismeroFacadeReportUnknownFormatException, GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeReportNotAvailableException
        """
        EXTENSIONS_BY_FORMAT = {
            'xml'    : 'xml',
            'html'   : 'html',
            'rst'    : 'rst',
            'text'   : 'txt'
        }
        try:
            # Check report format
            if report_format not in GoLismeroFacadeAudit.AVAILABLE_REPORT_FORMATS:
                raise GoLismeroFacadeReportUnknownFormatException("Unknown report format '%s'." % report_format)

            m_audit = Audit.objects.get(pk=audit_id)

            # Update state
            #GoLismeroFacadeAudit.get_state(m_audit.id)

            if m_audit.audit_state != "finished":
                raise GoLismeroFacadeReportNotAvailableException("Not finished audit. Report is not available.")

            # Get path of audit info
            l_path = path.join(get_user_settings_folder(), str(m_audit.id))

            # Each folder has one file for each type of report called "report.FORMAT"
            if not path.exists(l_path):
                raise GoLismeroFacadeReportNotAvailableException("Requested report is not available")

            # Get report

            return file(path.join(l_path, "report.%s" % EXTENSIONS_BY_FORMAT[report_format]), "rU")

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()




    #----------------------------------------------------------------------
    @staticmethod
    def get_results_summary(audit_id):
        """
        Get results by format.

        :param audit_id: audit ID.
        :type audit_id: str

		:returns: return a dic as format:
		{
		   'vulns_number'            = int
		   'discovered_hosts'        = int # Host discovered into de scan process
		   'total_hosts'             = int
		   'vulns_by_level'          = {
		      'info'     : int,
			  'low'      : int,
			  'medium'   : int,
			  'high'     : int,
			  'critical' : int,
		}

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditStateException
        """

        try:
            m_audit = Audit.objects.get(pk=audit_id)


            if m_audit.audit_state != "running":
                raise GoLismeroFacadeAuditStateException("Audit not running. Only can get summary from running audits.")

            # Get summary
            try:
                GoLismeroFacadeAudit.get_state(GoLismeroFacadeAudit._get_unique_id(m_audit.id, m_audit.audit_name))
            except ExceptionAuditNotFound,e:
                raise GoLismeroFacadeAuditStateException("Audit not running. Only can get summary from running audits.")

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()




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

        :returns: A list of GoLismeroAuditData objects.
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
		  "targets": ["127.0.0.2", "mysite.com"],
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

            # Checks for local host hosts
            t_h = [t for t in m_targets if t.startswith("127")]
            if len(t_h) > 0:
                raise GoLismeroFacadeAuditNotAllowedHostException("Host '%s' not allowed" % ",".join(t_h))

            m_targets_stored = []
            for t in m_targets:
                l_target         = Target(target_name=t)
                l_target.save()

                # Add to global
                m_targets_stored.append(l_target)

            #
            # PLUGINS
            #
            m_enable_plugins        = data.get('enable_plugins', [])

            # Not plugins selected
            if len(m_enable_plugins) == 0:
                raise GoLismeroFacadeAuditNotPluginsException("Not plugins selected.")


            # Transform "all" plugins in GoLismero format. For GoLismero, an empty list means
            # all plugins selected.
            if len(m_enable_plugins) == 1:
                if isinstance(m_enable_plugins, basestring):
                    if m_enable_plugins[0].strip().lower() == "all":
                        m_enable_plugins = []

            m_enable_plugins_stored = []

            for p in m_enable_plugins:
                l_plugin             = Plugins()
                l_plugin.plugin_name = p.get("plugin_name")
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

            for kk in m_enable_plugins_stored:
                m_audit.enable_plugins.add(kk)

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
            m_audit = Audit.objects.get(pk=audit_id)

            # Update the state.
            m_state = GoLismeroFacadeAudit.get_state(audit_id)

            # If audit is running, cant' delete it.
            if m_state == "running":
                raise GoLismeroFacadeAuditRunningException("Audit '%s' is running. Can't delete. Stop it first." % str(audit_id))

            m_audit.delete()

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()


    #----------------------------------------------------------------------
    @staticmethod
    def start(audit_id):
        """
        Start an audit in state 'new.

        :param audit_id: Audit id.
        :type audit_id: str

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditStateException, TypeError
        """

        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        try:
            m_audit = Audit.objects.get(pk=audit_id)

            # Checks if state is correct
            if m_audit.audit_state != "new":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is '%s'. Only new audits can be started." % (str(m_audit.id), m_audit.audit_state))

            #
            # Create dir to store audit info
            #

            # Create folder: home folder + audit id
            l_path = path.join(get_user_settings_folder(), str(m_audit.id))
            #if path.exists(l_path):
                #raise GoLismeroFacadeAuditUnknownException("Storage folder for audit already exits: '%s'" % l_path)

            #try:
                #os.mkdir(l_path)
            #except Exception,e:
                #raise GoLismeroFacadeAuditUnknownException("Can't create audit files in: '%s'" % l_path)

            # Configuration
            audit_config            = GoLismeroAuditData.from_django(m_audit)
            audit_config.store_path = l_path

            # Send to GoLismero core
            AuditBridge.new_audit(audit_config)

            # Change the state
            m_audit.audit_state = "running"
            m_audit.save()

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
            m_audit = Audit.objects.get(pk=audit_id)

            # Checks if state is correct
            if m_audit.audit_state != "running":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is '%s'. Only running audits can be stopped." % (str(m_audit.id), m_audit.audit_state))

            # Send to GoLismero core
            AuditBridge.stop(GoLismeroFacadeAudit._get_unique_id(m_audit.id, m_audit.audit_name))

            # Change the state
            m_audit.audit_state = "stopped"
            m_audit.save()

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
            m_audit = Audit.objects.get(pk=audit_id)

            # Checks if state is correct
            if m_audit.audit_state != "running":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is '%s'. Only running audits can be paused." % (str(m_audit.id), m_audit.audit_state))

            # Send to GoLismero core
            AuditBridge.stop(GoLismeroFacadeAudit._get_unique_id(m_audit.id, m_audit.audit_name))

            # Change the state
            m_audit.audit_state = "paused"
            m_audit.save()

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
            m_audit = Audit.objects.get(pk=audit_id)

            # Checks if state is correct
            if m_audit.audit_state != "paused":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is '%s'. Only paused audits can be resumed." % (str(m_audit.id), m_audit.audit_state))

            # Send to GoLismero core
            try:
                AuditBridge.resume(GoLismeroFacadeAudit._get_unique_id(m_audit.id, m_audit.audit_name))
            except ExceptionAuditUnknown:
                m_audit.audit_state = "error"
                m_audit.save()
                raise GoLismeroFacadeAuditStateException("Error while try to resume the audit '%s'." % m_audit.id)

            # Change the state
            m_audit.audit_state = "running"
            m_audit.save()

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()


    #----------------------------------------------------------------------
    @staticmethod
    def _get_unique_id(audit_id, audit_name=None):
        """
        GoLismero core don't understand audits ID. Instead use audit names. For that
        we need to generate a unique audit name.

        Unique audit name is based in audit ID + audit name, like:

        AUDIT_NAME + "_" + ID

        :param audit_id: Audit id.
        :type audit_id: str

        :param audit_name: string with name of audit.
        :type audit_name: str

        :returns: string with unique audit ID.
        :rtype: str
        """
        if not isinstance(audit_id, basestring) and not isinstance(audit_id, int):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        if not audit_name:
            if not isinstance(audit_name, basestring):
                raise TypeError("Expected basestring, got '%s' instead" % type(audit_name))

            return "%s_%s" % (audit_name, str(audit_id))

        # Get audit name
        try:
            audit_name = Audit.objects.get(pk=audit_id).audit_name

            return "%s_%s" % (audit_name, str(audit_id))

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()
