#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

__all__ = ["NetworkManager"]

from .rpcmanager import implementor
from ..common import random
from ..messaging.codes import MessageCode

from collections import defaultdict


#----------------------------------------------------------------------
# RPC implementors for the network connection manager API.

@implementor(MessageCode.MSG_RPC_REQUEST_SLOT)
def rpc_netdb_request_slot(orchestrator, audit_name, *argv, **argd):
    return orchestrator.netManager.request_slot(audit_name, *argv, **argd)

@implementor(MessageCode.MSG_RPC_RELEASE_SLOT)
def rpc_netdb_release_slot(orchestrator, audit_name, *argv, **argd):
    return orchestrator.netManager.release_slot(audit_name, *argv, **argd)


#--------------------------------------------------------------------------
class NetworkManager (object):
    """
    Manage and control network connections.
    """


    #----------------------------------------------------------------------
    def __init__(self, config):
        """
        Constructor.

        :param config: Global configuration object
        :type config: OrchestratorConfig
        """

        # Keep a reference to the global configuration.
        self.__config = config

        # Map of hosts to global connection count.
        self.__hosts = defaultdict(int)   # host -> count

        # Map of audits to hosts connection counts.
        self.__tokens = defaultdict(dict) # audit -> token -> (host, number)


    #----------------------------------------------------------------------
    @property
    def max_connections(self):
        return self.__config.max_connections


    #----------------------------------------------------------------------
    def request_slot(self, audit_name, host, number = 1):
        """
        Request the given number of connection slots for a host.

        :param audit_name: Audit name.
        :type audit_name: str

        :param host: Host to connect to.
        :type host: str

        :param number: Number of connection slots to request.
        :type number: int

        :returns: str -- Request token | None
        """
        if number != abs(number):
            raise ValueError("Number of slots can't be negative!")
        host = host.lower()
        if self.__hosts[host] + number <= self.max_connections:
            token = "%.8X|%s" % (random.randint(0, 0x7FFFFFFF), host)
            self.__tokens[audit_name][token] = (host, number)
            self.__hosts[host] += number
            return token


    #----------------------------------------------------------------------
    def release_slot(self, audit_name, token):
        """
        Release a previously requested number of connection slots for a host.

        :param audit_name: Audit name.
        :type audit_name: str

        :param token: Request token.
        :type token: str
        """
        try:
            host, number = self.__tokens[audit_name].pop(token)
            self.__hosts[host] -= number
            if self.__hosts[host] <= 0:
                del self.__hosts[host]
        except Exception:
            pass


    #----------------------------------------------------------------------
    def release_all_slots(self, audit_name):
        """
        Release all connection slots for the given audit.

        :param audit_name: Audit name.
        :type audit_name: str
        """
        for host, number in self.__tokens.pop(audit_name, {}).itervalues():
            self.__hosts[host] -= number
            if self.__hosts[host] <= 0:
                del self.__hosts[host]
