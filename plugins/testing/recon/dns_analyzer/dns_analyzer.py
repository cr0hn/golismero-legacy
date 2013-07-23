#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This plugin tries to find hidden subdomains.
"""

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: http://golismero-project.com
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

from golismero.api.config import Config
from golismero.api.data import discard_data
from golismero.api.data.information.dns import DnsRegister
from golismero.api.data.resource.domain import Domain
from golismero.api.logger import Logger
from golismero.api.net.dns import DNS
from golismero.api.parallel import pmap
from golismero.api.plugin import TestingPlugin
from golismero.api.text.wordlist_api import WordListAPI

from functools import partial


#--------------------------------------------------------------------------
#
# DNS analyzer
#
#--------------------------------------------------------------------------
class DNSAnalizer(TestingPlugin):
    """
    Find subdomains
    """


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [Domain]


    #----------------------------------------------------------------------
    def recv_info(self, info):

        m_domain = info.hostname

        # Checks if the hostname has been already processed
        m_return = None
        if not self.state.check(m_domain):
            Logger.log_more_verbose("starting DNS analyzer plugin")
            m_return = []

            # Send information status
            self.update_status(progress=0.19, text="Making DNS zone transfer")

            # Make the zone transfer
            m_return.extend(DNS.zone_transfer(m_domain))

            for l_type in DnsRegister.DNS_TYPES:
                self.update_status(progress=0.03, text="Making '%s' DNS query" % l_type)
                m_return.extend(DNS.resolve(m_domain, l_type))

            # Set the domain parsed
            self.state.set(m_domain, True)

            # Add the information to the host
            map(info.add_information, m_return)

            Logger.log_more_verbose("Ending DNS analyzer plugin. Found %s registers" % str(len(m_return)))

        return m_return



#--------------------------------------------------------------------------
#
# DNS Bruteforcer
#
#--------------------------------------------------------------------------
class DNSBruteforcer(TestingPlugin):
    """
    Find subdomains bruteforzing
    """


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [Domain]


    #----------------------------------------------------------------------
    def recv_info(self, info):

        m_domain = info.hostname

        # Checks if the hostname has been already processed
        m_return = None
        if not self.state.check(m_domain):
            Logger.log_more_verbose("starting DNS bruteforcer plugin")
            #
            # Looking for
            #
            m_subdomains = WordListAPI.get_advanced_wordlist_as_list("subs_small.txt")
            m_subdomains = [m_subdomains[x] for x in xrange(500)]

            # var used for update the plugin status
            m_num_probes = len(m_subdomains)

            # Run parallely
            func_with_static_field = partial(_get_subdomains_bruteforcer, m_domain)
            r = pmap(func_with_static_field, m_subdomains, pool_size=10)

            #
            # Remove repeated
            #

            # The results
            m_domains                  = set()
            m_domains_add              = m_domains.add
            m_domains_allready         = []

            m_ips                      = set()
            m_ips_add                  = m_ips.add
            m_ips_already              = []

            if r:
                for doms in r:
                    for dom in doms:
                        # Domains
                        if dom.type == "CNAME":
                            if not dom.target in m_domains_allready:
                                m_domains_allready.append(dom.target)
                                if dom.target in Config.audit_scope:
                                    m_domains.add(dom)
                                else:
                                    discard_data(dom)

                        # IPs
                        if dom.type == "A":
                            if dom.address not in m_ips_already:
                                m_ips_already.append(dom.address)
                                m_ips.add(dom)

                # Unify
                m_domains.update(m_ips)

                m_return = m_domains


                # Add the information to the host
                map(info.add_information, m_return)

            # Set the domain as processed
            self.state.set(m_domain, True)

            Logger.log_more_verbose("Ending DNS analyzer plugin. Found %s subdomains" % str(len(m_return)))


        return m_return


#----------------------------------------------------------------------
def _get_subdomains_bruteforcer(base_domain, subdomain):
    """
    Try to discover subdomains using bruteforce. This function is
    prepared to run parallely.

    To try to make as less as possible connections, discovered_domains
    contains a list with already discovered domains.

    :param base_domain: string with de domain to make the test.
    :type base_domain: str

    :param subdomain: string with the domain to process.
    :type subdomain: str
    """

    m_domain = "%s.%s" % (subdomain, base_domain)

    Logger.log_more_verbose("Looking for subdomain: %s" % m_domain)

    l_oks = DNS.get_a(m_domain, also_CNAME=True)

    return l_oks
