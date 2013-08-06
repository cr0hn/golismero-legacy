#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__ = """
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

from golismero.api.config import Config
from golismero.api.data.resource.url import BaseUrl
from golismero.api.external import run_external_tool
from golismero.api.logger import Logger
from golismero.api.plugin import TestingPlugin

import os
import stat

from csv import reader
from tempfile import NamedTemporaryFile
from os.path import abspath, join, basename, exists, sep
from traceback import format_exc


#----------------------------------------------------------------------
class NiktoPlugin(TestingPlugin):


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [BaseUrl]


    #----------------------------------------------------------------------
    def recv_info(self, info):

        # Get the path to the Nikto scanner.
        cwd = basename(__file__)
        cwd = join(cwd, "nikto")
        cwd = abspath(cwd)

        # Get the path to the Nikto script.
        command = join(cwd, "nikto.pl")

        # If it doesn't exist, try the system default.
        if not exists(command):
            command = "/usr/bin/nikto"

            # If it still doesn't exist, abort.
            if not exists(command):
                Logger.log_error("Nikto not found!")
                return

        # Get the path to the configuration file.
        config = Config.plugin_config.get("config", "nikto.conf")
        config = join(cwd, config)
        config = abspath(config)

        # If it doesn't exist, try the system default.
        if not exists(config):
            config = "/etc/nikto.conf"

            # If it still doesn't exist, abort.
            if not exists(command):
                Logger.log_error("Nikto config file not found!")
                return

        # Create the temporary output file.
        with NamedTemporaryFile(suffix = ".csv") as output_file:

            # Build the command line arguments.
            args = [
                "-config", config,
                "-host", info.hostname,
                "-ssl" if info.is_https else "-nossl",
                "-port", str(info.parsed_url.port),
                "-output", output_file.name,
                "-Format", "csv",
                "-ask", "no",
                "-nointeractive",
                ##"-useproxy",
            ]
            for option in ("maxtime", "Pause", "timeout", "Tuning"):
                if option in Config.plugin_config:
                    args.extend(["-" + option, Config.plugin_config[option]])

            # On Windows, we must always call Perl explicitly.
            # On Unix, only if the script is not marked as executable.
            # If Perl is not found in the PATH, this will fail.
            # TODO: maybe look for Perl in the default location?
            if sep == "\\" or os.stat(command)[stat.ST_MODE] & stat.S_IXUSR == 0:
                args.insert(0, command)
                command = "perl"

            # Run Nikto and capture the text output.
            Logger.log("Launching Nikto against: %s" % info.hostname)
            self.update_status(progress = 0)
            output, code = run_external_tool(command, args)

            # Log the output in extra verbose mode.
            if code:
                Logger.log_error("Nikto status code: %d" % code)
                Logger.log_error_more_verbose(output)
            else:
                Logger.log_more_verbose(output)

            # Parse the scan results.
            # On error log the exception and continue.
            results = []
            try:
                with open(output_file.name, "rU") as f:
                    total = float( sum(1 for _ in f) )
                current = 0.0
                with open(output_file.name, "rU") as f:
                    self.update_status(progress = current / total * 100.0)
                    csv_reader = reader(output_file)
                    for row in csv_reader:
                        try:

                            # TODO parse each row
                            Logger.log(", ".join(row))  # XXX FIXME

                        except Exception, e:
                            Logger.log_error_verbose(str(e))
                            Logger.log_error_more_verbose(format_exc())
            except Exception, e:
                Logger.log_error_verbose(str(e))
                Logger.log_error_more_verbose(format_exc())
            self.update_status(progress = 100)

            # Log how many results we found.
            Logger.log(
                "Nikto found %d results for host %s" % (
                    len(results),
                    info.hostname,
                )
            )

            # Return the parsed results.
            return results
