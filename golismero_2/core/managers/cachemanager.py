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


__all__ = ["CacheManager"]

from core.main.commonstructures import Singleton
from core.api.config import *

#------------------------------------------------------------------------------
class CacheManager(Singleton):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.__cache = {}

    #----------------------------------------------------------------------
    def get_cache(self, data):
        """
        Get URL from cache

        :returns: object cached | None
        """

        # Get audit name
        #m_audit = Config().audit_name
        m_audit = "aa"

        # Set cache for audit, if necessary
        if m_audit not in self.__cache.keys():
            self.__cache[m_audit] = {}

        try:
            # if cached
            return self.__cache[m_audit][data.request_id]
        except KeyError:
            # Not cached
            return None


    #----------------------------------------------------------------------
    def is_cached(self, data):
        """
        Indicates if URL is cached

        :returns: bool -- True if URL has cached. False otherwise.
        """

        #return data.request_id in self.__cache[Config().audit_name].keys()
        return data.request_id in self.__cache["aa"].keys()

    #----------------------------------------------------------------------
    def set_cache(self, data):
        """
        Include and URL, and their data, into cache.

        :param URL: String with URL
        :type URL: str

        :param data: data with information
        :type data: object
        """
        # None or empty?
        if data and data.request_id:
            #self.__cache[Config().audit_name][data.request_id] = data
            self.__cache["aa"][data.request_id] = data





