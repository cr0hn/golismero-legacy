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
from golismero.main.console import colorize


class ScreenReport(ReportPlugin):
    """
    Plugin to display reports on screen.
    """


    #----------------------------------------------------------------------
    def is_supported(self, output_file):
        return not output_file or output_file == "-"


    #----------------------------------------------------------------------
    def generate_report(self, output_file):

        #
        # Plugin vars
        #

        # ----------------------------------------
        # Header
        # ----------------------------------------
        print
        print
        print "--= %s =--" % colorize("Report", "cyan")

        #
        # Displayers
        #
        if Config.audit_config.only_vulns:
            self.general_display_only_vulns()
        else:
            self.general_display_by_resource()

        print


    #----------------------------------------------------------------------
    #
    # Common functions
    #
    #----------------------------------------------------------------------
    def common_get_resources(self, data_type=None, data_subtype=None):
        """
        Get a list of resources.

        :return: List of resources.
        :rtype: list(Resource)
        """
        # Get each resource
        m_resource = None
        m_len_urls = Database.count(data_type, data_type)
        if m_len_urls < 200:   # increase as you see fit...
            # fast but memory consuming method
            m_resource   = Database.get_many( Database.keys(data_type=data_type, data_subtype=data_subtype))
        else:
            # slow but lean method
            m_resource   = Database.iterate(data_type=data_type, data_subtype=data_subtype)

        return m_resource




    def common_display_general_summary(self):
        """
        Display the general summary.
        """

        # ----------------------------------------
        # Discovered resources
        # ----------------------------------------
        print "\n-# %s #- "% colorize("Summary", "yellow")


        # Fingerprint
        print "\n-- %s -- "% colorize("Target summary", "yellow")
        print "   +",

        m_table  = GolismeroTable(init_spaces=3)

        m_tmp_data = self.common_get_resources(data_type=Data.TYPE_INFORMATION, data_subtype=Information.INFORMATION_WEB_SERVER_FINGERPRINT)

        # Fingerprint
        if m_tmp_data: # There are data
            # For each host
            for l_host in m_tmp_data:
                t = '\n| -'.join(["%s - %s" % (l.url, colorize("Apache", "yellow")) for l in l_host.associated_resources if hasattr(l, "url")])
                m_table.add_row("Fingerprint: \n| -%s" % t)
        else:
            m_table.add_row("Main web server: %s" % colorize("Unknown", "yellow"))

        # Vhosts
        #m_table.add_row(["Vhosts", colorize("1", "yellow")])
        #m_table.add_row(["+  Vhosts2", colorize("1", "yellow")])

        # Audited hosts
        m_table.add_row("Hosts audited: %s" % colorize(len(self.common_get_resources(data_type=Data.TYPE_RESOURCE, data_subtype=Resource.RESOURCE_DOMAIN)), "yellow"))

        # Total vulns
        m_table.add_row("Total vulns: %s" % str(len(self.common_get_resources(data_type=Data.TYPE_VULNERABILITY))))

        # Set align
        print m_table.get_content()


    #----------------------------------------------------------------------
    #
    # Main display modes
    #
    #----------------------------------------------------------------------
    def general_display_only_vulns(self):

        # ----------------------------------------
        # General summary
        # ----------------------------------------
        self.common_display_general_summary()

        m_v = self.vuln_genereral_displayer(self.common_get_resources(data_type=Data.TYPE_VULNERABILITY))

        m_table = GolismeroTable(title="Vulnerabilities", init_spaces=0)
        if m_v:
            m_table.add_row(m_v)

        print
        print m_table.get_content()
        if not m_v:
            print
            print "No vulnerabilities found."


    #----------------------------------------------------------------------
    def general_display_by_resource(self):
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

        # ----------------------------------------
        # General summary
        # ----------------------------------------
        self.common_display_general_summary()

        # ----------------------------------------
        # Get the resource list
        # ----------------------------------------
        m_all_resources = set([x.resource_type for x in self.common_get_resources(data_type=Data.TYPE_RESOURCE)])

        self.concrete_display_resources()


    #----------------------------------------------------------------------
    #
    # Concrete displayers each type of resource
    #
    #----------------------------------------------------------------------
    def concrete_display_resources(self):
        """
        Display the results of web analysis.
        """


        # The main porperties of the resources
        MAIN_PROPERTIES = {
            'URL'           : 'url',
            'BASE_URL'      : 'url',
            'FOLDER_URL'    : 'url',
            'DOMAIN'        : 'name',
            'IP'            : 'address',
            'EMAIL'         : 'address'
        }


        # This properties/methods are the common info for the vulnerability types.
        PRIVATE_INFO = ['DEFAULTS', 'TYPE', 'add_information', 'RESOURCE',
                        'add_link', 'add_resource', 'add_vulnerability', 'associated_informations',
                        'associated_resources', 'associated_vulnerabilities', 'cve', 'cwe',
                        'data_type', 'discovered', 'get_associated_informations_by_category',
                        'get_associated_resources_by_category', 'get_associated_vulnerabilities_by_category',
                        'get_linked_data', 'get_links', 'identity', 'impact', 'is_in_scope', 'linked_data',
                        'links', 'max_data', 'max_informations', 'max_resources', 'max_vulnerabilities',
                        'merge', 'min_data', 'min_informations', 'min_resources', 'min_vulnerabilities',
                        'references', 'reverse_merge', 'risk', 'severity', 'validate_link_minimums', 'vulnerability_type',
                        'resource_type']

        # Get all type of resources
        m_all_resources = set([x for x in dir(Resource) if x.startswith("RESOURCE")])

        for l_resource in m_all_resources:

            # Get resources URL resources
            resource = self.common_get_resources(Data.TYPE_RESOURCE, getattr(Resource, l_resource))

            if not resource:
                continue

            # ----------------------------------------
            # Discovered resources
            # ----------------------------------------
            print "\n - %s - \n"% colorize(l_resource.replace("RESOURCE_", "").lower().replace("_", " ").capitalize(), "yellow")

            for i, r in enumerate(resource, start=1):
                l_b = StringIO()

                # Url to print
                l_resource     = colorize(getattr(r, MAIN_PROPERTIES[l_resource.replace("RESOURCE_", "")]), "white")

                #
                # Display the resource
                #
                l_b.write(" [%s] %s" % (colorize('{:^5}'.format(i), "Blue"), l_resource))

                # Displayer table
                l_table = GolismeroTable(init_spaces=10)

                m_valid_params = set()

                # Get all no trivial properties
                for x in dir(r):
                    found = False
                    for y in PRIVATE_INFO:
                        if x.startswith("_") or x.startswith(y):
                            found = True
                            break

                    if not found:
                        m_valid_params.add(x)

                    found = False

                #
                # Display resource params
                #
                for l_p in m_valid_params:
                    l_print_value = getattr(r, l_p)

                    if l_print_value is not None:

                        # String data
                        if isinstance(l_print_value, basestring):
                            l_table.add_row("%s: %s" % (l_p.capitalize(), getattr(r, l_p)))

                        # Dict data
                        if isinstance(l_print_value, dict) and len(l_print_value) > 0:
                            l_table.add_row([ "%s: %s" % (k.capitalize(), v) for k, v in l_print_value.iteritems()], cell_title= l_p.replace("_", " ").capitalize())

                        # List data
                        if isinstance(l_print_value, list) and len(l_print_value) > 0:
                            l_table.add_row(l_print_value, cell_title= l_p.replace("_", " ").capitalize())

                #
                # Display the vulns
                #
                if r.associated_vulnerabilities:
                    l_table.add_row(self.vuln_genereral_displayer(r.associated_vulnerabilities), "Vulnerabilities")

                a = l_table.get_content()
                if a:
                    l_b.write(a)

                print l_b.getvalue()



    #----------------------------------------------------------------------
    #
    # Concrete vulnerability displayers
    #
    # All functions must return an string
    #
    #----------------------------------------------------------------------
    def vuln_genereral_displayer(self, vulns):
        """
        Displays the vulnerabilities.
        """


        # This properties/methods are the common info for the vulnerability types.
        PRIVATE_INFO = ['DEFAULTS', 'TYPE_INFORMATION', 'TYPE_RESOURCE',
                        'TYPE_UNKNOWN', 'TYPE_VULNERABILITY', 'add_information',
                        'add_link', 'add_resource', 'add_vulnerability', 'associated_informations',
                        'associated_resources', 'associated_vulnerabilities', 'cve', 'cwe',
                        'data_type', 'discovered', 'get_associated_informations_by_category',
                        'get_associated_resources_by_category', 'get_associated_vulnerabilities_by_category',
                        'get_linked_data', 'get_links', 'identity', 'impact', 'is_in_scope', 'linked_data',
                        'links', 'max_data', 'max_informations', 'max_resources', 'max_vulnerabilities',
                        'merge', 'min_data', 'min_informations', 'min_resources', 'min_vulnerabilities',
                        'references', 'reverse_merge', 'risk', 'severity', 'validate_link_minimums', 'vulnerability_type']


        if not vulns:
            return

        #
        # Display the info
        #
        m_return        = []
        m_return_append = m_return.append
        for vuln in vulns:

            # Vuln name as raw format
            l_vuln_name      = vuln.vulnerability_type[vuln.vulnerability_type.rfind("/") + 1:]
            # Vuln name as display mode
            l_vuln_name_text = l_vuln_name.replace("_", " ").capitalize()

            # Call to the function resposible to display the vuln info
            try:
                l_table      = []
                l_table.append("Vuln name: %s" % colorize(l_vuln_name_text, "white"))
                l_table.append("%s" % ("-" * len("Vuln name: %s" % l_vuln_name_text)))

                # Get the vuln properties and add for display
                for l_v_prop in dir(vuln):
                    if l_v_prop not in PRIVATE_INFO and not l_v_prop.startswith("_"):
                        l_table.append("%s: %s" % (l_v_prop, colorize(getattr(vuln, l_v_prop), vuln.risk)))

                m_return_append(l_table)

            except KeyError:
                print "Function to display '%s' function are not available" % l_vuln_name
                continue

        return m_return

#------------------------------------------------------------------------------
class GolismeroTable:
    """
    This class represent the information like a "table" as a custom format.
    """

    #----------------------------------------------------------------------
    def __init__(self, title="", init_spaces_title=0, init_spaces=8, title_color = "red"):
        """
        :param init_spaces: inital spaces
        :type init_spaces: int

        :param title: title of table
        :type title: str
        """
        self.__text              = StringIO()
        self.__title             = StringIO()
        self.__title_length      = len(title) + 5 # The 5 is for the initial and ends characters
        self.__init_spaces       = init_spaces
        self.__init_title_spaces = init_spaces_title

        if title:
            self.__title.write("+%s+\n" % ("-" * (len(title) + 3)))
            self.__title.write("| %s  |\n" % (colorize(title, title_color)))
            self.__title.write("+%s+\n" % ("-" * (len(title) + 3)))


    #----------------------------------------------------------------------
    def add_row(self, row_info, cell_title = ""):
        """
        Add a row to the table.

        :param row_info: list or string with info to display in the row.
        :type row_info: list(str) | str

        :param cell_title: title for the next rows
        :type cell_title: str

        """
        if cell_title:
            self.__text.write("%s\n" % ("-" * (len(cell_title) + 4)))
            self.__text.write("| %s |\n" % cell_title)
            self.__text.write("%s\n" % ("-" * (len(cell_title) + 4)))

        if row_info:
            if isinstance(row_info, list):
                for r in row_info:
                    for l in r:
                        self.__text.write("| %s\n" % l)
                    self.__text.write("+-\n")

            else:
                self.__text.writelines("| %s" % row_info)
                self.__text.write("\n+-\n")



    #----------------------------------------------------------------------
    def get_content(self):
        """
        Get an string with the table
        """

        m_return = StringIO()

        # Title
        if self.__title_length > 5:
            m_return.write('\n'.join(( "%s%s" % (" " * self.__init_title_spaces, x) for x in self.__title.getvalue().splitlines())))


        if self.__text.getvalue():
            m_return.write("\n")
            # Rows
            m_return.write('\n'.join(( "%s%s" % (" " * self.__init_spaces, x) for x in self.__text.getvalue().splitlines()[:-1])))

            # End
            m_return.write("\n%s|___" % (" " * self.__init_spaces))

        return m_return.getvalue()
