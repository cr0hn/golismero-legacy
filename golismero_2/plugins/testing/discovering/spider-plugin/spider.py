#!/usr/bin/python
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

from core.api.plugin import TestingPlugin
from core.api.results.information.information import Information
from core.api.logger import Logger
from core.api.results.information.url import Url
from thirdparty_libs.urllib3.util import parse_url
from thirdparty_libs.urllib3.exceptions import LocationParseError
from core.api.net.netmanager import *

class Spider(TestingPlugin):
    """
    This plugin is used por testing purposes and as example of use of plugins
    """

    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        """
        Check input parameters passed by the user.

        Parameters will be passed as an instance of 'GlobalParams'.

        If any parameter is not correct o there is an error, an
        exception must be raised.

        :param inputParams: input parameters to check
        :type inputParams: GlobalParams
        """
        pass

    #----------------------------------------------------------------------
    def display_help(self):
        """Get the help message for this plugin."""
        # TODO: this could default to the description found in the metadata.
        return self.__doc__

    #----------------------------------------------------------------------
    def recv_info(self, info):
        """Receive URLs."""

        print "Spider run"
        m_return = []

        self.send_info(Url("google.com"))

        if isinstance(info, Url):

            # Request this URL
            m_manager = NetManager.get_connection()
            p = m_manager.get(info)

            # If error p = None => return
            if not p or not p.information:
                return None

            # Get hostname and schema to fix URL
            try:
                m_parsed_url = parse_url(info.url)
            except LocationParseError:
                # Error while parsing URL
                return None

            Logger.log_more_verbose("Spidering URL '%s'\n" % info.url)


            m_links = []

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

                    # Must has, at least, 2 params
                    if len(t1) > 1:
                        if t1[1].find("url") != -1 and len(t1[1]) > 5:
                            m_links.append(t1[1][4:])

            # Remove duplicates and fix URL
            m_tmp = []
            for u in m_links:
                try:
                    l_parsed = parse_url(u)
                except LocationParseError:
                    # Error while parsing URL
                    continue

                if u == '':
                    continue

                # Fix hostname
                m_hostname = ""
                if l_parsed.hostname is None:
                    m_hostname = m_parsed_url.hostname
                else:
                    m_hostname = l_parsed.hostname

                # Fix scheme
                m_scheme = m_parsed_url.scheme if l_parsed.scheme is None else l_parsed.scheme

                # Fix path
                m_path = ""
                if l_parsed.path:
                    m_path = '' if len(l_parsed.path) == 1 and l_parsed.path == "/" else l_parsed.path

                # Fix params of query
                m_query = l_parsed.query if l_parsed.query else ''

                # Add complete URL
                m_url = "%s://%s%s%s" % (
                        m_scheme,
                        m_hostname,
                        m_path,
                        m_query
                    )

                # Add to temporal list
                m_tmp.append(m_url)

            # Create instances of Url, and delete duplicates
            m_return = [Url(u) for u in set(m_tmp)]




        return m_return


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        """
        Return a list of constants describing
        which messages are accepted by this plugin.

        Messages types can be found at the Message class.

        :returns: list -- list with constants
        """
        return [Information.INFORMATION_URL]