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
from golismero.api.net import NetworkException
from golismero.api.net.web_utils import download
from golismero.api.plugin import TestingPlugin
from golismero.api.data.information import Information
from golismero.api.data.resource.url import Url
from golismero.api.config import Config
from golismero.api.net.web_utils import is_in_scope
from golismero.api.net.scraper import extract_from_html, extract_from_text
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
        if Config.audit_config.depth is not None and m_depth > Config.audit_config.depth:
            return m_return

        Logger.log_verbose("Spidering URL: '%s'" % m_url)

        # Check if need follow first redirect
        p = None
        try:
            allow_redirects = Config.audit_config.follow_redirects or \
                             (m_depth == 0 and Config.audit_config.follow_first_redirect)
            p = download(m_url, self.check_download, allow_redirects=allow_redirects)

        except NetworkException,e:
            Logger.log_more_verbose("Spider - error while processing: '%s': %s" % (m_url, e.message))

        # If error p == None => return
        if not p:
            return m_return

        # Send back the data
        m_return.append(p)

        # TODO: If it's a 301 response, get the Location header

        # Get links
        Logger.log("Info type: %r" % p.information_type)
        if p.information_type == Information.INFORMATION_HTML:
            m_links = extract_from_html(p.raw_data, m_url)
        else:
            m_links = extract_from_text(p.raw_data, m_url)

        # Do not follow URLs that contain certain keywords
        m_forbidden = WordListAPI.get_wordlist(Config.plugin_config["wordlist_no_spider"])

        # Convert to Url data type and filter out out of scope and forbidden URLs
        m_return.extend(
            Url(url = u, depth = m_depth + 1, referer = m_url)
            for u in m_links
            if is_in_scope(u) and not any(x in u for x in m_forbidden) )

        # Send the results
        return m_return


    #----------------------------------------------------------------------
    def check_download(self, url, name, content_length, content_type):

        # Returns True to continue or False to cancel.
        return (

            # Check the file type is text.
            content_type and content_type.strip().lower().startswith("text/") and

            # Check the file is not too big.
            content_length and content_length < 100000
        )
