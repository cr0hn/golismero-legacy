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

from difflib import SequenceMatcher
from thirdparty_libs.google_diff_match_patch import *
from string import ascii_letters, digits
from random import choice



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

    :returns: int - An integer between 0-100.
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
        m_return_value = SequenceMatcher(None, text1, text2).ratio() * 100.0

    else:
        # Google method
        l_differ = diff_match_patch()
        # Levenshtein comparation value
        l_google_value = float(l_differ.diff_levenshtein(l_differ.diff_main(text1, text2)))
        l_len_text2 = len(text2)
        # Calculate
        m_return_value = abs( (l_len_text2 - l_google_value) / l_len_text2 ) * 100

    return int(m_return_value)


#----------------------------------------------------------------------
def generate_random_string(string_length=30):
    """
    Generates a random string with length as parameter.

    :param string_length: length of string generated
    :type string_length: int
    """
    m_available_chars = "%s%s" % (ascii_letters, digits) #, "#!_-.;,")

    return ''.join(choice(m_available_chars) for x in xrange(string_length))