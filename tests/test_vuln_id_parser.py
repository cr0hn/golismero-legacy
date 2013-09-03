#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
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


from golismero.api.text.text_utils import extract_vuln_ids


_test_case = """
Testing BID: let's use 7 examples: BID-123, BID: 321, BID:456; BUGTRAQ: 1234, BUGTRAQ:4567, BUGTRAQ-4321;
  and finally BUGTRAQ ID: 12345 and BUGTRAQ ID:45678.
Testing CVE with CVE-1234-4321 and CVE-1234-12345, the new format.
Testing CWE with CWE-1234-1234. But CWE-1234-12345 must not match.
Testing OSVDB: using 3 examples. The first being OSVDB: 1 and the second being OSVDB-0. The third is: OSVDB:2
Testing SA: with 6 IDs, namely: SA-0, SA:1, SA: 2, SECUNIA-3, SECUNIA:4 and SECUNIA: 5.
Testing SECTRACK: try 3 samples; SECTRACK-0, SECTRACK: 1 and SECTRACK:2.
Testing XF: we have 4 samples now. XF:this-is-valid(123), XF: this-is-valid-too (321), XF: (55) and XF:(66).
  These should not match: XF-5, XF: 6 nor XF: this is not valid (7).

Now let's try breaking the parser with newlines! :)

BID:
890

OSVDB:
1234

SA:
9999

SECTRACK:
9876

XF:
this-is-broken (10)

XF:
this-is-broken
(11)

XF:
12

And now let's put some duplicates to see if they're being filtered:
CVE-1234-4321 CVE-1234-4321 CVE-1234-4321 CVE-1234-4321 CVE-1234-4321
"""

_test_case_solution = {
    "bid": ["BID-123", "BID-1234", "BID-12345", "BID-321", "BID-4321", "BID-456", "BID-4567", "BID-45678"],
    "cve": ["CVE-1234-12345", "CVE-1234-4321"],
    "cwe": ["CWE-1234-1234"],
    "osvdb": ["OSVDB-0", "OSVDB-1", "OSVDB-2"],
    "sa": ["SA-0", "SA-1", "SA-2", "SA-3", "SA-4", "SA-5"],
    "sectrack": ["SECTRACK-0", "SECTRACK-1", "SECTRACK-2", ],
    "xf": ["XF-123", "XF-321", "XF-55", "XF-66"],
}

def test_vuln_id_parser():
    print "Testing the vulnerability ID extractor parser..."
    ##from pprint import pprint
    ##print "-" * 79
    ##pprint(_test_case_solution)
    ##print "-" * 79
    ##pprint(extract_vuln_ids(_test_case))
    ##print "-" * 79
    assert extract_vuln_ids(_test_case) == _test_case_solution


if __name__ == "__main__":
    test_vuln_id_parser()
