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


# Import the base data types first.
from golismero.api.data import Data
from golismero.api.data.information import Information
from golismero.api.data.resource import Resource
from golismero.api.data.vulnerability import Vulnerability


# Helper function to test for duplicate type ID numbers.
def helper_test_dupes(clazz, prefix, numbers):
    print "Testing %s" % clazz.__name__
    n_first = prefix + "FIRST"
    n_last = prefix + "LAST"
    n_unknown = prefix + "UNKNOWN"
    first = getattr(clazz, n_first)
    last = getattr(clazz, n_last)
    unknown = getattr(clazz, n_unknown)
    assert type(first) is int
    assert type(last) is int
    assert unknown is 0
    assert first > 0
    assert last > 0
    assert first < last
    for name in dir(clazz):
        if not name.startswith(prefix) or name in (n_first, n_last, n_unknown):
            continue
        value = getattr(clazz, name)
        assert type(value) is int
        assert value not in numbers
        assert first <= value <= last
        numbers.add(value)


# This test will make sure the data type ID numbers aren't repeated.
def test_data_type_unique_ids():

    # Test the base types.
    helper_test_dupes(Data, "TYPE_", set())

    # Test the subtypes.
    numbers = set()
    helper_test_dupes(Information, "INFORMATION_", numbers)
    helper_test_dupes(Resource, "RESOURCE_", numbers)

    # Make sure the base vulnerability type is "generic".
    assert Vulnerability.vulnerability_type == "generic"


# Helper function to load all data types.
def helper_load_data_types():
    data_types = []

    # Look for Python files in golismero/api/data.
    api_data = path.join(golismero, "golismero", "api", "data")
    api_data = path.abspath(api_data)
    print "Looking for modules in %s" % api_data
    assert path.isdir(api_data)
    for root, folders, files in os.walk(api_data):
        for name in files:
            if name.startswith("_") or not name.endswith(".py"):
                continue

            # Get the module name from its file path.
            name = name[:-3]
            name = path.join(root, name)
            name = path.abspath(name)
            name = name[len(api_data):]
            if name.startswith(path.sep):
                name = name[1:]
            name = name.replace(path.sep, ".")
            name = "golismero.api.data." + name
            print "Loading %s" % name

            # Load the module and extract all its data types.
            module = __import__(name, globals(), locals(), ['*'])
            for name in dir(module):
                if name.startswith("_") or name in (
                    "Data",
                    "Information",
                    "Resource",
                    "Vulnerability",
                ):
                    continue
                clazz = getattr(module, name)
                if isinstance(clazz, type) and issubclass(clazz, Data) and clazz not in data_types:
                    print "Found %s" % name
                    data_types.append(clazz)

    return data_types


# This test will make sure all data types have a correct type ID.
def test_data_types_have_id():
    data_types = helper_load_data_types()
    assert len(data_types) > 0
    for clazz in data_types:
        print "Testing %s" % clazz.__name__
        assert type(clazz.data_type) == int
        if issubclass(clazz, Information):
            assert clazz.data_type == Data.TYPE_INFORMATION
            assert type(clazz.information_type) == int
            assert clazz.information_type != Information.INFORMATION_UNKNOWN
            assert Information.INFORMATION_FIRST <= clazz.information_type <= Information.INFORMATION_LAST
        elif issubclass(clazz, Resource):
            assert clazz.data_type == Data.TYPE_RESOURCE
            assert type(clazz.resource_type) == int
            assert clazz.resource_type != Resource.RESOURCE_UNKNOWN
            assert Resource.RESOURCE_FIRST <= clazz.resource_type <= Resource.RESOURCE_LAST
        elif issubclass(clazz, Vulnerability):
            assert clazz.data_type == Data.TYPE_VULNERABILITY
            assert type(clazz.vulnerability_type) == str
            assert clazz.vulnerability_type != "generic"
        else:
            assert False  # A new base data class?


# Run all tests from the command line.
if __name__ == "__main__":
    test_data_type_unique_ids()
    test_data_types_have_id()
