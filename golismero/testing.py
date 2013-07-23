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

__all__ = ["test_setup", "test_plugin"]

from golismero.api.data import LocalDataCache
from golismero.api.config import Config
from golismero.common import AuditConfig, OrchestratorConfig
from golismero.main.orchestrator import Orchestrator
from golismero.managers.auditmanager import Audit
from golismero.managers.processmanager import PluginContext
from golismero.messaging.message import Message

from os import getpid


#--------------------------------------------------------------------------
def test_setup(orchestrator_config = None, audit_config = None):
    """
    A simple testing bootstrap.

    :param orchestrator_config: Optional orchestrator configuration.
    :type orchestrator_config: OrchestratorConfig

    :param audit_config: Optional audit configuration.
    :type audit_config: AuditConfig

    :returns: Orchestrator instance.
    :rtype: Orchestrator
    """

    # If no config was given, use the default.
    if orchestrator_config is None:
        orchestrator_config = OrchestratorConfig()
    if audit_config is None:
        audit_config = AuditConfig()

    # Get the audit name, or generate one if missing.
    audit_name = audit_config.audit_name
    if not audit_name:
        audit_name = Audit.generate_audit_name()
        audit_config.audit_name = audit_name

    # Instance the Orchestrator.
    orchestrator = Orchestrator(orchestrator_config)

    # Setup a local plugin execution context.
    context = PluginContext(
        getpid(), orchestrator._Orchestrator__queue,
        audit_name = audit_name,
        audit_config = audit_config,
    )
    Config._context = context

    # Return the Orchestrator instance.
    return orchestrator


#--------------------------------------------------------------------------
def test_plugin(orchestrator, plugin_name, data_or_msg):
    """
    A simple testing invoker.

    It's the caller's resposibility to check the input message queue of
    the Orchestrator instance if the plugin sends any messages.

    :param orchestrator: Instance returned by :ref:`_testing_bootstrap`().
    :type orchestrator: Orchestrator

    :param plugin_name: Name of the plugin to test.
    :type plugin_name: str

    :param data_or_msg: Data or message to send.
    :type data_or_msg: Data | Message

    :returns: Return value from the plugin.
    :rtype: *
    """

    # Load the plugin.
    plugin_info = orchestrator.pluginManager.get_plugin_by_name(plugin_name)
    plugin = orchestrator.pluginManager.load_plugin_by_name(plugin_name)
    Config._context._PluginContext__plugin_info = plugin_info

    try:

        # Initialize the environment.
        HTTP._initialize()
        NetworkCache._clear_local_cache()
        LocalDataCache.on_run()

        # If it's a message, send it and return.
        if isinstance(data_or_msg, Message):
            return plugin.recv_msg(data_or_msg)

        # If it's data, run it through the plugin and return the results.
        result = plugin.recv_info(data_or_msg)
        result = LocalDataCache.on_finish(result)
        if data_or_msg not in result:
            result.insert(0, data_or_msg)
        return result

    finally:

        # Unload the plugin.
        Config._context._PluginContext__plugin_info = None
