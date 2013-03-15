#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com
  Mario Vilas | mvilas@gmail.com

Golismero project site: http://code.google.com/p/golismero/
Golismero project mail: golismero.project@gmail.com

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

from core.api.logger import Logger
from core.api.net.protocol import NetworkAPI
from core.api.plugin import TestingPlugin
from core.api.data.resource.url import Url
from core.api.net.web_utils import parse_url, convert_to_absolute_url

from requests.exceptions import RequestException

import codecs


class Robots(TestingPlugin):
    """
    This plugin search and analyze robots.txt files.
    """

    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        """
        """
        pass

    #----------------------------------------------------------------------
    def display_help(self):
        # TODO: this could default to the description found in the metadata.
        return self.__doc__

    #----------------------------------------------------------------------
    def recv_info(self, info):
        if not isinstance(info, Url):
            raise TypeError("Expected Url, got %s instead" % type(info))

        # Parse the url
        m_parsed_url = parse_url(info.url)

        # Only work for the root url
        if (m_parsed_url.path and m_parsed_url.path != "/") or m_parsed_url.query or m_parsed_url.fragment:
            return

        # Get the url of hosts
        m_url_robots_txt = "%s://%s/robots.txt" % (m_parsed_url.scheme, m_parsed_url.hostname)

        # Only do this once per robots.txt file

        # Request this URL
        m_manager = NetworkAPI.get_connection()

        Logger.log_verbose("Robots - looking for robots.txt in URL: '%s'" % m_url_robots_txt)

        p = None
        try:
            p = m_manager.get(m_url_robots_txt)
        except ValueError,e:
            Logger.log_more_verbose("Robots - value error while processing: '%s'. Error: %s" % (l_url, e.message))
        except RequestException:
            Logger.log_more_verbose("Robots - timeout for url: '%s'." % l_url)


        if not p or not p.information and p.content_type == "text":
            Logger.log_error("Robots - no robots.txt found.")
            return

        # Text with info
        m_robots_text = p.information
        try:
            m_robots_text = m_robots_text.raw_data
        except AttributeError:
            pass

        # Prepare for unicode
        try:
            if m_robots_text.startswith(codecs.BOM_UTF8):
                m_robots_text = m_robots_text.decode('utf-8').lstrip(unicode(codecs.BOM_UTF8, 'utf-8'))
            elif m_robots_text.startswith(codecs.BOM_UTF16):
                m_robots_text = m_robots_text.decode('utf-16')
        except UnicodeDecodeError:
            Logger.log_error_verbose("Robots - error while parsing robots.txt: Unicode format error.")
            return

        # Results
        m_return = []
        m_return_bind = m_return.append
        tmp_discovered = None
        for rawline in m_robots_text.splitlines():
            m_line = rawline

            # Remove comments
            m_octothorpe = m_line.find('#')
            if m_octothorpe >= 0:
                m_line = m_line[:m_octothorpe]

            # Delete init spaces
            m_line = m_line.rstrip()

            # Ignore no valid lines
            if m_line == '' and ':' not in m_line:
                continue

            # Looking for URLs
            try:
                m_key, m_value = [x.strip() for x in m_line.split(':', 1)]
                m_key = m_key.lower()

                # If a wildcard found, is not a valid URL
                if '*' in m_value:
                    continue

                if m_key in ('disallow', 'allow', 'sitemap') and m_value:
                    tmp_discovered = convert_to_absolute_url(info.url, m_value)
                    Logger.log_more_verbose("Robots - discovered new url: %s" % tmp_discovered)
                    m_return_bind(tmp_discovered)
            except Exception,e:
                continue

        # Generate results
        return [Url(u) for u in m_return]





    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [Url.RESOURCE_URL]