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

__all__ = ["CacheDB"]

from .common import BaseDB, transactional

from ..api.net.cache import NetworkCache
from ..main.commonstructures import get_user_settings_folder

import os.path
import sqlite3


#------------------------------------------------------------------------------
class NetworkCacheDB(NetworkCache, BaseDB, Singleton):
    """
    Network cache with a database backend.
    """


    #----------------------------------------------------------------------
    def __init__(self):
        filename = os.path.join(get_user_settings_folder(), "cache.db")
        self.__db = sqlite3.connect(filename)
        self.__cursor = None
        self.__busy = False
        self.__create()


    #----------------------------------------------------------------------
    def close(self):
        try:
            try:
                self.__db.execute("PURGE;")
            finally:
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
            CREATE TABLE IF NOT EXISTS cache (
                id INTEGER PRIMARY KEY,
                audit STRING NOT NULL,
                protocol STRING NOT NULL,
                key STRING NOT NULL,
                timestamp INTEGER NOT NULL
                          DEFAULT (DATETIME('now', 'unixepoch')),
                lifespan INTEGER DEFAULT NULL,
                data BLOB NOT NULL,

                UNIQUE (audit, protocol, key) ON CONFLICT REPLACE
            );
        """)


    #----------------------------------------------------------------------
    @transactional
    def get(self, audit, key, protocol="http"):
        self.__cursor.execute("""
            SELECT data FROM cache
            WHERE audit = ? AND key = ? AND protocol = ?
                AND (timestamp = NULL OR lifespan = NULL OR
                     timestamp + lifespan > DATETIME('now', 'unixepoch')
                )
            LIMIT 1;
        """, (audit, key, protocol) )
        row = self.__cursor.fetchone()
        if row is not None:
            return self.decode(row[0])


    #----------------------------------------------------------------------
    @transactional
    def set(self, audit, key, data, protocol="http", timestamp=None, lifespan=None):
        data = self.encode(data)
        data = sqlite3.Binary(data)
        self.__cursor.execute("""
            INSERT INTO cache (audit, key, protocol, data, timestamp, lifespan)
            VALUES            (  ?,    ?,     ?,       ?,      ?,        ?    );
        """,                  (audit, key, protocol, data, timestamp, lifespan))


    #----------------------------------------------------------------------
    @transactional
    def remove(self, audit, key, protocol="http"):
        self.__cursor.execute("""
            DELETE FROM cache
            WHERE audit = ? AND key = ? AND protocol = ?;
        """,     (audit,        key,        protocol) )


    #----------------------------------------------------------------------
    @transactional
    def exists(self, audit, key, protocol="http"):
        self.__cursor.execute("""
            SELECT COUNT(id) FROM cache
            WHERE audit = ? AND key = ? AND protocol = ?
                AND (timestamp = NULL OR lifespan = NULL OR
                     timestamp + lifespan > DATETIME('now', 'unixepoch')
                )
            LIMIT 1;
        """, (audit, key, protocol))
        return bool(self.__cursor.fetchone()[0])


    #----------------------------------------------------------------------
    @transactional
    def clean(self, audit):
        """
        Delete all cache entries for the given audit.

        :param audit: Audit name.
        :type audit: str
        """
        self.__cursor.execute("""
            DELETE FROM cache
            WHERE audit = ?;
        """, (audit,))


    #----------------------------------------------------------------------
    @transactional
    def compact(self):
        """
        Free unused disk space.
        """
        self.__cursor.executescript("""
            DELETE FROM cache
                WHERE timestamp != NULL AND lifespan != NULL AND
                      timestamp + lifespan <= DATETIME('now', 'unixepoch');
            VACUUM;
        """)
