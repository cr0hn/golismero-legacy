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

__all__ = ["HTMLReport"]

from golismero import __version__ as VERSION
from golismero.api.config import Config
from golismero.api.data.information import Information
from golismero.api.data.vulnerability.vuln_utils import TAXONOMY_NAMES
from golismero.api.external import tempfile
from golismero.api.logger import Logger
from golismero.api.plugin import import_plugin, get_plugin_name

from zipfile import ZipFile, ZIP_DEFLATED

import os
import os.path

json = import_plugin("json.py")


#------------------------------------------------------------------------------
class HTMLReport(json.JSONOutput):
    """
    Writes reports as offline web pages.
    """

    EXTENSION = ".zip"


    #--------------------------------------------------------------------------
    # def is_supported(self, output_file):
    #     if not output_file:
    #         return False
    #     output_file = output_file.lower()
    #     return (
    #         output_file.endswith(".html") or
    #         output_file.endswith(".htm")
    #     )


    #--------------------------------------------------------------------------
    def generate_report(self, output_file):

        Logger.log_more_verbose("Generating JSON database...")

        # Hardcode the arguments for the JSON plugin.
        Config.plugin_args["mode"] = "dump"
        Config.plugin_args["command"] = ""

        # Get the report data.
        report_data = self.get_report_data()

        Logger.log_more_verbose("Postprocessing JSON database...")

        # Remove the false positives, if any.
        del report_data["false_positives"]

        # It's easier for the JavaScript code in the report to access the
        # vulnerabilities as an array instead of a map, so let's fix that.
        vulnerabilities = report_data["vulnerabilities"]
        sort_keys = [
            (data["display_name"], data["plugin_id"], data["identity"])
            for data in vulnerabilities.itervalues()
        ]
        sort_keys.sort()
        report_data["vulnerabilities"] = [
            vulnerabilities[identity]
            for _, _, identity in sort_keys
        ]
        vulnerabilities.clear()

        # Remove a bunch of data that won't be shown in the report anyway.
        for identity, data in report_data["informations"].items():
            if data["information_category"] not in (
                Information.CATEGORY_ASSET,
                Information.CATEGORY_FINGERPRINT,
            ):
                del report_data["informations"][identity]

        # Remove any dangling links we may have.
        links = set()
        for iterator in (
            report_data["resources"].itervalues(),
            report_data["informations"].itervalues(),
            report_data["vulnerabilities"]
        ):
            links.update(data["identity"] for data in iterator)
        for iterator in (
            report_data["resources"].itervalues(),
            report_data["informations"].itervalues(),
            report_data["vulnerabilities"]
        ):
            for data in iterator:
                tmp = set(data["links"])
                tmp.intersection_update(links)
                data["links"] = sorted(tmp)
                tmp.clear()
        links.clear()

        # Now, let's go through all Data objects and try to resolve the
        # plugin IDs to user-friendly plugin names.
        plugin_map = dict()
        for iterator in (
            report_data["resources"].itervalues(),
            report_data["informations"].itervalues(),
            report_data["vulnerabilities"]
        ):
            for data in iterator:
                if "plugin_id" in data:
                    plugin_id = data["plugin_id"]
                    if plugin_id not in plugin_map:
                        plugin_map[plugin_id] = get_plugin_name(plugin_id)
                    data["plugin_name"] = plugin_map[plugin_id]
        plugin_map.clear()

        # We also want to tell the HTML report which of the vulnerability
        # properties are part of the taxonomy. This saves us from having to
        # change the HTML code every time we add a new taxonomy property.
        report_data["supported_taxonomies"] = TAXONOMY_NAMES

        # Save the report data to disk.
        Logger.log_more_verbose("Writing report to disk...")
        inner_dir = os.path.splitext(os.path.basename(output_file))[0]
        with tempfile(suffix=".json") as output_json:
            self.serialize_report(output_json, report_data)
            with ZipFile(output_file, mode="w", compression=ZIP_DEFLATED,
                         allowZip64=True) as zip:
                zip.comment = "Report generated with GoLismero %s at %s UTC\n"\
                            % (VERSION, report_data["summary"]["report_time"])
                html_report = os.path.dirname(__file__)
                html_report = os.path.join(html_report, "html_report")
                html_report = os.path.abspath(html_report)
                found = False
                for root, directories, files in os.walk(html_report):
                    for basename in files:
                        if basename == "index-orig.html":
                            continue
                        filename = os.path.join(root, basename)
                        arcname = filename[len(html_report):]
                        arcname = os.path.join(inner_dir, arcname)
                        if basename == "database.js":
                            filename = output_json
                            found = True
                        zip.write(filename, arcname)
                if not found:
                    arcname = os.path.join(inner_dir, "js", "database.js")
                    zip.write(output_json, arcname)
