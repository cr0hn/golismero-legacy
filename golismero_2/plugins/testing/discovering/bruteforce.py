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

# Acknowledgments:
#
#   We'd like to thank @capi_x for his idea on how
#   to detect fake 200 responses from servers by
#   issuing known good and bad queries and diffing
#   them to calculate the deviation.
#
#   https://twitter.com/capi_x

from golismero.api.logger import Logger
from golismero.api.net.protocol import NetworkAPI
from golismero.api.net.web_utils import convert_to_absolute_url, is_in_scope
from golismero.api.plugin import TestingPlugin
from golismero.api.data.resource.url import Url
from golismero.api.data.vulnerability.information_disclosure.url_disclosure import UrlDisclosure
from golismero.api.text.wordlist_api import WordListAPI
from golismero.api.net.web_utils import parse_url
from golismero.api.text.text_utils import get_matching_level, generate_random_string
from golismero.api.config import Config


from os.path import splitext, split, sep
from os import getpid
import threading


# Impact vectors. Available values: 0 - 3.
severity_vectors = {
    "suffixes" : 4,
    "prefixes" : 3,
    "file_extensions": 3,
    "permutations" : 3,
    "predictables": 4
}


#------------------------------------------------------------------------------
class DiscoveredInfo(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.__data = dict()
        self.__level_average = 0.0

        self.__curr_url = None
        self.__curr_risk = None
        self.__curr_level = None

        self.__index_iter = -1


    #----------------------------------------------------------------------
    @property
    def num_urls(self):
        """
        Number of URLs contained

        :rtype: int
        """
        return len(self.__data)

    #----------------------------------------------------------------------
    @property
    def average_level(self):
        """Return average of levels

        :rtype: float
        """
        if self.__level_average > 0:
            return self.num_urls / self.__level_average
        else:
            return self.num_urls


    #----------------------------------------------------------------------
    def append(self, URL, risk, level):
        """Add a new element

        :param URL: URL of element
        :type URL: str

        :type risk: int
        :type level: int
        """
        if URL and risk and level:
            self.__data[URL] = (
                risk,
                level
            )

            self.__level_average += level


    #----------------------------------------------------------------------
    @property
    def url(self):
        """URL of current element"""
        return self.__curr_url


    #----------------------------------------------------------------------
    @property
    def risk(self):
        """Risk of current element"""
        return self.__curr_risk

    #----------------------------------------------------------------------
    @property
    def level(self):
        """Level of current element"""
        return self.__curr_level



    #----------------------------------------------------------------------
    def __iter__(self):
        """"""
        return self

    #----------------------------------------------------------------------
    def next(self):
        """"""
        self.__index_iter += 1
        if self.__index_iter < len(self.__data):
            url, val = self.__data.popitem()
            self.__curr_url = url
            self.__curr_risk = val[0]
            self.__curr_level = val[1]
        else:
            raise StopIteration









#------------------------------------------------------------------------------
class ParallelBruter(threading.Thread):
    """

    """

    #----------------------------------------------------------------------
    def __init__(self, wordlist, results_queue, net, method, base_error):
        """Constructor"""
        self.__wordlist = wordlist
        self.__results = results_queue
        self.__net = net
        self.__method = method
        self.__lock = threading.Lock()
        self.__base_error = base_error
        super(ParallelBruter,self).__init__()

    #----------------------------------------------------------------------
    def run(self):
        """"""
        # Test all URLs (deleting duplicates)
        #for l_name, l_iter in self.__wordlist.iteritems():
        while True:
            m_name = None
            m_iter = None

            try:
                m_name, m_iter = self.__wordlist.popitem()
            except KeyError,e:
                return

            for l_url in m_iter:
                Logger.log_more_verbose("Bruteforcer - testing url: '%s'." % l_url)

                # Ge URL
                p = None
                try:
                    p = self.__net.get(l_url, cache=False, method=self.__method)
                except ValueError,e:
                    Logger.log_more_verbose("Bruteforcer - value error while processing: '%s'. Error: %s" % (l_url, e.message))
                except RuntimeError:
                    Logger.log_more_verbose("Bruteforcer - error getting url: '%s'." % l_url)

                # Check if the url is acceptable by comparing
                # the result content.
                #
                # If the maching level between the error page
                # and this url is greater than 52%, then it's
                # the same URL and must be discarded.
                #
                if p and p.http_response_code == 200:

                    if self.__method != "GET":
                        p = self.__net.get(l_url, cache=False, method="GET")

                    l_matching_level = get_matching_level(self.__base_error, p.raw)

                    if l_matching_level < 0.52:
                        # Append to partial results
                        self.__results.append(l_url, severity_vectors[m_name], l_matching_level)

                        Logger.log_more_verbose("Bruteforcer - Discovered partial url: '%s'!!" % l_url)

                        # Send_ response, HTML and URL to kernel.
                        #self.send_info(Url(l_url))
                        #self.send_info(p)
                        #if not p.information:
                        #    self.send_info(p.information)




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
        return [Url.RESOURCE_URL]


    #----------------------------------------------------------------------
    def recv_info(self, info):

        if not isinstance(info, Url):
            raise TypeError("Expected Url, got %s instead" % type(info))

        # Check if URL is in scope
        if not is_in_scope(info.url):
            return
        return

        # Parse original URL
        m_parsed_url = None
        try:
            m_parsed_url = parse_url(info.url)
        except ValueError:
            return

        # Split URL
        m_url_parts = self.split_url(m_parsed_url)

        # If file is a javascript, css or imagen, not run
        if m_url_parts['path_filename_ext'][1:] in ('css', 'js', 'jpeg', 'jpg', 'png', 'gif', 'svg'):
            Logger.log_more_verbose("Bruteforcer - skipping URL '%s'." % info.url)
            return

        Logger.log_verbose("Bruteforcer - processing URL: '%s'" % info.url)



        # Result info
        m_return = []

        # Network manager reference
        m_net_manager = NetworkAPI.get_connection()

        # Method for request: GET/HEAD
        m_http_method = self.get_http_method(info.url, m_net_manager)

        #
        # Load wordlists
        #
        m_wordlist = self.load_wordlist()
        #print m_wordlist
        #return

        #
        # Generate an error in server to get an error page, using a random string
        #
        # Make the URL
        m_error_url = "%s://%s%s%s.%s%s" % (
            m_url_parts['scheme'],
            m_url_parts['host'],
            m_url_parts['complete_path'],
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
        # 2 - Testing prefixes
        # 3 - Testing changing extension of files
        # 4 - Testing filename permutations
        # 5 - Testing predictable files and dirs: hidden files, config, lost files...
        #
        m_urls_to_test = {}


        # if URL looks like don't process suffixes:
        # - www.site.com/index.php
        #
        if not self.is_url_folder_point(m_url_parts) and 1==2:
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
        #
        # 5 - Predictable files
        m_urls_to_test["predictables"] = self.make_url_with_files_or_folder(m_wordlist, m_url_parts)

        # List for check discovered data
        m_discovered_url = []
        m_discovered_bind_url = m_discovered_url.append
        m_discovered_level = []
        m_discovered_bind_level = m_discovered_level.append

        # Run multithread bruteforcer
        #m_queue = Queue.Queue()
        m_store_info = DiscoveredInfo()
        m_threads = list()
        for i in xrange(5):
            l_t = ParallelBruter(m_urls_to_test, m_store_info, m_net_manager, m_http_method, m_error_response)
            m_threads.append(l_t)
            l_t.start()


        for i in xrange(len(m_threads)):
            m_threads[i].join()

        #
        # Calculate the level of correpondence for all elements. We calculate the
        # deviation of 5%. All elements in of these deviation are part of same page of
        # error, and then skip it.
        #
        # Calculate average
        m_results = []

        if m_store_info.average_level > 0:
            #m_length = 1.1 if len(m_discovered_level) == 0 else len(m_discovered_level)
            m_average = m_store_info.average_level

            m_results_append = m_results.append

            #for i, l_level in enumerate(m_discovered_level):
            for l_info in m_store_info:
                l_value = l_info.level # Original value
                l_value_deviation = l_value * 1.15 # 15% of deviation

                # value < average < value * 5% => skip
                if not (l_value < m_average and m_average < l_value_deviation):

                    Logger.log_verbose("Bruteforcer - discovered URL: %s !!!" % m_discovered_url[i][0])

                    #
                    # Send vulnerability
                    #
                    l_vuln = UrlDisclosure(l_info.url)
                    # Calculate impact
                    l_vuln.risk = l_info.risk
                    # Link resource associated
                    l_vuln.associated_resource = info
                    # Store
                    m_results_append(l_vuln)
                    #
                    # Send URL
                    #
                    self.send_info(Url(m_discovered_url[i][0]))

        # Report
        return m_results


    #----------------------------------------------------------------------
    def get_http_method(self, url, network_conn):
        """
        Get appropiate HTTP method: GET/HEAD.

        if HEAD is supported return instead of GET.

        :param url: URL to test methods.
        :type url: str.

        :param network_conn: network connection.
        :type network_conn: Protocol (Web).

        :returns: str -- HTTP method: GET/HEAD.
        """
        if not url or not network_conn:
            return "GET"

        p = network_conn.get(url, method="HEAD")

        if p.http_response_code == 200: # and 'Content-Length' in p.http_headers:
            return "HEAD"
        else:
            return "GET"





    #----------------------------------------------------------------------
    def load_wordlist(self):
        """
        Load all wordlist

        :returns: dict -- A dict with wordlists
        """
        m_wordlist = {
            'suffixes' : [],
            'prefixes' : [],
            'extensions' : [],
            'predictable_files' : []
        }

        # Load wordlist form config file
        for wordlist_name, wordlist_path in Config.plugin_info.plugin_config.iteritems():
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
                    url_parts['complete_path_without_filename'],
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
                    url_parts['complete_path_without_filename'],
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
                    url_parts['complete_path_without_filename'],
                    l_fixed_path,
                )

        # For locations source code of application, like:
        # www.site.com/folder/app1/ -> www.site.com/folder/app1.war
        #
        m_path = url_parts['complete_path']
        m_prev_folder = m_path[:m_path[:-1].rfind("/") + 1] # www.site.com/folder/
        m_last_folder = m_path[m_path[:-1].rfind("/") + 1: -1] # app1
        for l_wordlist in m_wordlist_suffix:
            # For errors
            if not l_wordlist:
                Logger.log_error("Can't load wordlist for category: 'suffixes'.")
                continue
            for l_suffix in l_wordlist:
                yield "%s://%s%s/%s%s." % (
                    url_parts['scheme'],
                    url_parts['host'],
                    m_prev_folder,
                    m_last_folder,
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
                    url_parts['complete_path_without_filename'],
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
                    url_parts['complete_path_without_filename']
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

        http://www.antpji.com/index.php/noticias/frontpage/6category_id=0

        then ==> Return False

        :param url_parts: Parsed URL to test.
        :type url_parts: dict

        :return: bool -- True if it's a folder, False if not.

        """
        return not (
            (url_parts['complete_path'] or url_parts['query']) and \
            (url_parts['path_filename_ext'] or url_parts['query'])
        )
    #----------------------------------------------------------------------
    def split_url(self, parsed_url):
        """Split URL in their parts"""

        m_parsed_url = parsed_url

        m_url_parts = {}
        m_url_parts['scheme']                     = m_parsed_url.scheme if m_parsed_url.scheme else ''
        m_url_parts['host']                       = m_parsed_url.host if m_parsed_url.host else ''
        m_url_parts['complete_path']              = m_parsed_url.path if m_parsed_url.path else ''
        # Fix path =
        m_url_parts['complete_path']              = m_url_parts['complete_path'] if m_url_parts['complete_path'].endswith("/") else m_url_parts['complete_path'] + "/"
        m_url_parts['path_filename_ext']          = splitext(m_parsed_url.path)[1] if m_parsed_url.path else ''
        m_url_parts['path_filename']              = split(m_parsed_url.path)[1] if m_parsed_url.path and m_url_parts['path_filename_ext'] else ''
        m_url_parts['path_filename_without_ext']  = splitext(m_url_parts['path_filename'])[0] if m_parsed_url.path and m_url_parts['path_filename'] else ''
        m_url_parts['query']                      = m_parsed_url.query if m_parsed_url.query else ''

        # Fix path for values like:
        # http://www.site.com/folder/value_id=0
        m_path = m_url_parts['complete_path']
        m_prev_folder = m_path[:m_path[:-1].rfind("/") + 1] # www.site.com/folder/
        m_last = m_path[m_path[:-1].rfind("/") + 1: -1] # value_id=0
        if m_last.find("=") != -1:
            m_url_parts['complete_path'] = m_prev_folder

        m_url_parts['complete_path_without_filename'] = '/' if not m_prev_folder else m_prev_folder



        return m_url_parts







class BackupSearcher_old(object):
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
        return [Url.RESOURCE_URL]


    #----------------------------------------------------------------------
    def recv_info(self, info):

        if not isinstance(info, Url):
            raise TypeError("Expected Url, got %s instead" % type(info))

        # Check if URL is in scope
        if not is_in_scope(info.url):
            return

        return

        # Parse original URL
        m_parsed_url = None
        try:
            m_parsed_url = parse_url(info.url)
        except ValueError:
            return

        # Split URL
        m_url_parts = self.split_url(m_parsed_url)

        # If file is a javascript, css or imagen, not run
        if m_url_parts['path_filename_ext'][1:] in ('css', 'js', 'jpeg', 'jpg', 'png', 'gif', 'svg'):
            Logger.log_more_verbose("Bruteforcer - skipping URL '%s'." % info.url)
            return

        Logger.log_verbose("Bruteforcer - processing URL: '%s'" % info.url)



        # Result info
        m_return = []

        # Network manager reference
        m_net_manager = NetworkAPI.get_connection()

        # Method for request: GET/HEAD
        m_http_method = self.get_http_method(info.url, m_net_manager)

        #
        # Load wordlists
        #
        m_wordlist = self.load_wordlist()

        #
        # Generate an error in server to get an error page, using a random string
        #
        # Make the URL
        m_error_url = "%s://%s%s%s.%s%s" % (
            m_url_parts['scheme'],
            m_url_parts['host'],
            m_url_parts['complete_path'],
            m_url_parts['path_filename'],
            generate_random_string(),
            m_url_parts['query']
        )
        # Get the request
        m_error_response = m_net_manager.get(m_error_url).raw


        # Impact vectors. Available values: 0 - 3.
        m_severity_vectors = {
            "suffixes" : 4,
            "prefixes" : 3,
            "file_extensions": 3,
            "permutations" : 3,
            "predictables": 4
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
        #
        # 5 - Predictable files
        m_urls_to_test["predictables"] = self.make_url_with_files_or_folder(m_wordlist, m_url_parts)

        # List for check discovered data
        m_discovered_url = []
        m_discovered_bind_url = m_discovered_url.append
        m_discovered_level = []
        m_discovered_bind_level = m_discovered_level.append

        # Test all URLs (deleting duplicates)
        for l_name, l_iter in m_urls_to_test.iteritems():
            for l_url in l_iter:

                Logger.log_more_verbose("Bruteforcer - testing url: '%s'." % l_url)

                # Ge URL
                try:
                    p = m_net_manager.get(l_url, cache=False, method=m_http_method)
                except ValueError,e:
                    Logger.log_more_verbose("Bruteforcer - value error while processing: '%s'. Error: %s" % (l_url, e.message))
                except RequestException:
                    Logger.log_more_verbose("Bruteforcer - timeout for url: '%s'." % l_url)
                except RuntimeError:
                    Logger.log_more_verbose("Bruteforcer - error getting url: '%s'." % l_url)

                # Check if the url is acceptable by comparing
                # the result content.
                #
                # If the maching level between the error page
                # and this url is greater than 52%, then it's
                # the same URL and must be discarded.
                #
                if p and p.http_response_code == 200:

                    if m_http_method != "GET":
                        p = m_net_manager.get(l_url, cache=False, method="GET")

                    l_matching_level = get_matching_level(m_error_response, p.raw)

                    if l_matching_level < 0.52:
                        # Append to partial results
                        m_discovered_bind_url((l_url, m_severity_vectors[l_name])) # Url + level of criticality
                        m_discovered_bind_level(l_matching_level)

                        Logger.log_more_verbose("Bruteforcer - Discovered partial url: '%s'!!" % l_url)

                        # Send_ response, HTML and URL to kernel.
                        #self.send_info(Url(l_url))
                        #self.send_info(p)
                        #if not p.information:
                        #    self.send_info(p.information)

        #
        # Calculate the level of correpondence for all elements. We calculate the
        # deviation of 5%. All elements in of these deviation are part of same page of
        # error, and then skip it.
        #
        if m_discovered_level:
            #m_length = 1.1 if len(m_discovered_level) == 0 else len(m_discovered_level)
            m_average = sum(m_discovered_level) / len(m_discovered_level)

            for i, l_level in enumerate(m_discovered_level):
                l_value = l_level # Original value
                l_value_deviation = l_level * 1.15 # 15% of deviation

                # value < average < value * 5% => skip
                if not (l_value < m_average and m_average < l_value_deviation):

                    Logger.log_verbose("Bruteforcer - discovered URL: %s" % m_discovered_url[i][0])

                    #
                    # Send vulnerability
                    #
                    l_vuln = UrlDisclosure(m_discovered_url[i][0])
                    # Calculate impact
                    l_vuln.risk = m_discovered_url[i][1]
                    # Send vulnerability
                    self.send_info(l_vuln)

                    #
                    # Send URL
                    #
                    self.send_info(Url(m_discovered_url[i][0]))


    #----------------------------------------------------------------------
    def get_http_method(self, url, network_conn):
        """
        Get appropiate HTTP method: GET/HEAD.

        if HEAD is supported return instead of GET.

        :param url: URL to test methods.
        :type url: str.

        :param network_conn: network connection.
        :type network_conn: Protocol (Web).

        :returns: str -- HTTP method: GET/HEAD.
        """
        if not url or not network_conn:
            return "GET"

        p = network_conn.get(url, method="HEAD")

        if p.http_response_code == 200: # and 'Content-Length' in p.http_headers:
            return "HEAD"
        else:
            return "GET"




    #----------------------------------------------------------------------
    def load_wordlist(self):
        """
        Load all wordlist

        :returns: dict -- A dict with wordlists
        """
        m_wordlist = {}

        # 1 - Suffixes
        m_wordlist['suffixes'] = []
        m_wordlist['suffixes'].append(WordListAPI().get_wordlist("fuzzdb_discovery_filenamebruteforce_extensions.backup.fuzz"))
        m_wordlist['suffixes'].append(WordListAPI().get_wordlist("golismero_predictables_file-compressed-suffixes"))

        # 2 - Prefixes
        m_wordlist['prefixes'] = []
        m_wordlist['prefixes'].append(WordListAPI().get_wordlist("golismero_predictables_file-prefix"))
        m_wordlist['prefixes'].append(WordListAPI().get_wordlist("fuzzdb_discovery_filenamebruteforce_copy_of.fuzz"))

        # 3 - File extensions
        m_wordlist['extensions'] = []
        m_wordlist['extensions'].append(WordListAPI().get_wordlist("golismero_predictables_java-file-extensions"))
        m_wordlist['extensions'].append(WordListAPI().get_wordlist("golismero_predictables_microsoft-file-extensions"))
        m_wordlist['extensions'].append(WordListAPI().get_wordlist("golismero_predictables_file-compressed-suffixes"))
        m_wordlist['extensions'].append(WordListAPI().get_wordlist("golismero_predictables_microsoft-file-extensions"))

        # 5 - Predictable filename and folders
        m_wordlist['predictable_files'] = []
        m_wordlist['predictable_files'].append(WordListAPI().get_wordlist("fuzzdb_discovery_predictableres_cgi_microsoft.fuzz"))
        m_wordlist['predictable_files'].append(WordListAPI().get_wordlist("fuzzdb_discovery_predictableres_apache.fuzz"))
        m_wordlist['predictable_files'].append(WordListAPI().get_wordlist("fuzzdb_discovery_predictableres_iis.fuzz"))
        m_wordlist['predictable_files'].append(WordListAPI().get_wordlist("fuzzdb_discovery_predictableres_php.fuzz"))
        #m_wordlist['predictable_files'].append(WordListAPI().get_wordlist("fuzzdb_discovery_predictableres_passwords.fuzz"))
        m_wordlist['predictable_files'].append(WordListAPI().get_wordlist("fuzzdb_discovery_predictableres_oracle9i.fuzz"))
        m_wordlist['predictable_files'].append(WordListAPI().get_wordlist("fuzzdb_discovery_predictableres_unixdotfiles.fuzz"))

        return m_wordlist


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
                    url_parts['complete_path_without_filename'],
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
                    url_parts['complete_path_without_filename'],
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
                    url_parts['complete_path_without_filename'],
                    l_fixed_path,
                )

        # For locations source code of application, like:
        # www.site.com/folder/app1/ -> www.site.com/folder/app1.war
        #
        m_path = url_parts['complete_path']
        m_prev_folder = m_path[:m_path[:-1].rfind("/") + 1] # www.site.com/folder/
        m_last_folder = m_path[m_path[:-1].rfind("/") + 1: -1] # app1
        for l_wordlist in m_wordlist_suffix:
            # For errors
            if not l_wordlist:
                Logger.log_error("Can't load wordlist for category: 'suffixes'.")
                continue
            for l_suffix in l_wordlist:
                yield "%s://%s%s/%s%s." % (
                    url_parts['scheme'],
                    url_parts['host'],
                    m_prev_folder,
                    m_last_folder,
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
                    url_parts['complete_path_without_filename'],
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
                    url_parts['complete_path_without_filename']
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

        http://www.antpji.com/index.php/noticias/frontpage/6category_id=0

        then ==> Return False

        :param url_parts: Parsed URL to test.
        :type url_parts: dict

        :return: bool -- True if it's a folder, False if not.

        """
        return not (
            (url_parts['complete_path'] or url_parts['query']) and \
            (url_parts['path_filename_ext'] or url_parts['query'])
        )
    #----------------------------------------------------------------------
    def split_url(self, parsed_url):
        """Split URL in their parts"""

        m_parsed_url = parsed_url

        m_url_parts = {}
        m_url_parts['scheme']                     = m_parsed_url.scheme if m_parsed_url.scheme else ''
        m_url_parts['host']                       = m_parsed_url.host if m_parsed_url.host else ''
        m_url_parts['complete_path']              = m_parsed_url.path if m_parsed_url.path else ''
        # Fix path =
        m_url_parts['complete_path']              = m_url_parts['complete_path'] if m_url_parts['complete_path'].endswith("/") else m_url_parts['complete_path'] + "/"
        m_url_parts['path_filename_ext']          = splitext(m_parsed_url.path)[1] if m_parsed_url.path else ''
        m_url_parts['path_filename']              = split(m_parsed_url.path)[1] if m_parsed_url.path and m_url_parts['path_filename_ext'] else ''
        m_url_parts['path_filename_without_ext']  = splitext(m_url_parts['path_filename'])[0] if m_parsed_url.path and m_url_parts['path_filename'] else ''
        m_url_parts['query']                      = m_parsed_url.query if m_parsed_url.query else ''

        # Fix path for values like:
        # http://www.site.com/folder/value_id=0
        m_path = m_url_parts['complete_path']
        m_prev_folder = m_path[:m_path[:-1].rfind("/") + 1] # www.site.com/folder/
        m_last = m_path[m_path[:-1].rfind("/") + 1: -1] # value_id=0
        if m_last.find("=") != -1:
            m_url_parts['complete_path'] = m_prev_folder

        m_url_parts['complete_path_without_filename'] = '/' if not m_prev_folder else m_prev_folder



        return m_url_parts


