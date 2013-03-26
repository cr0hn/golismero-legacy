#!/usr/bin/python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------
# 404 or not found pages analyzer
#-----------------------------------------------------------------------

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


#----------------------------------------------------------------------
def get_matching_level(text1, text2):
    """
    Compare two text and return a value between 0-100 with the level of
    difference. 0 is lowest and 100 the highest.

    - If text1 is more similar to text2, value will be near to 100.
    - If text1 is more different to text2, value will be near to 0.

    :param text1: First text to compare.
    :type text1: str

    :param text2: Text to comarpe text1.
    :type text2: str

    :returns: float - An integer between 0-1
    """
    if not text1 and not text2:
        return 100 # If two text are empty => are equals

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
        l_differ = diff_match_patch()
        # Levenshtein comparation value
        l_google_value = float(l_differ.diff_levenshtein(l_differ.diff_main(text1, text2)))
        l_len_text2 = len(text2)
        # Calculate
        m_return_value = abs( (l_len_text2 - l_google_value) / l_len_text2 )

    return m_return_value





#------------------------------------------------------------------------------
class MatchingAnalyzerElement:
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""





#------------------------------------------------------------------------------
class MatchingAnalyzer:
    """"""

    #----------------------------------------------------------------------
    def __init__(self, base_text):
        """Constructor"""
        self.__base_text = base_text
        self.__text_lists = {}


    #----------------------------------------------------------------------
    @property
    def base_text(self):
        """Base text for compare rest of strings"""
        return self.__base_text



    #----------------------------------------------------------------------
    def append(self, key, text, **kargs):
        """"""
        if text:
            #l_matching_level = get_matching_level(self.__base_text, text)

            #if l_matching_level < 0.52:
                # Append to partial results
            #    self.__results.append(key, severity_vectors[m_name], l_matching_level)
            pass


    #----------------------------------------------------------------------
    @property
    def unique_texts(self):
        """"""






#    Logger.log_more_verbose("Bruteforcer - Discovered partial url: '%s'!!" % l_url)

    # Send_ response, HTML and URL to kernel.
    #self.send_info(Url(l_url))
    #self.send_info(p)
    #if not p.information:
    #    self.send_info(p.information)


#    if m_store_info.average_level > 0:
#        m_average = m_store_info.average_level
#
#        m_results_append = m_results.append
#
#        #for i, l_level in enumerate(m_discovered_level):
#        for l_info in m_store_info:
#            l_value = l_info.level # Original value
#            l_value_deviation = l_value * 1.15 # 15% of deviation
#
#            # value < average < value * 5% => skip
#            if not (l_value < m_average and m_average < l_value_deviation):
#
#                Logger.log_verbose("Bruteforcer - discovered URL: %s !!!" % m_discovered_url[i][0])
#
#                #
#                # Send vulnerability
#                #
#                l_vuln = UrlDisclosure(l_info.url)