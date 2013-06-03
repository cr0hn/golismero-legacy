#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
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


# Fix the module path for the tests.
import sys
import os
from os import path
try:
    _FIXED_PATH_
except NameError:
    here = path.split(path.abspath(__file__))[0]
    if not here:  # if it fails use cwd instead
        here = path.abspath(os.getcwd())
    golismero = path.join(here, "..")
    thirdparty_libs = path.join(golismero, "thirdparty_libs")
    if path.exists(thirdparty_libs):
        sys.path.insert(0, thirdparty_libs)
        sys.path.insert(0, golismero)
    _FIXED_PATH_ = True


# Imports.
from golismero.api.data import Data
from golismero.api.data.information.text import Text
from golismero.api.data.resource.url import Url
from golismero.api.data.vulnerability.information_disclosure.url_disclosure import UrlDisclosure
from golismero.api.text.text_utils import generate_random_string
from golismero.database.auditdb import AuditDB
import time
import os


# Tests the audit DB for consistency.
def test_auditdb_consistency():
    mem = AuditDB("fake_audit", "memory://")
    disk = AuditDB("fake_audit", "sqlite://fake_audit.db")
    try:

        print "Testing consistency between in-memory and disk databases..."
        for x in xrange(100):
            key = generate_random_string(10)
            data = generate_random_string(100)
            helper_test_auditdb_consistency(mem, key, data)
            helper_test_auditdb_consistency(disk, key, data)

    finally:
        try:
            print "Cleaning up..."
            mem.close()
            del mem
        finally:
            try:
                disk.close()
                del disk
            finally:
                os.unlink("fake_audit.db")

def helper_test_auditdb_consistency(db, key, data):
    d1 = Url("http://www.example.com/" + key)
    d2 = Text(data)
    d3 = UrlDisclosure(d1)
    d1.add_resource(d2)
    db.add_data(d1)
    db.add_data(d2)
    db.add_data(d3)
    assert db.has_data_key(d1.identity)
    assert db.has_data_key(d2.identity)
    assert db.has_data_key(d3.identity)
    assert db.has_data_key(d1.identity, d1.data_type)
    assert db.has_data_key(d2.identity, d2.data_type)
    assert db.has_data_key(d3.identity, d3.data_type)
    d1p = db.get_data(d1.identity)
    d2p = db.get_data(d2.identity)
    d3p = db.get_data(d3.identity)
    assert d1p is not None
    assert d2p is not None
    assert d3p is not None
    assert d1p.identity == d1.identity
    assert d2p.identity == d2.identity
    assert d3p.identity == d3.identity
    assert d1p.links == d1.links
    assert d2p.links == d2.links
    assert d3p.links == d3.links


# Benchmark for the disk database.
def test_auditdb_stress():

    print "Stress testing the disk database..."
    helper_auditdb_stress(10)
    helper_auditdb_stress(20)
    helper_auditdb_stress(30)
    helper_auditdb_stress(100)
    helper_auditdb_stress(1000)

def helper_auditdb_stress(n):
    disk = AuditDB("fake_audit", "sqlite://fake_audit.db")
    try:
        print "  Testing %d elements..." % (n * 3)
        t1 = time.time()

        print "  -> Writing..."
        for x in xrange(n):
            d1 = Url("http://www.example.com/" + generate_random_string())
            d2 = Text(generate_random_string())
            d3 = UrlDisclosure(d1)
            d1.add_resource(d2)
            disk.add_data(d1)
            disk.add_data(d2)
            disk.add_data(d3)
        t2 = time.time()

        print "  -- Reading..."
        keys = disk.get_data_keys()
        assert len(keys) == (n * 3)
        for key in keys:
            assert disk.has_data_key(key)
            data = disk.get_data(key)
            assert data is not None
        keys = disk.get_data_keys(Data.TYPE_INFORMATION)
        assert len(keys) == n
        for key in keys:
            assert disk.has_data_key(key, Data.TYPE_INFORMATION)
            data = disk.get_data(key, Data.TYPE_INFORMATION)
            assert data is not None
            assert data.data_type == Data.TYPE_INFORMATION
            assert isinstance(data, Text)
        keys = disk.get_data_keys(Data.TYPE_RESOURCE)
        assert len(keys) == n
        for key in keys:
            assert disk.has_data_key(key, Data.TYPE_RESOURCE)
            data = disk.get_data(key, Data.TYPE_RESOURCE)
            assert data is not None
            assert data.data_type == Data.TYPE_RESOURCE
            assert isinstance(data, Url)
        keys = disk.get_data_keys(Data.TYPE_VULNERABILITY)
        assert len(keys) == n
        for key in keys:
            assert disk.has_data_key(key, Data.TYPE_VULNERABILITY)
            data = disk.get_data(key, Data.TYPE_VULNERABILITY)
            assert data is not None
            assert data.data_type == Data.TYPE_VULNERABILITY
            assert isinstance(data, UrlDisclosure)
        t3 = time.time()

        print "  <- Deleting..."
        for key in keys:
            disk.remove_data(key)
        t4 = time.time()

        print "  Write time: %d seconds (%f seconds per element)" % (t2 - t1, (t2 - t1) / (n * 3.0))
        print "  Read time: %d seconds (%f seconds per element)" % (t3 - t2, (t3 - t2) / (n * 3.0))
        print "  Delete time: %d seconds (%f seconds per element)" % (t4 - t3, (t4 - t3) / (n * 3.0))
        print "  Total time: %d seconds (%f seconds per element)" % (t4 - t1, (t4 - t1) / (n * 3.0))

    finally:
        print "Cleaning up..."
        try:
            disk.close()
            del disk
        finally:
            os.unlink("fake_audit.db")


# Run all tests from the command line.
if __name__ == "__main__":
    test_auditdb_consistency()
    test_auditdb_stress()
