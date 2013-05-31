#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
404 or not found pages analyzer.
"""

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


__all__ = ["get_matching_level", "MatchingAnalyzerElement", "MatchingAnalyzer", "HTTP_response_headers_comparer"]

import hashlib
from difflib import SequenceMatcher
from diff_match_patch import diff_match_patch


#----------------------------------------------------------------------
# Text analyzer.

def get_matching_level(text1, text2):
    """
    Compare two text and return a value between 0-1 with the level of
    difference. 0 is lowest and 1 the highest.

    - If text1 is more similar to text2, value will be near to 100.
    - If text1 is more different to text2, value will be near to 0.

    :param text1: First text to compare.
    :type text1: str

    :param text2: Second text to compare.
    :type text2: str

    :returns: Floating point value between 0 and 1.
    :rtype: float
    """
    if not text1 and not text2:
        return 1 # If two text are empty => are equals

    m_difference = abs(len(text1) - len(text2))

    m_return_value = 0

    CUTOFF_VALUE = 1000 # 200 (Min words of text) * 5 (The average letters contains a word)


    # Select the algorithm to make de diff.
    # - Google method: More efficient with texts more similar.
    # - difflib: More efficient with texts very different.
    if m_difference > CUTOFF_VALUE:
        # difflib method
        m_return_value = SequenceMatcher(None, text1, text2).ratio()

    else:
        # Google method
        l_differ       = diff_match_patch()
        # Levenshtein comparation value
        #l_google_value = float(l_differ.diff_levenshtein(l_differ.diff_main(text1, text2)))
        p = l_differ.diff_main(text1, text2)
        l_google_value = float(l_differ.diff_levenshtein(p))
        l_google_value = 1 if l_google_value == 0 else l_google_value

        l_len_text2    = len(text2)
        l_len_text1    = len(text1)
        # Calculate
        m_return_value = abs( 1 - ((l_len_text1 - l_len_text2) / l_google_value ))

    return m_return_value


#------------------------------------------------------------------------------
class MatchingAnalyzerElement(object):


    #----------------------------------------------------------------------
    def __init__(self, attrs):
        self.__attrs = attrs


    #----------------------------------------------------------------------
    def __getattr__(self, name):
        return self.__attrs[name]


#------------------------------------------------------------------------------
class MatchingAnalyzer(object):
    """
    Text analyzer.

    Compares any number of texts from a base text and generates
    an iterator with those that are sufficiently different.
    """


    #----------------------------------------------------------------------
    def __init__(self, base_text, matching_level = 0.52, deviation = 1.15):

        self.__base_text = base_text
        self.__unique_strings = []
        self.__new_data = False
        self.__average_level = 0.0

        # Results
        self.__results_matching_level = {}
        self.__results_other_args = {}

        # Advanced values
        self.__matching_level = matching_level
        self.__deviation = deviation


    #----------------------------------------------------------------------
    @property
    def base_text(self):
        """
        :returns: Base text for comparison.
        :rtype: str
        """
        return self.__base_text


    #----------------------------------------------------------------------
    def append(self, text, **kargs):
        """
        If the matching level is accepted,
        store it along with all the keyword arguments.

        :param text: Text to compare.
        :type text: str

        :returns: True if the text is accepted, False otherwise.
        :rtype: bool
        """
        if text:
            l_matching_level = get_matching_level(self.__base_text, text)

            if l_matching_level < self.__matching_level:
                # Set to new data received
                self.__new_data = True

                l_key = hashlib.md5(text).hexdigest()

                # Append to partial results
                self.__results_matching_level[l_key] = l_matching_level
                self.__results_other_args[l_key] = kargs

                return True
            else:
                return False


    #----------------------------------------------------------------------
    @property
    def unique_texts(self):
        """
        :returns: Iterable with unique texts.
        :rtype: iter(str)
        """
        if self.__new_data:
            self.__calculate()

        for ut in self.__unique_strings:
            yield ut


    #----------------------------------------------------------------------
    @property
    def level_average(self):
        """
        :returns: Average matching level.
        :rtype: float
        """
        if self.__new_data:
            if self.__results_matching_level:
                self.__average_level = sum(self.__results_matching_level.itervalues()) / len(self.__results_matching_level)
            else:
                self.__average_level = 0.0

        return self.__average_level


    #----------------------------------------------------------------------
    def __calculate(self):
        """
        Calculate the elements that are really different.

        Calculate the level of correpondence for all elements. We calculate the
        deviation of 5%. All elements in of these deviation are part of same page of
        error, and then skip it.

        .. warning: Private method, do not call!
        """
        if self.level_average:
            m_average = self.level_average
            m_unique_strings_append = self.__unique_strings.append

            for l_key, l_info in self.__results_matching_level.iteritems():
                l_value = l_info # Original value
                l_value_deviation = l_value * self.__deviation # 15% of deviation

                # NOT value < average < value * 5% => skip
                if not (l_value < m_average and m_average < l_value_deviation):
                    m_unique_strings_append(MatchingAnalyzerElement(self.__results_other_args[l_key]))

            self.__new_data = False


#----------------------------------------------------------------------
# HTTP response analyzer.

def HTTP_response_headers_analyzer(response_header_1, response_header_2):
    """
    Does a HTTP comparison to determinate if two HTTP response matches with the
    same content without need the body content. To do that, remove some HTTP headers
    (like Date or Cache info).

    Return a value between 0-1 with the level of difference. 0 is lowest and 1 the highest.

    - If response_header_1 is more similar to response_header_2, value will be near to 100.
    - If response_header_1 is more different to response_header_2, value will be near to 0.

    :param response_header_1: text with http response headers.
    :type response_header_1: str

    :param response_header_2: text with http response headers.
    :type response_header_2: str
    """

    m_invalid_headers = [
        "Date",
        "Expires",
        "Last-Modified",
    ]

    m_res1 = ''.join([ "%s:%s" % (k,v) for k,v in response_header_1.iteritems() if k not in m_invalid_headers ])
    m_res2 = ''.join([ "%s:%s" % (k,v) for k,v in response_header_2.iteritems() if k not in m_invalid_headers ])

    return get_matching_level(m_res1, m_res2)
