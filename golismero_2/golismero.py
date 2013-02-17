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

__author__ = "Daniel Garcia Garcia a.k.a cr0hn (@ggdaniel) - dani@iniqua.com"
__copyright__ = "Copyright 2011-2013 - GoLismero project"
__credits__ = ["Daniel Garcia Garcia a.k.a cr0hn (@ggdaniel)", "Mario Vilas (@Mario_Vilas"]
__maintainer__ = "cr0hn"
__email__ = "golismero.project@gmail.com"
__license__ = "GPL"
__version__ = "2.0.0"



import argparse
import textwrap
from sys import version_info, exit
from starter import launcher
from core.main.commonstructures import GlobalParams
from core.managers.priscillapluginmanager import PriscillaPluginManager
from core.api.logger import Logger


#----------------------------------------------------------------------
# Start of program
if __name__ == '__main__':

    # Show program banner
    print ""
    print "|--------------------------------------------------|"
    print "| GoLismero - The Web Knife.                       |"
    print "|                                                  |"
    print "| Daniel Garcia a.k.a cr0hn - dani@iniqua.com      |"
    print "|--------------------------------------------------|"
    print ""

    # Check for python version
    if version_info < (2, 7):
        print "\n[!] you must use python 2.7 or greater\n"
        sys.exit(1)

    # Configure command line parser
    parser = argparse.ArgumentParser()
    gr_main = parser.add_argument_group("main options")
    parser.add_argument('targets', metavar='TARGET', help='one or more target web sites', nargs='+')
    gr_main.add_argument('-M', action='store', dest='run_mode', help='run mode [default: Standalone]', default="Standalone", choices=[x.title() for x in GlobalParams.RUN_MODE._values.keys()])
    gr_main.add_argument('-I', action='store', dest='user_interface', help='user interface mode [default: Console]', default="console", choices=[x.title() for x in GlobalParams.USER_INTERFACE._values.keys()])
    gr_main.add_argument('-v', action='store_true', dest='verbose', help='set verbose mode')
    gr_main.add_argument('-vv', action='store_true', dest='verbose_more', help='increase verbosity')

    gr_net = parser.add_argument_group("network")
    gr_net.add_argument("-t", action="store", dest="max_connections", help="maximun number of simultaneous connections by host.", default=3)
    gr_net.add_argument("--no-subdomains", action="store_false", dest="include_subdomains", help="no include subdomains of selected host", default=True)

    gr_audit = parser.add_argument_group("audit")
    gr_audit.add_argument('--audit-name', action='store', dest='audit_name', help='customize the audit name')
    gr_audit.add_argument('--max-process', action='store', dest='max_process', help='maximun number of plugins to run concurrently.', default="4")

    gr_plugins = parser.add_argument_group("plugins")
    gr_plugins.add_argument('-P', '--plugin-enabled', action='append', dest='plugins', help="list of plugins to run [default: all]", default = ["all"] )
    gr_plugins.add_argument('--plugin-list', action='store_true', help="list available plugins")
    gr_plugins.add_argument('--plugin-info', action='store', dest="plugin_name", help="show plugin info")


    # Parse command line options
    try:
        P = parser.parse_args()
        cmdParams = GlobalParams.from_cmdline( P )
    except Exception, e:
        parser.error(str(e))


    #------------------------------------------------------------
    # List plugins
    if P.plugin_list:
        Logger.log("Plugin list\n-----------\n")
        for i in PriscillaPluginManager().get_all_plugins():
            Logger.log("- %s: %s\n" % (i[0], i[1]))
        Logger.log("\n")
        exit(0)

    #------------------------------------------------------------
    # Configure logger
    if P.verbose:
        Logger.configure(logLevel=Logger.STANDARD)
    if P.verbose_more:
        Logger.configure(logLevel=Logger.MORE_VERBOSE)

    #------------------------------------------------------------
    # Display plugin info
    if P.plugin_name:
        try:
            m_plugin_info = PriscillaPluginManager().get_plugin(P.plugin_name)
            if m_plugin_info:
                message = m_plugin_info.plugin_object.display_help()
                message = textwrap.dedent(message)
                Logger.log("Information of plugin: '%s'\n------------\n" % m_plugin_info.name)
                Logger.log(message)
                Logger.log("\n")
            else:
                Logger.log("[!] Plugin name not found\n")
            exit(0)
        except KeyError:
            Logger.log("[!] Plugin name not found\n")
            exit(1)
        except ValueError:
            Logger.log("[!] Plugin name not found\n")
            exit(1)
        except Exception,e:
            Logger.log("[!] Error recovering plugin info: %s\n" % e.message)
            exit(1)



    #------------------------------------------------------------
    # Launch GoLismero
    launcher(cmdParams)
