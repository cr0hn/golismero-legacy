#!/usr/bin/python
# -*- coding: utf-8 -*-

c="""
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

import timeit

def test_forx():
    a = ''.join(('%s' % str(i) for i in xrange(99999) ))

def test_map():
    #a = ''.join(map(lambda x: '%s' % str(x), xrange(99999)))
    a = ''.join(['%s' % str(i) for i in xrange(99999)])

def test_forx_filter():
    #a = ''.join(['%s' % str(i) for i in c if i =="a" ])
    a = ''.join([i.lower() for i in c if i =="a" ])

def test_map_filter():
    #a = ''.join(filter(lambda x: x == "a" , c))
    a = ''.join(map(str.lower , c))




print
print "'test_forx' time: %s s" % str(timeit.timeit("test_forx()", setup="from __main__ import test_forx", number=1))
print
print "'test_map' time: %s s" % str(timeit.timeit("test_map()", setup="from __main__ import test_map", number=1))
print
print "'test_forx_filter' time: %s s" % str(timeit.timeit("test_forx_filter()", setup="from __main__ import test_forx_filter", number=1))
print
print "'test_map_filter' time: %s s" % str(timeit.timeit("test_map_filter()", setup="from __main__ import test_map_filter", number=1))
