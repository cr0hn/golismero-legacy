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
from golismero.api.data.db import Database

# Data types
from golismero.api.data.data import Data
from golismero.api.data.resource.url import Url
from golismero.api.data.resource.resource import Resource

# XXX HACK
from golismero.main.console import colorize, colorize_substring

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

        # ----------------------------------------
        # Header
        # ----------------------------------------
        print "\n\n--= %s =--" % colorize("Report", "cyan")

        # ----------------------------------------
        # Discovered URLs
        # ----------------------------------------
        print "\n- %s - \n"% colorize("URLs", "yellow")
        # Get each resourcd
        m_len_urls = db.count(Data.TYPE_RESOURCE, Resource.RESOURCE_URL)
        if m_len_urls < 200:   # increase as you see fit...
            # fast but memory consuming method
            urls = db.get_many( db.keys(Data.TYPE_RESOURCE, Resource.RESOURCE_URL) )
        else:
            # slow but lean method
            urls = db.iterate(Data.TYPE_RESOURCE, Resource.RESOURCE_URL)

        for i, u in enumerate(urls):
            # Format to print:
            # [ 1 ] www.website.com/Param1=Value1&Param2=Value2
            #       | Method: GET              |
            #       |------PARAMS--------------|
            #       | Param1  = Value1         |
            #       | Param2  = Value2         |
            #       |------VULNERABILITES------|
            #       |-----------SQLi-----------|
            #       | Vulnerable param: Param2 |
            #       | Payload: or 1=1          |
            #       |__________________________|
            #
            # [ 2 ] www.website.com/Param1
            #       | Method: GET      |
            #       |------PARAMS------|
            #       | Param1  = Value1 |
            #       | Param2  = Value2 |
            #       |__________________|
            #
            #
            if not isinstance(u, Url):
                continue

            l_url = None # Url to print

            # If vulnerability type 'url_suspicious' exits:
            # - If there is only one vuln, it replace the URL.
            # - If there is more than one, vuln will be treated as
            #   normal vuln
            l_url_suspicious = u.associated_vulnerabilities_by_category(cat_name="information_disclosure/url_suspicious")

            if l_url_suspicious and len(l_url_suspicious) == 1: # There is 'url_suspicious' vulns and only one result
                l_val = iter(l_url_suspicious).next()

                l_url = colorize_substring(l_val.url.url, l_val.substring, l_val.severity)
                pass
            else:
                l_url = u.url

            #
            # Display URL
            #
            print "[%s] %s" % (colorize('{:^4}'.format(i), "Blue"), l_url)

            #
            # Display method
            #


            #
            # Display params
            #
            m_sep_lenght = 0


            print "+ %s" % str(l_url)
            for vuln in u.associated_vulnerabilities:
                print "  |- (%s) %s" % (vuln.vulnerability_type, str(vuln))

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
        print "+ Total URLs: %s\n\n" % colorize(str(m_len_urls), "yellow")
