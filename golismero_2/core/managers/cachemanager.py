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


__all__ = ["NetProtocolCacheManager"]

from ..main.commonstructures import Singleton
from ..api.config import *

#------------------------------------------------------------------------------
class LocalCacheManager(Singleton):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.__cache = {}

    #----------------------------------------------------------------------
    def get_cache(self, key):
        """
        Get info from cache

        :param key: str with key stored in cache.
        :type key: str

        :returns: object cached | None
        """

        # Get audit name
        m_audit = Config.audit_name

        try:
            # if cached
            return self.__cache[m_audit][key]
        except KeyError:
            # Not cached
            return None


    #----------------------------------------------------------------------
    def is_cached(self, key):
        """
        Indicates if URL is cached

        :param key: str with key stored in cache.
        :type key: str

        :returns: bool -- True if URL has cached. False otherwise.
        """

        return Config.audit_name in self.__cache and key in self.__cache[Config.audit_name]


    #----------------------------------------------------------------------
    def set_cache(self, key, data, ):
        """
        Include and URL, and their data, into cache.

        :param URL: String with URL
        :type URL: str

        :param key: str with key stored in cache.
        :type key: str

        :param data: data with information
        :type data: object
        """
        # None or empty?
        if key and data:

            m_audit = Config.audit_name

            # Set cache for audit, if necessary
            if m_audit not in self.__cache:
                self.__cache[m_audit] = {}


            self.__cache[m_audit][key] = data


#------------------------------------------------------------------------------
class NetProtocolCacheManager(Singleton):
    """"""


    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.__cache = {}


    #----------------------------------------------------------------------
    def get_cache(self, key, protocol="http"):
        """
        Get info from cache

        :param key: str with key stored in cache.
        :type key: str

        :returns: object cached | None
        """

        # Get audit name
        m_audit = Config.audit_name

        # Generate the key
        m_key = "%s%s" %(protocol, key)

        try:
            # if cached
            return self.__cache[m_audit][m_key]
        except KeyError:
            # Not cached
            return None


    #----------------------------------------------------------------------
    def is_cached(self, key, protocol="http"):
        """
        Indicates if URL is cached

        :param key: str with key stored in cache.
        :type key: str

        :returns: bool -- True if URL has cached. False otherwise.
        """
        # Generate the key
        m_key = "%s%s" %(protocol, key)

        return Config.audit_name in self.__cache and m_key in self.__cache[Config.audit_name]


    #----------------------------------------------------------------------
    def set_cache(self, key, data, protocol="http", timespan=0, lifetime=-1):
        """
        Include and URL, and their data, into cache.

        :param URL: String with URL
        :type URL: str

        :param key: str with key stored in cache.
        :type key: str

        :param data: data with information
        :type data: object

        :param timespan: time span for this key in cache.
        :type timespan: int

        :param lifetime: time to life in cache.
        :type lifetime: int
        """
        # None or empty?
        if key and data and protocol:

            m_audit = Config.audit_name

            # Set cache for audit, if necessary
            if m_audit not in self.__cache:
                self.__cache[m_audit] = {}

            # Generate the key
            m_key = "%s|%s" %(protocol, key)

            # Add
            self.__cache[m_audit][m_key] = data
