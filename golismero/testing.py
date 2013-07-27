#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A rudimentary testing bootstrap.
"""

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: https://github.com/cr0hn/golismero/
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

__all__ = ["PluginTester"]

from golismero.api.data import LocalDataCache
from golismero.api.config import Config
from golismero.api.file import FileManager
from golismero.api.net.cache import NetworkCache
from golismero.api.net.http import HTTP
from golismero.common import AuditConfig, OrchestratorConfig, get_default_config_file
from golismero.database.auditdb import AuditDB
from golismero.main.orchestrator import Orchestrator
from golismero.managers.auditmanager import Audit
from golismero.managers.processmanager import PluginContext
from golismero.messaging.message import Message
from golismero.scope import AuditScope

from os import getpid


#------------------------------------------------------------------------------
class PluginTester(object):
    """
    A simple plugin test bootstrap.
    """


    #--------------------------------------------------------------------------
    def __init__(self, orchestrator_config = None, audit_config = None):
        """
        :param orchestrator_config: Optional orchestrator configuration.
        :type orchestrator_config: OrchestratorConfig

        :param audit_config: Optional audit configuration.
        :type audit_config: AuditConfig
        """

        # If no config was given, use the default.
        if orchestrator_config is None:
            orchestrator_config = OrchestratorConfig()
        if not hasattr(orchestrator_config, "profile"):
            orchestrator_config.profile = None
            orchestrator_config.profile_file = None
        if not hasattr(orchestrator_config, "config_file"):
            orchestrator_config.config_file = get_default_config_file()
        if audit_config is None:
            audit_config = AuditConfig()
        if not hasattr(audit_config, "profile"):
            audit_config.profile = orchestrator_config.profile
            audit_config.profile_file = orchestrator_config.profile_file
        if not hasattr(audit_config, "config_file"):
            audit_config.config_file = orchestrator_config.config_file

        # Get the audit name, or generate one if missing.
        audit_name = audit_config.audit_name
        if not audit_name:
            audit_name = Audit.generate_audit_name()
            audit_config.audit_name = audit_name

        # Instance the Orchestrator.
        orchestrator = Orchestrator(orchestrator_config)

        # Instance an Audit.
        audit = Audit(audit_config, orchestrator)

        # Calculate the audit scope.
        audit_scope = AuditScope(audit_config)
        audit._Audit__audit_scope = audit_scope

        # Create the audit database.
        audit._Audit__database = AuditDB(audit_name, audit_config.audit_db)

        # Register the Audit with the AuditManager.
        orchestrator.auditManager._AuditManager__audits[audit_name] = audit

        # Setup a local plugin execution context.
        Config._context  = PluginContext(
            getpid(),
            orchestrator._Orchestrator__queue,
            audit_name   = audit_name,
            audit_config = audit_config,
            audit_scope  = audit_scope,
        )

        # Initialize the environment.
        HTTP._initialize()
        NetworkCache._clear_local_cache()
        FileManager._update_plugin_path()
        LocalDataCache._enabled = True  # force enable
        LocalDataCache.on_run()

        # Save the Orchestrator instance.
        self.__orchestrator = orchestrator


    #--------------------------------------------------------------------------
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        self.cleanup()


    #--------------------------------------------------------------------------
    @property
    def orchestrator(self):
        return self.__orchestrator


    #--------------------------------------------------------------------------
    def run_plugin(self, plugin_name, data_or_msg):
        """
        Run the requested plugin. You can test both data and messages.

        It's the caller's resposibility to check the input message queue of
        the Orchestrator instance if the plugin sends any messages.

        :param plugin_name: Name of the plugin to test.
        :type plugin_name: str

        :param data_or_msg: Data or message to send.
        :type data_or_msg: Data | Message

        :returns: Return value from the plugin.
        :rtype: *
        """

        # Load the plugin.
        plugin_info = self.orchestrator.pluginManager.get_plugin_by_name(plugin_name)
        plugin = self.orchestrator.pluginManager.load_plugin_by_name(plugin_name)
        Config._context._PluginContext__plugin_info = plugin_info

        try:

            # Initialize the environment.
            HTTP._initialize()
            NetworkCache._clear_local_cache()
            FileManager._update_plugin_path()
            LocalDataCache.on_run()

            # If it's a message, send it and return.
            if isinstance(data_or_msg, Message):
                return plugin.recv_msg(data_or_msg)

            # It's data.
            data = data_or_msg

            # If the data is out of scope, don't run the plugin.
            if not data.is_in_scope():
                return []

            # Make sure the plugin can actually process this type of data.
            # Raise an exception if it doesn't.
            found = False
            for clazz in plugin.get_accepted_info():
                if isinstance(data, clazz):
                    found = True
                    break
            if not found:
                msg = "Plugin %s cannot process data of type %s"
                raise TypeError(msg % (plugin_name, type(data)))

            # Call the plugin.
            result = plugin.recv_info(data)

            # Process the results.
            result = LocalDataCache.on_finish(result)

            # If the input data was not returned, make sure to add it.
            if data not in result:
                result.insert(0, data)

            # Return the results.
            return result

        finally:

            # Unload the plugin.
            Config._context._PluginContext__plugin_info = None


    #--------------------------------------------------------------------------
    def cleanup(self):
        """
        Cleanup the testing mock environment.

        You can't call run_plugin() again after calling this method,
        you'll need to create a new PluginTester instance.
        """

        FileManager._update_plugin_path()
        NetworkCache._clear_local_cache()
        LocalDataCache.on_run()
        HTTP._finalize()

        self.orchestrator.close()
        del self.__orchestrator  # so we can't call run_plugin again
