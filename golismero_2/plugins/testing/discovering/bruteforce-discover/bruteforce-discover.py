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
from core.api.net.web_utils import converto_to_absolute_url, is_in_scope
from core.api.plugin import TestingPlugin
from core.api.results.information.information import Information
from core.api.results.information.url import Url
from core.api.text.wordlistmanager import WordListManager
from os.path import splitext, split
from urllib3.util import parse_url
from urllib3.exceptions import LocationParseError
from core.api.text.text_utils import get_matching_level, generate_random_string

class BackupSearcher(TestingPlugin):
    """
    This plugin is used por testing purposes and as example of use of plugins
    """

    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        """
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

        if not isinstance(info, Url):
            raise TypeError("Expected Url, got %s instead" % type(info))

        # Check if Url is in scope
        if not is_in_scope(info.url):
            return

        # Parsed original URL
        m_parsed_url = None
        try:
            m_parsed_url = parse_url(info.url)
        except LocationParseError:
            return

        # Split URL as their parts
        m_url_parts = {}
        m_url_parts['scheme']        = m_parsed_url.scheme if m_parsed_url.scheme else ''
        m_url_parts['host']          = m_parsed_url.host if m_parsed_url.host else ''
        m_url_parts['path']          = m_parsed_url.path if m_parsed_url.path else ''
        m_url_parts['path_ext']      = splitext(m_parsed_url.path)[1] if m_parsed_url.path else ''
        m_url_parts['path_folder']   = split(m_parsed_url.path)[0] if m_parsed_url.path and m_url_parts['path_ext'] else ''
        m_url_parts['path_filename'] = split(m_parsed_url.path)[1] if m_parsed_url.path and m_url_parts['path_ext'] else ''
        m_url_parts['query']         = m_parsed_url.query if m_parsed_url.query else ''


        # if URL looks like:
        # - www.site.com/
        # - www.site.com
        if (not m_url_parts['path'] and not m_url_parts['query'])    \
           or (not m_url_parts['path_ext'] and not m_url_parts['query']):
            return

        # To log
        Logger.log_more_verbose("[i] Bruteforcing for discovering in URL: '%s'" % info.url)

        # Result info
        m_discovered = []

        # Network manager reference
        m_net_manager = NetManager.get_connection()

        #
        # Load wordlists
        #

        # Suffixes
        m_suffixes = WordListManager().get_wordlist("Extensions.Backup.fuzz")
        # Preffixes

        # Hidden files


        #
        # Generate an error in server to get an error page, using a random string
        #
        # Make the URL
        m_error_url = "%s://%s%s%s.%s%s" % (
            m_url_parts['scheme'],
            m_url_parts['host'],
            m_url_parts['path_folder'],
            m_url_parts['path_filename'],
            generate_random_string(),
            m_url_parts['query']
        )
        # Get the request
        m_error_response = m_net_manager.get(m_error_url).raw

        #
        # Start with bruteforcing. Cases to try:
        #
        # 1 - Testing suffixes
        # 2 - Testing preffixes
        # 3 - Testing predictable files: hidden files, config, lost files...
        #

        m_urls_to_test = []
        #
        # 1 - Suffixes
        m_urls_to_test.extend(self.make_url_with_suffixes(m_suffixes, m_url_parts))

        #
        # 2 - preffixes
        m_urls_to_test.extend([])

        # 3 - Predictable files
        m_urls_to_test.extend([])

        # Test all URLs
        for l_url in m_urls_to_test:

            # Ge URL
            p = m_net_manager.get(l_url)

            # Check if url is acceptable by comparing
            # result content.
            #
            # If the maching level between error page and
            # this l_url is greater than 52%, then is the
            # same URL and discart it.
            if p and p.http_response_code == 200:

                if get_matching_level(m_error_response, p.raw) < 52:
                    # Store it
                    m_discovered.append(l_url)

                    # Send responde, HTML and a URL to kernel
                    self.send_info(Url(l_url))
                    self.send_info(p)
                    self.send_info(p.information)


        # Create vulns instances
        #return [Url(u) for u in set()]

    #----------------------------------------------------------------------
    def get_accepted_info(self):
        """
        Accepted information
        """
        return [Information.INFORMATION_URL]



    #----------------------------------------------------------------------
    def make_url_with_suffixes(self, wordlist, url_parts):
        """
        Creates URLs with suffixes and return it.

        :param wordlist: iterable structure with wordlist.
        :type wordlist: WordList

        :param url_parts: dict with parts of an URL to permute.
        :type url_parts: dict
        """
        m_return = []

        for l_suffix in wordlist:

            # Make url
            m_return.append("%s://%s%s%s.%s%s" % (
                url_parts['scheme'],
                url_parts['host'],
                url_parts['path_folder'],
                url_parts['path_filename'],
                l_suffix,
                url_parts['query']
            ))

        return m_return




    #----------------------------------------------------------------------
    def is_url_acceptable(self, error_page, page_to_test):
        """
        Determine if passed URL if a valid page or is a mutation
        of error page.

        :param error_page: content of the well known error page.
        :type error_page: str

        :param page_to_test: content of the page to test.
        :type page_to_test: str

        :return: bool -- True if url is acceptable. False otherwise.
        """
        return True if get_matching_level(error_page, page_to_test) > 52 else False



