#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
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

from golismero.api.logger import Logger
from golismero.api.net.protocol import *
from golismero.api.plugin import TestingPlugin
from golismero.api.data.resource.url import Url
from golismero.api.data.resource.domain import Domain
from golismero.api.data.information.information import Information
from golismero.api.config import Config
from golismero.api.net.web_utils import parse_url, convert_to_absolute_urls, is_in_scope
from golismero.api.net.scraper import extract_from_html

from time import time
from os import getpid


#----------------------------------------------------------------------
class Spider(TestingPlugin):
    """
    This plugin is a web spider.
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

        # Extract data
        if not isinstance(info, Url):
            raise TypeError("Expected Url, got %s instead" % type(info))

        m_url = info.url
        m_deep = info.depth

        # Check depth
        if m_deep > int(Config.audit_config.depth):
            return

        Logger.log_verbose("Spidering URL: '%s'" % m_url)

        # Request this URL
        m_manager = NetworkAPI.get_connection()

        # Check if need follow first redirect
        p = None
        try:
            if m_deep == 0 and Config.audit_config.follow_first_redirect:
                p = m_manager.get(m_url, follow_redirect=True)
            else:
                p = m_manager.get(m_url)

            # Associate the resource
            p.associated_resource = info
            p.information.associated_resource = info

        except NetworkException,e:
            Logger.log_more_verbose("Spider - value error while processing: '%s'. Error: %s" % (m_url, e.message))

        # If error p == None => return
        if not p:
            return

        # Alert for redirect, if recursive spidering is not enabled.
        if m_deep == Config.audit_config.depth and p.http_response_code == 301:
            Logger.log("==> Initial redirection detected, but NOT followed. Try increasing the depth with the '-r' option.")

        # Send back the HTTP reponse to the kernel
        self.send_info(p)

        # If it's a 301 response, get the Location header
        if p.http_response_code == 301:
            m_location = p.http_headers.get("Location", "")
            if m_location:
                self.send_info(Url(url=m_location, depth=m_deep + 1, referer=m_url))

        # Stop if there's no embedded information
        if not p.information:
            return

        # Send back the embedded information to the kernel
        self.send_info(p.information)

        # Stop if the embedded information is not HTML
        if p.information.information_type != Information.INFORMATION_HTML:
            return

        s1 = time()

        # Get links from raw HTML
        m_links = extract_from_html(p.information.raw_data, m_url)

        # Do not follow URLs that contain certain keywords
        # TODO: put this in the plugin's configuration!
        m_forbidden = (
            "logout",
            "logoff",
            "exit",
            "sigout",
            "signout",
        )

        # Convert to Url data type and filter out out of scope and forbidden URLs
        m_return = [ Url(url=u, depth=m_deep + 1, referer=m_url)
                     for u in m_links
                     if is_in_scope(u) and not any(x in u for x in m_forbidden) ]

        s2 = time()

        # Send the URLs
        return m_return


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [Url.RESOURCE_URL]

