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

from plugins.testing.scan.openvas_plugin.openvas_lib import OpenvasManager

host         = "192.168.0.208"
user         = "admin"
password     = "admin"
target       = "192.168.0.194"
config       = "Full and fast"


#----------------------------------------------------------------------
def launch_scan_test():

	manager = OpenvasManager.connect(host, user, password)
	manager.launch_scan(target)

def get_info_test():
	manager = OpenvasManager.connect(host, user, password)
	print "All scans"
	print manager.get_all_scans
	print "Finished scans"
	print manager.get_finished_scans
	print "running scans"
	print manager.get_running_scans
	print "Available profiles"
	print manager.get_profiles


if __name__ == "__main__":
	launch_scan_test()
	get_info_test()