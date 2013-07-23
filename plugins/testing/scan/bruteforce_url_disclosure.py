#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: http://golismero-project.com
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

from golismero.api.config import Config
from golismero.api.data import discard_data
from golismero.api.data.resource import Resource
from golismero.api.data.information.webserver_fingerprint import WebServerFingerprint
from golismero.api.data.resource.url import Url
from golismero.api.data.resource.folderurl import FolderUrl
from golismero.api.data.vulnerability.information_disclosure.url_disclosure import UrlDisclosure
from golismero.api.logger import Logger
from golismero.api.net import NetworkException
from golismero.api.net.http import HTTP
from golismero.api.net.web_utils import DecomposedURL
from golismero.api.text.matching_analyzer import MatchingAnalyzer, HTTP_response_headers_analyzer
from golismero.api.text.wordlist_api import WordListAPI
from golismero.api.text.text_utils import generate_random_string

from golismero.api.plugin import TestingPlugin
from collections import defaultdict

import threading


__doc__ = """

.. note:
   Acknowledgments:

   We'd like to thank @capi_x for his idea on how
   to detect fake 200 responses from servers by
   issuing known good and bad queries and diffing
   them to calculate the deviation.

   https://twitter.com/capi_x
"""


#-------------------------------------------------------------------------

# Impact vectors. Available values: 0 - 4.
severity_vectors = {
    "suffixes" : 4,
    "prefixes" : 3,
    "file_extensions": 3,
    "permutations" : 3,
    "predictables": 4,
    "directories": 2
}


#-------------------------------------------------------------------------
class ParallelBruter(threading.Thread):
    """
    Worker threads for the bruteforcer plugin.
    """

    #----------------------------------------------------------------------
    def __init__(self, urls, results, method):
        self.__urls       = urls
        self.__results    = results
        self.__method     = method
        super(ParallelBruter,self).__init__()


    #----------------------------------------------------------------------
    def run(self):

        # Test all URLs (deleting duplicates)
        while True:
            m_name = None
            m_iter = None

            try:
                m_name, m_iter = self.__urls.popitem()
            except KeyError,e:
                break

            for l_url in m_iter:
                Logger.log_more_verbose("Bruteforcer - testing url: '%s'." % l_url)

                # Ge URL
                p = None
                try:
                    p = HTTP.get_url(l_url, use_cache=False, method=self.__method)
                    if p:
                        discard_data(p)
                except NetworkException,e:
                    Logger.log_more_verbose("Bruteforcer - value error while processing: '%s'. Error: %s" % (l_url, e.message))

                # Check if the url is acceptable by comparing
                # the result content.
                #
                # If the maching level between the error page
                # and this url is greater than 52%, then it's
                # the same URL and must be discarded.
                #
                if p and p.status == "200":

                    # If the method used to get URL was HEAD, get complete URL
                    if self.__method != "GET":
                        p = HTTP.get_url(l_url, use_cache=False, method="GET")
                        if p:
                            discard_data(p)

                    # Append for analyze and display info if is accepted
                    if self.__results.append(p.raw_response,url=l_url,risk = severity_vectors[m_name]):
                        Logger.log_more_verbose("Bruteforcer - Discovered partial url: '%s'!!" % l_url)


#----------------------------------------------------------------------
class UrlDisclosureBruteforcer(TestingPlugin):


    #----------------------------------------------------------------------
    def get_accepted_info(self):
        return [Url, FolderUrl]


    #----------------------------------------------------------------------
    def recv_info(self, info):

        # XXX DEBUG
        Logger.log_verbose("Bruteforcer - Start to process URL: '%s'" % str(info))

        if info.resource_type == Resource.RESOURCE_URL:
            return process_url(info)
        if info.resource_type == Resource.RESOURCE_FOLDER_URL:
            return process_folder_url(info)
        raise TypeError()


#----------------------------------------------------------------------
#
# Processors of input types
#
#----------------------------------------------------------------------
def process_folder_url(info):
    """
    Receive and process a Base URL.
    """
    #
    # Get the remote web server fingerprint
    #
    m_webserver_finger = info.get_associated_informations_by_category(WebServerFingerprint.information_type)

    # There is fingerprinting information?
    if m_webserver_finger:

        m_webserver_finger = m_webserver_finger.pop()

        m_server_canonical_name = m_webserver_finger.name_canonical
        m_servers_related       = m_webserver_finger.related # Set with related web servers
        #
        # Load wordlists
        #
        m_wordlist         = set()
        m_wordlist_update  = m_wordlist.update

        # Wordlist of server name
        try:
            w = Config.plugin_extra_config["%s_predictables" % m_server_canonical_name]
            m_wordlist_update([l_w for l_w in w.itervalues()])
        except KeyError:
            pass

        # Wordlist of related with the server found
        try:
            for l_servers_related in m_servers_related:
                w = Config.plugin_extra_config["%s_predictables" % m_server_canonical_name]
                m_wordlist_update([l_w for l_w in w.itervalues()])
        except KeyError:
            pass

        # Load content of wordlists
        m_return         = set()
        m_return_update  = m_return.update
        m_url            = info.url if info.url.endswith("/") else "%s/" % info.url

        for l_w in m_wordlist:
            # Use a copy of wordlist to avoid modify the original source
            l_loaded_wordlist = WordListAPI.get_advanced_wordlist_as_list(l_w)

            #
            # README!!!!!
            #
            # Here don't use urljoin because it doesn't works with complete URL. With urljoin:
            #
            # http://www.mysite.com/folder1/ + /folder/to/append/index.php
            # ---> http://www.mysite.com/folder/to/append/index.php
            # instead of
            # ---> http://www.mysite.com/folder1/folder/to/append/index.php
            #
            m_return_update(( "%s%s" % (m_url, l_wo[1:] if l_wo.startswith("/") else l_wo) for l_wo in l_loaded_wordlist))


        return analyze_urls(info, {'predictables' : m_return})

    else:
        return None


#----------------------------------------------------------------------
def process_url(info):
    """
    Receive and process an URL.
    """

    # Parse original URL
    m_url_parts = info.parsed_url

    # If file is a javascript, css or image, do not run
    if info.parsed_url.extension[1:] in ('css', 'js', 'jpeg', 'jpg', 'png', 'gif', 'svg') or not m_url_parts.extension:
        Logger.log_more_verbose("Bruteforcer - skipping URL '%s'." % str(info))
        return

    #
    # Load wordlists
    #

    #
    # README!!!!!
    #
    # Here don't use urljoin because it doesn't works with complete URL. With urljoin:
    #
    # http://www.mysite.com/folder1/ + /folder/to/append/index.php
    # ---> http://www.mysite.com/folder/to/append/index.php
    # instead of
    # ---> http://www.mysite.com/folder1/folder/to/append/index.php
    #
    m_urls_to_test = defaultdict(set)

    #
    # Start with bruteforcing. Cases to try:
    #
    # 1 - Testing suffixes: index.php -> index_0.php
    #
    # COMMON
    m_urls_to_test["suffixes"].update(make_url_with_suffixes(get_list_from_wordlist("common_suffixes"), m_url_parts))

    # 2 - Testing prefixes
    #
    # COMMON
    m_urls_to_test["prefixes"].update(make_url_with_prefixes(get_list_from_wordlist("common_prefixes"), m_url_parts))

    # 3 - Testing changing extension of files
    #
    # COMMON
    m_urls_to_test["file_extensions"].update(make_url_changing_extensions(get_list_from_wordlist("common_extensions"), m_url_parts))

    # 4 - Testing filename permutations
    #
    # COMMON
    m_urls_to_test["permutations"].update(make_url_mutate_filename(m_url_parts))

    # 5 - Testing urls with more than 2 number at the end of URL, like: www.misite.com/app302/ -> test:
    #     + www.misite.com/app300/
    #     + www.misite.com/app301/
    #     ...
    #     + www.misite.com/appNNN/
    m_urls_to_test["directories"].update(make_url_changing_folder_name(m_url_parts))

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

    :param urls_to_test: Dict with the type of URLs (predictables, backup...) and the values of URLs to test.
    :type urls_to_test: dict(TYPE_OF_URL, set(URLs)) -> {'predictables': set("url1", "url2") }

    :return: discovered resources and vulns
    :rtype: UrlDisclosure
    """

    # Local use of URL
    m_url         = info.url

    if m_url not in Config.audit_scope:
        return

    # Determine the HTTP Method
    m_http_method = get_http_method(m_url)

    #
    # Generate an error in server to get an error page, using a random string
    #
    # Make the URL
    m_error_url      = m_url + generate_random_string()

    # Get the request
    m_error_response = HTTP.get_url(m_error_url)
    discard_data(m_error_response)
    m_error_response = m_error_response.data

    # Run multithread bruteforcer
    m_store_info = MatchingAnalyzer(m_error_response, matching_level=0.65)

    # Does the resquests with the URLs
    m_threads = list()
    for i in xrange(5):
        l_t = ParallelBruter(urls_to_test, m_store_info, m_http_method)
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
        m_return[k] = [WordListAPI.get_wordlist(w) for w in w_paths]

    return m_return


#----------------------------------------------------------------------
def get_http_method(url):
    """
    This function determinates if the method HEAD is available. To do that, compare between two responses:
    - One with GET method
    - One with HEAD method

    If both are seem more than 90%, the response are the same and HEAD method are not allowed.
    """

    m_head_response = HTTP.get_url(url, method="HEAD")
    discard_data(m_head_response)

    m_get_response  = HTTP.get_url(url)
    discard_data(m_get_response)

    # Check if HEAD reponse is different that GET response, to ensure that results are valids
    return "HEAD" if HTTP_response_headers_analyzer(m_head_response.headers, m_get_response.headers) < 0.90 else "GET"


#----------------------------------------------------------------------
#
# Mutation functions
#
#----------------------------------------------------------------------
def make_url_with_prefixes(wordlist, url_parts):
    """
    Creates a set of URLs with prefixes.

    :param wordlist: Wordlist iterator.
    :type wordlist: WordList

    :param url_parts: Parsed URL to mutate.
    :type url_parts: DecomposedURL

    :returns: a set with urls.
    :rtype: set
    """

    if not isinstance(url_parts, DecomposedURL):
        raise TypeError("Expected DecomposedURL, got %s instead" % type(url_parts))

    if not wordlist:
        raise ValueError("Internal error!")

    m_new        = url_parts.copy() # Works with a copy
    m_return     = set()
    m_return_add = m_return.add
    m_filename   = m_new.filename
    for l_suffix in wordlist:

        # Format: _.index.php
        m_new.filename = "%s_%s" % (l_suffix, m_filename)
        m_return_add(m_new.url)

        # Format: .index_1.php
        m_new.filename = "%s%s" % (l_suffix, m_filename)
        m_return_add(m_new.url)

    return m_return


#----------------------------------------------------------------------
def make_url_with_suffixes(wordlist, url_parts):
    """
    Creates a set of URLs with suffixes.

    :param wordlist: Wordlist iterator.
    :type wordlist: WordList

    :param url_parts: Parsed URL to mutate.
    :type url_parts: DecomposedURL

    :returns: a set with urls.
    :rtype: set
    """

    if not isinstance(url_parts, DecomposedURL):
        raise TypeError("Expected DecomposedURL, got %s instead" % type(url_parts))

    if not wordlist:
        raise ValueError("Internal error!")

    m_new        = url_parts.copy() # Works with a copy
    m_return     = set()
    m_return_add = m_return.add
    m_filename   = m_new.filename
    for l_suffix in wordlist:

        # Format: index1.php
        m_new.filename = m_filename + str(l_suffix)
        m_return_add(m_new.url)

        # Format: index_1.php
        m_new.filename = "%s_%s" % (m_filename, l_suffix)
        m_return_add(m_new.url)

    return m_return


#----------------------------------------------------------------------
def make_url_mutate_filename(url_parts):
    """
    Creates a set of URLs with mutated filenames.

    :param url_parts: Parsed URL to mutate.
    :type url_parts: DecomposedURL

    :return: a set with URLs
    :rtype: set
    """

    if not isinstance(url_parts, DecomposedURL):
        raise TypeError("Expected DecomposedURL, got %s instead" % type(url_parts))

    # Change extension to upper case
    m_new                = url_parts.copy()
    m_new.all_extensions = m_new.all_extensions.upper()
    m_return             = set()
    m_return_add         = m_return.add

    m_return_add(m_new.url)

    # Adding numeric ends of filename
    m_new = url_parts.copy()
    filename = m_new.filename
    for n in xrange(5):

        # Format: index1.php
        m_new.filename = filename + str(n)
        m_return_add(m_new.url)

        # Format: index_1.php
        m_new.filename = "%s_%s" % (filename, str(n))
        m_return_add(m_new.url)

    return m_return


#----------------------------------------------------------------------
def make_url_changing_folder_name(url_parts):
    """
    Creates a set of URLs with prefixes.

    :param url_parts: Parsed URL to mutate.
    :type url_parts: DecomposedURL

    :returns: a set with urls.
    :rtype: set
    """

    if not isinstance(url_parts, DecomposedURL):
        raise TypeError("Expected DecomposedURL, got %s instead" % type(url_parts))


    # Making predictables
    m_new        = url_parts.copy()
    m_return     = set()
    m_return_add = m_return.add
    m_directory  = m_new.directory

    if len(m_directory.split("/")) > 1:
        for n in xrange(20):
            m_new.directory = "%s%s" % (m_directory, str(n))
            m_return_add(m_new.url)

        return m_return
    else:
        return set()


#----------------------------------------------------------------------
def make_url_with_files_or_folder(wordlist, url_parts):
    """
    Creates a set of URLs with guessed files and subfolders.

    :param wordlist: Wordlist iterator.
    :type wordlist: WordList

    :param url_parts: Parsed URL to mutate.
    :type url_parts: DecomposedURL

    :return: a set with URLs
    :rtype: set
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
    m_new        = url_parts.copy()
    m_return     = set()
    m_return_add = m_return.add
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
            m_return_add(m_new.url)

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
            m_return_add(m_new.url)

    return m_return


#----------------------------------------------------------------------
def make_url_changing_extensions(wordlist, url_parts):
    """
    Creates a set of URLs with alternative file extensions.

    :param wordlist: Wordlist iterator.
    :type wordlist: WordList

    :param url_parts: Parsed URL to mutate.
    :type url_parts: DecomposedURL

    :return: a set with the URLs
    :rtype: set
    """

    if not isinstance(url_parts, DecomposedURL):
        raise TypeError("Expected DecomposedURL, got %s instead" % type(url_parts))

    if not wordlist:
        raise ValueError("Internal error!")

    # Making predictables
    m_new        = url_parts.copy()
    m_return     = set()
    m_return_add = m_return.add
    for l_suffix in wordlist:
        m_new.all_extensions = l_suffix
        m_return_add(m_new.url)

    return m_return


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

    :return: True if it's a folder, False otherwise.
    :rtype: bool
    """
    return url_parts.path.endswith('/') and not url_parts.query_char == '/'


#----------------------------------------------------------------------
def get_list_from_wordlist(wordlist):
    """
    Load the content of the wordlist and return a set with the content.

    :param wordlist: wordlist name.
    :type wordlist: str

    :return: a set with the results.
    :rtype result_output: set
    """

    try:
        m_commom_wordlists = set()

        for v in Config.plugin_extra_config[wordlist].itervalues():
            m_commom_wordlists.update(WordListAPI.get_advanced_wordlist_as_list(v))

        return m_commom_wordlists
    except KeyError,e:
        Logger.log_error_more_verbose(e.message)
        return set()
