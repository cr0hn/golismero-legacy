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


__all__ = ["BaseDB", "transactional"]


import zlib
import urlparse
import functools


try:
    import cPickle as pickle
except ImportError:
    import pickle


try:
    from decorator import decorator
except ImportError:
    import functools
    def decorator(w):
        """
        The decorator module was not found. You can install it from:
        http://pypi.python.org/pypi/decorator/
        """
        def d(fn):
            @functools.wraps(fn)
            def x(*argv, **argd):
                return w(fn, *argv, **argd)
            return x
        return d


#------------------------------------------------------------------------------
@decorator
def transactional(fn):
    """
    Transactional method.
    """
    def wrapper(self, *argv, *argd):
        return self._transaction(fn, argv, argd)
    return wrapper


#------------------------------------------------------------------------------
class BaseDB (object):
    """
    Base class with common functionality for all database classes.
    """


    #----------------------------------------------------------------------
    def _transaction(self, fn, argv, argd):
        """
        Execute a transactional operation.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def encode(self, data):
        """
        Encode data for storage.
        """
        data = pickle.dumps(data, protocol = pickle.HIGHEST_PROTOCOL)
        data = zlib.compress(data, 9)
        return data


    #----------------------------------------------------------------------
    def decode(self, data):
        """
        Decode data from storage.
        """
        data = zlib.decompress(data)
        data = pickle.loads(data)
        return data


    #----------------------------------------------------------------------
    def close(self):
        """
        Clear all resources associated with this database.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")
