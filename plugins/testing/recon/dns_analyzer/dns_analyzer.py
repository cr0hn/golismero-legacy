#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """This plugin try to find hidden subdomains"""

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


from golismero.api.data.resource.domain import Domain
from golismero.api.logger import Logger
from golismero.api.plugin import TestingPlugin
from golismero.api.text.wordlist_api import WordListAPI
from golismero.api.net.dns import DNS



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
		d = None
		if not self.state.check(m_domain):
			print "AAAA"

			d = main_dns_analyzer(m_domain)

			self.state.set(m_domain, True)

		return d

#----------------------------------------------------------------------
def main_dns_analyzer(base_domain):
	"""
	Looking for new domains
	"""

	get_subdomains_bruteforcer(base_domain, [])

#----------------------------------------------------------------------
def get_subdomains_bruteforcer(base_domain, discovered_domains):
	"""
	Try to discover subdomains using bruteforce.

	To try to make as less as possible connections, discovered_domains
	contains a list with already discovered domains.

	:param base_domain: string with de domain to make the test.
	:type base_domain: str

	:param discovered_domains: List with already found domains.
	:type discovered_domains: list(str)
	"""
	m_subdomains = WordListAPI.get_advanced_wordlist_as_list("subs_small.txt")

	# Select only subdomains that are not already processed.
	m_non_repeated_domains = [d for d in m_subdomains if d not in discovered_domains]

	m_non_repeated_domains = ["kkkk", "jjjj"]

	# Manager for make DNS queries.
	m_dom_manager = DNS()

	# The results
	m_domains                  = set()
	m_domains_add              = m_domains.add
	m_domains_allready         = []

	m_ips                      = set()
	m_ips_add                  = m_ips.add
	m_ips_already              = []

	for l_d in m_non_repeated_domains:
		l_domain = "%s.%s" % (l_d, base_domain)

		Logger.log_more_verbose("Looking for subdomain: %s" % l_domain)

		l_oks = m_dom_manager.get_a(l_domain, also_CNAME=True)

		if l_oks:
			for dom in l_oks:
				# Domains
				if dom.type == "CNAME":
					if not dom.target in m_domains_allready:
						m_domains_allready.append(dom.target)
						m_domains.add(dom)

				# IPs
				if dom.type == "A":
					if dom.address not in m_ips_already:
						m_ips_already.append(dom.address)
						m_ips.add(dom)

	#Logger.log_error_more_verbose("!! Subdomain '%s' discovereds: " % ','.join(m_domains))
	#Logger.log_error_more_verbose("!! IPs '%s' discovereds: " % ','.join(m_ips))

	print "###"
	print m_domains
	print "@@@@"
	print m_ips
	print "----"

	print m_domains


#----------------------------------------------------------------------
def get_all_registers():
	""""""


#----------------------------------------------------------------------
def get_zone_transfer():
	""""""

#----------------------------------------------------------------------
def get_reverse_lookup():
	""""""




