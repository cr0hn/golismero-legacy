#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com
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

from golismero.api.plugin import ReportPlugin

from golismero.api.data.data import Data
from golismero.api.data.db import Database
from golismero.api.data.resource.resource import Resource

# XXX HACK
from golismero.main.console import colorize

from collections import defaultdict


class ScreenReport(ReportPlugin):
    """
    This plugin to display reports on screen
    """


    #----------------------------------------------------------------------
    def is_supported(self, output_file):
        """
        Determine if this plugin supports the requested file format.

        :param output_file: Output file to generate.
        :type output_file: str | None

        :returns: bool - True if this plugin supports the format, False otherwise.
        """
        return not output_file


    #----------------------------------------------------------------------
    def generate_report(self, output_file):
        """
        Run plugin and generate report.

        :param output_file: Output file to generate.
        :type output_file: str | None
        """

        # Get access to the database API.
        db = Database()

        # Dictionary where to keep all the counters.
        count = defaultdict(int)

        # ----------------------------------------
        # Header
        # ----------------------------------------
        print "\n\n--= %s =--" % colorize("Report", "cyan")

        # ----------------------------------------
        # Discovered URLs
        # ----------------------------------------
        print "\n- %s - \n"% colorize("Spidered URLs", "yellow")
        count["url"] = db.count(Data.TYPE_RESOURCE, Resource.RESOURCE_URL)
        if count["url"] < 200:   # increase as you see fit...
            # fast but memory consuming method
            #urls = db.get_many( db.keys(Data.TYPE_RESOURCE, Resource.RESOURCE_URL) )
            urls = db.get_many( db.keys(Data.TYPE_RESOURCE) )
        else:
            # slow but lean method
            #urls = db.iterate(Data.TYPE_RESOURCE, Resource.RESOURCE_URL)
            urls = db.iterate(Data.TYPE_RESOURCE)
        for u in urls:
            print "+ %s" % str(u)
            #print "+++ %s" % str(u.associated_vulnerabilities)

        #
        #
        # XXX TODO
        #
        #

        # ----------------------------------------
        # Summary
        # ----------------------------------------
        print "\n- %s -\n" % colorize("Summary", "yellow")

        # Urls
        print "+ Total URLs: %s\n\n" % colorize(str(count['url']), "yellow")
