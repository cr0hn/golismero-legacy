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

__all__ = ["IResultDB", "ResultMemoryDB"]

from core.api.results.result import Result


#------------------------------------------------------------------------------
class BaseResultDB (object):
    """
    Storage of Result objects.
    """


    #----------------------------------------------------------------------
    def __init__(self, audit):
        """
        Constructor.

        :param audit: Audit.
        :type audit: Audit
        """
        self.__audit_name   = audit.name
        self.__audit_params = audit.params


    @property
    def audit_name(self):
        return self.__audit_name

    @property
    def audit_params(self):
        return self.__audit_params


    #----------------------------------------------------------------------
    def add(self, result):
        """
        Add result to the database.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def __len__(self):
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def __contains__(self, result):
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def __iter__(self):
        raise NotImplementedError("Subclasses MUST implement this method!")


#------------------------------------------------------------------------------
class ResultMemoryDB (BaseResultDB):
    """
    Stores Result objects in memory.
    """


    #----------------------------------------------------------------------
    def __init__(self, audit):
        super(ResultMemoryDB, self).__init__(audit)
        self.__results = dict()


    #----------------------------------------------------------------------
    def add(self, result):
        if not isinstance(result, Result):
            raise TypeError("Expected Result, got %d instead" % type(result))
        hash_sum = result.hash_sum
        if hash_sum not in self.__results:
            self.__results[hash_sum] = result


    #----------------------------------------------------------------------
    def __len__(self):
        return len(self.__results)


    #----------------------------------------------------------------------
    def __contains__(self, result):
        if not isinstance(result, Result):
            raise TypeError("Expected Result, got %d instead" % type(result))
        return result.hash_sum in self.__results


    #----------------------------------------------------------------------
    def __iter__(self):
        return self.__results.itervalues()
