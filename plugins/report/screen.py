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
from golismero.api.data import Data
from golismero.api.data.resource import Resource
from golismero.api.data.resource.url import Url

# XXX HACK
from golismero.main.console import colorize, colorize_substring
from prettytable import *

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
            general_display_only_vulns(m_db)
        else:
            general_display_by_resource(m_db)

        print



#----------------------------------------------------------------------
#
# Common functions
#
#----------------------------------------------------------------------
def common_display_general_summary(database):
    """Display the summary of scan"""

    # ----------------------------------------
    # Discovered resources
    # ----------------------------------------
    print "\n-# %s #- \n"% colorize("Summary", "yellow")

    m_table = PrettyTable(hrules=ALL)
    m_table.header = False
    m_table.padding_width = 3

    # Fingerprint
    m_table.add_row(["Web server fingerprint", colorize("Apache", "yellow")])

    # Vhosts
    m_table.add_row(["Vhosts", colorize("1", "yellow")])
    m_table.add_row(["+  Vhosts2", colorize("1", "yellow")])

    # Audited hosts
    m_table.add_row(["Hosts audited", colorize("1", "yellow")])

    # Total vulns
    m_table.add_row(["Total vulns", "1"])

    # Set align
    m_table.align = "l"
    print m_table

    """Display information for one vuln"""

#----------------------------------------------------------------------
def common_get_resources(db, data_type, resource_type):
    """Get a list of resources as optimous as possible.

    :return: a resouce list.
    """
    # Get each resource
    m_resource = None
    m_len_urls = db.count(data_type, data_type)
    if m_len_urls < 200:   # increase as you see fit...
        # fast but memory consuming method
        m_resource   = db.get_many( db.keys(data_type, resource_type) )
    else:
        # slow but lean method
        m_resource   = db.iterate(data_type, resource_type)

    return m_resource







#----------------------------------------------------------------------
#
# Concrete displayers
#
#----------------------------------------------------------------------
def concrete_display_web_resources(database):
    """Display the results of web analysis"""

    # Get resources URL resources
    resource = common_get_resources(database, Data.TYPE_RESOURCE, Resource.RESOURCE_URL)

    # ----------------------------------------
    # Discovered resources
    # ----------------------------------------
    print "\n- %s - \n"% colorize("Web resources", "yellow")

    i = 0

    #left_padding_width


    for u in resource:

        # Initial vars
        i             += 1
        # Url to print
        l_url          = l_url = colorize(u.url, "white")

        #
        # Display URL and method
        #
        print "[%s] (%s) %s" % (colorize('{:^5}'.format(i), "Blue"), u.method, l_url)

        #
        # Display URL params
        #
        # GET
        if u.has_url_param:
            l_table = PrettyTable(["Params type", "GET"])
            for p,v in u.url_params().iteritems():
                l_table.add_row([p,v])

            print l_table

        # POST
        if u.has_post_param:
            l_table = PrettyTable(["Params type", "GET"])
            for p,v in u.post_params().iteritems():
                l_table.add_row([p,v])

            print l_table

        vuln_genereral_displayer(u.associated_vulnerabilities)



    # ----------------------------------------
    # Summary
    # ----------------------------------------
    print "\n\n- %s -\n" % colorize("Web summary", "yellow")

    # Urls
    m_table = PrettyTable(hrules=ALL)
    m_table.header = False
    m_table.add_row(["Total URLs:", colorize(str(i), "yellow")])

    print m_table

#----------------------------------------------------------------------
def concrete_display_vulns_results(database):
    """Display the list of vulns"""





RESOURCE_DISPLAYER = {
    Resource.RESOURCE_URL : concrete_display_web_resources # Urls
}
#----------------------------------------------------------------------
#
# General display modes
#
#----------------------------------------------------------------------
def general_display_only_vulns(db):
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
def general_display_by_resource(db):
    """
    This function display the results like this:

    [ 1 ] www.website.com/Param1=Value1&Param2=Value2
    +-----------------+
    | Vulnerabilities |
    +------------------+-----------------------------+
    |   Vuln name:     |        Url suspicious       |
    +------------------+-----------------------------+
    |       URL:       | http://website.com/admin    |
    | Suspicius text:  |            admin            |
    +------------------+-----------------------------+

    [ 2 ] www.website.com/contact/
    [ 3 ] www.website.com/Param1

    """


    if not isinstance(db, Database):
        raise ValueError("Espected 'Database' type, got %s." % type(db))

    # ----------------------------------------
    # General summary
    # ----------------------------------------
    common_display_general_summary(db)


    # ----------------------------------------
    # Get the resource list
    # ----------------------------------------
    m_all_resources = set([x.resource_type for x in db.get_many(db.keys(data_type=Data.TYPE_RESOURCE))])

    for rs in m_all_resources:
        try:
            RESOURCE_DISPLAYER[rs](db)
        except KeyError,e:
            pass
            #print "[!] No function to parse resources '%s'" % str(e.message)





#----------------------------------------------------------------------
#
# Concrete vulnerability displayers
#
# All functions must return an string
#
#----------------------------------------------------------------------
def vuln_genereral_displayer(vulns):
    """This functions is the responsible to display the vulns"""
    if not vulns:
        return

    #
    # Display the info
    #
    # Title
    print "+%s+" % ("-" * (len("Vulnerabilities") + 3))
    print "| %s  |" % colorize("Vulnerabilities", "Red")

    m_vulns      = {}
    for vuln in vulns:
        # Vuln name as raw format
        l_vuln_name      = vuln.vulnerability_type[vuln.vulnerability_type.rfind("/") + 1:]
        # Vuln name as display mode
        l_vuln_name_text = l_vuln_name.replace("_", " ").capitalize()

        # Call to the function resposible to display the vuln info
        try:
            l_table      = PrettyTable(["Vuln name: ", l_vuln_name_text])

            # String value of handler
            l_func_ret = VULN_DISPLAYER[l_vuln_name](vuln, l_table)

            # Display the table
            print l_table

        except KeyError:
            print "Function to display '%s' function are not available" % l_vuln_name
            continue

def vuln_display_url_suspicious(vuln, table):
    """"""

    table.add_row(["URL:", colorize_substring(vuln.url.url, vuln.substring, "red")])
    table.add_row(["Suspicius text: ", colorize(vuln.substring, "red")])


#
# Vulneravility functions
#
VULN_DISPLAYER = {
    'url_suspicious' : vuln_display_url_suspicious
}
