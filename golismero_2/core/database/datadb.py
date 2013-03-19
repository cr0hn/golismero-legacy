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

__all__ = ["DataDB"]

from .common import BaseDB, atomic, transactional
from ..api.data.data import Data
from ..api.data.information.information import Information
from ..api.data.resource.resource import Resource
from ..api.data.vulnerability.vulnerability import Vulnerability
from ..messaging.codes import MessageCode
from ..managers.rpcmanager import implementor

import urlparse
import warnings

# Lazy imports
anydbm  = None
sqlite3 = None


#----------------------------------------------------------------------
# RPC implementors for the database API.

@implementor(MessageCode.MSG_RPC_DATA_ADD)
def rpc_datadb_add(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.add(*argv, **argd)

@implementor(MessageCode.MSG_RPC_DATA_REMOVE)
def rpc_datadb_remove(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.remove(*argv, **argd)

@implementor(MessageCode.MSG_RPC_DATA_GET)
def rpc_datadb_get(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.get(*argv, **argd)

@implementor(MessageCode.MSG_RPC_DATA_KEYS)
def rpc_datadb_keys(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.keys(*argv, **argd)

@implementor(MessageCode.MSG_RPC_DATA_COUNT)
def rpc_datadb_count(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.count(*argv, **argd)

@implementor(MessageCode.MSG_RPC_DATA_CHECK)
def rpc_datadb_check(orchestrator, audit_name, identity):
    return orchestrator.auditManager.get_audit(audit_name).database.has_key(identity)


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

        :param data: Data to add.
        :type data: Data

        :returns: bool -- True if the data was added, False if it was updated
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def remove(self, identity, data_type = None):
        """
        Remove an object given its identity hash.

        Optionally restrict the result by data type. Depending on the
        underlying database, this may result in a performance gain.

        :param identity: Identity hash.
        :type identity: str

        :param data_type: Optional data type. One of the Data.TYPE_* values.
        :type data_type: int

        :returns: bool -- True if the object was removed, False if it didn't exist.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def has_key(self, identity, data_type = None):
        """
        Check if an object with the given
        identity hash is present in the database.

        Optionally restrict the result by data type. Depending on the
        underlying database, this may result in a performance gain.

        :param identity: Identity hash.
        :type identity: str

        :returns: bool - True if the object is present, False otherwise.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def get(self, identity, data_type = None):
        """
        Get an object given its identity hash.

        Optionally restrict the result by data type. Depending on the
        underlying database, this may result in a performance gain.

        :param identity: Identity hash.
        :type identity: str

        :param data_type: Optional data type. One of the Data.TYPE_* values.
        :type data_type: int

        :returns: Data | None
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def keys(self, data_type = None, data_subtype = None):
        """
        Get a list of identity hashes for all objects of the requested
        type, optionally filtering by subtype.

        :param data_type: Optional data type. One of the Data.TYPE_* values.
        :type data_type: int

        :param data_subtype: Optional data subtype.
        :type data_subtype: int | str

        :returns: set(str) -- Identity hashes.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def count(self, data_type = None, data_subtype = None):
        """
        Count all objects of the requested type,
        optionally filtering by subtype.

        :param data_type: Optional data type. One of the Data.TYPE_* values.
        :type data_type: int

        :param data_subtype: Optional data subtype.
        :type data_subtype: int | str

        :returns: set(str) -- Identity hashes.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def __len__(self):
        return self.count()


    #----------------------------------------------------------------------
    def __contains__(self, data):
        if not isinstance(data, Data):
            raise TypeError("Expected Data, got %d instead" % type(data))
        return self.has_key(data.identity)


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
        identity = data.identity
        is_new = identity not in self.__results
        self.__results[identity] = data
        return is_new


    #----------------------------------------------------------------------
    def remove(self, identity, data_type = None):
        try:
            if data_type is None or self.__results[identity].data_type == data_type:
                del self.__results[identity]
                return True
        except KeyError:
            pass
        return False


    #----------------------------------------------------------------------
    def has_key(self, identity, data_type = None):
        return self.get(identity, data_type) is not None


    #----------------------------------------------------------------------
    def get(self, identity, data_type = None):
        data = self.__results.get(identity, None)
        if data_type is not None and data is not None and data.data_type != data_type:
            data = None
        return data


    #----------------------------------------------------------------------
    def keys(self, data_type = None, data_subtype = None):

        # Ugly but (hopefully) efficient code follows.

        if data_type is None:
            if data_subtype is not None:
                raise NotImplementedError(
                    "Can't filter by subtype for all types")
            return { identity
                     for identity, data in self.__results.iteritems() }
        if data_subtype is None:
            return { identity
                     for identity, data in self.__results.iteritems()
                     if data.data_type == data_type }
        if data_type == Data.TYPE_INFORMATION:
            return { identity
                     for identity, data in self.__results.iteritems()
                     if data.data_type == data_type
                     and data.information_type == data_subtype }
        if data_type == Data.TYPE_RESOURCE:
            return { identity
                     for identity, data in self.__results.iteritems()
                     if data.data_type == data_type
                     and data.resource_type == data_subtype }
        if data_type == Data.TYPE_VULNERABILITY:
            return { identity
                     for identity, data in self.__results.iteritems()
                     if data.data_type == data_type
                     and data.vulnerability_type == data_subtype }
        raise NotImplementedError(
            "Unknown data type: %r" % data_type)


    #----------------------------------------------------------------------
    def count(self, data_type = None, data_subtype = None):

        # Ugly but (hopefully) efficient code follows.

        if data_type is None:
            if data_subtype is not None:
                raise NotImplementedError(
                    "Can't filter by subtype for all types")
            return len(self.__results)
        if data_subtype is None:
            return len({ identity
                     for identity, data in self.__results.iteritems()
                     if data.data_type == data_type })
        if data_type == Data.TYPE_INFORMATION:
            return len({ identity
                     for identity, data in self.__results.iteritems()
                     if data.data_type == data_type
                     and data.information_type == data_subtype })
        if data_type == Data.TYPE_RESOURCE:
            return len({ identity
                     for identity, data in self.__results.iteritems()
                     if data.data_type == data_type
                     and data.resource_type == data_subtype })
        if data_type == Data.TYPE_VULNERABILITY:
            return len({ identity
                     for identity, data in self.__results.iteritems()
                     if data.data_type == data_type
                     and data.vulnerability_type == data_subtype })
        raise NotImplementedError(
            "Unknown data type: %r" % data_type)


    #----------------------------------------------------------------------
    def __len__(self):
        return len(self.__results)


    #----------------------------------------------------------------------
    def __contains__(self, data):
        if not isinstance(data, Data):
            raise TypeError("Expected Data, got %d instead" % type(data))
        return data.identity in self.__results


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
        self.__busy = False


    #----------------------------------------------------------------------
    def _atom(self, fn, argv, argd):
        # this will fail for multithreaded accesses,
        # but dbm implementations are usually not multithreaded either
        if self.__busy:
            raise RuntimeError("The database is busy")
        self.__busy = True
        try:
            return fn(self, *argv, **argd)
        finally:
            self.__busy = False


    #----------------------------------------------------------------------
    @atomic
    def close(self):
        try:
            self.__db.close()
        except Exception:
            pass


    #----------------------------------------------------------------------
    @atomic
    def add(self, data):
        if not isinstance(data, Data):
            raise TypeError("Expected Data, got %d instead" % type(data))
        identity = data.identity
        is_new = identity not in self.__db
        self.__db[identity] = self.encode(data)
        return is_new


    #----------------------------------------------------------------------
    @atomic
    def remove(self, identity, data_type = None):
        # XXX data_type is ignored because it'd be grossly inefficient
        try:
            del self.__db[identity]
        except KeyError:
            return False
        return True


    #----------------------------------------------------------------------
    def has_key(self, identity, data_type = None):
        # not using @atomic because we're calling self.get()
        return self.get(identity, data_type) is not None


    #----------------------------------------------------------------------
    @atomic
    def get(self, identity, data_type = None):
        data = self.__db.get(identity, None)
        if data_type is not None and data is not None and data.data_type != data_type:
            data = None
        return data


    #----------------------------------------------------------------------
    @atomic
    def keys(self, data_type = None, data_subtype = None):

        # This code is ugly, but there's not that much
        # we can do when the dbm databases only support
        # a subset of dictionary methods, and are only
        # barely documented anyway. :(

        # Validate the data type.
        if data_type is None:
            if data_subtype is not None:
                raise NotImplementedError(
                    "Can't filter by subtype for all types")
        elif data_type not in (Data.TYPE_INFORMATION,
                               Data.TYPE_RESOURCE,
                               Data.TYPE_VULNERABILITY):
            raise NotImplementedError(
                "Unknown data type: %r" % data_type)

        # Shortcut to get all identity hashes.
        if data_type is None:
            return set(self.__db)

        # Build a set of identity hashes.
        hashes = set()

        # For each identity hash in the database...
        for identity in self.__db:

            # Get the data object.
            data = self.__db[identity]

            # If the data type doesn't match, skip it.
            if data_type is not None and data.data_type != data_type:
                continue

            # If we need to filter by subtype...
            if data_subtype is not None:

                # Filter by information_type.
                if data_type == Data.TYPE_INFORMATION:
                    if data.information_type != data_subtype:
                        continue

                # Filter by resource_type.
                if data_type == Data.TYPE_RESOURCE:
                    if data.resource_type == data_subtype:
                        continue

                # Filter by vulnerability_type.
                if data_type == Data.TYPE_VULNERABILITY:
                    if data.vulnerability_type == data_subtype:
                        continue

            # Add the identity hash to the set.
            hashes.add(identity)

        # Return the set of identity hashes.
        return hashes


    #----------------------------------------------------------------------
    def count(self, data_type = None, data_subtype = None):
        # not using @atomic here!

        # Shortcut to get the total count.
        if data_type is None:
            if data_subtype is not None:
                raise NotImplementedError(
                    "Can't filter by subtype for all types")
            return len(self)

        # Count the requested elements.
        return len(self.keys(data_type, data_subtype))


    #----------------------------------------------------------------------
    @atomic
    def __len__(self):
        return len(self.__db)


    #----------------------------------------------------------------------
    @atomic
    def __contains__(self, data):
        if not isinstance(data, Data):
            raise TypeError("Expected Data, got %d instead" % type(data))
        return self.__db.has_key(data.identity)


    #----------------------------------------------------------------------
    def __iter__(self):
        # we can't use @atomic here
        if self.__busy:
            raise RuntimeError("The database is busy")
        self.__busy = True
        try:
            for identity in self.__db:
                yield self.decode( self.__db[identity] )
        finally:
            self.__busy = False


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
    def _atom(self, fn, argv, argd):
        # this will fail for multithreaded accesses,
        # but sqlite is not multithreaded either
        if self.__busy:
            raise RuntimeError("The database is busy")
        try:
            self.__busy = True
            return fn(self, *argv, **argd)
        finally:
            self.__busy = False


    #----------------------------------------------------------------------
    def _transaction(self, fn, argv, argd):
        """
        Execute a transactional operation.
        """
        # this will fail for multithreaded accesses,
        # but sqlite is not multithreaded either
        if self.__busy:
            raise RuntimeError("The database is busy")
        try:
            self.__busy = True
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
                rowid INTEGER PRIMARY KEY,
                identity STRING UNIQUE NOT NULL,
                type INTEGER NOT NULL,
                data BLOB NOT NULL
            );
        """)
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS resource (
                rowid INTEGER PRIMARY KEY,
                identity STRING UNIQUE NOT NULL,
                type INTEGER NOT NULL,
                data BLOB NOT NULL
            );
        """)
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS vulnerability (
                rowid INTEGER PRIMARY KEY,
                identity STRING UNIQUE NOT NULL,
                type STRING NOT NULL,
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
        table, dtype = self.__get_data_table_and_type(data)
        identity = data.identity
        query = "SELECT COUNT(rowid) FROM %s WHERE identity = ? LIMIT 1;"
        self.__cursor.execute(query % table, (identity,))
        is_new = not bool(self.__cursor.fetchone()[0])
        query  = "INSERT OR REPLACE INTO %s VALUES (NULL, ?, ?, ?);" % table
        values = (identity, dtype, sqlite3.Binary(self.encode(data)))
        self.__cursor.execute(query, values)
        return is_new


    #----------------------------------------------------------------------
    @transactional
    def remove(self, identity, data_type = None):
        if data_type is None:
            tables = ("information", "resource", "vulnerability")
        elif data_type == Data.TYPE_INFORMATION:
            tables = ("information",)
        elif data_type == Data.TYPE_RESOURCE:
            tables = ("resource",)
        elif data_type == Data.TYPE_VULNERABILITY:
            tables = ("vulnerability",)
        else:
            raise NotImplementedError(
                "Unknown data type %r!" % data_type)
        for table in tables:
            query  = "DELETE FROM identity WHERE identity = ?;" % table
            self.__cursor.execute(query, (identity,))
            if self.__cursor.rowcount:
                return True
        return False


    #----------------------------------------------------------------------
    @transactional
    def has_key(self, identity, data_type = None):
        if data_type is None:
            tables = ("information", "resource", "vulnerability")
        elif data_type == Data.TYPE_INFORMATION:
            tables = ("information",)
        elif data_type == Data.TYPE_RESOURCE:
            tables = ("resource",)
        elif data_type == Data.TYPE_VULNERABILITY:
            tables = ("vulnerability",)
        else:
            raise NotImplementedError(
                "Unknown data type %r!" % data_type)
        for table in tables:
            query = "SELECT COUNT(rowid) FROM %s WHERE identity = ? LIMIT 1;" % table
            self.__cursor.execute(query, (identity,))
            row = self.__cursor.fetchone()
            if row[0]:
                return True
        return False


    #----------------------------------------------------------------------
    @transactional
    def get(self, identity, data_type = None):
        if data_type is None:
            tables = ("information", "resource", "vulnerability")
        elif data_type == Data.TYPE_INFORMATION:
            tables = ("information",)
        elif data_type == Data.TYPE_RESOURCE:
            tables = ("resource",)
        elif data_type == Data.TYPE_VULNERABILITY:
            tables = ("vulnerability",)
        else:
            raise NotImplementedError(
                "Unknown data type %r!" % data_type)
        for table in tables:
            query = "SELECT data FROM %s WHERE identity = ? LIMIT 1;" % table
            self.__cursor.execute(query, (identity,))
            row = self.__cursor.fetchone()
            if row and row[0]:
                return self.decode(row[0])


    #----------------------------------------------------------------------
    @transactional
    def keys(self, data_type = None, data_subtype = None):

        # Get all the keys.
        if data_type is None:
            if data_subtype is not None:
                raise NotImplementedError(
                    "Can't filter by subtype for all types")
            hashes = set()
            for table in ("information", "resource", "vulnerability"):
                query  = "SELECT identity FROM %s;" % table
                self.__cursor.execute(query)
                hashes.update( row[0] for row in self.__cursor.fetchall() )
            return hashes

        # Get keys filtered by type and subtype.
        if   data_type == Data.TYPE_INFORMATION:
            table = "information"
        elif data_type == Data.TYPE_RESOURCE:
            table = "resource"
        elif data_type == Data.TYPE_VULNERABILITY:
            table = "vulnerability"
        else:
            raise NotImplementedError(
                "Unknown data type %r!" % data_type)
        if data_subtype is None:
            query  = "SELECT identity FROM %s;" % table
            values = ()
        else:
            query  = "SELECT identity FROM %s WHERE type = ?;" % table
            values = (data_subtype,)
        self.__cursor.execute(query, values)
        return { row[0] for row in self.__cursor.fetchall() }


    #----------------------------------------------------------------------
    @transactional
    def count(self, data_type = None, data_subtype = None):

        # Count all the keys.
        if data_type is None:
            if data_subtype is not None:
                raise NotImplementedError(
                    "Can't filter by subtype for all types")
            count = 0
            for table in ("information", "resource", "vulnerability"):
                self.__cursor.execute("SELECT COUNT(rowid) FROM %s;" % table)
                count += int(self.__cursor.fetchone()[0])
            return count

        # Count keys filtered by type and subtype.
        if   data_type == Data.TYPE_INFORMATION:
            table = "information"
        elif data_type == Data.TYPE_RESOURCE:
            table = "resource"
        elif data_type == Data.TYPE_VULNERABILITY:
            table = "vulnerability"
        else:
            raise NotImplementedError(
                "Unknown data type %r!" % data_type)
        if data_subtype is None:
            query  = "SELECT COUNT(rowid) FROM %s;" % table
            values = ()
        else:
            query  = "SELECT COUNT(rowid) FROM %s WHERE type = ?;" % table
            values = (data_subtype,)
        self.__cursor.execute(query, values)
        return int(self.__cursor.fetchone()[0])


    #----------------------------------------------------------------------
    @transactional
    def __len__(self):
        count = 0
        for table in ("information", "resource", "vulnerability"):
            self.__cursor.execute("SELECT COUNT(rowid) FROM %s;" % table)
            count += int(self.__cursor.fetchone()[0])
        return count


    #----------------------------------------------------------------------
    @transactional
    def __contains__(self, data):
        if not isinstance(data, Data):
            raise TypeError("Expected Data, got %d instead" % type(data))
        table, _ = self.__get_data_table_and_type(data)
        query = "SELECT COUNT(rowid) FROM %s WHERE identity = ? LIMIT 1;"
        self.__cursor.execute(query % table, (data.identity,))
        return bool(self.__cursor.fetchone()[0])


    #----------------------------------------------------------------------
    def __iter__(self):
        # can't use @transactional or @atomic here!
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
    @atomic
    def dump(self, filename):
        """
        Dump the database in SQL format.

        :param filename: Output filename.
        :type filename: str
        """
        with open(filename, 'w') as f:
            for line in self.__db.iterdump():
                f.write(line + "\n")


    #----------------------------------------------------------------------
    @atomic
    def close(self):
        try:
            try:
                self.__db.execute("PURGE;")
            finally:
                self.__db.close()
        except Exception:
            pass


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

        ##if any(map(scheme.startswith, ("mysql", "mssql", "plsql", "oracle"))):
        ##    return DataSQLDB(audit_name, audit_db)

        raise ValueError("Unsupported database type: %r" % scheme)
