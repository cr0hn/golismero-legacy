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

__all__ = ["GoLismeroFacadeAuditPolling",
           "GoLismeroFacadeState",
           "GoLismeroFacadeAuditNotAllowedHostException",
           "GoLismeroFacadeAuditNotFoundException",
           "GoLismeroFacadeAuditNotPluginsException",
           "GoLismeroFacadeAuditFinishedException",
           "GoLismeroFacadeAuditStoppedException",
           "GoLismeroFacadeAuditRunningException",
           "GoLismeroFacadeAuditNotStartedException",
           "GoLismeroFacadeAuditStateException",
           "GoLismeroFacadeAuditUnknownException",
           "GoLismeroFacadeReportUnknownFormatException",
           "GoLismeroFacadeReportNotAvailableException",
           "GoLismeroFacadeAuditImportFileExitsException",
           "GoLismeroFacadeTimeoutException"]

import os
import os.path as path
import datetime
from zipfile import ZipFile, BadZipfile

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
class GoLismeroFacadeAuditNotStartedException(Exception):
    """Audit not started"""
class GoLismeroFacadeAuditStateException(Exception):
    """Audit state general exception"""
class GoLismeroFacadeAuditUnknownException(Exception):
    """Audit unknown exception"""
class GoLismeroFacadeReportUnknownFormatException(Exception):
    """Unknown format of report requested"""
class GoLismeroFacadeReportNotAvailableException(Exception):
    """Unknown format of report requested"""

class GoLismeroFacadeAuditImportFileExitsException(Exception):
    """Import exception"""

class GoLismeroFacadeTimeoutException(Exception):
    """Timeout when connect with the core"""


#------------------------------------------------------------------------------
#
# Audit methods: Polling and pushing aproaches.
#
#------------------------------------------------------------------------------
class GoLismeroFacadeAuditCommon(object):
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
    def get_results(audit_id, report_format="html"):
        """
        Get results by format.

        :param audit_id: audit ID.
        :type audit_id: str

        :param report_format: report format. Availables: rst, xml, html, text
        :type report_format: str

        :returns: return file handler ready to read report.
        :rtype: file

        :raises: GoLismeroFacadeAuditNotStartedException, GoLismeroFacadeReportUnknownFormatException, GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeReportNotAvailableException
        """

        try:
            # Check report format
            report_format = report_format.lower().strip()

            if report_format not in EXTENSIONS_BY_FORMAT:
                raise GoLismeroFacadeReportUnknownFormatException("Unknown report format '%s'." % report_format)

            m_audit = Audit.objects.get(pk=audit_id)

            # Update state
            #GoLismeroFacadeAuditPolling.get_state(m_audit.id)


            if m_audit.audit_state == "error":
                raise GoLismeroFacadeAuditNotStartedException()
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
            #GoLismeroFacadeAudit.get_state(l_audit_id)

            # Store audit info
            m_return.append(GoLismeroFacadeAuditPolling.get_audit(str(l_audit_id)))

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

            # Check regex, if specified
            if data.get("subdomain_regex", False):
                import re
                reg_expr = data.get("subdomain_regex")
                try:
                    re.compile(reg_expr)
                except re.error:
                    raise GoLismeroFacadeAuditUnknownException("'subdomain_regex' value contain a not valid regex: %s" % reg_expr)

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
            #if len(m_enable_plugins) == 0:
                #raise GoLismeroFacadeAuditNotPluginsException("Not plugins selected.")


            # Transform "all" plugins in GoLismero format. For GoLismero, an empty list means
            # all plugins selected.
            #if len(m_enable_plugins) == 1:
                #if isinstance(m_enable_plugins, basestring):
                    #if m_enable_plugins[0].strip().lower() == "all":
                        #m_enable_plugins = []

            m_enable_plugins_stored = []

            if len(m_enable_plugins) == 0:
                l_plugin             = Plugins()
                l_plugin.plugin_name = "all"
                l_plugin.save()
                m_enable_plugins_stored.append(l_plugin)
            else:
                for p in m_enable_plugins:
                    l_plugin             = Plugins()
                    l_plugin.plugin_name = p.get("plugin_name")
                    l_plugin.save()

                    # Plugins params
                    for pp in p.get("params", []):
                        l_param = PluginParameters()
                        l_param.param_name    = pp['param_name']
                        l_param.param_value   = pp['param_value']
                        l_param.plugin        = l_plugin
                        l_param.audit         = m_audit
                        l_param.save()
                    # Add to total
                    m_enable_plugins_stored.append(l_plugin)

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

    @staticmethod
    def audit_import(data):
        """
        Creates an audit instance into BBDD. Dara param must have this format:

        {
           "audit_name":: str,
           "imports":: [str],
           "enable_plugins" :: [
              {
                 'plugin_name'  :: str,
                 'params' :: [
                    {
                       'param_name'  :: str,
                       'param_value' :: str
                    }
                 ]
              }
           ]
        }

        :param data: A JSON info.
        :type data: dict

        :raises: TypeError, ValueError, GoLismeroFacadeAuditUnknownException
        """
        if not isinstance(data, dict):
            raise TypeError("Expected dict, got '%s' instead" % type(data))

        try:

            #
            # AUDIT
            #
            m_audit = Audit()
            m_audit.audit_name = str(data.get("audit_name"))
            m_audit.audit_type = "import"

            # Set user
            m_audit.user = User.objects.get(pk=5)
            m_audit.save()


            #
            # PLUGINS
            #
            m_enable_plugins        = data.get('enable_plugins', [])
            m_enable_plugins_stored = []

            if len(m_enable_plugins) == 0:
                l_plugin             = Plugins()
                l_plugin.plugin_name = "all"
                l_plugin.save()
                m_enable_plugins_stored.append(l_plugin)
            else:
                for p in m_enable_plugins:
                    l_plugin             = Plugins()
                    l_plugin.plugin_name = p.get("plugin_name")
                    l_plugin.save()

                    # Plugins params
                    for pp in p.get("params", []):
                        l_param = PluginParameters()
                        l_param.param_name    = pp['param_name']
                        l_param.param_value   = pp['param_value']
                        l_param.plugin        = l_plugin
                        l_param.audit         = m_audit
                        l_param.save()
                    # Add to total
                    m_enable_plugins_stored.append(l_plugin)

            # Relations
            for kk in m_enable_plugins_stored:
                m_audit.enable_plugins.add(kk)



            # Local storage
            l_path       = path.join(get_user_settings_folder(), str(m_audit.id))

            # Load data from database
            dj = GoLismeroAuditData.from_django(m_audit)
            dj.store_path = l_path

            # Prepare config
            tmp_import     = list(set((os.path.abspath(y.strip()) for y in data.get("imports"))))
            # Checks if files exits
            m_imports      = []
            for x in tmp_import:
                # File exists?
                if not os.path.exists(x):
                    raise GoLismeroFacadeAuditImportFileExitsException("File '%s' not exists." % x)
                # Is really a file?
                if not os.path.isfile(x):
                    raise GoLismeroFacadeAuditImportFileExitsException("'%s' is not a file." % x)

                # Checks if file is a zip
                if x.endswith("zip"):
                    # Extract
                    try:
                        l_zip = ZipFile(x)

                        for l_zip_file in l_zip.filelist:
                            # Checks if file is a dir
                            if os.path.sep in l_zip_file.filename:
                                continue
                            l_zip.extract(l_zip_file, l_path)

                            l_file_name = os.path.join(l_path, l_zip_file.filename)
                            m_imports.append(l_file_name)

                    except BadZipfile:
                        raise ValueError("Error zip file format for file: '%s'" % x)
                else:
                    m_imports.append(x)

            # Launch command
            AuditBridge.import_audit(dj, m_imports)

            # Update audit state
            m_audit.audit_state = "running"
            m_audit.save()

            return m_audit.id
        except ExceptionTimeout:
            raise GoLismeroFacadeTimeoutException()
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

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditRunningException, TypeError, GoLismeroFacadeTimeoutException
        """

        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        try:
            m_audit = Audit.objects.get(pk=audit_id)

            # Update the state.
            #m_state = GoLismeroFacadeAuditPolling.get_state(audit_id)

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

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditStateException, TypeError, GoLismeroFacadeTimeoutException
        """

        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        try:
            m_audit = Audit.objects.get(pk=audit_id)

            # Checks if state is correct
            if m_audit.audit_state != "new":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is '%s'. Only new audits can be started." % (str(m_audit.id), m_audit.audit_state))

            # Create folder: home folder + audit id
            l_path = path.join(get_user_settings_folder(), str(m_audit.id))

            # Configuration
            audit_config            = GoLismeroAuditData.from_django(m_audit)
            audit_config.store_path = l_path

            #
            # Create dir to store audit info
            #
            if path.exists(l_path):
                raise GoLismeroFacadeAuditUnknownException("Storage folder for audit already exists: '%s'" % l_path)
            try:
                os.mkdir(l_path)
            except Exception,e:
                raise GoLismeroFacadeAuditUnknownException("Can't create audit files in: '%s'. Error: %s" % l_path, str(e))


            try:
                # Send to GoLismero core
                AuditBridge.new_audit(audit_config)
            except ExceptionTimeout:
                raise GoLismeroFacadeTimeoutException()
            except ExceptionAudit, e:
                raise GoLismeroFacadeAuditStateException("Error starting audit: %s" % e)


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

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditStateException, TypeError, GoLismeroFacadeTimeoutException
        """

        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        try:
            m_audit = Audit.objects.get(pk=audit_id)

            if m_audit.audit_state == "error":
                raise GoLismeroFacadeAuditNotStartedException()

            # Checks if state is correct
            if m_audit.audit_state != "running":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is '%s'. Only running audits can be stopped." % (str(m_audit.id), m_audit.audit_state))

            # Send to GoLismero core
            try:
                r = AuditBridge.stop(GoLismeroFacadeAuditPolling._get_unique_id(m_audit.id, m_audit.audit_name))
            except ExceptionTimeout:
                raise GoLismeroFacadeTimeoutException()

            if r == False:
                raise GoLismeroFacadeAuditStateException()

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

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditStateException, TypeError, GoLismeroFacadeTimeoutException
        """

        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        try:
            m_audit = Audit.objects.get(pk=audit_id)

            if m_audit.audit_state == "error":
                raise GoLismeroFacadeAuditNotStartedException()

            # Checks if state is correct
            if m_audit.audit_state != "running":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is '%s'. Only running audits can be paused." % (str(m_audit.id), m_audit.audit_state))

            # Send to GoLismero core
            try:
                r = AuditBridge.stop(GoLismeroFacadeAuditPolling._get_unique_id(m_audit.id, m_audit.audit_name))
            except ExceptionTimeout:
                raise GoLismeroFacadeTimeoutException()

            if r == False:
                raise GoLismeroFacadeAuditStateException()


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

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditStateException, TypeError, GoLismeroFacadeTimeoutException
        """

        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        try:

            if m_audit.audit_state == "error":
                raise GoLismeroFacadeAuditNotStartedException()

            m_audit = Audit.objects.get(pk=audit_id)

            # Checks if state is correct
            if m_audit.audit_state != "paused":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is '%s'. Only paused audits can be resumed." % (str(m_audit.id), m_audit.audit_state))

            # Create folder: home folder + audit id
            l_path = path.join(get_user_settings_folder(), str(m_audit.id))

            # Configuration
            audit_config            = GoLismeroAuditData.from_django(m_audit)
            audit_config.store_path = l_path

            # Send to GoLismero core
            try:
                AuditBridge.new_audit(audit_config)
            except ExceptionTimeout:
                raise GoLismeroFacadeTimeoutException()
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
        if not isinstance(audit_id, basestring) and not isinstance(audit_id, int) and not isinstance(audit_id, long):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        if audit_name:
            if not isinstance(audit_name, basestring):
                raise TypeError("Expected basestring, got '%s' instead" % type(audit_name))
            return "%s_%s" % (audit_name, str(audit_id))

        # Get audit name
        try:
            audit_name = Audit.objects.get(pk=audit_id).audit_name

            return "%s_%s" % (audit_name, str(audit_id))

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()




#------------------------------------------------------------------------------
class GoLismeroFacadeAuditPolling(GoLismeroFacadeAuditCommon):
    """
    This calls implements real time methods using polling.
    """

    #----------------------------------------------------------------------
    #
    # Getters
    #
    #----------------------------------------------------------------------

    #----------------------------------------------------------------------
    @staticmethod
    def get_state(audit_id):
        """
        Get audit state and update it. Each call updates the state of provided audit.

        :param audit_id: audit ID.
        :type audit_id: str

        :returns: an string with the state
        :rtype: str

        :raises: GoLismeroFacadeAuditNotFoundException, TypeError, GoLismeroFacadeTimeoutException
        """
        try:
            audit_id = long(audit_id)
        except TypeError:
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        # Call to GoLismero
        try:
            m_audit = Audit.objects.get(pk=audit_id)

            if m_audit.audit_state == "error":
                raise GoLismeroFacadeAuditNotStartedException()

            # If audit is new or finished return
            if m_audit.audit_state != "running":
                return m_audit.audit_state

            #
            # FIXME: When GoLismero core works, do that instead of above commands.
            #
            m_new_state = None
            try:

                m_new_state = AuditBridge.get_state(GoLismeroFacadeAuditPolling._get_unique_id(m_audit.id, m_audit.audit_name))

                # Do that because AuditBridge regurns the STAGE, not the state
                if m_new_state != "finished":
                    m_new_state = "running"
            except ExceptionTimeout:
                raise GoLismeroFacadeTimeoutException()
            except ExceptionAuditNotStarted:
                m_audit.audit_state = "error"
                m_audit.save()

                # Audit not working
                raise GoLismeroFacadeAuditNotStartedException()

            except ExceptionAuditNotFound:
                # Audit not working
                raise GoLismeroFacadeAuditNotFoundException()

            #
            # Ensure that golismero was generated all reports
            #
            if m_new_state == "finished":

                # Only when audit type is SCAN type
                if m_audit.audit_type.lower() == "scan":
                    m_total = 0
                    for f in REPORT_FORMATS:
                        l_folder =  get_user_settings_folder()
                        l_id     = str(m_audit.id)
                        l_format = f
                        l_path   = "%s%s/report.%s" % (l_folder, l_id, f)

                        if os.path.exists(l_path):
                            m_total +=1

                    if m_total == len(REPORT_FORMATS):
                        m_new_state = "finished"
                    else:
                        m_new_state = "running"

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

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditRunningException, TypeError, GoLismeroFacadeAuditFinishedException, GoLismeroFacadeTimeoutException
        """
        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        # Call to GoLismero
        try:

            # Update state
            GoLismeroFacadeAuditPolling.get_state(audit_id)

            m_audit = Audit.objects.get(pk=audit_id)

            if m_audit.audit_state == "error":
                raise GoLismeroFacadeAuditNotStartedException()

            # If audit are not running return error.
            #if m_audit.audit_state != "running":
                #raise GoLismeroFacadeAuditStateException("Audit '%s' is not running. Can't obtain progress from not running audits." % str(audit_id))

            try:
                r = AuditBridge.get_progress(GoLismeroFacadeAuditPolling._get_unique_id(m_audit.id, m_audit.audit_name))
                if r:
                    # Store the state
                    GoLismeroFacadeState.set_progress(audit_id, r)
                    return r

            except ExceptionTimeout:
                raise GoLismeroFacadeTimeoutException()
            except ExceptionAuditNotStarted:
                # Audit error when started
                raise GoLismeroFacadeAuditNotStartedException()
            except ExceptionAuditNotFound:
                # Return last progress state, because audit is finished
                try:
                    return GoLismeroFacadeState.get_progress(audit_id)
                except ExceptionAuditNotFound:
                    # If not info stored in database returned general info
                    return GoLismeroAuditProgress({
                        'current_stage' : "cleanup",
                        'steps'         : 1,
                        'tests_remain'  : 0,
                        'tests_done'    : 1,
                      })

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

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditStateException, TypeError, GoLismeroFacadeTimeoutException
        """
        if not isinstance(audit_id, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(audit_id))

        # Call to GoLismero
        try:

            m_audit = Audit.objects.get(pk=audit_id)

            if m_audit.audit_state == "error":
                raise GoLismeroFacadeAuditNotStartedException()

            # If audit is new, return state
            if m_audit.audit_state == "new":
                raise GoLismeroFacadeAuditStateException("Audit '%s' is not running. Can't obtain log for non started audits." % str(audit_id))

            m_info = None
            try:
                m_info = AuditBridge.get_log(GoLismeroFacadeAuditPolling._get_unique_id(m_audit.id, m_audit.audit_name))

                if m_info:
                    # Store data
                    GoLismeroFacadeState.set_log(audit_id, m_info)

                    return '\n'.join([ "[%s] %s" % (
                        datetime.datetime.fromtimestamp(
                            float(x.to_json['timestamp'])).strftime('%Y-%m-%d %H:%M:%S:%s'), x.to_json['text']) for x in m_info])

            except ExceptionTimeout:
                raise GoLismeroFacadeTimeoutException()
            except ExceptionAuditNotStarted:
                # Audit error when started
                raise GoLismeroFacadeAuditNotStartedException()

            except ExceptionAuditNotFound:
                # Return last log
                try:
                    m_info = GoLismeroFacadeState.get_log(audit_id)

                    return '\n'.join([ "[%s] %s" % (
                        x.to_json['timestamp'].strftime('%Y-%m-%d %H:%M:%S:%s'), x.to_json['text']) for x in m_info])

                except ExceptionAuditNotFound:
                    # If not info stored in database returned general info
                    return ""


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
        }

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditStateException, GoLismeroFacadeTimeoutException
        """

        try:
            m_audit = Audit.objects.get(pk=audit_id)

            if m_audit.audit_state == "error":
                raise GoLismeroFacadeAuditNotStartedException()

            #if m_audit.audit_state != "running":
                #raise GoLismeroFacadeAuditStateException("Audit not running. Only can get summary from running audits.")

            # Get summary
            try:
                r =  AuditBridge.get_summary(GoLismeroFacadeAuditPolling._get_unique_id(m_audit.id, m_audit.audit_name)).to_json

                if r:
                    # Store info
                    GoLismeroFacadeState.set_summary(audit_id, r)
                    return r
            except ExceptionTimeout:
                raise GoLismeroFacadeTimeoutException()
            except ExceptionAuditNotStarted:
                # Audit error when started
                raise GoLismeroFacadeAuditNotStartedException()

            except ExceptionAuditNotFound,e:
                try:
                    return GoLismeroFacadeState.get_summary(audit_id).to_json
                except GoLismeroFacadeAuditNotFoundException:
                    # If not info stored in database, returned only total hosts scanned
                    return {
                        'vulns_number'            : '0',
                        'discovered_hosts'        : len(m_audit.targets.all()),
                        'total_hosts'             : '0',
                        'vulns_by_level'          : {
                            'info'     : '0',
                            'low'      : '0',
                            'medium'   : '0',
                            'high'     : '0',
                            'critical' : '0',
                        }
                    }

        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()






#------------------------------------------------------------------------------
class GoLismeroFacadeAuditPushing(GoLismeroFacadeAuditCommon):
    """
    This calls implements real time methods using polling.
    """

    #----------------------------------------------------------------------
    #
    # Getters
    #
    #----------------------------------------------------------------------

    #----------------------------------------------------------------------
    @staticmethod
    def get_state(audit_id):
        """
        Get audit state and update it. Each call updates the state of provided audit.

        :param audit_id: audit ID.
        :type audit_id: str

        :returns: an string with the state
        :rtype: str

        :raises: GoLismeroFacadeAuditNotFoundException, TypeError
        """
        raise NotImplemented()

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
        raise NotImplemented()


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
        raise NotImplemented()

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
        }

        :raises: GoLismeroFacadeAuditNotFoundException, GoLismeroFacadeAuditStateException
        """
        raise NotImplemented()



#------------------------------------------------------------------------------
class GoLismeroFacadeState(object):
    """
    This class has the methods to store real time information for an audit:
       - progress.
       - summary.
       - log.
       - plugins errors.
       - plugins warning.
       - audit stages
    """
    #----------------------------------------------------------------------
    @staticmethod
    def set_progress(audit_id, data, token=None):
        """
        Update audit progress status .

        :param audit_id: Audit id.
        :type audit_id: str

        :param data: Progress object
        :type data: GoLismeroAuditProgress

        :param token: auth token
        :type token: str

        :raises: GoLismeroFacadeAuditNotFoundException
        """
        # Audit exits?
        try:
            m_audit = Audit.objects.get(pk=audit_id)
        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()

        # Get Audit progress old info
        m_audit_progress = None
        try:
            m_audit_progress = RTAuditProgress.objects.get(audit__id=audit_id)
        except ObjectDoesNotExist:
            # If not exit the object, create it
            m_audit_progress = RTAuditProgress()
            m_audit_progress.audit = m_audit
            m_audit_progress.save()

        # Checks if all parameters are equals
        save = False
        for x in GoLismeroAuditProgress.PROPERTIES:
            if getattr(m_audit_progress, x) != data[x]:
                save = True

        if save:
            # Update params if there is some differents values
            for x in GoLismeroAuditProgress.PROPERTIES:
                setattr(m_audit_progress, x, data[x])
            # Save changes
            m_audit_progress.save()





    #----------------------------------------------------------------------
    @staticmethod
    def get_progress(audit_id, token=None):
        """
        Get audit progress status.

        :param audit_id: Audit id.
        :type audit_id: str

        :param token: auth token
        :type token: str

        :return: a GoLismeroAuditProgress type.
        :rtype: GoLismeroAuditProgress

        :raises: GoLismeroFacadeAuditNotFoundException
        """


        # Audit exits?
        try:
            m_audit = Audit.objects.get(pk=audit_id)
        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()

        # Get Audit progress old info
        m_audit_progress = None
        try:
            m_audit_progress = RTAuditProgress.objects.get(pk=audit_id)
        except ObjectDoesNotExist:
            # If not exit the object, create it
            raise GoLismeroFacadeAuditNotFoundException()

        # If audit current stage is finished, updated
        if m_audit.current_stage != m_audit_progress.current_stage:
            m_audit.current_stage = m_audit_progress.current_stage
            m_audit_progress.save()

        info = {}
        # Checks if all parameters are equals
        for x in GoLismeroAuditProgress.PROPERTIES:
            info[x] = getattr(m_audit_progress, x)

        return GoLismeroAuditProgress(info)



    #----------------------------------------------------------------------
    @staticmethod
    def set_summary(audit_id, data, token=None):
        """
        Update audit summary.

        :param audit_id: Audit id.
        :type audit_id: str

        :param data: Summary object
        :type data: GoLismeroAuditSummary

        :param token: auth token
        :type token: str

        :raises: GoLismeroFacadeAuditNotFoundException
        """
        # Audit exits?
        try:
            m_audit = Audit.objects.get(pk=audit_id)
        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()

        # Get Audit progress old info
        m_audit_summary = None
        try:
            m_audit_summary = RTAuditSummary.objects.get(audit__id=audit_id)
        except ObjectDoesNotExist:
            # If not exit the object, create it
            m_audit_summary = RTAuditSummary()
            m_audit_summary.audit = m_audit
            m_audit_summary.save()

        # If total vulns or total hosts are not equals, update is needed.
        save = False
        for x in ("vulns_number", "total_hosts"):
            if getattr(m_audit_summary, x) != data[x]:
                save = True

        if save:
            # Update general info
            for x in GoLismeroAuditSummary.PROPERTIES:
                setattr(m_audit_summary, x, data[x])
            # Update vulns by level
            for x in GoLismeroAuditSummary.LEVEL_VULNS:
                setattr(m_audit_summary, "vuln_level_%s_number" % x, data["vulns_by_level"][x])

            # Save changes
            m_audit_summary.save()



    #----------------------------------------------------------------------
    @staticmethod
    def get_summary(audit_id, token=None):
        """
        Get audit progress status.

        :param audit_id: Audit id.
        :type audit_id: str

        :param token: auth token
        :type token: str

        :return: a GoLismeroAuditSummary type.
        :rtype: GoLismeroAuditSummary

        :raises: GoLismeroFacadeAuditNotFoundException
        """


        # Audit exits?
        try:
            Audit.objects.get(pk=audit_id)
        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()

        # Get Audit progress old info
        m_audit_summary = None
        try:
            m_audit_summary = RTAuditSummary.objects.get(pk=audit_id)
        except ObjectDoesNotExist:
            # If not exit the object, create it
            raise GoLismeroFacadeAuditNotFoundException()

        info = {}
        # Checks if all parameters are equals
        for x in GoLismeroAuditSummary.PROPERTIES:
            info[x] = getattr(m_audit_summary, x)
            # Update vulns by level
        info["vulns_by_level"] = {}
        for x in GoLismeroAuditSummary.LEVEL_VULNS:
            info["vulns_by_level"][x] = getattr(m_audit_summary, "vuln_level_%s_number" % x)

        return GoLismeroAuditSummary(info)




    #----------------------------------------------------------------------
    @staticmethod
    def set_log(audit_id, data, token=None):
        """
        Update audit log.

        :param audit_id: Audit id.
        :type audit_id: str

        :param data: Audit log object list
        :type data: list(GoLismeroAuditLog)

        :param token: auth token
        :type token: str

        :raises: GoLismeroFacadeAuditNotFoundException
        """
        if not isinstance(data, list):
            raise TypeError("Expected list, got '%s' instead" % type(data))

        # Audit exits?
        try:
            m_audit = Audit.objects.get(pk=audit_id)
        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()


        for d in data:
            # Create new log entry
            l_info = RTAuditLog()
            l_info.audit = m_audit

            # Set properties
            for x in GoLismeroAuditLog.PROPERTIES:
                if x == "timestamp":
                    setattr(l_info, x, datetime.datetime.fromtimestamp(d[x]))
                else:
                    setattr(l_info, x, d[x])

            # Save changes
            l_info.save()


    #----------------------------------------------------------------------
    @staticmethod
    def get_log(audit_id, token=None):
        """
        Get audit log status.

        :param audit_id: Audit id.
        :type audit_id: str

        :param token: auth token
        :type token: str

        :return: a list of GoLismeroAuditInfo type.
        :rtype: list(GoLismeroAuditInfo)

        :raises: GoLismeroFacadeAuditNotFoundException
        """

        # Audit exits?
        try:
            Audit.objects.get(pk=audit_id)
        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()

        # Get Audit progress old info
        logs = None
        try:
            logs = RTAuditLog.objects.filter(audit__id=audit_id).all()
        except ObjectDoesNotExist:
            # If not exit the object, create it
            raise GoLismeroFacadeAuditNotFoundException()

        m_return        = []
        m_return_append = m_return.append

        for log in logs:
            info = {}
            # Checks if all parameters are equals
            for x in GoLismeroAuditLog.PROPERTIES:
                info[x] = getattr(log, x)
                # Update vulns by level

            m_return_append(GoLismeroAuditLog(info))

        return m_return


    #----------------------------------------------------------------------
    @staticmethod
    def set_stage(audit_id, stage, token=None):
        """
        Update audit progress stage.

        :param audit_id: Audit id.
        :type audit_id: str

        :param stage: string with stage
        :type stage: str

        :param token: auth token
        :type token: str

        :raises: GoLismeroFacadeAuditNotFoundException
        """
        # Audit exits?
        try:
            m_audit = Audit.objects.get(pk=audit_id)
        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()

        if m_audit.current_stage != stage:
            m_audit.current_stage = stage
            m_audit.save()


    #----------------------------------------------------------------------
    @staticmethod
    def set_stage(audit_id, token=None):
        """
        Get audit stage

        :param audit_id: Audit id.
        :type audit_id: str

        :param token: auth token
        :type token: str

        :raises: GoLismeroFacadeAuditNotFoundException
        """
        # Audit exits?
        try:
            m_audit = Audit.objects.get(pk=audit_id)
            return m_audit.current_stage
        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()









    #----------------------------------------------------------------------
    #
    # WARNING: Not tested methods
    #
    #----------------------------------------------------------------------
    @staticmethod
    def _plugin_set_generic(audit_id, data, action, token=None): # TEST NEEDED
        """
        Common function plugin setting.

        :param audit_id: Audit id.
        :type audit_id: str

        :param data: Audit info object
        :type data: GoLismeroAuditInfo

        :param action: action to get: (error|warning)
        :type action: str

        :param token: auth token
        :type token: str

        :raises: GoLismeroFacadeAuditNotFoundException
        """
        ACTIONS = {
            'error'    : RTPluginErrors,
            'warning'  : RTPluginWarning,
        }

        if action not in ACTIONS:
            raise ValueError("Unknown action: %s" % action)

        # Audit exits?
        try:
            m_audit = Audit.objects.get(pk=audit_id)
        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()



        # Create new log entry
        m_info = ACTIONS[action]()
        m_info.audit = m_audit

        # Set properties
        for x in GoLismeroAuditInfo.PROPERTIES:
            setattr(m_info, x, d[x])

        # Save changes
        m_info.save()

    #----------------------------------------------------------------------
    @staticmethod
    def _plugin_get_generic(audit_id, action, token=None): # TEST NEEDED
        """
        Common function for getting actions.

        :param audit_id: Audit id.
        :type audit_id: str

        :param token: auth token
        :type token: str

        :param action: action to get: (error|warning)
        :type action: str

        :return: a GoLismeroAuditInfo type.
        :rtype: GoLismeroAuditInfo
        """
        ACTIONS = {
            'error'    : RTPluginErrors,
            'warning'  : RTPluginWarning,
        }

        if action not in ACTIONS:
            raise ValueError("Unknown action: %s" % action)


        # Audit exits?
        try:
            Audit.objects.get(pk=audit_id)
        except ObjectDoesNotExist:
            raise GoLismeroFacadeAuditNotFoundException()


        try:
            logs = ACTIONS[action].objects.filter(audit__id=audit_id).all()
        except ObjectDoesNotExist:
            # If not exit the object, create it
            raise GoLismeroFacadeAuditNotFoundException()

        m_return        = []
        m_return_append = m_return.append

        for log in logs:
            info = {}
            # Checks if all parameters are equals
            for x in GoLismeroAuditInfo.PROPERTIES:
                info[x] = getattr(log, x)
                # Update vulns by level

            m_return_append(GoLismeroAuditInfo(info))

        return m_return


    #----------------------------------------------------------------------
    @staticmethod
    def set_plugin_errors(audit_id, data, token=None): # TEST NEEDED
        """
        Update error for a plugin in an audit

        :param audit_id: Audit id.
        :type audit_id: str

        :param data: Progress object
        :type data: GoLismeroAuditProgress

        :param token: auth token
        :type token: str

        :raises: GoLismeroFacadeAuditNotFoundException
        """
        return GoLismeroFacadeState._plugin_set_generic(audit_id, data, "error", token=token)

    #----------------------------------------------------------------------
    @staticmethod
    def get_plugin_errors(audit_id, token=None): # TEST NEEDED
        """
        Get error for a plugin in an audit

        :param audit_id: Audit id.
        :type audit_id: str

        :param token: auth token
        :type token: str

        :raises: GoLismeroFacadeAuditNotFoundException
        """
        return GoLismeroFacadeState._plugin_get_generic(audit_id, data, "error", token=token)

    #----------------------------------------------------------------------
    @staticmethod
    def set_plugin_warning(audit_id, data, token=None): # TEST NEEDED
        """
        Update error for a plugin in an audit

        :param audit_id: Audit id.
        :type audit_id: str

        :param data: Progress object
        :type data: GoLismeroAuditProgress

        :param token: auth token
        :type token: str

        :raises: GoLismeroFacadeAuditNotFoundException
        """
        return GoLismeroFacadeState._plugin_set_generic(audit_id, data, "warning", token=token)

    #----------------------------------------------------------------------
    @staticmethod
    def get_plugin_warning(audit_id, token=None): # TEST NEEDED
        """
        Get error for a plugin in an audit

        :param audit_id: Audit id.
        :type audit_id: str

        :param token: auth token
        :type token: str

        :raises: GoLismeroFacadeAuditNotFoundException
        """
        return GoLismeroFacadeState._plugin_get_generic(audit_id, data, "warning", token=token)


