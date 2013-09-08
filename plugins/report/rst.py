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
from datetime import datetime
from pprint import pformat
from texttable import Texttable
from textwrap import wrap

from golismero.api.audit import get_audit_times, parse_audit_times
from golismero.api.config import Config
from golismero.api.data.db import Database
from golismero.api.logger import Logger
from golismero.api.plugin import ReportPlugin
from golismero.api.text.text_utils import hexdump

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
            print >>f, ".. footer:: Report generation date: %s" % datetime.now()
            print >>f, ""
            print >>f, ".. contents:: Table of Contents"
            print >>f, "   :depth: 2"
            print >>f, "   :backlinks: top"
            print >>f, ""

            # Print the summary.
            start_time, stop_time, run_time = parse_audit_times( *get_audit_times() )
            print >>f, "Summary"
            print >>f, "-------"
            print >>f, ""
            print >>f, "- Audit name: " + self.__format_rst(Config.audit_name)
            print >>f, "- Start date: " + start_time
            print >>f, "- End date: " + stop_time
            print >>f, "- Execution time: " + run_time
            print >>f, ""

            # Print the audit scope.
            print >>f, "Audit Scope"
            print >>f, "-----------"
            print >>f, ""
            print >>f, "- IP Addresses: "
            for address in Config.audit_scope.addresses:
                print >>f, "  + " + self.__format_rst(address)
            print >>f, "- Domains:"
            scope_domains = ["*." + r for r in Config.audit_scope.roots]
            scope_domains.extend(Config.audit_scope.domains)
            for domain in scope_domains:
                print >>f, "  + " + self.__format_rst(domain)
            print >>f, "- Web Pages:"
            for url in Config.audit_scope.web_pages:
                print >>f, "  + " + self.__format_rst(url)
            print >>f, ""

            # Dump the data.
            self.__full_report = not Config.audit_config.only_vulns
            self.__vulnerable  = set()
            self.__write_rst(f, Data.TYPE_VULNERABILITY, "Vulnerabilities")
            self.__write_rst(f, Data.TYPE_RESOURCE,      "Resources"    if self.__full_report else "Assets")
            self.__write_rst(f, Data.TYPE_INFORMATION,   "Informations" if self.__full_report else "Evidences")


    #--------------------------------------------------------------------------
    def __iterate_data(self, identities = None, data_type = None, data_subtype = None):
        if identities is None:
            identities = list(Database.keys(data_type))
        if identities:
            for page in xrange(0, len(identities), 100):
                for data in Database.get_many(identities[page:page + 100], data_type):
                    yield data


    #--------------------------------------------------------------------------
    __re_escape_rst = re.compile("(%s)" % "|".join("\\" + x for x in "*:,.\"!-/';~?@[]<>|+^=_\\"))
    __re_escape_indent = re.compile("^( +)", re.M)
    def __escape_rst(self, s):
        s = s.replace("\t", " " * 8)
        s = s.replace("\r\n", "\n")
        s = s.replace("\r", "\n")
        s = self.__re_escape_rst.sub(r"\\\1", s)
        m = self.__re_escape_indent.search(s)
        while m:
            s = s[:m.start()] + "\\" + "\\".join(s[m.start():m.end()]) + s[m.end():]
            m = self.__re_escape_indent.search(s, m.end() + 1 + (m.end() - m.start()))
        return s


    #--------------------------------------------------------------------------
    def __format_rst(self, obj, hyperlinks = False, width = 70):
        if hyperlinks:
            return "\n".join("`ID: %s`_" % x for x in obj)
        if isinstance(obj, basestring):
            obj = str(obj)
            if any(ord(c) > 127 for c in obj):
                obj = hexdump(obj)
            elif width:
                obj = "\n".join(wrap(obj, width, replace_whitespace=False,
                                     expand_tabs=False, drop_whitespace=False))
            return self.__escape_rst(obj)
        if isinstance(obj, dict):
            return "\n".join(self.__escape_rst("%s: %s" % (k,v)) for k,v in obj.iteritems())
        try:
            text = str(obj)
        except Exception:
            text = pformat(obj)
        return self.__escape_rst(text)


    #--------------------------------------------------------------------------
    def __write_rst(self, f, data_type, header):

        # Collect the data.
        datas = defaultdict(list)
        if self.__full_report or data_type == Data.TYPE_VULNERABILITY:
            for data in self.__iterate_data(data_type=data_type):
                datas[data.display_name].append(data.identity)
        else:
            for data in self.__iterate_data(data_type=data_type):
                if data.identity in self.__vulnerable:
                    datas[data.display_name].append(data.identity)
        for x in datas.itervalues():
            x.sort()

        # If there's nothing to show...
        if not datas:

            # If it's a brief report, show a message.
            if not self.__full_report and data_type == Data.TYPE_VULNERABILITY:
                print >>f, "No vulnerabilities found."
                print >>f, ""

            # Nothing else to do.
            return

        # Get the titles.
        titles = datas.keys()
        titles.sort()

        # Print the data type header.
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
                property_groups = data.display_properties

                # Add the graph links.
                linked_info = data.get_links(Data.TYPE_INFORMATION)
                linked_res  = data.get_links(Data.TYPE_RESOURCE)
                linked_vuln = data.get_links(Data.TYPE_VULNERABILITY)
                if self.__full_report:
                    if linked_info:
                        property_groups["Graph Links"]["Informations"]    = sorted(linked_info)
                    if linked_res:
                        property_groups["Graph Links"]["Resources"]       = sorted(linked_res)
                    if linked_vuln:
                        property_groups["Graph Links"]["Vulnerabilities"] = sorted(linked_vuln)
                elif data_type == Data.TYPE_VULNERABILITY:
                    if linked_info:
                        self.__vulnerable.update(linked_info)
                        property_groups["Graph Links"]["Evidences"]       = sorted(linked_info)
                    if linked_res:
                        self.__vulnerable.update(linked_res)
                        property_groups["Graph Links"]["Assets"]          = sorted(linked_res)
                    if linked_vuln:
                        property_groups["Graph Links"]["Related"]         = sorted(linked_vuln)
                elif linked_vuln:
                    property_groups["Graph Links"]["Vulnerabilities"]     = sorted(linked_vuln)

                # Get the groups.
                groups = property_groups.keys()
                groups.sort()

                # Dump the data per group.
                for group in groups:

                    # Get the properties.
                    properties = property_groups[group]

                    # Format the data for printing.
                    hyperlinks = group == "Graph Links"
                    properties = {
                        key: self.__format_rst(value, hyperlinks).split("\n")
                        for key, value in properties.iteritems()
                        if value
                    }

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
                    w_values = len(h_values)
                    for v in properties.itervalues():
                        for x in v:
                            w_values = max(w_values, len(x))

                    # Print the group header.
                    if group:
                        print >>f, group
                        print >>f, "*" * len(group)
                        print >>f, ""

                    # Dump the properties.
                    fmt = "| %%-%ds | %%-%ds |" % (w_names, w_values)
                    separator = "+-%s-+-%s-+" % (("-" * w_names), ("-" * w_values))
                    print >>f, separator
                    print >>f, fmt % (h_names, h_values)
                    print >>f, separator.replace("-", "=")
                    for name in names:
                        lines = properties[name]
                        print >>f, fmt % (name, lines.pop(0))
                        for x in lines:
                            print >>f, fmt % ("", x)
                        print >>f, separator
                    print >>f, ""
