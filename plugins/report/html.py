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

from golismero.api.plugin import ReportPlugin

from golismero.api.config import Config
from golismero.api.data import Data
from golismero.api.data.db import Database
from golismero.api.data.resource import Resource

from os.path import join, dirname
from collections import Counter
import datetime


#------------------------------------------------------------------------------
class HTMLReport(ReportPlugin):
    """
    Plugin to generate HTML reports.
    """


    #--------------------------------------------------------------------------
    def is_supported(self, output_file):
        return output_file and (
            output_file.lower().endswith(".html") or
            output_file.lower().endswith(".htm")
        )


    def common_get_resources(self, data_type=None, data_subtype=None):
        """
        Get a list of datas.

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




    #--------------------------------------------------------------------------
    def generate_report(self, output_file):

        #
        # configure django
        #

        import django.conf
        django.conf.settings.configure(
            TEMPLATE_DIRS = (join(dirname(__file__), './html_report'),)
        )

        from django.template import Template, loader, Context
        from django.conf import settings

        c = Context()
        t = loader.get_template(template_name="template.html")

        #
        # Fill the context
        #

        # Audit name
        c['audit_name']        = Config.audit_name

        # Start date
        c['start_date']        = datetime.datetime.fromtimestamp(Config.audit_config.start_time)
        c['end_date']          = datetime.datetime.fromtimestamp(Config.audit_config.stop_time)

        # Execution time
        c['execution_time']    = '{:.3f}'.format(Config.audit_config.stop_time - Config.audit_config.start_time)

        # Targets
        c['targets']           = Config.audit_config.targets

        # Fill the vulnerabilities summary
        self.fill_summary_vulns(c)

        # Fill the info of the resources
        self.fill_content_resource(c)

        #
        # Write the output
        #
        m_rendered = t.render(c)

        f = open(output_file, "w")
        f.write("%s" % m_rendered.encode("utf-8"))
        f.close()

    #----------------------------------------------------------------------
    def fill_summary_vulns(self, context):
        """
        Fill the context var with summary of the vulnerabilities.

        :param context: Context var to fill.
        :type context: Context
        """

        m_all_vulns   = self.common_get_resources(data_type=Data.TYPE_VULNERABILITY)

        m_results          = {}

        # Total vulns
        m_results['total'] = len(m_all_vulns)

        # Count each type of vuln
        m_counter = Counter()

        # Init
        m_counter['critical']       = 0
        m_counter['high']           = 0
        m_counter['middle']         = 0
        m_counter['low']            = 0
        m_counter['informational']  = 0
        m_counter['no_vulns']       = 0

        # Vulnerabilities by type
        if m_results['total'] > 0:

            for l_v in m_all_vulns:
                m_counter[l_v.level] +=1
        else:
            m_counter['no_vulns'] = m_results['total'] if m_results['total'] > 0 else 1

        for k,v in m_counter.iteritems():
            m_results[k] = v

        context['summary_vulns']     = m_results



    #----------------------------------------------------------------------
    def fill_content_resource__(self, context):
        """
        Fill the context var with the "resource" information.

        :param context: Context var to fill.
        :type context: Context
        """


        context['info_by_resource']  = [
            {
                # Resource type URL
                'resource_type' : "URL",
                'info'          : [
                    # Resource 1
                    {
                        # Index of row
                        'index'  :  '1',

                        # Resource info
                        'resource' : {
                            'URI'       : "http",
                            'main_info' : "http://www.mytest.site.com"
                        },

                        # Vulns
                        'vulns'  : [
                            {
                                'level'   : 'high',
                                'number'  : '4'
                            }
                        ]
                    },

                    # Resource 2
                    {
                        # Index of row
                        'index'  :  '2',

                        # Resource info
                        'resource' : {
                            'URI'       : "http",
                            'main_info' : "http://www.othersite.com"
                        },

                        # Vulns
                        'vulns'  : [
                            {
                                'level'   : 'high',
                                'number'  : '2'
                            },
                            {
                                'level'   : 'middle',
                                'number'  : '23'
                            },
                            {
                                'level'   : 'low',
                                'number'  : '1'
                            }
                        ]
                    }
                ]
            }
        ]


    #----------------------------------------------------------------------
    #
    # Concrete displayer for resources
    #
    #----------------------------------------------------------------------
    def fill_content_resource(self, context):
        """
        Fill the context var with the "resource" information.

        :param context: Context var to fill.
        :type context: Context
        """

        # The main porperties of the resources
        MAIN_PROPERTIES = {
            'URL'           : 'url',
            'BASE_URL'      : 'url',
            'FOLDER_URL'    : 'url',
            'DOMAIN'        : 'hostname',
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


        m_results        = []
        m_results_append = m_results.append

        # Get all type of resources
        m_all_resources = set([x for x in dir(Resource) if x.startswith("RESOURCE")])

        for l_resource in m_all_resources:
            l_res_result = {}

            # Get resources URL resources
            resource = self.common_get_resources(Data.TYPE_RESOURCE, getattr(Resource, l_resource))

            if not resource:
                continue

            l_res_result['resource_type'] = l_resource.replace("RESOURCE_", "").lower().replace("_", " ").capitalize()
            l_res_result['info']          = []

            # ----------------------------------------
            # Discovered resources
            # ----------------------------------------
            m_resource_appender           =  l_res_result['info'].append

            for i, r in enumerate(resource, start=1):
                # Dict where store the results
                l_concrete_res  = {}

                # Index
                l_concrete_res['index']    = i

                # Resource to display
                l_concrete_res['resource'] = {}
                l_concrete_res['resource']['main_info'] = getattr(r, MAIN_PROPERTIES[l_resource.replace("RESOURCE_", "")])

                # Summary vulns
                l_concrete_res['vulns']    = self.__get_vulns_counter(r.associated_vulnerabilities)

                m_resource_appender(l_concrete_res)

                continue

                #
                # Display the resource
                #

                # Get all no trivial properties
                m_valid_params = set()
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



            # Add to the global results
            m_results_append(l_res_result)

        context['info_by_resource'] = m_results


    #----------------------------------------------------------------------
    def __get_vulns_counter(self, vuln):
        """"""
        m_counter                   = Counter()

        m_total                     = len(vuln)

        # Init
        m_counter['critical']       = 0
        m_counter['high']           = 0
        m_counter['middle']         = 0
        m_counter['low']            = 0
        m_counter['informational']  = 0

        # Vulnerabilities by type
        if m_total > 0:

            for l_v in vuln:
                m_counter[l_v.level] +=1

        m_results                   = []
        m_results_append            = m_results.append
        for k,v in m_counter.iteritems():
            if v > 0:
                m_results_append({'level' : k, 'number' : v})

        return m_results
