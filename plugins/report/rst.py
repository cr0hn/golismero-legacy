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

import re
import sys

from collections import defaultdict
from pprint import pformat
from texttable import Texttable

from golismero.api.audit import get_audit_times, parse_audit_times
from golismero.api.config import Config
from golismero.api.data.db import Database
from golismero.api.logger import Logger
from golismero.api.plugin import ReportPlugin

# Data types
from golismero.api.data import Data
from golismero.api.data.information import Information
from golismero.api.data.resource import Resource
from golismero.api.data.vulnerability import Vulnerability


#------------------------------------------------------------------------------
class RSTReport(ReportPlugin):
    """
    Creates reports in reStructured Text format.
    """


    #--------------------------------------------------------------------------
    def is_supported(self, output_file):
        return output_file and output_file.lower().endswith(".rst")


    #--------------------------------------------------------------------------
    def generate_report(self, output_file):
        Logger.log_verbose("Writing reStructured text report to file: %s" % output_file)

        # Open the output file.
        with open(output_file, "w") as f:

            # Print the main header.
            print >>f, "GoLismero Report"
            print >>f, "================"
            print >>f, ""

            # Print the audit name.
            print >>f, "- Audit name: " + Config.audit_name

            # Print the audit times.
            start_time, stop_time, run_time = parse_audit_times( *get_audit_times() )
            print >>f, "- Start date: " + start_time
            print >>f, "- End date: " + stop_time
            print >>f, "- Execution time: " + run_time
            print >>f, ""

            # Dump the data.
            self.__write_rst(f, Data.TYPE_VULNERABILITY, "Vulnerability")
            if not Config.audit_config.only_vulns:
                self.__write_rst(f, Data.TYPE_RESOURCE,    "Resource")
                self.__write_rst(f, Data.TYPE_INFORMATION, "Information")


    #--------------------------------------------------------------------------
    def __iterate_data(self, identities = None, data_type = None, data_subtype = None):
        if identities is None:
            identities = list(Database.keys(data_type))
        if identities:
            for page in xrange(0, len(identities), 100):
                for data in Database.get_many(identities[page:page + 100], data_type):
                    yield data


    #--------------------------------------------------------------------------
    __escape_rst = re.compile("(%s)" % "|".join("\\" + x for x in "*:,.\"!-/';~?@[]|+^=_\\"))
    def __format_rst(self, obj, hyperlinks = False):
        if not hyperlinks:
            return self.__escape_rst.sub(r"\\\1", pformat(obj))
        return "\n".join("`ID: %s`_" % x for x in obj)


    #--------------------------------------------------------------------------
    def __write_rst(self, f, data_type, data_title):

        # Collect the data.
        datas = defaultdict(list)
        for data in self.__iterate_data(data_type=data_type):
            datas[data.display_name].append(data.identity)
        if datas:
            for x in datas.itervalues():
                x.sort()

            # Get the titles.
            titles = datas.keys()
            titles.sort()

            # Print the data type header.
            header = "%s objects" % data_title
            print >>f, header
            print >>f, "-" * len(header)
            print >>f, ""

            # Dump the data per type.
            for title in titles:

                # Print the title.
                print >>f, title
                print >>f, "+" * len(title)
                print >>f, ""

                # Dump the data per title.
                show_ruler = False
                for data in self.__iterate_data(datas[title], data_type):

                    # Show the horizontal ruler for all items but the first.
                    if show_ruler:
                        print >>f, "----"
                        print >>f, ""
                    show_ruler = True

                    # Show the data title.
                    data_title = "ID: %s" % (data.identity)
                    print >>f, data_title
                    print >>f, "^" * len(data_title)
                    print >>f, ""

                    # Collect the properties.
                    # TODO: make them references so they can link to the corresponding object.
                    property_groups = data.display_properties
                    linked_info = data.get_links(Data.TYPE_INFORMATION)
                    linked_res  = data.get_links(Data.TYPE_RESOURCE)
                    linked_vuln = data.get_links(Data.TYPE_VULNERABILITY)
                    if linked_info:
                        property_groups["Graph Links"]["Associated Informations"]    = sorted(linked_info)
                    if linked_res:
                        property_groups["Graph Links"]["Associated Resources"]       = sorted(linked_res)
                    if linked_vuln:
                        property_groups["Graph Links"]["Associated Vulnerabilities"] = sorted(linked_vuln)

                    # Get the groups.
                    groups = property_groups.keys()
                    groups.sort()

                    # Dump the data per group.
                    for group in groups:

                        # Get the properties.
                        properties = property_groups[group]

                        # Get the property names.
                        names = properties.keys()
                        names.sort()

                        # Hack to reorder some groups.
                        if group == "Description":
                            if "References" in names:
                                names.remove("References")
                                names.append("References")
                            if "Title" in names:
                                names.remove("Title")
                                names.insert(0, "Title")
                        elif group == "Risk":
                            if "Level" in names:
                                names.remove("Level")
                                names.insert(0, "Level")

                        # Get the width of the names column.
                        h_names = "Property name"
                        w_names = max(len(x) for x in names)
                        w_names = max(w_names, len(h_names))

                        # Get the width of the values column.
                        h_values = "Property value"
                        w_values = 0
                        for v in properties.itervalues():
                            for x in self.__format_rst(v).split("\n"):
                                w_values = max(w_values, len(x.strip()))
                        w_values = max(w_values, len(h_values))

                        # Print the group header.
                        if group:
                            print >>f, group
                            print >>f, "*" * len(group)
                            print >>f, ""

                        # Determine if we need to insert hyperlinks.
                        hyperlinks = group == "Graph Links"

                        # Dump the properties.
                        fmt = "| %%-%ds | %%-%ds |" % (w_names, w_values)
                        separator = "+-%s-+-%s-+" % (("-" * w_names), ("-" * w_values))
                        print >>f, separator
                        print >>f, fmt % (h_names, h_values)
                        print >>f, separator.replace("-", "=")
                        for name in names:
                            lines = self.__format_rst(properties[name], hyperlinks).split("\n")
                            print >>f, fmt % (name, lines.pop(0).strip())
                            for x in lines:
                                print >>f, fmt % ("", x.strip())
                            print >>f, separator
                        print >>f, ""
