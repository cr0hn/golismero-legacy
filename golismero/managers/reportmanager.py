#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn@cr0hn.com
  Mario Vilas | mvilas@gmail.com

Golismero project site: http://code.google.com/p/golismero/
Golismero project mail: golismero.project@gmail.com

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

__all__ = ["ReportManager"]

from ..api.logger import Logger
from .priscillapluginmanager import *

from traceback import format_exc


#------------------------------------------------------------------------------
class ReportManager (object):
    """This class manages the generation of reports."""


    #----------------------------------------------------------------------
    def __init__(self, config, orchestrator):
        """
        Constructor.

        :param config: Audit configuration.
        :type config: AuditConfig.

        :param orchestrator: Orchestrator.
        :type orchestrator: Orchestrator
        """

        # Keep a reference to the audit configuration.
        self.__config = config

        # Keep a reference to the orchestrator.
        self.__orchestrator = orchestrator

        # Load the report plugins.
        self.__plugins = PriscillaPluginManager().load_plugins(
            config.enabled_plugins, config.disabled_plugins,
            category = "report")

        # Map report plugins to output files.
        self.__reporters = {}
        for output_file in config.reports:
            if output_file in self.__reporters:
                continue
            found = [name for name, plugin in self.__plugins.iteritems()
                          if plugin.is_supported(output_file)]
            if not found:
                raise ValueError(
                    "Output file format not supported: %r" % output_file)
            if len(found) > 1:
                msg = "Output file format supported by multiple plugins!\nFile: %r\nPlugins:\n\t"
                msg %= output_file
                msg += "\n\t".join(found)
                raise ValueError(msg)
            self.__reporters[output_file] = found[0]


    @property
    def config(self):
        return self.__config

    @property
    def orchestrator(self):
        return self.__orchestrator


    #----------------------------------------------------------------------
    def generate_reports(self, notifier):
        """
        Generate all the requested reports for the audit.

        :param notifier: Plugin notifier.
        :type notifier: AuditNotifier

        :returns: int -- Number of plugins executed.
        """

        # Abort if reporting is disabled.
        if not self.__reporters:
            return 0

        # For each output file, run its corresponding report plugin.
        count = 0
        for output_file, plugin_name in self.__reporters.iteritems():
            try:
                notifier.start_report(self.__plugins[plugin_name], output_file)
            except Exception, e:
                Logger.log_error("Failed to start report for file %r: %s" % (output_file, e.message))
                Logger.log_error_more_verbose(format_exc())
            count += 1
        return count
