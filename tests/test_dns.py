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


# Imports
from golismero.api.net.dns import *
from golismero.api.data.information.dns import *


def test_all_registers():

    d = DNS()
    HOSTS = ["twitter.com", "bing.com", "tuenti.es", "facebook.com", "google.com", "terra.es"]

    print

    for l_host in HOSTS:

        print "Host: %s" % l_host
        print "^" * (len(l_host) + 7)

        for l_dns_type in DnsRegister.DNS_TYPES:
            print "   Type: " + l_dns_type
            print "   %s" % ("=" * (len(l_dns_type ) + 6))

            r = d.resolve(l_host, l_dns_type)

            for i, c in enumerate(r):
                l_properties = [x for x in c.__dict__ if "__" in x]

                for l_prop in l_properties:
                    l_p = l_prop.find("__") + 2
                    print "     - %s: %s" % (l_prop[l_p:], getattr(c, l_prop))

            print "   %s" % ("-" * 30)

if __name__ == "__main__":
    test_all_registers()
