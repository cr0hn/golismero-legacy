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


# Fix the module load path.
if __name__ == "__main__":
    import os, sys
    from os import path
    root = path.split(path.abspath(__file__))[0]
    if not root:  # if it fails use cwd instead
        root = path.abspath(os.getcwd())
    root = path.abspath(path.join(root, ".."))
    thirdparty_libs = path.join(root, "thirdparty_libs")
    if path.exists(thirdparty_libs):
        sys.path.insert(0, thirdparty_libs)
        sys.path.insert(0, root)


text = """The loop in álines 13 and 14 is how we send the data off to the reducers. The WMR system for Python3 defines a class Wmr that includes a class method emit() for producing key-value pairs to be forwarded (via shuffling) to a reducer. Wmr.emit() requires two string arguments, so both foundword and counts[foundword] are being interpreted as strings in line 14.
The loop in lines 13 and 14 is how we send the data off to the reducers. The WMR system for Python3 defines a class Wmr that includes a class method emit() for producing key-value pairs to be forwarded (via shuffling) to a reducer. Wmr.emit() requires two string arguments, so both foundword and counts[foundword] are being interpreted as strings in line 14.
The loop in lines 13 and 14 is how we send the data off to the reducers. The WMR system for Python3 defines a class Wmr that includes a class method emit() for producing key-value pairs to be forwarded (via shuffling) to a reducer. Wmr.emit() requires two string arguments, so both foundword and counts[foundword] are being interpreted as strings in line 14.
The loop in lines 13 and 14 is how we send the data off to the reducers. The WMR system for Python3 defines a class Wmr that includes a class method emit() for producing key-value pairs to be forwarded (via shuffling) to a reducer. Wmr.emit() requires two string arguments, so both foundword and counts[foundword] are being interpreted as strings in line 14."""


from re import findall
import timeit
import difflib
from diff_match_patch import diff_match_patch

def unotext():
    """"""
    count = dict()
    count['\n'] = 0
    count[' '] = 0
    count['total'] = 0
    for a in text:
        if a in count:
            count[a] += 1
        else:
            count['total'] += 1

    print "Lineas: %s" % str(count['\n'])
    print "Palabras: %s" % str(count[' '])
    print "Total: %s" % str(count['total'])
    print ""

def dostext():
    """"""
    print ""
    print "Lineas 2: %s" % text.count('\n')
    print "Palabras 2: %s" % str(len(findall("\S+",text)))
    print "Total 2: %s" % str(len(text))





text1 = None
text2 = None

#----------------------------------------------------------------------
def difflib_diff():
    """"""
    global text1, text2
    a = difflib.SequenceMatcher(None, text1, text2)
    print "DiffLib Ratio: " + str(a.ratio())
    #print "DiffLib Quick: " + str(a.quick_ratio())


#----------------------------------------------------------------------
def google_diff():
    """"""
    global text1, text2
    a = diff_match_patch()
    diffs = a.diff_main(text1, text2)
    test1 = a.diff_levenshtein(diffs)

    print "Google Test1: " + str(abs(( (float(test1)/float(len(text2))))))

#----------------------------------------------------------------------
def mezcla():
    global text1, text2

    r = abs(len(text1) - len(text2))
    print "Resta: " + str(r)

    if r > (200 * 5):
        a = difflib.SequenceMatcher(None, text1, text2)
        print "DiffLib Ratio: " + str(a.ratio()*100)
    else:
        a = diff_match_patch()
        diffs = a.diff_main(text1, text2)
        test1 = float(a.diff_levenshtein(diffs))

        m_len_text2 = float(len(text2))

        #t = abs(((float(len(text2))-float(test1)/float(len(text2))))) * 100
        t = (abs((m_len_text2-test1))/m_len_text2) * 100

        print "Google Test1: " + str(t)



if __name__=='__main__':
    from time import time
    from sys import exit

    a=list()
    s1=time()
    for x in xrange(2600):
        a.extend([x,x,x,x,x,x])

    print "Tiempo append: " + (str(time() - s1))

    b=set()
    s1=time()
    for x in xrange(2600):
        b.update([x,x,x,x,x,x])

    print "Tiempo set: " + (str(time() - s1))


    exit(0)




    text1 = open("diff_text1.txt").read()
    text2 = open("diff_text2.txt").read()

    print
    print "difflib time:     " + str(timeit.timeit("difflib_diff()", setup="from __main__ import difflib_diff", number=2))
    print
    print "Google Diff time: " + str(timeit.timeit("google_diff()", setup="from __main__ import google_diff", number=2))
    print
    print "Mezcla time: " + str(timeit.timeit("mezcla()", setup="from __main__ import mezcla", number=2))
