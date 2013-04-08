#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn@cr0hn.com
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

__all__ = ["AuditDB"]

from .common import BaseDB, atomic, transactional
from ..api.data.data import Data
from ..api.data.information.information import Information
from ..api.data.resource.resource import Resource
from ..api.data.vulnerability.vulnerability import Vulnerability
from ..messaging.codes import MessageCode
from ..managers.rpcmanager import implementor

import collections
import urlparse  # cannot use DecomposeURL here!
import warnings

# Lazy imports
sqlite3 = None


#----------------------------------------------------------------------
# RPC implementors for the database API.

@implementor(MessageCode.MSG_RPC_DATA_ADD)
def rpc_data_db_add(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.add_data(*argv, **argd)

@implementor(MessageCode.MSG_RPC_DATA_REMOVE)
def rpc_data_db_remove(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.remove_data(*argv, **argd)

@implementor(MessageCode.MSG_RPC_DATA_CHECK)
def rpc_data_db_check(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.has_data_key(*argv, **argd)

@implementor(MessageCode.MSG_RPC_DATA_GET)
def rpc_data_db_get(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.get_data(*argv, **argd)

@implementor(MessageCode.MSG_RPC_DATA_KEYS)
def rpc_data_db_keys(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.get_data_keys(*argv, **argd)

@implementor(MessageCode.MSG_RPC_DATA_COUNT)
def rpc_data_db_count(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.get_data_count(*argv, **argd)

@implementor(MessageCode.MSG_RPC_STATE_ADD)
def rpc_plugin_db_add(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.add_state_variable(*argv, **argd)

@implementor(MessageCode.MSG_RPC_STATE_REMOVE)
def rpc_plugin_db_remove(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.remove_state_variable(*argv, **argd)

@implementor(MessageCode.MSG_RPC_STATE_CHECK)
def rpc_plugin_db_check(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.has_state_variable(*argv, **argd)

@implementor(MessageCode.MSG_RPC_STATE_GET)
def rpc_plugin_db_get(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.get_state_variable(*argv, **argd)

@implementor(MessageCode.MSG_RPC_STATE_KEYS)
def rpc_plugin_db_keys(orchestrator, audit_name, *argv, **argd):
    return orchestrator.auditManager.get_audit(audit_name).database.get_state_variable_names(*argv, **argd)


#------------------------------------------------------------------------------
class BaseAuditDB (BaseDB):
    """
    Storage of Audit results.
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
    def add_data(self, data):
        """
        Add data to the database.

        :param data: Data to add.
        :type data: Data

        :returns: bool -- True if the data was new, False if it was updated.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def remove_data(self, identity, data_type = None):
        """
        Remove data given its identity hash.

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
    def has_data_key(self, identity, data_type = None):
        """
        Check if a data object with the given
        identity hash is present in the database.

        Optionally restrict the result by data type. Depending on the
        underlying database, this may result in a performance gain.

        :param identity: Identity hash.
        :type identity: str

        :returns: bool - True if the object is present, False otherwise.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def get_data(self, identity, data_type = None):
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
    def get_data_keys(self, data_type = None, data_subtype = None):
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
    def get_data_count(self, data_type = None, data_subtype = None):
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
    def add_state_variable(self, plugin_name, key, value):
        """
        Add a plugin state variable to the database.

        :param plugin_name: Plugin name.
        :type plugin_name: str

        :param key: Variable name.
        :type key: str

        :param value: Variable value.
        :type value: anything
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def remove_state_variable(self, plugin_name, key):
        """
        Remove a plugin state variable from the database.

        :param plugin_name: Plugin name.
        :type plugin_name: str

        :param key: Variable name.
        :type key: str
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def has_state_variable(self, plugin_name, key):
        """
        Check if plugin state variable is present in the database.

        :param plugin_name: Plugin name.
        :type plugin_name: str

        :param key: Variable name.
        :type key: str

        :returns: bool - True if the variable is present, False otherwise.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def get_state_variable(self, plugin_name, key):
        """
        Get the value of a plugin state variable given its name.

        :param plugin_name: Plugin name.
        :type plugin_name: str

        :param key: Variable name.
        :type key: str

        :returns: anything -- Variable value.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def get_state_variable_names(self, plugin_name):
        """
        Get all plugin state variable names in the database.

        :param plugin_name: Plugin name.
        :type plugin_name: str

        :returns: set(str) -- Variable names.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def mask_data_as_processed(self, identity, plugin_name):
        """
        Mark the data as having been processed by the plugin.

        :param identity: Identity hash.
        :type identity: str

        :param plugin_name: Plugin name.
        :type plugin_name: str

        :returns: set(str) -- Set of names of plugins that processed the data.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


    #----------------------------------------------------------------------
    def get_plugins_for_data(self, identity):
        """
        Get the plugins that have already processed the given data.

        :param identity: Identity hash.
        :type identity: str

        :returns: set(str) -- Set of plugin names.
        """
        raise NotImplementedError("Subclasses MUST implement this method!")


#------------------------------------------------------------------------------
class AuditMemoryDB (BaseAuditDB):
    """
    Stores Audit results in memory.
    """


    #----------------------------------------------------------------------
    def __init__(self, audit_name):
        super(AuditMemoryDB, self).__init__(audit_name)
        self.__results = dict()
        self.__state = collections.defaultdict(dict)
        self.__history = collections.defaultdict(set)


    #----------------------------------------------------------------------
    def encode(self, data):
        return data


    #----------------------------------------------------------------------
    def decode(self, data):
        return data


    #----------------------------------------------------------------------
    def add_data(self, data):
        if not isinstance(data, Data):
            raise TypeError("Expected Data, got %d instead" % type(data))
        identity = data.identity
        if identity in self.__results:
            self.__results[identity].merge(data)
            return False
        self.__results[identity] = data
        return True


    #----------------------------------------------------------------------
    def remove_data(self, identity, data_type = None):
        try:
            if data_type is None or self.__results[identity].data_type == data_type:
                del self.__results[identity]
                return True
        except KeyError:
            pass
        return False


    #----------------------------------------------------------------------
    def has_data_key(self, identity, data_type = None):
        return self.get_data(identity, data_type) is not None


    #----------------------------------------------------------------------
    def get_data(self, identity, data_type = None):
        data = self.__results.get(identity, None)
        if data_type is not None and data is not None and data.data_type != data_type:
            data = None
        return data


    #----------------------------------------------------------------------
    def get_data_keys(self, data_type = None, data_subtype = None):

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
    def get_data_count(self, data_type = None, data_subtype = None):

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
    def add_state_variable(self, plugin_name, key, value):
        self.__state[plugin_name][key] = value


    #----------------------------------------------------------------------
    def remove_state_variable(self, plugin_name, key):
        del self.__state[plugin_name][key]


    #----------------------------------------------------------------------
    def has_state_variable(self, plugin_name, key):
        return key in self.__state[plugin_name]


    #----------------------------------------------------------------------
    def get_state_variable(self, plugin_name, key):
        return self.__state[plugin_name][key]


    #----------------------------------------------------------------------
    def get_state_variable_names(self, plugin_name):
        return set(self.__state[plugin_name].iterkeys())


    #----------------------------------------------------------------------
    def mask_data_as_processed(self, identity, plugin_name):
        self.__history[identity].add(plugin_name)
        return self.__history[identity]


    #----------------------------------------------------------------------
    def get_plugins_for_data(self, identity):
        return self.__history[identity]


    #----------------------------------------------------------------------
    def close(self):
        self.__results = dict()
        self.__state = collections.defaultdict(dict)
        self.__history = collections.defaultdict(set)


#------------------------------------------------------------------------------
class AuditSQLiteDB (BaseAuditDB):
    """
    Stores Audit results in a database file using SQLite.
    """

    # The current schema version.
    SCHEMA_VERSION = 1


    #----------------------------------------------------------------------
    def __init__(self, audit_name, filename = None):
        """
        Constructor.

        :param audit_name: Audit name.
        :type audit_name: str

        :param filename: Optional SQLite database file name.
        :type filename: str
        """
        super(AuditSQLiteDB, self).__init__(audit_name)
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
    def encode(self, data):

        # Encode the data.
        data = super(AuditSQLiteDB, self).encode(data)

        # Tell SQLite the encoded data is a BLOB and not a TEXT.
        return sqlite3.Binary(data)


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

        # Check if the schema is already created.
        self.__cursor.execute((
            "SELECT count(*) FROM sqlite_master"
            " WHERE type = 'table' AND name = 'golismero';"))

        # If it's already present...
        if self.__cursor.fetchone()[0]:

            # Check if the schema version and audit name match.
            self.__cursor.execute(
                "SELECT schema_version, audit_name FROM golismero LIMIT 1;")
            row = self.__cursor.fetchone()
            if not row:
                raise IOError("Broken database!")
            if row[0] != self.SCHEMA_VERSION:
                raise IOError(
                    "Incompatible schema version: %r != %r" % \
                    (row[0], self.SCHEMA_VERSION))
            if row[1] != self.audit_name:
                raise IOError(
                    "Database belongs to another audit: %r != %r" % \
                    (row[0], self.audit_name))

        # If not present...
        else:

            # Create the schema.
            self.__cursor.executescript(
            """

            ----------------------------------------------------------
            -- Table to store the file information.
            -- There must only be one row in it.
            ----------------------------------------------------------

            CREATE TABLE golismero (
                schema_version INTEGER NOT NULL,
                audit_name STRING NOT NULL
            );

            ----------------------------------------------------------
            -- Tables to store the data.
            ----------------------------------------------------------

            CREATE TABLE information (
                rowid INTEGER PRIMARY KEY,
                identity STRING UNIQUE NOT NULL,
                type INTEGER NOT NULL,
                data BLOB NOT NULL
            );

            CREATE TABLE resource (
                rowid INTEGER PRIMARY KEY,
                identity STRING UNIQUE NOT NULL,
                type INTEGER NOT NULL,
                data BLOB NOT NULL
            );

            CREATE TABLE vulnerability (
                rowid INTEGER PRIMARY KEY,
                identity STRING UNIQUE NOT NULL,
                type STRING NOT NULL,
                data BLOB NOT NULL
            );

            ----------------------------------------------------------
            -- Tables to store the plugin state and history.
            ----------------------------------------------------------

            CREATE TABLE plugin (
                rowid INTEGER PRIMARY KEY,
                name STRING UNIQUE NOT NULL
            );

            CREATE TABLE state (
                rowid INTEGER PRIMARY KEY,
                plugin_id INTEGER NOT NULL,
                key STRING NOT NULL,
                value BLOB NOT NULL,
                FOREIGN KEY(plugin_id) REFERENCES(plugin.rowid),
                UNIQUE(plugin_id, key) ON CONFLICT REPLACE
            );

            CREATE TABLE history (
                rowid INTEGER PRIMARY KEY,
                plugin_id INTEGER NOT NULL,
                identity STRING NOT NULL,
                FOREIGN KEY(plugin_id) REFERENCES(plugin.rowid),
                UNIQUE(plugin_id, identity) ON CONFLICT IGNORE
            );

            """)

            # Insert the file information.
            self.__cursor.execute(
                "INSERT INTO golismero VALUES (?, ?);",
                (self.SCHEMA_VERSION, self.audit_name))


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
                if dtype == Information.INFORMATION_UNKNOWN:
                    warnings.warn(
                        "Received %s object of subtype INFORMATION_UNKNOWN" % type(data),
                        RuntimeWarning)
            elif isinstance(data, Resource):
                data.data_type = Data.TYPE_RESOURCE
                table = "resource"
                dtype = data.resource_type
                if dtype == Resource.RESOURCE_UNKNOWN:
                    warnings.warn(
                        "Received %s object of subtype RESOURCE_UNKNOWN" % type(data),
                        RuntimeWarning)
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
    def add_data(self, data):
        if not isinstance(data, Data):
            raise TypeError("Expected Data, got %d instead" % type(data))
        table, dtype = self.__get_data_table_and_type(data)
        identity = data.identity
        old_data = self.__get(identity, data.data_type)
        is_new = old_data is None
        if not is_new:
            old_data.merge(data)
            data = old_data
        query  = "INSERT OR REPLACE INTO %s VALUES (NULL, ?, ?, ?);" % table
        values = (identity, dtype, self.encode(data))
        self.__cursor.execute(query, values)
        return is_new


    #----------------------------------------------------------------------
    @transactional
    def remove_data(self, identity, data_type = None):
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
    def has_data_key(self, identity, data_type = None):
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
    def get_data(self, identity, data_type = None):
        return self.__get_data(identity, data_type)

    def __get_data(self, identity, data_type = None):
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
    def get_data_keys(self, data_type = None, data_subtype = None):

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
    def get_data_count(self, data_type = None, data_subtype = None):

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
    def add_state_variable(self, plugin_name, key, value):

        # Fetch the plugin rowid, add it if missing.
        self.__cursor.execute(
            "SELECT rowid FROM plugin WHERE name = ? LIMIT 1;",
            (plugin_name,))
        rows = self.__cursor.fetchone()
        if rows:
            plugin_id = rows[0]
        else:
            self.__cursor.execute(
                "INSERT INTO plugin VALUES (NULL, ?);",
                (plugin_name,))
            plugin_id = self.__cursor.lastrowid
            if plugin_id is None:
                self.__cursor.execute(
                    "SELECT rowid FROM plugin WHERE name = ? LIMIT 1;",
                    (plugin_name,))
                rows = self.__cursor.fetchone()
                plugin_id = rows[0]

        # Save the state variable.
        self.__cursor.execute(
            "INSERT INTO state VALUES (NULL, ?, ?, ?);",
            (plugin_id, key, self.encode(value)))


    #----------------------------------------------------------------------
    @transactional
    def remove_state_variable(self, plugin_name, key):

        # Fetch the plugin rowid, fail if missing.
        self.__cursor.execute(
            "SELECT rowid FROM plugin WHERE name = ? LIMIT 1;",
            (plugin_name,))
        rows = self.__cursor.fetchone()
        plugin_id = rows[0]

        # Delete the state variable.
        self.__cursor.execute(
            "DELETE FROM state WHERE plugin_id = ? AND key = ?;",
            (plugin_id, key))


    #----------------------------------------------------------------------
    @transactional
    def has_state_variable(self, plugin_name, key):

        # Fetch the plugin rowid, return False if missing.
        self.__cursor.execute(
            "SELECT rowid FROM plugin WHERE name = ? LIMIT 1;",
            (plugin_name,))
        rows = self.__cursor.fetchone()
        if not rows:
            return False
        plugin_id = rows[0]

        # Check if the state variable is defined.
        self.__cursor.execute((
            "SELECT COUNT(rowid) FROM state"
            " WHERE plugin_id = ? AND key = ? LIMIT 1"),
            (plugin_id, key))
        return bool(self.__cursor.fetchone()[0])


    #----------------------------------------------------------------------
    @transactional
    def get_state_variable(self, plugin_name, key):

        # Fetch the plugin rowid, fail if missing.
        self.__cursor.execute(
            "SELECT rowid FROM plugin WHERE name = ? LIMIT 1;",
            (plugin_name,))
        rows = self.__cursor.fetchone()
        plugin_id = rows[0]

        # Get the state variable value, fail if missing.
        self.__cursor.execute((
            "SELECT value FROM state"
            " WHERE plugin_id = ? AND key = ? LIMIT 1;"),
            (plugin_id, key))
        return self.decode(self.__cursor.fetchone()[0])


    #----------------------------------------------------------------------
    @transactional
    def get_state_variable_names(self, plugin_name):

        # Fetch the plugin rowid, return an empty set if missing.
        self.__cursor.execute(
            "SELECT rowid FROM plugin WHERE name = ? LIMIT 1;",
            (plugin_name,))
        rows = self.__cursor.fetchone()
        if not rows:
            return set()
        plugin_id = rows[0]

        # Get the state variable names.
        self.__cursor.execute(
            "SELECT key FROM state WHERE plugin_id = ?;",
            (plugin_id,))
        return set(self.__cursor.fetchall())


    #----------------------------------------------------------------------
    @transactional
    def mask_data_as_processed(self, identity, plugin_name):

        # Fetch the plugin rowid, add it if missing.
        self.__cursor.execute(
            "SELECT rowid FROM plugin WHERE name = ? LIMIT 1;",
            (plugin_name,))
        rows = self.__cursor.fetchone()
        if rows:
            plugin_id = rows[0]
        else:
            self.__cursor.execute(
                "INSERT INTO plugin VALUES (NULL, ?);",
                (plugin_name,))
            plugin_id = self.__cursor.lastrowid
            if plugin_id is None:
                self.__cursor.execute(
                    "SELECT rowid FROM plugin WHERE name = ? LIMIT 1;",
                    (plugin_name,))
                rows = self.__cursor.fetchone()
                plugin_id = rows[0]

        # Mark the data as processed by this plugin.
        self.__cursor.execute(
            "INSERT INTO history VALUES (NULL, ?, ?);",
            (plugin_id, identity))


    #----------------------------------------------------------------------
    @transactional
    def get_plugins_for_data(self, identity):
        self.__cursor.execute((
            "SELECT plugin.name FROM plugin, history"
            " WHERE history.plugin_id = plugin.rowid AND"
            "       history.identity = ?;"),
            (identity,))
        return set(self.__cursor.fetchall())


    #----------------------------------------------------------------------
    @atomic
    def close(self):
        try:
            try:
                self.__db.execute("VACUUM;")
            finally:
                self.__db.close()
        except Exception:
            pass


#------------------------------------------------------------------------------
class AuditDB (BaseAuditDB):
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
        parsed = urlparse.urlparse(audit_db)  # cannot use DecomposeURL here!
        scheme = parsed.scheme.lower()

        if scheme == "memory":
            return AuditMemoryDB(audit_name)

        if scheme == "sqlite":

            from os import path
            import posixpath

            filename = posixpath.join(parsed.netloc, parsed.path)
            if path.sep != posixpath.sep:
                filename.replace(posixpath.sep, path.sep)
            if filename.endswith(posixpath.sep):
                filename = filename[:-1]

            return AuditSQLiteDB(audit_name, filename)

        raise ValueError("Unsupported database type: %r" % scheme)
