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

from golismero.api.config import Config
from golismero.api.data.resource.url import Url
from golismero.api.data.vulnerability.information_disclosure.url_suspicious import SuspiciousURL
from golismero.api.plugin import TestingPlugin
from golismero.api.text.wordlist_api import WordListAPI


class SuspiciousURLPlugin(TestingPlugin):
    """
    Find suspicious words in URLs.
    """


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [Url]


    #----------------------------------------------------------------------
    def recv_info(self, info):

        m_url = info.url

        # Load wordlists
        m_wordlist_middle     = WordListAPI().get_wordlist(Config.plugin_extra_config['Wordlist_middle']['wordlist'])
        m_wordlist_extensions = WordListAPI().get_wordlist(Config.plugin_extra_config['Wordlist_extensions']['wordlist'])


        # Results store
        m_results          = []
        m_results_extend   = m_results.extend

        # Add matching keywords at any positions of URL
        m_results_extend([SuspiciousURL(info, x)
                          for x in m_wordlist_middle
                          if x in m_url])

        # Add matching keywords at any positions of URL
        m_results_extend([SuspiciousURL(info, x)
                          for x in m_wordlist_extensions
                          if m_url.endswith(x)])

        return m_results
