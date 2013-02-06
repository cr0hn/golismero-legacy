#!/usr/bin/python

# -*- coding: utf-8 -*-
"""
GoLismero 2.0 - The web kniffe.

Copyright (C) 2011-2013 - Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com

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

__author__ = "Daniel Garcia Garcia a.k.a cr0hn (@ggdaniel) - dani@iniqua.com"
__copyright__ = "Copyright 2011-2013 - GoLismero project"
__credits__ = ["Daniel Garcia Garcia a.k.a cr0hn (@ggdaniel)", "Mario Vilas (@Mario_Vilas"]
__maintainer__ = "cr0hn"
__email__ = "golismero.project@gmail.com"
__license__ = "GPL"
__version__ = "2.0.0"



import argparse
from sys import version_info,exit
from starter import launcher
from core.main.commonstructures import GlobalParams
from core.plugins.priscillapluginmanager import PriscillaPluginManager
from core.main.ioconsole import IO


#----------------------------------------------------------------------
def Credits():

	print ""
	print "|--------------------------------------------------|"
	print "| GoLismero - The Web Knife.                       |"
	print "|                                                  |"
	print "| Daniel Garcia a.k.a cr0hn - dani@iniqua.com)     |"
	print "|--------------------------------------------------|"
	print ""

#
# Start of program
#
if __name__ == '__main__':

	# Check for python version
	if version_info < (2, 7):
		print "\n[!] you must use python 2.7 or greater\n"
		sys.exit(1)

	# Load plugin engine
	Credits()

	#------------------------------------------------------------
	# Configure command line parser
	parser = argparse.ArgumentParser()
	gr1 = parser.add_argument_group("Main options")
	gr1.add_argument('-t', action='append', dest='target', help='target web site.')
	gr1.add_argument('-M', action='store', dest='runmode', help='run mode. Default=StandAlone ', default= "StandAlone", choices= ["standAlone", "cloudServer", "cloudClient" ])
	gr1.add_argument('-I', action='store', dest='interface', help='user interface mode', default= "console", choices= ["console"])
	gr1.add_argument('-a', action='store', dest='auditname', help='customize the audit name')

	gr_plugins = parser.add_argument_group("Plugins")
	gr_plugins.add_argument('-P', '--plugin-enabled', action='store', dest='enabledplugins', help="list of plugins to run. Default=all", )
	gr_plugins.add_argument('--plugin-list', action='store_true', help="list available plugins")
	gr_plugins.add_argument('--plugin-info', action='store', dest="plugin_name", help="list available plugins")



	P = parser.parse_args()

	#
	# store command line options
	#
	cmdParams = GlobalParams()
	cmdParams.Target = P.target
	cmdParams.AuditName = P.auditname

	#------------------------------------------------------------
	# Prepare run mode
	m_runMode = P.runmode.lower()
	getattr(GlobalParams.RUN_MODE, m_runMode)
	if m_runMode == "standalone":
		cmdParams.RunMode = GlobalParams.RUN_MODE.standalone
	elif m_runMode == "cloudclient":
		cmdParams.RunMode = GlobalParams.RUN_MODE.cloudclient
	elif m_runMode == "cloudserver":
		cmdParams.RunMode = GlobalParams.RUN_MODE.cloudserver

	#------------------------------------------------------------
	# Prepare user interface
	m_userInterface = P.interface
	if m_userInterface == "console":
		cmdParams.UserInterface = GlobalParams.USER_INTERFACE.console

	#------------------------------------------------------------
	# List plugins?
	if P.plugin_list:
		IO.log("Plugin list\n-----------\n")
		for i in PriscillaPluginManager().get_all_plugins_descriptions():
			IO.log("- %s: %s\n" % (i[0], i[1]))
		IO.log("\n")
		exit(0)



	#------------------------------------------------------------
	# Display plugin info
	if P.plugin_name:
		try:
			m_plugin_info = PriscillaPluginManager().get_plugin(P.plugin_name)
			if m_plugin_info:
				IO.log("Information of plugin: '%s'\n------------\n" % m_plugin_info.name)
				IO.log(m_plugin_info.plugin_object.display_help())
				IO.log("\n")
			else:
				IO.log("[!] Plugin name not found\n")
			exit(0)
		except ValueError:
			IO.log("[!] Plugin name not found\n")
			exit(1)
		except Exception,e:
			IO.log("[!] Error recovering plugin info: %s\n" % e.message)
			exit(1)


	#------------------------------------------------------------
	# Call to API
	launcher(cmdParams)

