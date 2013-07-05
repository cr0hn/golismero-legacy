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

from golismero.api.logger import Logger
from golismero.api.net.protocol import *
from golismero.api.plugin import TestingPlugin
from golismero.api.data.information import Information
from golismero.api.data.resource.url import Url
from golismero.api.config import Config
from golismero.api.net.web_utils import is_in_scope
from golismero.api.net.scraper import extract_from_html
from golismero.api.text.wordlist_api import WordListAPI


#----------------------------------------------------------------------
class Spider(TestingPlugin):
    """
    This plugin is a web spider.
    """


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [Url]


    #----------------------------------------------------------------------
    def recv_info(self, info):

        m_return = []

        m_url = info.url
        m_depth = info.depth

        # Check depth
        if m_depth > int(Config.audit_config.depth):
            return m_return

        Logger.log_verbose("Spidering URL: '%s'" % m_url)

        # Get a connection pool
        m_manager = NetworkAPI.get_connection()

        # Check if need follow first redirect
        p = None
        try:
            if m_depth == 0 and Config.audit_config.follow_first_redirect:
                p = m_manager.get(m_url, follow_redirect=True)
            else:
                p = m_manager.get(m_url)

        except NetworkException,e:
            Logger.log_more_verbose("Spider - value error while processing: '%s'. Error: %s" % (m_url, e.message))

        # If error p == None => return
        if not p:
            return m_return

        # Alert for redirect, if recursive spidering is not enabled.
        if m_depth == Config.audit_config.depth and p.http_response_code == 301:
            Logger.log("==> Initial redirection detected, but NOT followed. Try increasing the depth with the '-r' option.")

        # Send back the HTTP reponse
        ##m_return.append(p)

        # If it's a 301 response, get the Location header
        if p.http_response_code == 301:
            m_location = p.http_headers.get("Location", "")
            if m_location:
                m_return.append(Url(url=m_location, depth=m_depth + 1, referer=m_url))

        # Stop if there's no embedded information
        if not p.information or not p.information.startswith("text"):
            return m_return

        # If there's embedded information, it will be sent as a result
        m_return.append( p.information )

        # Stop if the embedded information is not HTML
        if p.information.information_type != Information.INFORMATION_HTML:
            return m_return

        # Get links from raw HTML
        m_links = extract_from_html(p.information.raw_data, m_url)

        # Do not follow URLs that contain certain keywords
        # TODO: put this in the plugin's configuration!
        m_forbidden = WordListAPI().get_wordlist(Config.plugin_extra_config["Wordlist_NoSpider"]["wordlist"])

        # Convert to Url data type and filter out out of scope and forbidden URLs
        m_return.extend(
            Url(url = u, depth = m_depth + 1, referer = m_url)
            for u in m_links
            if is_in_scope(u) and not any(x in u for x in m_forbidden) )

        # Send the results
        return m_return
