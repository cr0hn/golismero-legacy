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

import timeit

class TestClas(object):
    pass

#----------------------------------------------------------------------
def method_instaceof(num):

    p = TestClas()
    for x in xrange(num):
        if isinstance(p, TestClas):
            pass

#----------------------------------------------------------------------
def method_type(num):

    p = TestClas()
    for x in xrange(num):
        if type(p) == type(TestClas):
            pass

if __name__ == "__main__":
    print ""
    n = 20
    print "'instanceof' with %s loops: %s s" % (str(n), str(timeit.timeit("benchmark_instanceof.method_instaceof(%s)" % str(n), setup="import benchmark_instanceof", number=n)))
    print "'type' with %s loops: %s s" % (str(n), str(timeit.timeit("benchmark_instanceof.method_type(%s)" % str(n), setup="import benchmark_instanceof", number=n)))
    print ""
    n = 50
    print "'instanceof' with %s loops: %s s" % (str(n), str(timeit.timeit("benchmark_instanceof.method_instaceof(%s)" % str(n), setup="import benchmark_instanceof", number=n)))
    print "'type' with %s loops: %s s" % (str(n), str(timeit.timeit("benchmark_instanceof.method_type(%s)" % str(n), setup="import benchmark_instanceof", number=n)))
    print ""
    n = 100
    print "'instanceof' with %s loops: %s s" % (str(n), str(timeit.timeit("benchmark_instanceof.method_instaceof(%s)" % str(n), setup="import benchmark_instanceof", number=n)))
    print "'type' with %s loops: %s s" % (str(n), str(timeit.timeit("benchmark_instanceof.method_type(%s)" % str(n), setup="import benchmark_instanceof", number=n)))
    print ""
