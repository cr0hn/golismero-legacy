#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn@cr0hn.com
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

# Acknowledgments:
#
#   We'd like to thank @capi_x for his idea on how
#   to detect fake 200 responses from servers by
#   issuing known good and bad queries and diffing
#   them to calculate the deviation.
#
#   https://twitter.com/capi_x

from golismero.api.config import Config
from golismero.api.data.resource.url import Url
from golismero.api.data.vulnerability.information_disclosure.url_disclosure import UrlDisclosure
from golismero.api.logger import Logger
from golismero.api.net.protocol import *
from golismero.api.net.web_utils import DecomposedURL, is_in_scope, is_method_allowed, generate_error_page_url
from golismero.api.plugin import TestingPlugin
from golismero.api.text.matching_analyzer import *
from golismero.api.text.wordlist_api import WordListAPI

import threading


# Impact vectors. Available values: 0 - 3.
severity_vectors = {
    "suffixes" : 4,
    "prefixes" : 3,
    "file_extensions": 3,
    "permutations" : 3,
    "predictables": 4
}


#-------------------------------------------------------------------------
class ParallelBruter(threading.Thread):
    """
    Worker threads for the bruteforcer plugin.
    """

    #----------------------------------------------------------------------
    def __init__(self, wordlist, results, net, method):
        self.__wordlist = wordlist
        self.__results = results
        self.__net = net
        self.__method = method
        super(ParallelBruter,self).__init__()


    #----------------------------------------------------------------------
    def run(self):

        # Test all URLs (deleting duplicates)
        while True:
            m_name = None
            m_iter = None

            try:
                m_name, m_iter = self.__wordlist.popitem()
            except KeyError,e:
                break

            for l_url in m_iter:
                Logger.log_more_verbose("Bruteforcer - testing url: '%s'." % l_url)

                # Ge URL
                p = None
                try:
                    p = self.__net.get(l_url, cache=False, method=self.__method)
                except NetworkException,e:
                    Logger.log_more_verbose("Bruteforcer - value error while processing: '%s'. Error: %s" % (l_url, e.message))

                # Check if the url is acceptable by comparing
                # the result content.
                #
                # If the maching level between the error page
                # and this url is greater than 52%, then it's
                # the same URL and must be discarded.
                #
                if p and p.http_response_code == 200:

                    # If the method used to get URL was HEAD, get complete URL
                    if self.__method != "GET":
                        p = self.__net.get(l_url, cache=False, method="GET")

                    # Append for analyzate and display info if is accepted
                    if self.__results.append(p.raw,url=l_url,risk = severity_vectors[m_name]):
                        Logger.log_more_verbose("Bruteforcer - Discovered partial url: '%s'!!" % l_url)

                        # Send_ response, HTML and URL to kernel.
                        #m_return = [Url(l_url), p]
                        #if p.information:
                        #    m_return.append(p.information)
                        #return m_return


#----------------------------------------------------------------------
class BackupSearcher(TestingPlugin):


    #----------------------------------------------------------------------
    def check_input_params(self, inputParams):
        pass


    #----------------------------------------------------------------------
    def display_help(self):
        # TODO: this could default to the description found in the metadata.
        return self.__doc__


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [Url.RESOURCE_URL]


    #----------------------------------------------------------------------
    def recv_info(self, info):
        if not isinstance(info, Url):
            raise TypeError("Expected Url, got %s instead" % type(info))

        # XXX DEBUG
        return

        # Check if URL is in scope
        if not is_in_scope(info.url):
            return

        # Local use of URL
        m_url = info.url

        # Parse original URL
        m_url_parts = info.parsed_url

        # If file is a javascript, css or image, do not run
        if m_url_parts.extension[1:] in ('css', 'js', 'jpeg', 'jpg', 'png', 'gif', 'svg'):
            Logger.log_more_verbose("Bruteforcer - skipping URL '%s'." % m_url)
            return

        Logger.log_verbose("Bruteforcer - Start to process URL: '%s'" % m_url)

        # Result info
        m_return = []

        # Network manager reference
        m_net_manager = NetworkAPI.get_connection()

        # Method for request: GET/HEAD
        m_http_method = "HEAD" if is_method_allowed("HEAD", m_url, m_net_manager) else "GET"

        #
        # Load wordlists
        #
        m_wordlist = self.load_wordlists()

        #
        # Generate an error in server to get an error page, using a random string
        #
        # Make the URL
        m_error_url = generate_error_page_url(m_url)
        # Get the request
        m_error_response = m_net_manager.get(m_error_url).raw

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
        if not self.is_folder_url(m_url_parts) and 1==2:
            #
            #   1 - Suffixes
            m_urls_to_test["suffixes"] = self.make_url_with_suffixes(m_wordlist, m_url_parts)

            #
            #   2 - Preffixes
            m_urls_to_test["prefixes"] = self.make_url_with_suffixes(m_wordlist, m_url_parts)

            #
            #   3 - Changing extension of files
            m_urls_to_test["file_extensions"] = self.make_url_changing_extensions(m_wordlist, m_url_parts)

            #
            #   4 - Permutation of file
            m_urls_to_test["permutations"] = self.make_url_mutate_filename(m_url_parts)


        # if URL looks like don't process suffixes:
        # - www.site.com/ or
        # - www.site.com
        #
        #
        # 5 - Predictable files
        #m_urls_to_test["predictables"] = self.make_url_with_files_or_folder(m_wordlist, m_url_parts)
        m_urls_to_test["predictables"] = [m_url + "error_log"]

        # Run multithread bruteforcer
        m_store_info = MatchingAnalyzer(m_error_response)

        m_threads = list()
        for i in xrange(5):
            l_t = ParallelBruter(m_urls_to_test, m_store_info, m_net_manager, m_http_method)
            m_threads.append(l_t)
            l_t.start()

        # Wait for threads
        for i in xrange(len(m_threads)):
            m_threads[i].join()

        # Analyze resutls
        m_results = []
        m_results_append = m_results.append

        for l_match in m_store_info.unique_texts:
            Logger.log_verbose("Bruteforcer - discovered URL: %s" % l_match.url)

            #
            # Set disclosure vulnerability
            l_url = Url(l_match.url)
            l_vuln = UrlDisclosure(l_url)
            # Set impact
            l_vuln.risk = l_match.risk
            # Link resource associated
            l_vuln.associated_resource = info
            # Store
            m_results_append(l_url)
            m_results_append(l_vuln)

        # Send results
        return m_results


    #----------------------------------------------------------------------
    def load_wordlists(self):
        """
        Load all wordlists.

        :returns: dict -- A dict with wordlists
        """
        m_wordlist = {
            'suffixes' : [],
            'prefixes' : [],
            'extensions' : [],
            'predictable_files' : [],
        }

        # Load wordlist form config file
        for wordlist_name, wordlist_path in Config.plugin_config.iteritems():
            l_tmp_wordlist = None
            if wordlist_name.startswith('wordlist_suffixes'):
                l_tmp_wordlist = 'suffixes'
            elif wordlist_name.startswith('wordlist_prefixes'):
                l_tmp_wordlist = 'prefixes'
            elif wordlist_name.startswith('wordlist_extensions'):
                l_tmp_wordlist = 'extensions'
            elif wordlist_name.startswith('wordlist_predictable_files'):
                l_tmp_wordlist = 'predictable_files'

            if l_tmp_wordlist:
                m_wordlist[l_tmp_wordlist].append(WordListAPI().get_wordlist(wordlist_path))

        return m_wordlist


    #----------------------------------------------------------------------
    def make_url_with_suffixes(self, wordlist, url_parts):
        """
        Creates an iterator of URLs with suffixes.

        :param wordlist: Wordlist iterator.
        :type wordlist: WordList

        :param url_parts: Parsed URL to mutate.
        :type url_parts: DecomposedURL

        :returns: iterator with urls.
        """

        if not isinstance(url_parts, DecomposedURL):
            raise TypeError("Expected DecomposedURL, got %s instead" % type(url_parts))

        if not wordlist:
            raise ValueError("Internal error!")

        m_new = url_parts.copy()
        for l_wordlist in wordlist['suffixes']:
            # For errors
            if not l_wordlist:
                Logger.log_error("Can't load one of wordlist fo category: 'suffixes'.")
                continue

            for l_suffix in l_wordlist:
                m_new.extension = l_suffix
                yield m_new.url


    #----------------------------------------------------------------------
    def make_url_with_prefixes(self, wordlist, url_parts):
        """
        Creates an iterator of URLs with prefixes.

        :param wordlist: Wordlist iterator.
        :type wordlist: WordList

        :param url_parts: Parsed URL to mutate.
        :type url_parts: DecomposedURL

        :returns: iterator with urls.
        """

        if not isinstance(url_parts, DecomposedURL):
            raise TypeError("Expected DecomposedURL, got %s instead" % type(url_parts))

        if not wordlist:
            raise ValueError("Internal error!")

        # Making predictables
        m_new = url_parts.copy()
        m_filename = m_new.filename
        for l_wordlist in wordlist_suffix['prefixes']:
            # For errors
            if not l_wordlist:
                Logger.log_error("Can't load wordlist for category: 'prefixes'.")
                continue

            for l_prefix in l_wordlist:
                m_new.filename = l_prefix + m_filename
                yield m_new.url


    #----------------------------------------------------------------------
    def make_url_with_files_or_folder(self, wordlist, url_parts):
        """
        Creates an iterator of URLs with guessed files and subfolders.

        :param wordlist: Wordlist iterator.
        :type wordlist: WordList

        :param url_parts: Parsed URL to mutate.
        :type url_parts: DecomposedURL
        """

        if not isinstance(url_parts, DecomposedURL):
            raise TypeError("Expected DecomposedURL, got %s instead" % type(url_parts))

        if not wordlist:
            raise ValueError("Internal error!")

        m_wordlist_predictable = wordlist['predictable_files']
        if not m_wordlist_predictable:
            m_wordlist_predictable = set()
        m_wordlist_suffix = wordlist['suffixes']
        if not m_wordlist_suffix:
            m_wordlist_suffix = set()

        # Making predictables
        m_new = url_parts.copy()
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

                m_new.filename = l_fixed_path
                yield m_new.url

        # For locations source code of application, like:
        # www.site.com/folder/app1/ -> www.site.com/folder/app1.war
        #
        m_new = url_parts.copy()
        m_path = m_new.directory
        if m_path.endswith('/'):
            m_path = m_path[:-1]
        for l_wordlist in m_wordlist_suffix:
            # For errors
            if not l_wordlist:
                Logger.log_error("Can't load wordlist for category: 'suffixes'.")
                continue
            for l_suffix in l_wordlist:
                m_new.path = m_path + l_suffix
                yield m_new.url


    #----------------------------------------------------------------------
    def make_url_changing_extensions(self, wordlist, url_parts):
        """
        Creates an iterator of URLs with alternative file extensions.

        :param wordlist: Wordlist iterator.
        :type wordlist: WordList

        :param url_parts: Parsed URL to mutate.
        :type url_parts: DecomposedURL
        """

        if not isinstance(url_parts, DecomposedURL):
            raise TypeError("Expected DecomposedURL, got %s instead" % type(url_parts))

        if not wordlist:
            raise ValueError("Internal error!")

        # Making predictables
        m_new = url_parts.copy()
        for l_wordlist in wordlist['extensions']:
            # For errors
            if not l_wordlist:
                Logger.log_error("Can't load wordlist for category: 'extensions'.")
                continue
            for l_suffix in l_wordlist:
                m_new.extension = l_suffix
                yield m_new.url


    #----------------------------------------------------------------------
    def make_url_mutate_filename(self, url_parts):
        """
        Creates an iterator of URLs with mutated filenames.

        :param url_parts: Parsed URL to mutate.
        :type url_parts: DecomposedURL
        """

        if not isinstance(url_parts, DecomposedURL):
            raise TypeError("Expected DecomposedURL, got %s instead" % type(url_parts))

        # Change extension to upper case
        m_new = url_parts.copy()
        m_new.extension = m_new.extension.upper()
        yield m_new.url

        # Adding numeric ends of filename
        m_new = url_parts.copy()
        filename = m_new.filename
        for n in xrange(5):

            # Format: index1.php
            m_new.filename = filename + str(n)
            yield m_new.url

            # Format: index_1.php
            m_new.filename = "%s_%s" % (filename, str(n))
            yield m_new.url


    #----------------------------------------------------------------------
    def is_folder_url(self, url_parts):
        """
        Determine if the given URL points to a folder or a file:

        if URL looks like:
        - www.site.com/
        - www.site.com

        then ==> Return True

        if URL looks like:
        - www.site.com/index.php
        - www.site.com/index.php?id=1&name=bb
        - www.site.com/index.php/id=1&name=bb

        then ==> Return False

        :param url_parts: Parsed URL to test.
        :type url_parts: DecomposedURL

        :return: bool -- True if it's a folder, False otherwise.
        """
        return url_parts.path.endswith('/') and not url_parts.query_char == '/'
