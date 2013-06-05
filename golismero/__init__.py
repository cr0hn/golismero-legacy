#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
GoLismero 2.0 - The web knife.

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

__all__ = ["launcher", "OrchestratorConfig", "AuditConfig"]

from .common import OrchestratorConfig, AuditConfig
from .main.orchestrator import Orchestrator


#----------------------------------------------------------------------
# Exported function to launch GoLismero

def launcher(options, *audits):

    # We need to validate the arguments,
    # since it may be called from outside.
    if not isinstance(options, OrchestratorConfig):
        raise TypeError("Expected OrchestratorConfig, got %s instead" % type(options))
    for params in audits:
        if not isinstance(params, AuditConfig):
            raise TypeError("Expected AuditConfig, got %s instead" % type(options))

    # Run the Orchestrator.
    with Orchestrator(options) as orchestrator:
        orchestrator.run(*audits)
