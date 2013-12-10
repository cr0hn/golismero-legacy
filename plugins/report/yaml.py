#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

# Horrible hack to load a class from another plugin.
# TODO we really should put this as part of the API!
import sys
from os.path import abspath, split
cwd = abspath(split(__file__)[0])
sys.path.insert(0, cwd)
old_mod = sys.modules.pop("json", None)
try:
    from json import JSONOutput
finally:
    sys.path.remove(cwd)
    if "json" in sys.modules:
        sys.modules["json_output_plugin"] = sys.modules["json"]
        del sys.modules["json"]
    if old_mod is not None:
        sys.modules["json"] = old_mod
del cwd

from StringIO import StringIO

from yaml import dump
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper


#------------------------------------------------------------------------------
class YAMLOutput(JSONOutput):
    """
    Dumps the output in YAML format.
    """

    EXTENSION = ".yaml"


    #--------------------------------------------------------------------------
    def serialize_report(self, output_file, report_data):
        with open(output_file, "wb") as fp:
            dump(report_data, fp, Dumper=Dumper)


    #--------------------------------------------------------------------------
    def test_data_serialization(self, data):
        fp = StringIO()
        dump(data, fp, Dumper=Dumper)
