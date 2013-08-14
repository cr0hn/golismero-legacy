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
from golismero.api.data.resource.domain import Domain
from golismero.api.data.resource.ip import IP
from golismero.api.data.resource.url import BaseUrl, Url
from golismero.api.data.vulnerability import UrlVulnerability
from golismero.api.external import run_external_tool, \
     win_to_cygwin_path, cygwin_to_win_path
from golismero.api.logger import Logger
from golismero.api.plugin import TestingPlugin

import os
import stat

from csv import reader
from tempfile import NamedTemporaryFile
from os.path import abspath, join, basename, exists, pathsep, sep, split
from traceback import format_exc
from urlparse import urljoin


#------------------------------------------------------------------------------
class NiktoPlugin(TestingPlugin):


    #--------------------------------------------------------------------------
    def get_accepted_info(self):
        return [BaseUrl]


    #--------------------------------------------------------------------------
    def recv_info(self, info):

        # We can't calculate how long will Nikto take.
        self.update_status(progress = None)

        # Get the path to the Nikto scanner.
        cwd = split(__file__)[0]
        cwd = abspath(cwd)

        # Get the path to the Nikto script.
        nikto_script = join(cwd, "nikto.pl")

        # If it doesn't exist, try the system default.
        if not exists(nikto_script):
            nikto_script = "/usr/bin/nikto"

            # If it still doesn't exist, abort.
            if not exists(nikto_script):
                Logger.log_error("Nikto not found! File: %s" % nikto_script)
                return

        # Get the path to the configuration file.
        config = Config.plugin_args["config"]
        config = join(cwd, config)
        config = abspath(config)

        # If it doesn't exist, try the system default.
        if not exists(config):
            config = "/etc/nikto.conf"

            # If it still doesn't exist, abort.
            if not exists(command):
                Logger.log_error("Nikto config file not found! File: %s" % config)
                return

        # On Windows, we must always call Perl explicitly.
        # On POSIX, only if the script is not marked as executable.
        command = nikto_script
        if sep == "\\" or os.stat(command)[stat.ST_MODE] & stat.S_IXUSR == 0:
            if sep == "\\":
                command = "perl.exe"
            else:
                command = "perl"

            # Look for the Perl binary on the PATH. Fail if not found.
            found = False
            for candidate in os.environ.get("PATH", "").split(pathsep):
                candidate = candidate.strip()
                candidate = join(candidate, command)
                if exists(candidate):
                    found = True
                    command = candidate
                    break
            if not found:
                Logger.log_error("Perl interpreter not found!")

            # Detect if it's the Cygwin version but we're outside Cygwin.
            # If so we need to use Unix style paths.
            use_cygwin = False
            if sep == "\\":
                cygwin = split(command)[0]
                cygwin = join(cygwin, "cygwin1.dll")
                if exists(cygwin):
                    nikto_script = win_to_cygwin_path(nikto_script)
                    config = win_to_cygwin_path(config)
                    use_cygwin = True

        # Build the command line arguments.
        # The -output argument will be filled by run_nikto.
        args = [
            "-config", config,
            "-host", info.hostname,
            "-ssl" if info.is_https else "-nossl",
            "-port", str(info.parsed_url.port),
            "-Format", "csv",
            "-ask", "no",
            "-nointeractive",
            ##"-useproxy",
        ]
        if command != nikto_script:
            args.insert(0, nikto_script)
        for option in ("Pause", "timeout", "Tuning"):
            value = Config.plugin_args.get(option.lower(), None)
            if value:
                args.extend(["-" + option, value])

        # On Windows we can't open a temporary file twice
        # (although it's actually Python who won't let us).
        if sep == "\\":
            output_file = NamedTemporaryFile(suffix = ".csv", delete = False)
            try:
                output = output_file.name
                if use_cygwin:
                    output = win_to_cygwin_path(output)
                output_file.close()
                return self.run_nikto(info, output, command, args)
            finally:
                os.unlink(output_file.name)

        # On POSIX we can do things more elegantly.
        else:
            with NamedTemporaryFile(suffix = ".csv") as output_file:
                output = output_file.name
                return self.run_nikto(info, output, command, args)


    #--------------------------------------------------------------------------
    def run_nikto(self, info, output_filename, command, args):
        """
        Run Nikto and convert the output to the GoLismero data model.

        :param info: Base URL to scan.
        :type info: BaseUrl

        :param output_filename: Path to the output filename.
            The format should always be CSV.
        :type output_filename:

        :param command: Path to the Nikto executable.
            May also be the Perl interpreter executable, with the
            Nikto script as its first argument.
        :type command: str

        :param args: Arguments to pass to the executable.
        :type args: list(str)

        :returns: Results from the Nikto scan.
        :rtype: list(Data)
        """

        # Append the output file name to the arguments.
        args.append("-output")
        args.append(output_filename)

        # Turn off DOS path warnings for Cygwin.
        # Does nothing on other platforms.
        env = os.environ.copy()
        cygwin = env.get("CYGWIN", "")
        if "nodosfilewarning" not in cygwin:
            if cygwin:
                cygwin += " "
            cygwin += "nodosfilewarning"
        env["CYGWIN"] = cygwin

        # Run Nikto and capture the text output.
        Logger.log("Launching Nikto against: %s" % info.hostname)
        Logger.log_more_verbose("Nikto arguments: %s %s" % (command, " ".join(args)))
        ##output, code = run_external_tool("C:\\cygwin\\bin\\perl.exe", ["-V"], env) # DEBUG
        output, code = run_external_tool(command, args, env)

        # Log the output in extra verbose mode.
        if code:
            Logger.log_error("Nikto execution failed, status code: %d" % code)
            if output:
                Logger.log_error_more_verbose(output)
        elif output:
            Logger.log_more_verbose(output)

        # Parse the results and return them.
        return self.parse_nikto_results(info, output_filename)


    #--------------------------------------------------------------------------
    def parse_nikto_results(self, info, output_filename):
        """
        Run Nikto and convert the output to the GoLismero data model.

        :param info: Base URL to scan.
        :type info: BaseUrl

        :param output_filename: Path to the output filename.
            The format should always be CSV.
        :type output_filename:

        :returns: Results from the Nikto scan.
        :rtype: list(Data)
        """

        # Parse the scan results.
        # On error log the exception and continue.
        results = []
        vuln_count = 0
        hosts_seen = set()
        urls_seen = {}
        try:
            if output_filename.startswith("/cygdrive/"):
                output_filename = cygwin_to_win_path(output_filename)
            with open(output_filename, "rU") as f:
                total = float( sum(1 for _ in f) )
            if not total:
                Logger.log_verbose("Nikto produced no output for target: %s" % info.hostname)
                return []
            current = 0.0
            with open(output_filename, "rU") as f:
                csv_reader = reader(f)
                csv_reader.next()  # ignore the first line
                for row in csv_reader:
                    try:
                        self.update_status(progress = current / total * 100.0)
                        current += 1.0

                        # Each row (except for the first) has always
                        # the same 7 columns, but some may be empty.
                        host, ip, port, vuln_tag, method, path, text = row

                        # Report domain names and IP addresses.
                        if host != info.hostname and host not in hosts_seen:
                            hosts_seen.add(host)
                            if host in Config.audit_scope:
                                results.append( Domain(host) )
                        if ip not in hosts_seen:
                            hosts_seen.add(ip)
                            if ip in Config.audit_scope:
                                results.append( IP(ip) )

                        # Skip rows not informing of vulnerabilities.
                        if not vuln_tag:
                            continue

                        # Calculate the vulnerable URL.
                        target = urljoin(info.url, path)

                        # Skip if out of scope.
                        if target not in Config.audit_scope:
                            continue

                        # Report the URLs.
                        if (target, method) not in urls_seen:
                            url = Url(target, method, referer=info.url)
                            urls_seen[ (target, method) ] = url
                            results.append(url)
                        else:
                            url = urls_seen[ (target, method) ]

                        # Report the vulnerabilities.
                        vuln = UrlVulnerability(
                            url = url,
                            level = "informational",
                            description = "%s: %s" % (vuln_tag, text),
                        )
                        results.append(vuln)
                        vuln_count += 1

                    # On error, log the exception and continue.
                    except Exception, e:
                        Logger.log_error_verbose(str(e))
                        Logger.log_error_more_verbose(format_exc())

            # We're done parsing the results.
            self.update_status(progress = 100)

        # On error, log the exception.
        except Exception, e:
            Logger.log_error_verbose(str(e))
            Logger.log_error_more_verbose(format_exc())

        # Log how many results we found.
        msg = (
            "Nikto found %d vulnerabilities for host %s" % (
                vuln_count,
                info.hostname,
            )
        )
        if vuln_count:
            Logger.log(msg)
        else:
            Logger.log_verbose(msg)

        # Return the results.
        return results
