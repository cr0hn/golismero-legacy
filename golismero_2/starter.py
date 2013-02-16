#!/usr/bin/python

# -*- coding: utf-8 -*-
"""
GoLismero 2.0 - The web knife.

Copyright (C) 2011-2013 - Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com

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



from core.main.commonstructures import GlobalParams
from core.main.orchestrator import Orchestrator
from core.api.logger import Logger



def launcher(options):

    if not isinstance(options, GlobalParams):
        raise TypeError("Expected GlobalParams, got %s instead" % type(options))

    m_orchestrator = None

    try:
        if options.run_mode == GlobalParams.RUN_MODE.standalone:
            try:

                # Run Orchestrator
                m_orchestrator = Orchestrator(options)

                # Start UI
                m_orchestrator.start_ui()

                # New audit with command line options
                m_orchestrator.add_audit(options)

                # Wait for it to end
                m_orchestrator.wait()

            finally:
                if m_orchestrator is not None:

                    # Generate reports
                    m_orchestrator.start_report()

        elif options.run_mode == GlobalParams.RUN_MODE.cloudclient:
            raise NotImplementedError("Cloud client mode not yet implemented!")


        elif options.run_mode == GlobalParams.RUN_MODE.cloudserver:
            raise NotImplementedError("Cloud server mode not yet implemented!")

        else:
            raise ValueError("Invalid run mode: %r" % options.run_mode)

    except KeyboardInterrupt:
        Logger.log("\n[i] Stopping. Please wait...\n")
