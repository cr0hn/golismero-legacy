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

from golismero.api.config import Config
from golismero.api.plugin import import_plugin, get_plugin_name

json = import_plugin("json.py")

from os.path import split, join, splitext


#------------------------------------------------------------------------------
class HTMLReport(json.JSONOutput):
    """
    Writes reports as offline web pages.
    """


    #--------------------------------------------------------------------------
    def is_supported(self, output_file):
        if not output_file:
            return False
        output_file = output_file.lower()
        return (
            output_file.endswith(".html") or
            output_file.endswith(".htm")
        )


    #--------------------------------------------------------------------------
    def generate_report(self, output_file):

        # Hardcode the arguments for the JSON plugin.
        Config.plugin_args["mode"] = "dump"
        Config.plugin_args["command"] = ""

        # Get the report data.
        report_data = self.get_report_data()

        # It's easier for the JavaScript code in the report to access the
        # vulnerabilities as an array instead of a map, so let's fix that.
        vulnerabilities = report_data["vulnerabilities"]
        report_data["vulnerabilities"] = [
            vulnerabilities[identity]
            for identity in sorted(vulnerabilities.iterkeys())
        ]
        del vulnerabilities

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
        del plugin_map

        # Save the report data to disk in JSON format.
        output_json = splitext(output_file)[0] + "_data.json"
        self.serialize_report(output_json, report_data)

        # Save the report HTML skeleton.
        # TODO
