#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

__all__ = ["DataDB"]

from .common import BaseDB, transactional

from ..api.data.data import Data
from ..api.data.information.information import Information
from ..api.data.resource.resource import Resource
from ..api.data.vulnerability.vulnerability import Vulnerability

import urlparse
import warnings

# Lazy imports
anydbm = None
sqlite3 = None


#------------------------------------------------------------------------------
class BaseDataDB (BaseDB):
    """
    Storage of Data objects.
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
    def add(self, data):
        """
        Add data to the database.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def __len__(self):
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def __contains__(self, data):
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def __iter__(self):
        raise NotImplementedError("Subclasses MUST implement this method!")


#------------------------------------------------------------------------------
class DataMemoryDB (BaseDataDB):
    """
    Stores Data objects in memory.
    """


    #----------------------------------------------------------------------
    def __init__(self, audit_name):
        super(DataMemoryDB, self).__init__(audit_name)
        self.__results = dict()


    #----------------------------------------------------------------------
    def add(self, data):
        if not isinstance(data, Data):
            raise TypeError("Expected Data, got %d instead" % type(data))
        hash_sum = data.hash_sum
        if hash_sum not in self.__results:
            self.__results[hash_sum] = data


    #----------------------------------------------------------------------
    def __len__(self):
        return len(self.__results)


    #----------------------------------------------------------------------
    def __contains__(self, data):
        if not isinstance(data, Data):
            raise TypeError("Expected Data, got %d instead" % type(data))
        return data.hash_sum in self.__results


    #----------------------------------------------------------------------
    def __iter__(self):
        return self.__results.itervalues()


    #----------------------------------------------------------------------
    def close(self):
        self.__results = dict()


#------------------------------------------------------------------------------
class DataFileDB (BaseDataDB):
    """
    Stores Data objects in a DBM database file.
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
        super(DataFileDB, self).__init__(audit_name)
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
    def add(self, data):
        if not isinstance(data, Data):
            raise TypeError("Expected Data, got %d instead" % type(data))
        hash_sum = data.hash_sum
        if hash_sum not in self.__db:
            self.__db[hash_sum] = self.encode(data)


    #----------------------------------------------------------------------
    def __len__(self):
        return len(self.__db)


    #----------------------------------------------------------------------
    def __contains__(self, data):
        if not isinstance(data, Data):
            raise TypeError("Expected Data, got %d instead" % type(data))
        return self.__db.has_key(data.hash_sum)


    #----------------------------------------------------------------------
    def __iter__(self):
        for data in self.__db.itervalues():
            yield self.decode(data)


#------------------------------------------------------------------------------
class DataSQLiteDB (BaseDataDB):
    """
    Stores Data objects in an SQLite database file.
    """


    #----------------------------------------------------------------------
    def __init__(self, audit_name, filename = None):
        """
        Constructor.

        :param audit_name: Audit name.
        :type audit_name: str

        :param filename: Optional SQLite database file name.
        :type filename: str
        """
        super(DataSQLiteDB, self).__init__(audit_name)
        global sqlite3
        if sqlite3 is None:
            import sqlite3
        if not filename:
            filename = audit_name + ".db"
        self.__db = sqlite3.connect(filename)
        self.__cursor = None
        self.__busy = False
        self.__create()


    #----------------------------------------------------------------------
    def close(self):
        try:
            self.__db.close()
        except Exception:
            pass
        self.__busy = True


    #----------------------------------------------------------------------
    def _transaction(self, fn, argv, argd):
        """
        Execute a transactional operation.
        """
        # this will fail for multithread accesses,
        # but sqlite is not multithreaded either
        if self.__busy:
            raise RuntimeError("The database is busy")
        self.__busy = True
        try:
            self.__cursor = self.__db.cursor()
            try:
                retval = fn(self, *argv, **argd)
                self.__db.commit()
                return retval
            except:
                self.__db.rollback()
                raise
        finally:
            self.__cursor = None
            self.__busy = False


    #----------------------------------------------------------------------
    @transactional
    def __create(self):
        """
        Create the database schema if needed.
        """
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS information (
                id INTEGER PRIMARY KEY,
                hash_sum STRING UNIQUE NOT NULL,
                information_type INTEGER NOT NULL,
                data BLOB NOT NULL
            );
        """)
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS resource (
                id INTEGER PRIMARY KEY,
                hash_sum STRING UNIQUE NOT NULL,
                resource_type INTEGER NOT NULL,
                data BLOB NOT NULL
            );
        """)
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS vulnerability (
                id INTEGER PRIMARY KEY,
                hash_sum STRING UNIQUE NOT NULL,
                vulnerability_type STRING NOT NULL,
                data BLOB NOT NULL
            );
        """)


    #----------------------------------------------------------------------
    def __get_data_table_and_type(self, data):
        data_type = data.data_type
        if   data_type == Data.TYPE_INFORMATION:
            table = "information"
            dtype = data.information_type
        elif data_type == Data.TYPE_RESOURCE:
            table = "resource"
            dtype = data.resource_type
        elif data_type == Data.TYPE_VULNERABILITY:
            table = "vulnerability"
            dtype = data.vulnerability_type
        elif data_type == Data.TYPE_ANY:
            warnings.warn(
                "Received %s object of type TYPE_ANY" % type(data),
                RuntimeWarning)
            if   isinstance(data, Information):
                data.data_type = Data.TYPE_INFORMATION
                table = "information"
                dtype = data.information_type
            elif isinstance(data, Resource):
                data.data_type = Data.TYPE_RESOURCE
                table = "resource"
                dtype = data.resource_type
            elif isinstance(data, Vulnerability):
                data.data_type = Data.TYPE_VULNERABILITY
                table = "vulnerability"
                dtype = data.vulnerability_type
            else:
                raise NotImplementedError(
                    "Unknown data type %r!" % type(data))
        else:
            raise NotImplementedError(
                "Unknown data type %r!" % data_type)
        return table, dtype


    #----------------------------------------------------------------------
    @transactional
    def add(self, data):
        if not isinstance(data, Data):
            raise TypeError("Expected Data, got %d instead" % type(data))
        table, type = self.__get_data_table_and_type(data)
        query  = "INSERT OR REPLACE INTO %s VALUES (NULL, ?, ?, ?);" % table
        values = (data.hash_sum, type, sqlite3.Binary(self.encode(data)))
        self.__cursor.execute(query, values)


    #----------------------------------------------------------------------
    @transactional
    def __len__(self):
        count = 0
        for table in ("information", "resource", "vulnerability"):
            self.__cursor.execute("SELECT COUNT(id) FROM %s;" % table)
            count += int(self.__cursor.fetchone()[0])
        return count


    #----------------------------------------------------------------------
    @transactional
    def __contains__(self, data):
        if not isinstance(data, Data):
            raise TypeError("Expected Data, got %d instead" % type(data))
        table, type = self.__get_data_table_and_type(data)
        query = "SELECT COUNT(id) FROM %s WHERE hash_sum = ? LIMIT 1;"
        self.__cursor.execute(query % table, (data.hash_sum,))
        return bool(self.__cursor.fetchone()[0])


    #----------------------------------------------------------------------
    def __iter__(self):
        # can't use @transactional here!
        try:
            self.__busy = True
            cursor = self.__db.cursor()
            for table in ("information", "resource", "vulnerability"):
                cursor.execute("SELECT data FROM %s;" % table)
                while True:
                    row = cursor.fetchone()
                    if row is None:
                        break
                    yield self.decode(str(row[0]))
        finally:
            self.__busy = False


    #----------------------------------------------------------------------
    def dump(self, filename):
        """
        Dump the database in SQL format.
        """
        # no need for @transactional here, we don't use a cursor
        try:
            self.__busy = True
            with open(filename, 'w') as f:
                apply(f.write, (line + "\n" for line in self.__db.iterdump()))
        finally:
            self.__busy = False


#------------------------------------------------------------------------------
class DataSQLDB (BaseDataDB):
    """
    Stores Data objects in a SQL database.
    """


    #----------------------------------------------------------------------
    def __init__(self, audit_name, audit_db):
        """
        :param audit_name: Audit name.
        :type audit_name: str

        :param audit_db: Database connection string in URL format.
        :type audit_db: str
        """
        super(DataSQLDB, self).__init__(audit_name)
        #
        # TODO add SQLAlchemy support
        #
        raise NotImplementedError("SQL databases not supported yet")


#------------------------------------------------------------------------------
class DataDB (BaseDataDB):
    """
    Stores Data objects in a database.

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
            return DataMemoryDB(audit_name)

        if scheme in ("dbm", "sqlite"):

            from os import path
            import posixpath

            filename = posixpath.join(parsed.netloc, parsed.path)
            if path.sep != posixpath.sep:
                filename.replace(posixpath.sep, path.sep)
            if filename.endswith(posixpath.sep):
                filename = filename[:-1]

            if scheme == "dbm":
                return DataFileDB(audit_name, filename)
            return DataSQLiteDB(audit_name, filename)

        ##if any(map(scheme.startswith, ("sqlite+", "mysql", "mssql", "plsql", "oracle"))):
        ##    return DataSQLDB(audit_name, audit_db)

        raise ValueError("Unsupported database type: %r" % scheme)
