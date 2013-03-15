#!/usr/bin/env python
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

__all__ = ["CacheDB"]

from .common import BaseDB, transactional

from ..api.net.cache import NetworkCache
from ..main.commonstructures import get_user_settings_folder

import sqlite3


#------------------------------------------------------------------------------
class NetworkCacheDB(NetworkCache, BaseDB):
    """
    Cache for network resources, separated by protocol.
    """


    #----------------------------------------------------------------------
    def __init__(self):
        # audit -> protocol -> key -> data
        self.__cache = defaultdict( partial(defaultdict, dict) )


    #----------------------------------------------------------------------
    def get(self, key, protocol="http"):
        """
        Get a network resource from the cache.

        :param key: key to reference the network resource
        :type key: str

        :param protocol: network protocol
        :type protocol: str

        :returns: object -- resource from the cache | None
        """
        return self.__cache[Config.audit_name][protocol].get(key, None)


    #----------------------------------------------------------------------
    def set(self, key, data, protocol="http", timestamp=None, lifespan=None):
        """
        Include and URL, and their data, into cache.

        :param key: key to reference the network resource
        :type key: str

        :param data: data to store in the cache
        :type data: object

        :param protocol: network protocol
        :type protocol: str

        :param timestamp: timestamp for this network resource
        :type timestamp: int

        :param lifespan: time to live in the cache
        :type lifespan: int
        """
        self.__cache[Config.audit_name][protocol][key] = data


    #----------------------------------------------------------------------
    def exists(self, key, protocol="http"):
        """
        Verify if the given key exists in the cache.

        :param key: key to reference the network resource
        :type key: str

        :returns: True if the resource is in the cache, False otherwise.
        """
        return key in self.__cache[Config.audit_name][protocol]
