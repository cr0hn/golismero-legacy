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

# Fix the module path for the test.
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

# Run the test from the command line.
if __name__ == "__main__":

    # Disable the magic of the colorizer module.
    import colorizer
    colorizer.deinit()

    # This automatically begins testing every module imported from now on.
    os.environ['PYCHECKER'] = ('--stdlib --keepgoing --limit 500 '
                               '--blacklist BeautifulSoup,colorizer'
                               ',decorator,diff_match_patch,distutils,django'
                               ',httpparser,nltk,repoze'
                               ',requests,requests_ntlm,_socket,ssl,_ssl'
                               ',select,_tkinter,yaml')
    import pychecker.checker # Not included in thirdparty_libs on purpose!

    # Capture the output and error logs.
    with open(path.join(here, "pychecker.log"), "w+") as fd:
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = fd, fd

            # Look for Python files.
            sources = path.join(golismero, "golismero")
            sources = path.abspath(sources)
            print >>old_out, "Target: %s" % sources
            assert path.isdir(sources)
            for root, folders, files in os.walk(sources):
                for name in files:
                    if name == "__init__.py":
                        name = ".py"
                    elif name.startswith("_") or not name.endswith(".py"):
                        continue

                    # Get the module name from its file path.
                    name = name[:-3]
                    name = path.join(root, name)
                    name = path.abspath(name)
                    name = name[len(sources):]
                    if name.startswith(path.sep):
                        name = name[1:]
                    name = name.replace(path.sep, ".")
                    if name.startswith("."):
                        name = name[1:]
                    name = "golismero." + name
                    if name.endswith("."):
                        name = name[:-1]
                    print >>old_out, "Analyzing %s" % name

                    # Load the module. This triggers PyChecker.
                    module = __import__(name, globals(), locals(), ['*'])

                    # Flush the text output.
                    sys.stdout.flush()
                    sys.stderr.flush()

        # Stop capturing the output and error logs.
        finally:
            sys.stdout, sys.stderr = old_out, old_err
