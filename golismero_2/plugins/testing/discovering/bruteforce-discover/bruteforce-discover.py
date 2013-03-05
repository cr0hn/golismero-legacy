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
from core.api.net.web_utils import convert_to_absolute_url, is_in_scope
from core.api.plugin import TestingPlugin
from core.api.results.information.information import Information
from core.api.results.information.url import Url
from core.api.results.vulnerability.information_disclosure.url_disclosure import UrlDisclosure
from core.api.text.wordlistmanager import WordListManager
from os.path import splitext, split, sep
from urllib3.util import parse_url
from urllib3.exceptions import LocationParseError
from core.api.text.text_utils import get_matching_level, generate_random_string


class BackupSearcher(TestingPlugin):
    """
    This plugin is used por testing purposes and as example of use of plugins
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
        return [Information.INFORMATION_URL]


    #----------------------------------------------------------------------
    def recv_info(self, info):

        if not isinstance(info, Url):
            raise TypeError("Expected Url, got %s instead" % type(info))

        # Check if URL is in scope
        if not is_in_scope(info.url):
            return

        # Parse original URL
        m_parsed_url = None
        try:
            m_parsed_url = parse_url(info.url)
        except LocationParseError:
            return

        # Split URL
        m_url_parts = {}
        m_url_parts['scheme']        = m_parsed_url.scheme if m_parsed_url.scheme else ''
        m_url_parts['host']          = m_parsed_url.host if m_parsed_url.host else ''
        m_url_parts['path']          = m_parsed_url.path if m_parsed_url.path else ''
        m_url_parts['path_filename_ext']      = splitext(m_parsed_url.path)[1] if m_parsed_url.path else ''
        m_url_parts['path_folder']   = split(m_parsed_url.path)[0] if m_parsed_url.path and m_url_parts['path_filename_ext'] else ''
        m_url_parts['path_filename'] = split(m_parsed_url.path)[1] if m_parsed_url.path and m_url_parts['path_filename_ext'] else ''
        m_url_parts['path_filename_without_ext'] = splitext(m_url_parts['path_filename'])[0] if m_parsed_url.path and m_url_parts['path_filename'] else ''
        m_url_parts['query']         = m_parsed_url.query if m_parsed_url.query else ''
        # Fix path folder
        m_url_parts['path_folder'] = m_url_parts['path_folder'] if m_url_parts['path_folder'].endswith("/") else m_url_parts['path_folder'] + "/"

        Logger.log_more_verbose("[i] Bruteforcing for discovering in URL: '%s'" % info.url)

        # Result info
        m_return = []

        # Network manager reference
        m_net_manager = NetManager.get_connection()

        #
        # Load wordlists
        #
        m_wordlist = {}

        # 1 - Suffixes
        m_wordlist['suffixes'] = []
        m_wordlist['suffixes'].append(WordListManager().get_wordlist("fuzzdb_discovery_filenamebruteforce_extensions.backup.fuzz"))
        m_wordlist['suffixes'].append(WordListManager().get_wordlist("golismero_predictables_file-compressed-suffixes"))


        # 2 - Prefixes
        m_wordlist['prefixes'] = []
        m_wordlist['prefixes'].append(WordListManager().get_wordlist("golismero_predictables_file-prefix"))
        m_wordlist['prefixes'].append(WordListManager().get_wordlist("fuzzdb_discovery_filenamebruteforce_copy_of.fuzz"))

        # 3 - File extensions
        m_wordlist['extensions'] = []
        m_wordlist['extensions'].append(WordListManager().get_wordlist("golismero_predictables_java-file-extensions"))
        m_wordlist['extensions'].append(WordListManager().get_wordlist("golismero_predictables_microsoft-file-extensions"))
        m_wordlist['extensions'].append(WordListManager().get_wordlist("golismero_predictables_file-compressed-suffixes"))
        m_wordlist['extensions'].append(WordListManager().get_wordlist("golismero_predictables_microsoft-file-extensions"))

        # 5 - Predictable filename and folders
        m_wordlist['predictable_files'] = []
        m_wordlist['predictable_files'].append(WordListManager().get_wordlist("fuzzdb_discovery_predictableres_cgi_microsoft.fuzz"))
        m_wordlist['predictable_files'].append(WordListManager().get_wordlist("fuzzdb_discovery_predictableres_apache.fuzz"))
        m_wordlist['predictable_files'].append(WordListManager().get_wordlist("fuzzdb_discovery_predictableres_iis.fuzz"))
        m_wordlist['predictable_files'].append(WordListManager().get_wordlist("fuzzdb_discovery_predictableres_php.fuzz"))
        m_wordlist['predictable_files'].append(WordListManager().get_wordlist("fuzzdb_discovery_predictableres_passwords.fuzz"))
        m_wordlist['predictable_files'].append(WordListManager().get_wordlist("fuzzdb_discovery_predictableres_oracle9i.fuzz"))
        m_wordlist['predictable_files'].append(WordListManager().get_wordlist("fuzzdb_discovery_predictableres_unixdotfiles.fuzz"))

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


        # Impact vectors. Available values: 0 - 3.
        m_impact_vectors = {
            "suffixes" : 2,
            "prefixes" : 1,
            "file_extensions": 1,
            "permutations" : 1,
            "predictables": 3
        }

        #
        # Start with bruteforcing. Cases to try:
        #
        # 1 - Testing suffixes
        # 2 - Testing prefixes
        # 3 - Testing changing extension of files
        # 4 - Testing filename permutations
        # 5 - Testing predictable files and dirs: hidden files, config, lost files...
        #
        m_urls_to_test = {}


        # if URL looks like don't process suffixes:
        # - www.site.com/index.php
        #
        if not self.is_url_folder_point(m_url_parts):
            #
            #   1 - Suffixes
            m_urls_to_test["suffixes"] = self.make_url_with_suffixes(m_wordlist, m_url_parts)

            #
            #   2 - Preffixes
            m_urls_to_test["prefixes"] = self.make_url_with_suffixes(m_wordlist, m_url_parts)

            #
            #   3 - Changing extension of files
            m_urls_to_test["fife_extensions"] = self.make_url_changing_extensions(m_wordlist, m_url_parts)

            #
            #   4 - Permutation of file
            m_urls_to_test["permutations"] = self.make_url_permutate_filename(m_url_parts)


        # if URL looks like don't process suffixes:
        # - www.site.com/ or
        # - www.site.com
        #
        if self.is_url_folder_point(m_url_parts):
            #
            # 5 - Predictable files
            m_urls_to_test["predictables"] = self.make_url_with_files_or_folder(m_wordlist, m_url_parts)

        # Test all URLs (deleting duplicates)
        for l_name, l_iter in m_urls_to_test.iteritems():
            for l_url in l_iter:

                # Ge URL
                p = m_net_manager.get(l_url)

                # Check if the url is acceptable by comparing
                # the result content.
                #
                # If the maching level between the error page
                # and this url is greater than 52%, then it's
                # the same URL and must be discarded.
                #
                if p and p.http_response_code == 200:

                    if get_matching_level(m_error_response, p.raw) < 52:
                        # Send response, HTML and URL to kernel
                        self.send_info(Url(l_url))
                        self.send_info(p)
                        self.send_info(p.information)

                        #
                        # Vulnerability
                        #
                        l_vuln = UrlDisclosure(l_url)
                        # Calculate
                        l_vuln.severity = m_impact_vectors[l_name]
                        # Send
                        self.send_info(l_vuln)


    #----------------------------------------------------------------------
    def make_url_with_suffixes(self, wordlist, url_parts):
        """
        Creates an iterator of URLs with suffixes.

        :param wordlist: Wordlist iterator.
        :type wordlist: WordList

        :param url_parts: Parsed URL to permute.
        :type url_parts: dict

        :returns: iterator with urls.
        """


        if not wordlist or not url_parts:
            yield None

        for l_wordlist in wordlist['suffixes']:
            # For errors
            if not l_wordlist:
                Logger.log_error("Can't load one of wordlist fo category: 'suffixes'.")
                continue

            for l_suffix in l_wordlist:

                yield "%s://%s%s%s.%s%s" % (
                    url_parts['scheme'],
                    url_parts['host'],
                    url_parts['path_folder'],
                    url_parts['path_filename'],
                    l_suffix,
                    url_parts['query']
                )


    #----------------------------------------------------------------------
    def make_url_with_preffixes(self, wordlist, url_parts):
        """
        Creates an iterator of URLs with prefixes.

        :param wordlist: Wordlist iterator.
        :type wordlist: WordList

        :param url_parts: Parsed URL to permute.
        :type url_parts: dict

        :returns: iterator with urls.
        """


        if not wordlist or not url_parts:
            yield None

        # Making predictables
        for l_wordlist in wordlist_suffix['prefixes']:
            # For errors
            if not l_wordlist:
                Logger.log_error("Can't load wordlist for category: 'prefixes'.")
                continue

            for l_preffix in l_wordlist:

                yield "%s://%s%s%s%s%s" % (
                    url_parts['scheme'],
                    url_parts['host'],
                    url_parts['path_folder'],
                    l_preffix,
                    url_parts['path_filename'],
                    url_parts['query']
                )



    #----------------------------------------------------------------------
    def make_url_with_files_or_folder(self, wordlist, url_parts):
        """
        Creates an iterator of URLs with guessed files and subfolders.

        :param wordlist: Wordlist iterator.
        :type wordlist: WordList

        :param url_parts: Parsed URL to permute.
        :type url_parts: dict
        """

        if not wordlist or not url_parts:
            yield None

        m_wordlist_predictable = set() if not wordlist['predictable_files'] else wordlist['predictable_files']
        m_wordlist_suffix = set() if not wordlist['suffixes'] else wordlist['suffixes']

        # Making predictables
        for l_wordlist in m_wordlist_predictable:
            # For errors
            if not l_wordlist:
                Logger.log_error("Can't load wordlist for category: 'predictable_files'.")
                continue

            for l_path in l_wordlist:

                # Delete wordlist comment lines
                if l_path.startswith("#"):
                    continue

                # Fix l_path
                l_fixed_path = l_path[1:] if l_path.startswith("/") else l_path

                yield "%s://%s%s%s" % (
                    url_parts['scheme'],
                    url_parts['host'],
                    url_parts['path_folder'],
                    l_fixed_path,
                )

        # For locations source code of application, like:
        # www.site.com/app1/ -> www.site.com/app1.war
        #
        m_last_folder_parts = split(url_parts['path_folder'])[0]
        for l_wordlist in m_wordlist_suffix:
            # For errors
            if not l_wordlist:
                Logger.log_error("Can't load wordlist for category: 'suffixes'.")
                continue
            for l_suffix in l_wordlist:
                yield "%s://%s%s/%s." % (
                    url_parts['scheme'],
                    url_parts['host'],
                    m_last_folder_parts,
                    l_suffix,
                )




    #----------------------------------------------------------------------
    def make_url_changing_extensions(self, wordlist, url_parts):
        """
        Creates an iterator of URLs with alternative file extensions.

        :param wordlist: Wordlist iterator.
        :type wordlist: WordList

        :param url_parts: Parsed URL to permute.
        :type url_parts: dict
        """

        if not wordlist or not url_parts:
            yield None

        # Making predictables
        for l_wordlist in wordlist['extensions']:
            # For errors
            if not l_wordlist:
                Logger.log_error("Can't load wordlist for category: 'extensions'.")
                continue
            for l_suffix in l_wordlist:
                yield "%s://%s%s%s.%s%s" % (
                    url_parts['scheme'],
                    url_parts['host'],
                    url_parts['path_folder'],
                    url_parts['path_filename_without_ext'],
                    l_suffix,
                    url_parts['query']
                )


    #----------------------------------------------------------------------
    def make_url_permutate_filename(self, url_parts):
        """
        Creates an iterator of URLs with mutated filenames.

        :param url_parts: Parsed URL to permute.
        :type url_parts: dict
        """

        if not url_parts:
            yield None

        m_base_string = "%s://%s%s" % (
                    url_parts['scheme'],
                    url_parts['host'],
                    url_parts['path_folder']
                )

        # Change extension to upper case
        yield "%s%s%s%s" % (
            m_base_string,
            url_parts['path_filename_without_ext'],
            url_parts['path_filename_ext'].upper(),
            url_parts['query']
        )

        # Adding numeric ends of filename
        for n in xrange(5):
            # Format: index1.php
            yield "%s%s%s%s%s" % (
                m_base_string,
                url_parts['path_filename_without_ext'],
                str(n),
                url_parts['path_filename_ext'],
                url_parts['query']
            )

            # Format: index_1.php
            yield "%s%s_%s%s%s" % (
                m_base_string,
                url_parts['path_filename_without_ext'],
                str(n),
                url_parts['path_filename_ext'],
                url_parts['query']
            )


    #----------------------------------------------------------------------
    def is_url_acceptable(self, error_page, page_to_test):
        """
        Determine if the given URL is a valid page or a variant
        of the error page.

        :param error_page: content of the well known error page.
        :type error_page: str

        :param page_to_test: content of the page to test.
        :type page_to_test: str

        :return: bool -- True if url is acceptable, False otherwise.
        """
        return get_matching_level(error_page, page_to_test) > 52


    #----------------------------------------------------------------------
    def is_url_folder_point(self, url_parts):
        """
        Determine if the given URL points to a folder or a file:

        if URL looks like:
        - www.site.com/
        - www.site.com

        then ==> Return True

        if URL looks like:
        - www.site.com/index.php
        - www.site.com/index.php?id=1&name=bb

        then ==> Return False

        :param url_parts: Parsed URL to test.
        :type url_parts: dict

        :return: bool -- True if it's a folder, False if not.

        """
        return not (
            (url_parts['path'] or url_parts['query']) and \
            (url_parts['path_filename_ext'] or url_parts['query'])
        )
