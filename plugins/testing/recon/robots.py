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

from golismero.api.logger import Logger
from golismero.api.net.protocol import *
from golismero.api.plugin import TestingPlugin
from golismero.api.data.resource.url import Url
from golismero.api.data.resource.domain import Domain
from golismero.api.net.web_utils import *
from golismero.api.text.matching_analyzer import *

import codecs
from urlparse import urljoin


class Robots(TestingPlugin):
    """
    This plugin search and analyze robots.txt files.
    """


    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        pass


    #----------------------------------------------------------------------
    def display_help(self):
        # TODO: this could default to the description found in the metadata.
        return self.__doc__


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [Domain.RESOURCE_DOMAIN]


    #----------------------------------------------------------------------
    def recv_info(self, info):
        if not isinstance(info, Domain):
            raise TypeError("Expected Url, got %s instead" % type(info))

        # Get the url of hosts
        m_url = fix_url(info.name)
        m_url_robots_txt = urljoin(m_url, 'robots.txt')

        Logger.log_verbose("Robots - looking for robots.txt in URL: '%s'" % m_url_robots_txt)

        # Request this URL
        m_manager = NetworkAPI.get_connection()

        p = None
        try:
            p = m_manager.get(m_url_robots_txt)
        except NetworkException,e:
            Logger.log_more_verbose("Robots - value error while processing: '%s'. Error: %s" % (m_url_robots_txt, e.message))

        # Check for errors
        if not p or not p.content_type == "text" or not p.information:  # order is important!
            Logger.log_verbose("Robots - no robots.txt found.")
            return

        # Text with info
        m_robots_text = p.information

        # Prepare for unicode
        try:
            if m_robots_text.startswith(codecs.BOM_UTF8):
                m_robots_text = m_robots_text.decode('utf-8').lstrip(unicode(codecs.BOM_UTF8, 'utf-8'))
            elif m_robots_text.startswith(codecs.BOM_UTF16):
                m_robots_text = m_robots_text.decode('utf-16')
        except UnicodeDecodeError:
            Logger.log_error_verbose("Robots - error while parsing robots.txt: Unicode format error.")
            return

        # Extract URLs
        m_discovered_urls = []
        m_discovered_urls_append = m_discovered_urls.append
        tmp_discovered = None
        for rawline in m_robots_text.splitlines():
            m_line = rawline

            # Remove comments
            m_octothorpe = m_line.find('#')
            if m_octothorpe >= 0:
                m_line = m_line[:m_octothorpe]

            # Delete init spaces
            m_line = m_line.rstrip()

            # Ignore invalid lines
            if not m_line or ':' not in m_line:
                continue

            # Looking for URLs
            try:
                m_key, m_value = m_line.split(':', 1)
                m_key = m_key.strip().lower()
                m_value = m_value.strip()

                # Ignore wildcards
                if '*' in m_value:
                    continue

                if m_key in ('disallow', 'allow', 'sitemap') and m_value:
                    tmp_discovered = urljoin(m_url, m_value)
                    Logger.log_more_verbose("Robots - discovered new url: %s" % tmp_discovered)
                    m_discovered_urls_append( Url(tmp_discovered) )
            except Exception,e:
                continue


        #
        # Filter results
        #

        # Generating error page
        m_error_page = generate_error_page_url(m_url_robots_txt)
        m_response_error_page = m_manager.get(m_error_page)

        # Analyze results
        m_analyzer = MatchingAnalyzer(m_response_error_page.raw)

        # Add results for analyze
        for l_url in m_discovered_urls:
            m_analyzer.append(m_manager.get(l_url).raw)

        # Generate results
        return [r for i in m_analyzer.unique_texts]
