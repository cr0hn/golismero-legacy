#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Author: Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com

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
from core.api.net.netmanager import *
from core.api.net.web_utils import *
from core.api.plugin import TestingPlugin
from core.api.results.information.information import Information
from core.api.results.information.url import Url
from core.api.config import Config
from urllib3.util import parse_url
from urllib3.exceptions import LocationParseError
from time import time
from os import getpid



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
        if not isinstance(info, Url):
            raise TypeError("Expected Url, got %s instead" % type(info))

        # Check recursivity
        if info.depth > Config().audit_config.recursivity:
            return

        print "Spider - Process PID: %s " % str(getpid()) # FIXME

        m_return = []

        # Request this URL
        m_manager = NetManager.get_connection()

        # Check if need follow first redirect
        if info.depth == 0 and Config().audit_config.follow_first_redirect:
            p = m_manager.get(info, follow_redirect=True)
        else:
            p = m_manager.get(info)

        # If error p == None => return
        if not p:
            return

        # Alert for redirect, if recursivity is not enabled.
        if info.depth == Config().audit_config.recursivity and p.http_response_code == 301:
            Logger.log("==> Initial redirection detected, and not followed. Try with increasion recursivity with '-r' option.")

        # Send back the HTTP reponse to the kernel
        self.send_info(p)

        # Stop if there's no embedded information
        if not p.information:
            return

        # Send back the embedded information to the kernel
        self.send_info(p.information)

        # Stop if the embedded information is not HTML
        if p.information.information_type != Information.INFORMATION_HTML:
            return

        # Get hostname and schema to fix URL
        try:
            m_parsed_url = parse_url(info.url)
        except LocationParseError:
            # Error while parsing URL
            return [p, p.information]

        Logger.log_more_verbose("Spidering URL: '%s'" % info.url)

        s1 = time()

        m_links = []

        # If is 301 response, get Location property
        if p.http_response_code == 301:
            try:
                m_links.append(p.http_headers["Location"])
            except KeyError:
                pass

        # Get links
        m_links.extend([x.attrs['href'] for x in p.information.links if 'href' in x.attrs and not x.attrs["href"].startswith("#") and not x.attrs["href"].startswith("javascript")])

        # Get links to css
        m_links.extend([x.attrs['href'] for x in p.information.css_links if 'href' in x.attrs])

        # Get javascript links
        m_links.extend([x.attrs['src'] for x in p.information.javascript_links if 'src' in x.attrs])

        # Get Action of forms
        m_links.extend([x.attrs['src'] for x in p.information.forms if 'src' in x.attrs])

        # Get links to objects
        m_links.extend([x.attrs['param']['movie'] for x in p.information.objects if 'param' in x.attrs and 'movie' in x.attrs['param']])

        # Get HTML redirections in meta
        if p.information.metas:
            # We are looking for content like: '...; url=XXXXX>'
            if "content" in p.information.metas[0].attrs:
                t1 = p.information.metas[0].attrs["content"].split(';')

                # Must have at least 2 params
                if len(t1) > 1:
                    if t1[1].find("url") != -1 and len(t1[1]) > 5:
                        m_links.append(t1[1][4:])

        # Create instances of Url, convert to absolute url, remove duplicates URL and check if URLs are in scope.
        converted_urls = convert_to_absolute_urls(info.url, m_links)
        if converted_urls:
            # Not followed URL that contains:
            m_no_follow = (
                "logout",
                "logoff",
                "exit",
                "sigout"
            )

            m_return = map(lambda u: Url(url=u, depth=info.depth + 1, referer=info.url), filter(lambda x: is_in_scope(x) and x not in m_no_follow, converted_urls))

        s2 = time()
        Logger.log_more_verbose("Spider: Time to process links: %ss" % (s2 - s1))

        # Send info
        return m_return


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [Information.INFORMATION_URL]
