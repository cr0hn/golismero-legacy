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

# Acknowledgments:
#
#   We'd like to thank @capi_x for his idea on how
#   to detect fake 200 responses from servers by
#   issuing known good and bad queries and diffing
#   them to calculate the deviation.
#
#   https://twitter.com/capi_x

from golismero.api.config import Config
from golismero.api.data.resource import Resource
from golismero.api.data.resource.url import Url
from golismero.api.data.resource.baseurl import BaseUrl
from golismero.api.data.vulnerability.information_disclosure.url_disclosure import UrlDisclosure
from golismero.api.logger import Logger
from golismero.api.net.protocol import *
from golismero.api.net.web_utils import DecomposedURL, is_in_scope
from golismero.api.plugin import TestingPlugin
from golismero.api.text.matching_analyzer import *
from golismero.api.text.wordlist_api import WordListAPI
from golismero.api.text.text_utils import generate_random_string

import threading


# Impact vectors. Available values: 0 - 4.
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
                    if self.__results.append(p.raw_content,url=l_url,risk = severity_vectors[m_name]):
                        Logger.log_more_verbose("Bruteforcer - Discovered partial url: '%s'!!" % l_url)

                        # Send_ response, HTML and URL to kernel.
                        #m_return = [Url(l_url), p]
                        #if p.information:
                        #    m_return.append(p.information)
                        #return m_return


#----------------------------------------------------------------------
class UrlDisclosureBruteforcer(TestingPlugin):


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [Url, BaseUrl]


    #----------------------------------------------------------------------
    def recv_info(self, info):

        # XXX DEBUG
        #return

        Logger.log_verbose("Bruteforcer - Start to process URL: '%s'" % str(info))

        if info.resource_type == Resource.RESOURCE_URL:
            return process_url(info)
        if info.resource_type == Resource.RESOURCE_BASE_URL:
            return process_base_url(info)
        raise TypeError()


#----------------------------------------------------------------------
#
# Processors of input types
#
#----------------------------------------------------------------------
def process_base_url(info):
    """
    Receive and process a Base URL.
    """


    # Parse original URL
    #m_url_parts = info.parsed_url

    # If file is a javascript, css or image, do not run
    if info.parsed_url.extension[1:] in ('css', 'js', 'jpeg', 'jpg', 'png', 'gif', 'svg'):
        Logger.log_more_verbose("Bruteforcer - skipping URL '%s'." % str(info))
        return

    #
    # Load wordlists
    #
    # -   Word lists to load
    #m_wordlists_names  = [
    #    "predictables"
    #]
    # -   Wordlist instances
    #m_wordlist         = load_wordlists(m_wordlists_names)

    #
    # Start with bruteforcing. Cases to try:
    #
    # 1 - Testing predictable files and dirs: hidden files, config, lost files...
    #
    m_urls_to_test = {}

    #
    # if URL looks like don't process suffixes:
    # - www.site.com/ or
    # - www.site.com
    #
    # 5 - Predictable files
    #m_urls_to_test["predictables"] = make_url_with_files_or_folder(m_wordlist, m_url_parts)
    m_urls_to_test["predictables"] = [info.url + "error_log"]


    return analyze_urls(info, m_urls_to_test)


#----------------------------------------------------------------------
def process_url(info):
    """
    Receive and process an URL.
    """

    # Parse original URL
    m_url_parts = info.parsed_url

    # If file is a javascript, css or image, do not run
    if info.parsed_url.extension[1:] in ('css', 'js', 'jpeg', 'jpg', 'png', 'gif', 'svg'):
        Logger.log_more_verbose("Bruteforcer - skipping URL '%s'." % str(info))
        return

    #
    # Load wordlists
    #
    # -   Word lists to load
    m_wordlists_names  = [
        "suffixes",
        "prefixes",
        "commonextensions",
        "fileextensions"
    ]
    # -   Wordlist instances
    m_wordlist         = load_wordlists(m_wordlists_names)

    #
    # Start with bruteforcing. Cases to try:
    #
    # 1 - Testing suffixes
    # 2 - Testing prefixes
    # 3 - Testing changing extension of files
    # 4 - Testing filename permutations
    # 5 - Testing urls with more than 2 number at the end of URL, like: www.misite.com/app302/ -> test:
    #     + www.misite.com/app300/
    #     + www.misite.com/app301/
    #     ...
    #     + www.misite.com/appNNN/
    m_urls_to_test = {}


    #
    # if URL looks like don't process suffixes:
    # - www.site.com/index.php
    #
    if not is_folder_url(m_url_parts):
        #
        #   1 - Suffixes
        m_urls_to_test["suffixes"]        = make_url_with_suffixes(m_wordlist, m_url_parts)

        #
        #   2 - Preffixes
        m_urls_to_test["prefixes"]        = make_url_with_suffixes(m_wordlist, m_url_parts)

        #
        #   3 - Changing extension of files
        m_urls_to_test["file_extensions"] = make_url_changing_extensions(m_wordlist, m_url_parts)

        #
        #   4 - Permutation of file
        m_urls_to_test["permutations"]    = make_url_mutate_filename(m_url_parts)

    return analyze_urls(info, m_urls_to_test)



#----------------------------------------------------------------------
#
# The analyzer
#
#----------------------------------------------------------------------
def analyze_urls(info, urls_to_test):
    """
    Analyze a list of URL, tryining it its exits.

    :param info: Resource that will be associated discovered URLs
    :type info: Url or BaseUrl

    :param urls_to_test: dicts with URLs
    :type urls_to_test: dict(WORDLIST_NAME, list(URLs))

    :return: discovered resources and vulns
    :rtype: UrlDisclosure
    """

    # Local use of URL
    m_url         = info.url

    # Network manager reference
    m_net_manager = NetworkAPI.get_connection()

    # Determine the HTTP Method
    m_http_method = get_http_method(m_url, m_net_manager)

    #
    # Generate an error in server to get an error page, using a random string
    #
    # Make the URL
    m_error_url      = m_url + generate_random_string()

    # Get the request
    m_error_response = m_net_manager.get(m_error_url).raw_content

    # Run multithread bruteforcer
    m_store_info = MatchingAnalyzer(m_error_response, matching_level=0.65)

    # Does the resquests with the URLs
    m_threads = list()
    for i in xrange(5):
        l_t = ParallelBruter(urls_to_test, m_store_info, m_net_manager, m_http_method)
        m_threads.append(l_t)
        l_t.start()

    # Wait for threads
    for i in xrange(len(m_threads)):
        m_threads[i].join()

    # Analyze resutls
    m_results        = []
    m_results_append = m_results.append

    for l_match in m_store_info.unique_texts:

        Logger.log_verbose("Bruteforcer - discovered URL: %s" % l_match.url)

        #
        # Set disclosure vulnerability
        l_url                      = Url(l_match.url)
        l_vuln                     = UrlDisclosure(l_url)

        # Set impact
        l_vuln.risk                = l_match.risk

        # Link resource associated
        l_vuln.associated_resource = info

        # Store
        m_results_append(l_url)
        m_results_append(l_vuln)

    return m_results



#----------------------------------------------------------------------
#
# Aux functions
#
#----------------------------------------------------------------------
def load_wordlists(wordlists):
    """
    Load the with names pased as parameter.

    This function receives a list of names of wordlist, defined in plugin
    configuration file, and return a dict with instances of wordlists.

    :param wordlists: list with wordlists names
    :type wordlists: list

    :returns: A dict with wordlists
    :rtype: dict
    """
    #m_wordlist = {
        #'suffixes' : [],
        #'prefixes' : [],
        #'extensions' : [],
        #'predictable' : [],
    #}


    m_tmp_wordlist = {}

    # Get wordlist to load
    for l_w in wordlists:
        for wordlist_family, l_wordlists in Config.plugin_extra_config.iteritems():
            if wordlist_family.lower() in l_w.lower():
                m_tmp_wordlist[l_w] = l_wordlists

    # Load the wordlist
    m_return = {}
    for k, w_paths in m_tmp_wordlist.iteritems():
        m_return[k] = [WordListAPI().get_wordlist(w) for w in w_paths]

    return m_return

    # Load wordlist form config file
    #for wordlist_name, wordlist_path in Config.plugin_extra_config.iteritems():
        #l_tmp_wordlist = None
        #if wordlist_name.startswith('wordlist_suffixes'):
            #l_tmp_wordlist = 'suffixes'
        #elif wordlist_name.startswith('wordlist_prefixes'):
            #l_tmp_wordlist = 'prefixes'
        #elif wordlist_name.startswith('wordlist_extensions'):
            #l_tmp_wordlist = 'extensions'
        #elif wordlist_name.startswith('wordlist_predictable_files'):
            #l_tmp_wordlist = 'predictable_files'

        #if l_tmp_wordlist:
            #m_wordlist[l_tmp_wordlist].append(WordListAPI().get_wordlist(wordlist_path))

    #return m_wordlist
    return m_return



#----------------------------------------------------------------------
def get_http_method(url, net_manager):
    """
    This function determinates if the method HEAD is available. To do that, compare between two responses:
    - One with GET method
    - One with HEAD method

    If both are seem more than 90%, the response are the same and HEAD method are not allowed.
    """
    m_head_response = net_manager.get(url, method="HEAD")
    m_get_response  = net_manager.get(url)


    # Check if HEAD reponse is different that GET response, to ensure that results are valids
    return "HEAD" if HTTP_response_headers_analyzer(m_head_response.http_headers, m_get_response.http_headers) < 0.90 else "GET"


#----------------------------------------------------------------------
#
# Mutation functions
#
#----------------------------------------------------------------------
def make_url_with_suffixes(wordlist, url_parts):
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
def make_url_with_prefixes(wordlist, url_parts):
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
def make_url_with_files_or_folder(wordlist, url_parts):
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
def make_url_changing_extensions(wordlist, url_parts):
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
def make_url_mutate_filename(url_parts):
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
def is_folder_url(url_parts):
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
