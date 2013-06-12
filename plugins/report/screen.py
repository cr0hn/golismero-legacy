#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__ = """
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

from cStringIO import StringIO

from golismero.api.plugin import ReportPlugin
from golismero.api.data.db import Database
from golismero.api.config import Config

# Data types
from golismero.api.data import Data
from golismero.api.data.resource import Resource
from golismero.api.data.information import Information

# XXX HACK
from golismero.main.console import colorize, colorize_substring
from prettytable import *


class ScreenReport(ReportPlugin):
    """
    Plugin to display reports on screen.
    """


    #----------------------------------------------------------------------
    def is_supported(self, output_file):
        return not output_file


    #----------------------------------------------------------------------
    def generate_report(self, output_file):

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
def common_get_resources(db, data_type=None, data_subtype=None):
    """
    Get a list of resources.

    :return: List of resources.
    :rtype: list(Resource)
    """
    # Get each resource
    m_resource = None
    m_len_urls = db.count(data_type, data_type)
    if m_len_urls < 200:   # increase as you see fit...
        # fast but memory consuming method
        m_resource   = db.get_many( db.keys(data_type=data_type, data_subtype=data_subtype))
    else:
        # slow but lean method
        m_resource   = db.iterate(data_type=data_type, data_subtype=data_subtype)

    return m_resource




def common_display_general_summary(database):
    """
    Display the general summary.
    """

    # ----------------------------------------
    # Discovered resources
    # ----------------------------------------
    print "\n-# %s #- \n"% colorize("Summary", "yellow")


    # Fingerprint
    print "\n-- %s -- \n"% colorize("Fingerprinting results", "yellow")
    m_table = common_get_table_without(with_header=False)

    m_tmp_data = common_get_resources(database, data_type=Data.TYPE_INFORMATION, data_subtype=Information.INFORMATION_WEB_SERVER_FINGERPRINT)


    if m_tmp_data: # There are data
        # For each host
        for l_host in m_tmp_data:
            for l_res in l_host.associated_resources:
                if hasattr(l_res, "url"):
                    m_table.add_row(["Fingerprint: %s" % l_res.url, colorize("Apache", "yellow")])
    else:
        m_table.add_row(["Main web server:", colorize("Unknown", "yellow")])

    # Vhosts
    #m_table.add_row(["Vhosts", colorize("1", "yellow")])
    #m_table.add_row(["+  Vhosts2", colorize("1", "yellow")])

    # Audited hosts
    m_table.add_row(["Hosts audited", colorize(len(common_get_resources(database, data_type=Data.TYPE_RESOURCE, data_subtype=Resource.RESOURCE_DOMAIN)), "yellow")])

    # Total vulns
    m_table.add_row(["Total vulns", str(len(common_get_resources(database, data_type=Data.TYPE_VULNERABILITY)))])

    # Set align
    m_table.align = "l"
    print m_table


#----------------------------------------------------------------------
def common_get_table_without(main_cols = [], with_header=True, with_hrules=True):
    """
    Get PrettyTable with params.

    :param main_cols: cols of header.
    :type main_cols: list

    :param with_header: set the table header or not.
    :type with_header: bool

    :param with_hrules: set rules at each row.
    :type with_hrules: bool

    :return: a PrettyTable object
    :rtype: PrettyTable

    """
    m_table = PrettyTable(main_cols, hrules=(ALL if with_hrules else None))
    m_table.header = with_header
    m_table.padding_width = 3

    return m_table


#----------------------------------------------------------------------
#
# Main display modes
#
#----------------------------------------------------------------------
def general_display_only_vulns(db):

    if not isinstance(db, Database):
        raise ValueError("Expected Database, got %s" % type(db))

    # ----------------------------------------
    # General summary
    # ----------------------------------------
    common_display_general_summary(db)

    print "\n- %s - \n"% colorize("Vulnerabilities", "yellow")

    # Title
    print "+%s+" % ("-" * (len("Vulnerabilities") + 3))
    print "| %s  |" % colorize("Vulnerabilities", "Red")
    print "+%s+" % ("-" * (len("Vulnerabilities") + 3))
    print

    common_get_resources(db, data_type=Data.TYPE_VULNERABILITY)


#----------------------------------------------------------------------
def general_display_by_resource(db):
    """
    This function displays the results like this:

    >>>
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
        raise ValueError("Expected Database, got %s" % type(db))

    # ----------------------------------------
    # General summary
    # ----------------------------------------
    common_display_general_summary(db)

    # ----------------------------------------
    # Get the resource list
    # ----------------------------------------
    m_all_resources = set([x.resource_type for x in common_get_resources(db, data_type=Data.TYPE_RESOURCE)])

    # There are some types that calls the same function for process it. To avoid to call 2 o more times the same
    # function, filter it:
    m_functions_to_call = set([RESOURCE_DISPLAYER[f] for f in m_all_resources if f in RESOURCE_DISPLAYER])

    for x in m_functions_to_call:
        x(db)


#----------------------------------------------------------------------
#
# Concrete displayers each type of resource
#
#----------------------------------------------------------------------
def concrete_display_web_resources(database):
    """
    Display the results of web analysis.
    """

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

        if u.associated_vulnerabilities:
            # Title
            print "%s+%s+" % (" " * 8,"-" * (len("Vulnerabilities") + 3))
            print "%s| %s  |" % (" " * 8, colorize("Vulnerabilities", "Red"))
            print "%s+%s+" % (" " * 8,"-" * (len("Vulnerabilities") + 3))

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


RESOURCE_DISPLAYER = {
    # Web related: URL + Base_URL
    Resource.RESOURCE_URL          : concrete_display_web_resources,
    Resource.RESOURCE_BASE_URL     : concrete_display_web_resources
}


#----------------------------------------------------------------------
#
# Concrete vulnerability displayers
#
# All functions must return an string
#
#----------------------------------------------------------------------
def vuln_genereral_displayer(vulns):
    """
    Displays the vulnerabilities.
    """

    if not vulns:
        return

    #
    # Display the info
    #
    m_pre_spaces = 8
    for vuln in vulns:
        # Vuln name as raw format
        l_vuln_name      = vuln.vulnerability_type[vuln.vulnerability_type.rfind("/") + 1:]
        # Vuln name as display mode
        l_vuln_name_text = l_vuln_name.replace("_", " ").capitalize()

        # Call to the function resposible to display the vuln info
        try:
            #l_table      = PrettyTable(["Vuln name: ", l_vuln_name_text])
            l_table      = StringIO()
            l_table.write("Vuln name: %s\n" % colorize(l_vuln_name_text, "white"))
            l_table.write("%s\n" % ("-" * len("Vuln name: %s" % l_vuln_name_text)))


            # String value of handler
            VULN_DISPLAYER[l_vuln_name](vuln, l_table.write)

            # Display the table
            print '\n'.join([ "        | " + x for x in l_table.getvalue().splitlines()])
            print "        *-"

        except KeyError:
            print "Function to display '%s' function are not available" % l_vuln_name
            continue


#----------------------------------------------------------------------
def vuln_display_url_suspicious(vuln, func):
    """Diplay the vuln: URL Suspicious"""
    func("URL: %s\n" % colorize_substring(vuln.url.url, vuln.substring, "red"))
    func("Suspicius text: %s\n" % colorize(vuln.substring, "red"))


#----------------------------------------------------------------------
def vuln_display_url_disclosure(vuln, func):
    """Diplay the vuln: URL Disclosure"""
    func("URL: %s\n" % colorize_substring(vuln.url.url, vuln.discovered, "red"))
    func("Path discovered: %s\n" % colorize(vuln.discovered, "red"))


#----------------------------------------------------------------------
def vuln_display_default_error_page(vuln, func):
    """Diplay the vuln: URL Disclosure"""

    func("URL: %s\n" % colorize_substring(vuln.url.url, vuln.discovered, "red"))
    func("Default error page for server: %s\n" % colorize(vuln.server_name, "red"))


VULN_DISPLAYER = {
    'url_suspicious'          : vuln_display_url_suspicious,
    'url_disclosure'          : vuln_display_url_disclosure,
    'default_error_page'      : vuln_display_default_error_page
}
