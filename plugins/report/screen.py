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
from golismero.api.config import Config

# Data types
from golismero.api.data.data import Data
from golismero.api.data.resource.url import Url
from golismero.api.data.resource.resource import Resource

# XXX HACK
from golismero.main.console import colorize, colorize_substring

from cStringIO import StringIO

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

        #
        # Plugin vars
        #

        # Get access to the database API.
        m_db = Database()

        # Display all URLs or only vulns?
        m_only_vulns = Config.audit_config.only_vulns

        # ----------------------------------------
        # Header
        # ----------------------------------------
        print "\n\n--= %s =--" % colorize("Report", "cyan")

        #
        # Displayers
        #
        if m_only_vulns:
            display_only_vulns(m_db)
        else:
            display_all(m_db)


#----------------------------------------------------------------------
#
# Display modes
#
#----------------------------------------------------------------------
def display_only_vulns(db):
    """"""

    # ----------------------------------------
    # Discovered URLs
    # ----------------------------------------
    print "\n- %s - "% colorize("Vulnerabilities", "yellow")


    # Get each resourcd
    urls       = None
    m_len_urls = db.count(Data.TYPE_RESOURCE, Resource.RESOURCE_URL)
    if m_len_urls < 200:   # increase as you see fit...
        # fast but memory consuming method
        urls   = db.get_many( db.keys(Data.TYPE_RESOURCE, Resource.RESOURCE_URL) )
    else:
        # slow but lean method
        urls   = db.iterate(Data.TYPE_RESOURCE, Resource.RESOURCE_URL)

    i = 0

    for u in urls:

        # Initial vars
        i             += 1
        l_screen       = StringIO()
        l_pre_spaces   = " " * 6
        l_max_word     = len(u.url)
        # Url to print
        l_url          = l_url = colorize(u.url, "white")

        #
        # Display URL and method
        #
        l_screen.write("\n[%s] (%s) %s" % (colorize('{:^3}'.format(i), "Blue"), u.method, l_url))

        #
        # Display URL params
        #
        # GET
        if u.has_url_param:
            l_screen.write("\n%s|%s" % (l_pre_spaces, '{:-^20}'.format("GET PARAMS")))
            for p,v in u.url_params().iteritems():
                l_screen.write("\n%s| %s = %s" % (l_pre_spaces, p, v))

        # POST
        if u.has_post_param:
            l_screen.write("\n%s|%s" % (l_pre_spaces, '{:-^20}'.format("POST PARAMS")))
            for p,v in u.post_params().iteritems():
                l_screen.write("\n%s| %s = %s" % (l_pre_spaces, p, v))

        #
        # Display vulns
        #
        if u.associated_vulnerabilities:
            # Display de line in the box
            l_screen.write("\n%s| %s" % (l_pre_spaces, '{:-^40}'.format(" Vulnerabilities ")))

            for vuln in u.associated_vulnerabilities:
                l_vuln_name = vuln.vulnerability_type[vuln.vulnerability_type.rfind("/") + 1:]

                # Display de line in the box
                l_screen.write("\n%s| %s " % (l_pre_spaces, '{:=^40}'.format(" %s " % l_vuln_name.replace("_", " ").capitalize())))

                # Call to the funcition resposible to display the vuln info
                if l_vuln_name in VULN_DISPLAYER:
                    l_screen.write(VULN_DISPLAYER[l_vuln_name](vuln, l_pre_spaces, 40))
                else:
                    print "Function to display '%s' function are not available" % l_vuln_name

            # Close vulnerabilites box
            l_screen.write("\n%s|%s" % (l_pre_spaces, "_" * 41 ))

        # Diplay info
        print l_screen.getvalue(),

    # ----------------------------------------
    # Summary
    # ----------------------------------------
    print "\n\n- %s -\n" % colorize("Summary", "yellow")

    # Urls
    print "+ Total URLs: %s\n\n" % colorize(str(i), "yellow")

#----------------------------------------------------------------------
def display_all(db):
    """
    This function display the results like this:

    [ 1 ] www.website.com/Param1=Value1&Param2=Value2
          | Method: GET              |
          |------PARAMS--------------|
          | Param1  = Value1         |
          | Param2  = Value2         |
          |------VULNERABILITES------|
          |-----------SQLi-----------|
          | Vulnerable param: Param2 |
          | Payload: or 1=1          |
          |__________________________|

    [ 2 ] www.website.com/contact/
    [ 3 ] www.website.com/Param1
          | Method: GET      |
          |------PARAMS------|
          | Param1  = Value1 |
          | Param2  = Value2 |
          |__________________|

    """

    # ----------------------------------------
    # Discovered URLs
    # ----------------------------------------
    print "\n- %s - "% colorize("URLs", "yellow")


    # Get each resourcd
    urls       = None
    m_len_urls = db.count(Data.TYPE_RESOURCE, Resource.RESOURCE_URL)
    if m_len_urls < 200:   # increase as you see fit...
        # fast but memory consuming method
        urls   = db.get_many( db.keys(Data.TYPE_RESOURCE, Resource.RESOURCE_URL) )
    else:
        # slow but lean method
        urls   = db.iterate(Data.TYPE_RESOURCE, Resource.RESOURCE_URL)

    i = 0

    for u in urls:

        # Initial vars
        i             += 1
        l_screen       = StringIO()
        l_pre_spaces   = " " * 7
        l_max_word     = len(u.url)
        # Url to print
        l_url          = l_url = colorize(u.url, "white")

        #
        # Display URL and method
        #
        l_screen.write("\n[%s] (%s) %s" % (colorize('{:^5}'.format(i), "Blue"), u.method, l_url))

        #
        # Display URL params
        #
        # GET
        if u.has_url_param:
            l_screen.write("\n%s|%s" % (l_pre_spaces, '{:-^20}'.format("GET PARAMS")))
            for p,v in u.url_params().iteritems():
                l_screen.write("\n%s| %s = %s" % (l_pre_spaces, p, v))

        # POST
        if u.has_post_param:
            l_screen.write("\n%s|%s" % (l_pre_spaces, '{:-^20}'.format("POST PARAMS")))
            for p,v in u.post_params().iteritems():
                l_screen.write("\n%s| %s = %s" % (l_pre_spaces, p, v))

        #
        # Display vulns
        #
        if u.associated_vulnerabilities:
            # Display de line in the box
            l_screen.write("\n%s| %s" % (l_pre_spaces, '{:-^40}'.format(" Vulnerabilities ")))

            for vuln in u.associated_vulnerabilities:
                l_vuln_name = vuln.vulnerability_type[vuln.vulnerability_type.rfind("/") + 1:]

                # Display de line in the box
                l_screen.write("\n%s| %s " % (l_pre_spaces, '{:=^40}'.format(" %s " % l_vuln_name.replace("_", " ").capitalize())))

                # Call to the funcition resposible to display the vuln info
                if l_vuln_name in VULN_DISPLAYER:
                    l_screen.write(VULN_DISPLAYER[l_vuln_name](vuln, l_pre_spaces, 40))
                else:
                    print "Function to display '%s' function are not available" % l_vuln_name

            # Close vulnerabilites box
            l_screen.write("\n%s|%s" % (l_pre_spaces, "_" * 41 ))

        # Diplay info
        print l_screen.getvalue(),



    # ----------------------------------------
    # Summary
    # ----------------------------------------
    print "\n\n- %s -\n" % colorize("Summary", "yellow")

    # Urls
    print "+ Total URLs: %s\n\n" % colorize(str(i), "yellow")


#----------------------------------------------------------------------
#
# These funcions are the responsible of display info for each vuln.
#
# All functions must return an string
#
#----------------------------------------------------------------------
def display_url_suspicious(vuln, init_spaces = 6, line_width = 40):
    """"""
    m_return = StringIO()
    m_return.write("\n")
    m_return.write("%s| URL: '%s'\n" % (init_spaces, colorize_substring(vuln.url.url, vuln.substring, "red")))
    m_return.write("%s| Suspicius text: %s" % (init_spaces, colorize(vuln.substring, "red")))


    return m_return.getvalue()



#
# Vulneravility functions
#
VULN_DISPLAYER = {
    'url_suspicious' : display_url_suspicious
}
