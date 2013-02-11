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

from core.main.commonstructures import Singleton
from core.api.results.result import Result

#------------------------------------------------------------------------------
class ResultManager(Singleton):
    """
    This interface manage the results. Shorten, organizing and storing it.
    """


    #----------------------------------------------------------------------
    def __vinit__(self):
        """Constructor"""

        self.__results = dict()

    #----------------------------------------------------------------------
    def add_result(self, result):
        """
        Add new result to store, if no already in store.
        """
        if isinstance(result, Result):
            if result.hash_sum not in self.__results.keys():
                self.__results[result.hash_sum] = result

    #----------------------------------------------------------------------
    def contains(self, result):
        """
        Check if a result is already stored or not.

        :param result: the result to check.
        :type result: Result

        :returns: bool -- True if is already store. False otherwise
        """
        return result.hash_sum in self.__results.keys()

    #----------------------------------------------------------------------
    def get_results(self):
        """
        Get stored results
        """
        return self.__results

    results = property(get_results)

