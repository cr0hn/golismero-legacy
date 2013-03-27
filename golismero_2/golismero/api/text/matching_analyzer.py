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
import hashlib
from difflib import SequenceMatcher
from diff_match_patch import diff_match_patch


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
    def __init__(self, attrs):
        """Constructor"""
        self.__attrs = attrs

    #----------------------------------------------------------------------
    def __getattr__(self, name):
        """"""
        return self.__attrs[name]






#------------------------------------------------------------------------------
class MatchingAnalyzer:
    """
    Text analyzer and comparer texts.

    Compare an undetermined number of text from a base text and generates
    an iterator with those that are sufficiently different.
    """

    #----------------------------------------------------------------------
    def __init__(self, base_text, matching_level = 0.52, deviation = 1.15):
        """Constructor"""
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
        """Base text for compare rest of strings"""
        return self.__base_text



    #----------------------------------------------------------------------
    def append(self, text, **kargs):
        """
        If the matching level is accepted store it and the others params in
        **kargs.

        :param text: text to compare.
        :type text: str

        :param **kargs: undefined numbre of params.
        :type **kargs: special param.

        :return: True if text is accepted. False otherwise.
        :retype: bool
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
        Return an iterable with unique text.
        """
        if self.__new_data:
            self.__calculate()

        for ut in self.__unique_strings:
            yield ut

    #----------------------------------------------------------------------
    @property
    def level_average(self):
        """
        Average of maching level.

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
        Calculate the elements that are really different:

        Calculate the level of correpondence for all elements. We calculate the
        deviation of 5%. All elements in of these deviation are part of same page of
        error, and then skip it.
        """
        if self.level_average:
            m_average = self.level_average
            m_results_append = self.__unique_strings

            m_unique_strings_append = self.__unique_strings.append

            for l_key, l_info in self.__results_matching_level.iteritems():
                l_value = l_info # Original value
                l_value_deviation = l_value * self.__deviation # 15% of deviation

                # NOT value < average < value * 5% => skip
                if not (l_value < m_average and m_average < l_value_deviation):
                    m_unique_strings_append(MatchingAnalyzerElement(self.__results_other_args[l_key]))

            self.__new_data = False