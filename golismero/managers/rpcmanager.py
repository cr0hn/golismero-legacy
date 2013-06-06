#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Manager of RPC calls from plugins.
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

__all__ = ["RPCManager"]

from ..common import pickle
from ..messaging.codes import MessageCode, MSG_RPC_CODES

from functools import partial

import sys
import warnings
import traceback


#------------------------------------------------------------------------------
# Decorator to automatically register RPC implementors at import time.

# Global map of RPC codes to implementors.
rpcMap = {}

def implementor(rpc_code):
    """
    RPC implementation function.
    """
    return partial(_add_implementor, rpc_code)

def _add_implementor(rpc_code, fn):
    """
    RPC implementation function.
    """
    rpcMap[rpc_code] = fn
    # TODO: use introspection to validate the function signature
    return fn  # no function wrapping is needed :)


#------------------------------------------------------------------------------
# Implementor for the special MSG_RPC_BULK code for bulk RPC calls.

@implementor(MessageCode.MSG_RPC_BULK)
def rpc_bulk(orchestrator, audit_name, rpc_code, *arguments):

    # Get the implementor for the RPC code.
    # Raise NotImplementedError if it's not defined.
    try:
        method = rpcMap[rpc_code]
    except KeyError:
        raise NotImplementedError("RPC code not implemented: %r" % rpc_code)

    # Prepare a partial function call to the implementor.
    caller = partial(method, orchestrator, audit_name)

    # Use the built-in map() function to issue all the calls.
    # This ensures we support the exact same interface and functionality.
    return map(caller, *arguments)


#------------------------------------------------------------------------------
class RPCManager (object):
    """
    Executes remote procedure calls from plugins.
    """


    #----------------------------------------------------------------------
    def __init__(self, orchestrator):
        """
        Constructor.

        :param orchestrator: Orchestrator
        :type orchestrator: Orchestrator
        """

        # Keep a reference to the orchestrator.
        self.__orchestrator = orchestrator

        # Keep a reference to the global RPC map (it's faster this way).
        self.__rpcMap = rpcMap

        # Check all RPC messages have been mapped at this point.
        missing = MSG_RPC_CODES.difference(self.__rpcMap.keys())
        if missing:
            msg  = "Missing RPC implementors for codes: %s"
            msg %= ", ".join(str(x) for x in sorted(missing))
            warnings.warn(msg, RuntimeWarning)


    #----------------------------------------------------------------------
    def execute_rpc(self, audit_name, rpc_code, response_queue, argv, argd):
        """
        Honor a remote procedure call request from a plugin.

        :param audit_name: Name of the audit requesting the call.
        :type audit_name: str

        :param rpc_code: RPC code.
        :type rpc_code: int

        :param response_queue: Response queue.
        :type response_queue: Queue

        :param argv: Positional arguments to the call.
        :type argv: tuple

        :param argd: Keyword arguments to the call.
        :type argd: dict
        """
        success = True
        try:

            # Get the implementor for the RPC code.
            # Raise NotImplementedError if it's not defined.
            try:
                method = self.__rpcMap[rpc_code]
            except KeyError:
                raise NotImplementedError("RPC code not implemented: %r" % rpc_code)

            # Call the implementor and get the response.
            response = method(self.__orchestrator, audit_name, *argv, **argd)

        # Catch exceptions and prepare them for sending.
        except Exception:
            success  = False
            response = self.__prepare_exception(*sys.exc_info())

        # If the call was synchronous, send the response/error back to the plugin.
        if response_queue:
            response_queue.put_nowait( (success, response) )


    #----------------------------------------------------------------------
    @staticmethod
    def __prepare_exception(exc_type, exc_value, exc_traceback):
        """
        Prepare an exception for sending back to the plugins.

        :param exc_type: Exception type.
        :type exc_type: class

        :param exc_value: Exception value.
        :type exc_value:

        :returns: tuple(class, object, str) -- Exception type, exception value
            and formatted traceback. The exception value may be formatted too
            and the exception type replaced by Exception if it's not possible
            to serialize them for sending.
        """
        exc_type, exc_value, exc_traceback = sys.exc_info()
        try:
            pickle.dumps(exc_value, -1)
        except Exception:
            exc_value = traceback.format_exception_only(exc_type, exc_value)
        try:
            pickle.dumps(exc_type, -1)
        except Exception:
            exc_type = Exception
        exc_traceback = traceback.extract_tb(exc_traceback)
        return exc_type, exc_value, exc_traceback
