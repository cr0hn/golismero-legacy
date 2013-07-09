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
from golismero.api.net.protocol import NetworkAPI
from golismero.api.plugin import TestingPlugin
from golismero.api.text.wordlist_api import WordListAPI



class DNSBruteforce(TestingPlugin):
    """
    Find subdomains
    """


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [Domain]


    #----------------------------------------------------------------------
    def recv_info(self, info):

        m_domain = info.name

        d = main_dns_bruter(m_domain)

        return d

#----------------------------------------------------------------------
def main_dns_bruter(base_domain):
    """
    Looking for new domains
    """
    r = WordListAPI.get_advanced_wordlist_as_list("/Users/Dani/Documents/Pruebas/subbrute/subs_small.txt")

    print "XXXXX"
    for x in r:
        print x