#!/usr/bin/env python

"""
NIST CPE dictionary.
"""

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: https://github.com/golismero
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

# Adapted from:
# https://github.com/MarioVilas/network_tools/blob/master/cpe.py

__all__ = ["CPEDB"]

import re

from time import gmtime, asctime
from os import unlink
from os.path import exists, getctime, join
from threading import RLock
from urllib import quote, unquote
from urllib2 import urlopen, Request, HTTPError  # TODO use requests instead!

import shutil
import sqlite3

try:
    from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree

from ..api.data.vulnerability.vuln_utils import get_cpe_version, parse_cpe
from ..api.logger import Logger
from ..api.net.web_utils import parse_url
from ..common import get_user_settings_folder
from ..messaging.codes import MessageCode
from ..managers.rpcmanager import implementor


#------------------------------------------------------------------------------
# RPC implementors.

@implementor(MessageCode.MSG_RPC_CPE_GET_TITLE)
def rpc_cpe_get_title(orchestrator, audit_name, *args, **kwargs):
    return orchestrator.cpedb.get_title(*args, **kwargs)

@implementor(MessageCode.MSG_RPC_CPE_RESOLVE)
def rpc_cpe_resolve(orchestrator, audit_name, *args, **kwargs):
    return orchestrator.cpedb.resolve(*args, **kwargs)

@implementor(MessageCode.MSG_RPC_CPE_SEARCH)
def rpc_cpe_search(orchestrator, audit_name, *args, **kwargs):
    return orchestrator.cpedb.search(*args, **kwargs)


#------------------------------------------------------------------------------
def transactional(fn):
    def wrapper(self, *args, **kwargs):
        return self._transaction(fn, args, kwargs)
    return wrapper

def iter_transactional(fn):
    def wrapper(self, *args, **kwargs):
        return self._iter_transaction(fn, args, kwargs)
    return wrapper


#------------------------------------------------------------------------------
class CPEDB(object):
    """
    Translates between CPE 2.2 and CPE 2.3 names, and looks up user-friendly
    software names from CPE names and visceversa.

    The official CPE dictionary is converted to SQLite format from the
    original XML file mantained by NIST: https://nvd.nist.gov/cpe.cfm
    """

    DB_FILE  = "official-cpe-dictionary_v2.3.db"
    XML_FILE = "official-cpe-dictionary_v2.3.xml"
    DOWNLOAD_URL = (
        "http://static.nvd.nist.gov/feeds/xml/cpe/dictionary/" + XML_FILE
    )


    #--------------------------------------------------------------------------
    def __init__(self):

        # Get the database filename.
        db_file = join( get_user_settings_folder(), self.DB_FILE )

        # Create the lock to make this class thread safe.
        self.__lock = RLock()

        # The busy flag prevents reentrance.
        self.__busy = False

        # Determine if the database existed.
        is_new = exists(db_file)

        # Open the database file.
        self.__db = sqlite3.connect(db_file)

        # Initialize the database if needed.
        # On error close the database and raise an exception.
        try:
            is_empty = self.__initialize()
            if is_empty:
                self.update(force = True)
        except:
            self.close()
            if is_new:
                unlink(db_file)
            raise


    #--------------------------------------------------------------------------
    def close(self):
        try:
            self.__db.close()
        finally:
            self.__db     = None
            self.__cursor = None
            self.__lock   = None


    #--------------------------------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, etype, value, tb):
        try:
            self.close()
        except Exception:
            pass


    #--------------------------------------------------------------------------
    def _transaction(self, fn, args, kwargs):
        with self.__lock:
            if self.__busy:
                raise RuntimeError("The database is busy")
            try:
                self.__busy   = True
                self.__cursor = self.__db.cursor()
                try:
                    retval = fn(self, *args, **kwargs)
                    self.__db.commit()
                    return retval
                except:
                    self.__db.rollback()
                    raise
            finally:
                self.__cursor = None
                self.__busy   = False

    def _iter_transaction(self, fn, args, kwargs):
        with self.__lock:
            if self.__busy:
                raise RuntimeError("The database is busy")
            try:
                self.__busy   = True
                self.__cursor = self.__db.cursor()
                try:
                    for item in fn(self, *args, **kwargs):
                        yield item
                    self.__db.commit()
                except:
                    self.__db.rollback()
                    raise
            finally:
                self.__cursor = None
                self.__busy   = False


    #--------------------------------------------------------------------------
    @transactional
    def __initialize(self):

        # If the file already contains the schema, do nothing.
        self.__cursor.execute(
            "SELECT count(*) FROM sqlite_master"
            " WHERE type = 'table' AND name = 'cpe';"
        )
        if self.__cursor.fetchone()[0]:
            return False

        # Create the database schema.
        self.__cursor.executescript(
            """
            CREATE TABLE `cpe` (
                `rowid` INTEGER PRIMARY KEY,
                `name23` STRING UNIQUE NOT NULL,
                `name22` STRING NOT NULL,
                `title` STRING NOT NULL,
                `deprecated` INTEGER(1) NOT NULL DEFAULT 0,
                `part` STRING NOT NULL DEFAULT '*',
                `vendor` STRING NOT NULL DEFAULT '*',
                `product` STRING NOT NULL DEFAULT '*',
                `version` STRING NOT NULL DEFAULT '*',
                `update` STRING NOT NULL DEFAULT '*',
                `edition` STRING NOT NULL DEFAULT '*',
                `language` STRING NOT NULL DEFAULT '*',
                `sw_edition` STRING NOT NULL DEFAULT '*',
                `target_sw` STRING NOT NULL DEFAULT '*',
                `target_hw` STRING NOT NULL DEFAULT '*',
                `other` STRING NOT NULL DEFAULT '*'
            );
            CREATE INDEX `cpe_name22` ON `cpe`(`name22`);
            CREATE INDEX `cpe_title` ON `cpe`(`title`);
            CREATE INDEX `cpe_part` ON `cpe`(`part`);
            CREATE INDEX `cpe_vendor` ON `cpe`(`vendor`);
            CREATE INDEX `cpe_product` ON `cpe`(`product`);
            CREATE INDEX `cpe_version` ON `cpe`(`version`);
            CREATE INDEX `cpe_update` ON `cpe`(`update`);
            CREATE INDEX `cpe_edition` ON `cpe`(`edition`);
            CREATE INDEX `cpe_language` ON `cpe`(`language`);
            CREATE INDEX `cpe_sw_edition` ON `cpe`(`sw_edition`);
            CREATE INDEX `cpe_target_sw` ON `cpe`(`target_sw`);
            CREATE INDEX `cpe_target_hw` ON `cpe`(`target_hw`);
            CREATE INDEX `cpe_other` ON `cpe`(`other`);
            """
        )
        return True


    #--------------------------------------------------------------------------
    @transactional
    def update(self, force = False):
        """
        Update the database.

        This downloads a newer XML file from NIST if available,
        and recreates the database from it.

        :param force: True to force the update, False to only
            load the data from NIST if outdated.
        :type force: bool
        """

        # If the XML file from NIST is missing, broken or older, download it.
        msg = "Connecting to %s..." % parse_url(self.DOWNLOAD_URL).hostname
        xml_file = join( get_user_settings_folder(), self.XML_FILE )
        tree = None
        if not exists(xml_file):
            Logger.log_verbose(msg)
            src = urlopen(self.DOWNLOAD_URL)
        else:
            try:
                tree = etree.parse(xml_file)
                src  = None
            except Exception:
                Logger.log_verbose(msg)
                src = urlopen(self.DOWNLOAD_URL)
            else:
                try:
                    ftm = getctime(xml_file)
                    ftm -= 3600 # -1 minute to compensate timing errors
                    ims = asctime(gmtime(ftm))
                    req = Request(self.DOWNLOAD_URL, headers = {
                        "If-Modified-Since": ims
                    })
                    Logger.log_verbose(msg)
                    src = urlopen(req)
                except HTTPError, e:
                    if e.code != 304:
                        raise
                    Logger.log_verbose("Already up-to-date.")
                    src = None
        if src is not None:
            force = True
            Logger.log("Downloading NIST CPE dictionary...")
            with open(xml_file, "wb") as dst:
                shutil.copyfileobj(src, dst)

        # Do we have to reload the data?
        if force:
            Logger.log("Updating the NIST CPE dictionary...")

            # Open the XML file.
            if tree is None:
                tree = etree.parse(xml_file)
            root = tree.getroot()

            # Delete the old data.
            self.__cursor.execute("DELETE FROM `cpe`;")

            # Parse the XML file and store the data into the database.
            prefix20 = "{http://cpe.mitre.org/dictionary/2.0}"
            prefix23 = "{http://scap.nist.gov/schema/cpe-extension/2.3}"
            prefixns = "{http://www.w3.org/XML/1998/namespace}"
            gen = root.find(".//%sgenerator" % prefix20)
            ##product_name = gen.find(".//%sproduct_name" % prefix20).text
            product_version = gen.find(".//%sproduct_version" % prefix20).text
            timestamp = gen.find(".//%stimestamp" % prefix20).text
            for item in root.iter(prefix20 + "cpe-item"):
                name22 = item.attrib["name"]
                name23 = item.find(".//%scpe23-item" % prefix23).attrib["name"]
                deprecated = int(
                            item.attrib.get("deprecated", "false") == "true")
                titles = {
                    t.attrib[prefixns + "lang"]: t.text
                    for t in item.iter(prefix20 + "title")
                }
                try:
                    title = titles["en-US"]
                except KeyError:
                    found = False
                    for lang, title in sorted(titles.items()):
                        if lang.startswith("en-"):
                            found = True
                            break
                    if not found:
                        title = titles[sorted(titles.keys())[0]]
                params = (name23, name22, title, deprecated)
                params = params + tuple( parse_cpe(name23) )
                self.__cursor.execute(
                    "INSERT INTO `cpe` VALUES "
                    "(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                    params
                )

            # Tell the user we're done.
            Logger.log("NIST CPE dictionary updated to: %s %s"
                       % (product_version, timestamp))


    #--------------------------------------------------------------------------
    @transactional
    def resolve(self, cpe, include_deprecated = True):
        """
        Resolve the given CPE with wildcards.

        :param CPE: CPE name.
        :type CPE: str | unicode

        :param include_deprecated: True to include deprecated names in the
            results, False otherwise.
        :type include_deprecated: bool

        :returns: Set of matching CPE names.
        :rtype: set(str|unicode)
        """

        ver = get_cpe_version(cpe).replace(".", "")
        parsed = parse_cpe(cpe)

        params = [x for x in parsed if x != "*"]
        if not params:
            return set([cpe])
        params.insert(0, cpe)

        columns = ["part", "vendor", "product", "version", "update"]
        if ver == "23":
            columns.extend([
                "edition", "language", "sw_edition",
                "target_sw", "target_hw", "other"
            ])

        query = "SELECT `name%s` FROM `cpe` WHERE " % ver
        if not include_deprecated:
            query += "`deprecated` = 0 AND "
        query += "(`name%s` = ?" % ver
        query += " OR (%s)" % " AND ".join(
            "`%s` = ?" % columns[i]
            for i in xrange(len(columns))
            if parsed[i] != "*"
        )
        query += ");"

        self.__cursor.execute(query, params)
        return set(row[0] for row in self.__cursor.fetchall())


    #--------------------------------------------------------------------------
    @transactional
    def get_title(self, cpe):
        """
        Get the user-friendly title of a CPE name.

        :param CPE: CPE name.
        :type CPE: str | unicode
        """
        ver = get_cpe_version(cpe).replace(".", "")
        query = (
            "SELECT `title` FROM `cpe` WHERE `name%s` = ? LIMIT 1;"
        ) % ver
        self.__cursor.execute(query, (cpe,))
        row = self.__cursor.fetchone()
        if not row:
            raise KeyError("CPE name not found: %s" % cpe)
        return row[0]


    #--------------------------------------------------------------------------
    @transactional
    def search(self, **kwargs):
        """
        Search the CPE database for the requested fields.
        The value '*' is assumed for missing fields.

        :keyword title: User-friendly product name.
        :type title: str | unicode

        :keyword part: CPE class. Use "a" for applications,
            "o" for operating systems or "h" for hardware devices.
        :type part: str | unicode

        :keyword vendor: Person or organization that manufactured or
            created the product.
        :type vendor: str | unicode

        :keyword product: The most common and recognizable title or name
            of the product.
        :type product: str | unicode

        :keyword version: Vendor-specific alphanumeric strings
            characterizing the particular release version of the product.
        :type version: str | unicode

        :keyword update: Vendor-specific alphanumeric strings
            characterizing the particular update, service pack, or point
            release of the product.
        :type update: str | unicode

        :keyword edition: Legacy 'edition' attribute from CPE 2.2.
        :type edition: str | unicode

        :keyword language: Language tag for the language supported in the user
            interface of the product.
        :type language: str | unicode

        :keyword sw_edition: Characterizes how the product is tailored to a
            particular market or class of end users.
        :type sw_edition: str | unicode

        :keyword target_sw: Software computing environment within which the
            product operates.
        :type target_sw: str | unicode

        :keyword target_hw: Instruction set architecture (e.g., x86) on which
            the product operates.
        :type target_hw: str | unicode

        :keyword other: Any other general descriptive or identifying
            information which is vendor- or product-specific and which
            does not logically fit in any other attribute value.
        :type other: str | unicode

        :returns: Set of matching CPE names.
        :rtype: set(str|unicode)
        """
        columns = [
            "title",
            "part", "vendor", "product", "version", "update", "edition",
            "language", "sw_edition", "target_sw", "target_hw", "other"
        ]
        if set(kwargs).difference(columns):
            raise TypeError("Unknown keyword arguments: %s"
                    % ", " % sorted(set(kwargs).difference(columns)) )
        query = "SELECT `name23` FROM `cpe` WHERE "
        query += " AND ".join(
            "`%s` LIKE ?" % field
            for field in columns
            if field in kwargs and kwargs[field] != "*"
        )
        params = [
            "%%%s%%" % kwargs[field].replace("%", "%%")
            for field in columns
            if field in kwargs and kwargs[field] != "*"
        ]
        self.__cursor.execute(query, params)
        return set(row[0] for row in self.__cursor.fetchall())
