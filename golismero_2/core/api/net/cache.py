#!/usr/bin/python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------
# Network cache API
#-----------------------------------------------------------------------

"""
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

__all__ = ["NetworkCache"]

from ..config import Config
from ...common import Singleton
from ...messaging.message import Message

from collections import defaultdict
from functools import partial


#------------------------------------------------------------------------------
class AbstractCache(Singleton):
    """
    Abstract class for caches.
    """


##    #----------------------------------------------------------------------
##    # Python operators mapped to the cache operations.
##    def __getitem__(self, key):
##        return self.get(key)
##    def __setitem__(self, key, data):
##        return self.set(key, data)
##    def __contains__(self, key):
##        return self.exists(key)


    #----------------------------------------------------------------------
    def get(self, key):
        """
        Get data from the cache.

        :param key: key to reference the data
        :type key: str

        :returns: object -- data from the cache | None
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def set(self, key, data):
        """
        Add data to the cache.

        :param key: key to reference the data
        :type key: str

        :param data: data to store in the cache
        :type data: object
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def exists(self, key):
        """
        Verify if the given key exists in the cache.

        :param key: key to reference the data
        :type key: str

        :returns: True if the data is in the cache, False otherwise.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


#------------------------------------------------------------------------------
class NetworkCache(AbstractCache):
    """
    Cache for network resources, separated by protocol.
    """


    #----------------------------------------------------------------------
    def __init__(self):
        self._clear_local_cache()


    #----------------------------------------------------------------------
    def _clear_local_cache(self):

        # This method is called from the plugin bootstrap.

        # During the lifetime of the plugin,
        # results from the centralized cache
        # are also stored in memory here.
        #
        # audit -> protocol -> key -> data
        #
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

        # First, try to get the resource from the local cache.
        data = self.__cache[Config.audit_name][protocol].get(key, None)
        if data is None:

            # If not found locally, query the global cache.
            data = Config._get_context().remote_call(
                                Message.MSG_RPC_CACHE_GET, key, protocol)

            # Store the global cache result locally.
            if data is not None:
                self.__cache[Config.audit_name][protocol][key] = data

        # Return the cached data.
        return data


    #----------------------------------------------------------------------
    def set(self, key, data, protocol="http", timestamp=None, lifespan=None):
        """
        Store a network resource in the cache.

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

        # Store the resource in the local cache.
        self.__cache[Config.audit_name][protocol][key] = data

        # Send the resource to the global cache.
        Config._get_context().async_remote_call(
                            Message.MSG_RPC_CACHE_SET, key, protocol, data)


    #----------------------------------------------------------------------
    def remove(self, audit, key, protocol="http"):
        """
        Remove a network resource from the cache.

        :param key: key to reference the network resource
        :type key: str

        :param protocol: network protocol
        :type protocol: str
        """

        # Remove the resource from the local cache.
        try:
            del self.__cache[Config.audit_name][protocol][key]
        except KeyError:
            pass

        # Remove the resource from the global cache.
        Config._get_context().async_remote_call(
                            Message.MSG_RPC_CACHE_REMOVE, key, protocol)


    #----------------------------------------------------------------------
    def exists(self, key, protocol="http"):
        """
        Verify if the given key exists in the cache.

        :param key: key to reference the network resource
        :type key: str

        :returns: True if the resource is in the cache, False otherwise.
        """

        # First, check if it's in the local cache.
        found = key in self.__cache[Config.audit_name][protocol]

        # If not found, check the global cache.
        if not found:
            found = Config._get_context().remote_call(
                                Message.MSG_RPC_CACHE_CHECK, key, protocol)
            found = bool(found)

        # Return the status.
        return found
