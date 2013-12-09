#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: https://github.com/golismero
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

from golismero.api import VERSION
from golismero.api.audit import get_audit_times
from golismero.api.config import Config
from golismero.api.data import Data
from golismero.api.data.db import Database
from golismero.api.external import run_external_tool
from golismero.api.logger import Logger
from golismero.api.plugin import ReportPlugin

from datetime import datetime
from shlex import split
from warnings import warn

import os.path

try:
    # The fastest JSON parser available for Python.
    from cjson import encode
    dumps = encode
    def dump(obj, fp):
        fp.write( encode(obj) )
except ImportError:
    try:
        # Faster than the built-in module, usually found.
        from simplejson import dump, dumps
    except ImportError:
        # Built-in module since Python 2.6, very very slow!
        from json import dump, dumps


#------------------------------------------------------------------------------
class JSONOutput(ReportPlugin):
    """
    Dumps the output in JSON format.
    """


    #--------------------------------------------------------------------------
    def is_supported(self, output_file):
        return output_file and output_file.lower().endswith(".json")


    #--------------------------------------------------------------------------
    def generate_report(self, output_file):
        Logger.log_verbose("Writing audit results to file: %s" % output_file)

        # Parse the audit times.
        start_time, stop_time = get_audit_times()
        run_time = stop_time - start_time

        # Create the root element.
        root = {
            "golismero":   "GoLismero " + VERSION,
            "output_time": str(datetime.now()),
            "audit_name":  Config.audit_name,
            "start_time":  str(start_time),
            "stop_time":   str(stop_time),
            "run_time":    str(run_time),
        }

        # Create the audit scope element and subelements.
        root["audit_scope"] = {
            "addresses": sorted(Config.audit_scope.addresses),
            "roots":     sorted(Config.audit_scope.roots),
            "domains":   sorted(Config.audit_scope.domains),
            "web_pages": sorted(Config.audit_scope.web_pages),
        }

        # Determine the report type.
        self.__full_report = not Config.audit_config.only_vulns

        # Collect the vulnerabilities that are not false positives.
        datas = self.__collect_vulns(False)

        # If we have vulnerabilities and/or it's a full report...
        if datas or self.__full_report:

            # Collect the false positives.
            # In brief mode, this is used to eliminate the references to them.
            fp = self.__collect_vulns(True)
            self.__fp = set(fp)

            try:
                # Report the vulnerabilities.
                if datas:
                    vulns = {}
                    root["vulnerabilities"] = vulns
                    self.__add_to_json(vulns, datas, Data.TYPE_VULNERABILITY)

                # This dictionary tracks which data to show
                # and which not to in brief report mode.
                self.__vulnerable = set()

                try:

                    # Show the resources in the report.
                    datas = self.__collect_data(Data.TYPE_RESOURCE)
                    if datas:
                        res = {}
                        root["resources"] = res
                        self.__add_to_json(res, datas, Data.TYPE_RESOURCE)

                    # Show the informations in the report.
                    datas = self.__collect_data(Data.TYPE_INFORMATION)
                    if datas:
                        infos = {}
                        root["informations"] = infos
                        self.__add_to_json(infos, datas, Data.TYPE_INFORMATION)

                finally:
                    self.__vulnerable.clear()

            finally:
                self.__fp.clear()

            # Show the false positives in the full report.
            if self.__full_report and fp:
                fps = {}
                root["false_positives"] = fps
                self.__add_to_json(fps, fp, Data.TYPE_VULNERABILITY)

        # Write the JSON data to disk.
        with open(output_file, "wb") as fp:
            dump(root, fp)
        del root

        # Launch the build command, if any.
        command = Config.plugin_config.get("command", "")
        if command:
            Logger.log_verbose("Launching command: %s" % command)
            args = split(command)
            for i in xrange(len(args)):
                token = args[i]
                p = token.find("$1")
                while p >= 0:
                    if p == 0 or (p > 0 and token[p-1] != "$"):
                        token = token[:p] + output_file + token[p+2:]
                    p = token.find("$1", p + len(output_file))
                args[i] = token
            cwd = os.path.split(output_file)[0]
            log = lambda x: Logger.log_verbose(
                x[:-1] if x.endswith("\n") else x)
            run_external_tool(args[0], args[1:], cwd=cwd, callback=log)


    #--------------------------------------------------------------------------
    def __iterate_data(self, identities = None, data_type = None, data_subtype = None):
        if identities is None:
            identities = list(Database.keys(data_type))
        if identities:
            for page in xrange(0, len(identities), 100):
                for data in Database.get_many(identities[page:page + 100], data_type):
                    yield data


    #--------------------------------------------------------------------------
    def __collect_data(self, data_type):
        if self.__full_report:
            datas = [
                data.identity
                for data in self.__iterate_data(data_type=data_type)
            ]
        else:
            datas = [
                data.identity
                for data in self.__iterate_data(data_type=data_type)
                if data.identity in self.__vulnerable
            ]
        datas.sort()
        return datas


    #--------------------------------------------------------------------------
    def __collect_vulns(self, fp_filter):
        vulns = [
            vuln.identity
            for vuln in self.__iterate_data(data_type=Data.TYPE_VULNERABILITY)
            if bool(vuln.false_positive) == fp_filter
        ]
        vulns.sort()
        return vulns


    #--------------------------------------------------------------------------
    def __add_to_json(self, parent, datas, data_type):
        for data in self.__iterate_data(datas, data_type):
            i = data.identity
            d = i
            try:
                d = data.to_dict()
                dumps(d)
            except Exception:
                warn("Cannot serialize data: %r" % d, RuntimeWarning)
                continue
            parent[i] = d
