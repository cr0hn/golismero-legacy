#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

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


from golismero.api.plugin import ReportPlugin

from golismero.api.data import Data
from golismero.api.data.db import Database
from golismero.api.data.resource import Resource

from collections import defaultdict


class TextReport(ReportPlugin):
    """
    This plugin generate text reports
    """


    #----------------------------------------------------------------------
    def is_supported(self, output_file):
        """
        Determine if this plugin supports the requested file format.

        :param output_file: Output file to generate.
        :type output_file: str | None

        :returns: bool - True if this plugin supports the format, False otherwise.
        """
        return output_file and output_file.endswith(".txt")


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

        # Open the output file for writing.
        with open(output_file, mode='w') as fd:

            # Show all discovered URLs.
            fd.write("\nSpidered URLs\n=============\n\n")
            count["url"] = db.count(Data.TYPE_RESOURCE, Resource.RESOURCE_URL)
            if count["url"] < 200:   # increase as you see fit...
                # fast but memory consuming method
                urls = db.get_many( db.keys(Data.TYPE_RESOURCE, Resource.RESOURCE_URL) )
            else:
                # slow but lean method
                urls = db.iterate(Data.TYPE_RESOURCE, Resource.RESOURCE_URL)
            for u in urls:
                fd.write("+ %s\n" % str(u))

            #
            #
            # XXX TODO
            #
            #

            # Write summary.
            fd.write("\nSummary\n=======\n\n")
            fd.write("+ Total URLs: %s.\n\n" % str(count['url']))
