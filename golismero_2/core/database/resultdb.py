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

__all__ = ["ResultDB"]

from core.api.results.result import Result

import zlib
import urlparse

try:
    import cPickle as pickle
except ImportError:
    import pickle


# Lazy imports
anydbm = None


#------------------------------------------------------------------------------
class BaseResultDB (object):
    """
    Storage of Result objects.
    """


    #----------------------------------------------------------------------
    def __init__(self, audit_name):
        """
        Constructor.

        :param audit_name: Audit name.
        :type audit_name: str
        """
        self.__audit_name   = audit_name


    @property
    def audit_name(self):
        return self.__audit_name


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


    #----------------------------------------------------------------------
    def close(self):
        """
        Clear all resources associated with this database.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


#------------------------------------------------------------------------------
class ResultMemoryDB (BaseResultDB):
    """
    Stores Result objects in memory.
    """


    #----------------------------------------------------------------------
    def __init__(self, audit_name):
        super(ResultMemoryDB, self).__init__(audit_name)
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


    #----------------------------------------------------------------------
    def close(self):
        self.__results = dict()


#------------------------------------------------------------------------------
class ResultFileDB (BaseResultDB):
    """
    Stores Result objects in a DBM database file.
    """


    #----------------------------------------------------------------------
    def __init__(self, audit_name, filename = None):
        """
        Constructor.

        :param audit_name: Audit name.
        :type audit_name: str

        :param filename: Optional DBM database file name.
        :type filename: str
        """
        super(ResultFileDB, self).__init__(audit_name)
        global anydbm
        if anydbm is None:
            import anydbm
        if not filename:
            filename = audit_name + ".dbm"
        self.__db = anydbm.open(filename, "c", 0600)


    #----------------------------------------------------------------------
    def close(self):
        try:
            self.__db.close()
        except Exception:
            pass


    #----------------------------------------------------------------------
    def add(self, result):
        if not isinstance(result, Result):
            raise TypeError("Expected Result, got %d instead" % type(result))
        hash_sum = result.hash_sum
        if hash_sum not in self.__db:
            data = pickle.dumps(result, protocol = pickle.HIGHEST_PROTOCOL)
            data = zlib.compress(data, 9)
            self.__db[hash_sum] = data


    #----------------------------------------------------------------------
    def __len__(self):
        return len(self.__db)


    #----------------------------------------------------------------------
    def __contains__(self, result):
        if not isinstance(result, Result):
            raise TypeError("Expected Result, got %d instead" % type(result))
        return self.__db.has_key(result.hash_sum)


    #----------------------------------------------------------------------
    def __iter__(self):
        return self.__db.itervalues()


#------------------------------------------------------------------------------
class ResultSQLDB (BaseResultDB):
    """
    Stores Result objects in a SQL database.
    """


    #----------------------------------------------------------------------
    def __init__(self, audit_name, audit_db):
        """
        :param audit_name: Audit name.
        :type audit_name: str

        :param audit_db: Database connection string in URL format.
        :type audit_db: str
        """
        super(ResultSQLDB, self).__init__(audit_name)
        #
        # TODO add SQLAlchemy support
        #
        raise NotImplementedError("SQL databases not supported yet")


#------------------------------------------------------------------------------
class ResultDB (BaseResultDB):
    """
    Stores Result objects in a database.

    The database type is chosen automatically based on the connection string.
    """

    def __new__(cls, audit_name, audit_db):
        """
        :param audit_name: Audit name.
        :type audit_name: str

        :param audit_db: Database connection string in URL format.
        :type audit_db: str
        """
        parsed = urlparse.urlparse(audit_db)
        scheme = parsed.scheme.lower()

        if scheme == "memory":
            return ResultMemoryDB(audit_name)

        if scheme == "dbm":

            from os import path
            import posixpath

            filename = posixpath.join(parsed.netloc, parsed.path)
            if path.sep != posixpath.sep:
                filename.replace(posixpath.sep, path.sep)
            if filename.endswith(posixpath.sep):
                filename = filename[:-1]

            return ResultFileDB(audit_name, filename)

        ##if any(map(scheme.startswith, ("sqlite", "mysql", "mssql", "plsql", "oracle"))):
        ##    return ResultSQLDB(audit_name, audit_db)

        raise ValueError("Unsupported database type: %s" % scheme)
