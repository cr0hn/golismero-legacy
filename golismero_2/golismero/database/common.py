#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

__all__ = ["BaseDB", "atomic", "transactional"]

from ..common import pickle, decorator

import zlib
import functools


#------------------------------------------------------------------------------
@decorator
def transactional(fn, self, *argv, **argd):
    """
    Transactional method.
    """
    return self._transaction(fn, argv, argd)


#------------------------------------------------------------------------------
@decorator
def atomic(fn, self, *argv, **argd):
    """
    Atomic method.
    """
    return self._atom(fn, argv, argd)


#------------------------------------------------------------------------------
class BaseDB (object):
    """
    Base class with common functionality for all database classes.
    """

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()


    #----------------------------------------------------------------------
    def _atom(self, fn, argv, argd):
        """
        Execute an atomic operation.

        Called automatically when using the @atomic decorator.

        :param fn: Method in this class marked as @atomic.
        :type fn: unbound method

        :param argv: Positional arguments.
        :type argv: tuple

        :param argd: Keyword arguments.
        :type argd: dict

        :returns: The return value after calling the 'fn' method.
        :raises: NotImplementedError -- Transactions not supported
        """
        raise NotImplementedError("Atomic operations not supported")


    #----------------------------------------------------------------------
    def _transaction(self, fn, argv, argd):
        """
        Execute a transactional operation.

        Called automatically when using the @transactional decorator.

        :param fn: Method in this class marked as @transactional.
        :type fn: unbound method

        :param argv: Positional arguments.
        :type argv: tuple

        :param argd: Keyword arguments.
        :type argd: dict

        :returns: The return value after calling the 'fn' method.
        :raises: NotImplementedError -- Transactions not supported
        """
        raise NotImplementedError("Transactions not supported")


    #----------------------------------------------------------------------
    def encode(self, data):
        """
        Encode data for storage.

        :param data: Data to encode.

        :returns: str -- Encoded data.
        """
        data = pickle.dumps(data, protocol = pickle.HIGHEST_PROTOCOL)
        data = zlib.compress(data, 9)
        return data


    #----------------------------------------------------------------------
    def decode(self, data):
        """
        Decode data from storage.

        :param data: Data to decode.
        :type data: str

        :returns: Decoded data.
        """
        data = zlib.decompress(data)
        data = pickle.loads(data)
        return data


    #----------------------------------------------------------------------
    def compact(self):
        """
        Free unused disk space.

        This method does nothing when the underlying
        database doesn't support this operation.
        """
        return


    #----------------------------------------------------------------------
    def dump(self, filename):
        """
        Dump the database contents to a file.

        :param filename: Output filename.
        :type filename: str

        :raises: NotImplementedError -- Operation not supported
        """
        raise NotImplementedError("Operation not supported")


    #----------------------------------------------------------------------
    def close(self):
        """
        Free all resources associated with this database.

        This instance may no longer be used after calling this method.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")
