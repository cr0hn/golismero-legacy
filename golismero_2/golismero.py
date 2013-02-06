#!/usr/bin/python

# -*- coding: utf-8 -*-
"""
GoLismero 2.0 - The web knife.

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

__author__ = "Daniel Garcia Garcia a.k.a cr0hn - dani@iniqua.com"
__copyright__ = "Copyright 2011-2013 - GoLismero project"
__credits__ = ["Daniel Garcia Garcia a.k.a cr0hn"]
__maintainer__ = "cr0hn"
__email__ = "golismero.project@gmail.com"
__license__ = "GPL"
__version__ = "2.0.0"



import argparse
from sys import version_info,exit
from starter import launcher
from core.main.commonstructures import GlobalParams
from core.plugins.priscillapluginmanager import PriscillaPluginManager
from core.main.ioconsole import IOConsole


#----------------------------------------------------------------------
# Start of program
if __name__ == '__main__':

    # Show program banner
    print ""
    print "|--------------------------------------------------|"
    print "| GoLismero - The Web Knife.                       |"
    print "|                                                  |"
    print "| Daniel Garcia a.k.a cr0hn - dani@iniqua.com)     |"
    print "|--------------------------------------------------|"
    print ""

    # Check for python version
    if version_info < (2, 7):
        print "\n[!] you must use python 2.7 or greater\n"
        sys.exit(1)

    # Configure command line parser
    parser = argparse.ArgumentParser()

    gr_main = parser.add_argument_group("Main options")
    gr_main.add_argument('-t', action='append', dest='targets', help='target web site, use multiple times for many targets')
    gr_main.add_argument('-M', action='store', dest='run_mode', help='run mode [default: Standalone]', default="Standalone", choices=[x.title() for x in GlobalParams.RUN_MODE._values.keys()])
    gr_main.add_argument('-I', action='store', dest='user_interface', help='user interface mode [default: Console]', default="console", choices=[x.title() for x in GlobalParams.USER_INTERFACE._values.keys()])
    gr_main.add_argument('-a', action='store', dest='audit_name', help='customize the audit name')

    gr_plugins = parser.add_argument_group("Plugins")
    gr_plugins.add_argument('-P', '--plugin-enabled', action='store', dest='plugins', help="list of plugins to run [default: all]", )
    gr_plugins.add_argument('--plugin-list', action='store_true', help="list available plugins")
    gr_plugins.add_argument('--plugin-info', action='store', dest="plugin_name", help="show plugin info")


    # Parse command line options
    try:
        cmdParams = GlobalParams.from_cmdline( parser.parse_args() )
    except Exception, e:
        parser.error(str(e))



    #------------------------------------------------------------
    # List plugins
    if P.plugin_list:
        IOConsole.log("Plugin list\n-----------\n")
        for i in PriscillaPluginManager().get_all_plugins():
            IOConsole.log("- %s: %s\n" % (i[0], i[1]))
        IOConsole.log("\n")
        exit(0)



    #------------------------------------------------------------
    # Display plugin info
    if P.plugin_name:
        try:
            m_plugin_info = PriscillaPluginManager().get_plugin(P.plugin_name)
            if m_plugin_info:
                IOConsole.log("Information of plugin: '%s'\n------------\n" % m_plugin_info.name)
                IOConsole.log(m_plugin_info.plugin_object.display_help())
                IOConsole.log("\n")
            else:
                IOConsole.log("[!] Plugin name not found\n")
            exit(0)
        except ValueError:
            IOConsole.log("[!] Plugin name not found\n")
            exit(1)
        except Exception,e:
            IOConsole.log("[!] Error recovering plugin info: %s\n" % e.message)
            exit(1)



    #------------------------------------------------------------
    # Launch GoLismero
    launcher(cmdParams)
