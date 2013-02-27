#!/usr/bin/env python
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

__all__ = ["launcher"]


#----------------------------------------------------------------------
# Metadata

__author__ = "Daniel Garcia Garcia a.k.a cr0hn (@ggdaniel) - dani@iniqua.com"
__copyright__ = "Copyright 2011-2013 - GoLismero project"
__credits__ = ["Daniel Garcia Garcia a.k.a cr0hn (@ggdaniel)", "Mario Vilas (@Mario_Vilas"]
__maintainer__ = "cr0hn"
__email__ = "golismero.project@gmail.com"
__license__ = "GPL"
__version__ = "2.0.0"


#----------------------------------------------------------------------
# Show program banner
def show_banner():
    print
    print "|--------------------------------------------------|"
    print "| GoLismero - The Web Knife                        |"
    print "| Contact: golismero.project@gmail.com             |"
    print "|                                                  |"
    print "| Daniel Garcia a.k.a cr0hn (@ggdaniel)            |"
    print "| Mario Vilas (@mario_vilas)                       |"
    print "|--------------------------------------------------|"
    print


#----------------------------------------------------------------------
# Python version check.
# We must do it now before trying to import any more modules.

import sys
from sys import version_info, exit
if __name__ == "__main__":
    if version_info < (2, 7) or version_info > (3, 0):
        show_banner()
        print "[!] You must use Python version 2.7"
        exit(1)


#----------------------------------------------------------------------
# Make sure the modules path points to the core first,
# then the third party libs, and then the system.

import os
from os import path
try:
    _FIXED_PATH_
except NameError:
    where = path.split(path.abspath(__file__))[0]
    if not where:  # if it fails use cwd instead
        where = path.abspath(os.getcwd())
    sys.path.insert(0, path.join(where, "thirdparty_libs"))
    sys.path.insert(0, where)
    _FIXED_PATH_ = True


#----------------------------------------------------------------------
# Imported modules

import argparse
import datetime
import textwrap

from core.api.logger import Logger
from core.main.commonstructures import GlobalParams
from core.main.orchestrator import Orchestrator
from core.managers.priscillapluginmanager import PriscillaPluginManager


#----------------------------------------------------------------------
# Exported function to launch GoLismero

def launcher(options):

    if not isinstance(options, GlobalParams):
        raise TypeError("Expected GlobalParams, got %s instead" % type(options))

    Logger.configure(level = options.verbose)

    m_orchestrator = None

    try:
        if options.run_mode == GlobalParams.RUN_MODE.standalone:

            # Run Orchestrator
            m_orchestrator = Orchestrator(options)

            # Start UI
            m_orchestrator.start_ui()

            # New audit with command line options
            m_orchestrator.add_audit(options)

            # Message loop
            m_orchestrator.msg_loop()

        elif options.run_mode == GlobalParams.RUN_MODE.cloudclient:
            #
            # TODO
            #
            raise NotImplementedError("Cloud client mode not yet implemented!")


        elif options.run_mode == GlobalParams.RUN_MODE.cloudserver:
            #
            # TODO
            #
            raise NotImplementedError("Cloud server mode not yet implemented!")

        else:
            raise ValueError("Invalid run mode: %r" % options.run_mode)

    except KeyboardInterrupt:
        Logger.log("\n[i] Stopping. Please wait...")


#----------------------------------------------------------------------
# Start of program

def main():

    # Show the program banner
    show_banner()

    # Configure command line parser
    parser = argparse.ArgumentParser()
    parser.add_argument('targets', metavar='TARGET', help='one or more target web sites', nargs='+')

    gr_main = parser.add_argument_group("main options")
    gr_main.add_argument('-M', "--run-mode", action='store', dest='run_mode', help='run mode [default: Standalone]', default="Standalone", choices=[x.title() for x in GlobalParams.RUN_MODE._values.keys()])
    gr_main.add_argument('-I', "--user-interface", action='store', dest='user_interface', help='user interface mode [default: Console]', default="console", choices=[x.title() for x in GlobalParams.USER_INTERFACE._values.keys()])
    gr_main.add_argument("-v", "--verbose", action="count", default=1, help="increase output verbosity")
    gr_main.add_argument("-q", "--quiet", action="store_const", dest="verbose", const=0, help="suppress text output")
    ##gr_audit.add_argument('--max-process', action='store', dest='max_process', help='maximum number of plugins to run concurrently.', default="0")

    gr_net = parser.add_argument_group("network")
    gr_net.add_argument("--max-connections", action="store", dest="max_connections", help="maximum number of concurrent connections per host [default: 4]", default=50)
    gr_net.add_argument("--no-subdomains", action="store_false", dest="include_subdomains", help="do not include subdomains in the target scope", default=True)
    gr_net.add_argument("--regex", action="store", dest="subdomain_regex", help="include subdomains as regex exprexion", default="")
    gr_net.add_argument("--recursivity", action="store", dest="recursivity", help="recursivity level of spider.", default=0)
    gr_net.add_argument("-f","--follow-redirects", action="store_true", dest="follow_redirects", help="follow redirects", default=False)

    gr_audit = parser.add_argument_group("audit")
    gr_audit.add_argument('--audit-name', action='store', dest='audit_name', help='customize the audit name')
    gr_audit.add_argument('--audit-database', action='store', dest='audit_db', default="memory://", help='specify a database connection string')

    gr_plugins = parser.add_argument_group("plugins")
    gr_plugins.add_argument('-P', '--enable-plugin', action='append', dest='plugins', help="customize which plugins to load" )
    gr_plugins.add_argument('--plugins-folder', action='store', dest="plugins_folder", help="customize the location of the plugins" )
    gr_plugins.add_argument('--plugin-list', action='store_true', help="list available plugins")
    gr_plugins.add_argument('--plugin-info', action='store', dest="plugin_name", help="show plugin info")


    # Parse command line options
    try:
        P = parser.parse_args()
        cmdParams = GlobalParams.from_cmdline( P )
    except Exception, e:
        ##raise
        parser.error(str(e))


    # Get the plugins folder from the parameters
    # TODO: allow more than one plugin location!
    plugins_folder = cmdParams.plugins_folder

    # If no plugins folder is given, use the default
    if not plugins_folder:
        plugins_folder = path.abspath(__file__)
        plugins_folder = path.split(plugins_folder)[0]
        plugins_folder = path.join(plugins_folder, "plugins")
        cmdParams.plugins_folder = plugins_folder


    #------------------------------------------------------------
    # List plugins
    if P.plugin_list:

        # Load the plugins list
        try:
            manager = PriscillaPluginManager()
            manager.find_plugins(plugins_folder)
        except Exception, e:
            Logger.log("[!] Error loading plugins list: %s" % e.message)
            exit(1)

        # Show the list of plugins
        Logger.configure(level=Logger.VERBOSE)
        Logger.log("Plugin list")
        Logger.log("-----------")
        for name, info in manager.get_plugins().iteritems():
            Logger.log("- %s: %s" % (name, info.display_name))
        exit(0)


    #------------------------------------------------------------
    # Display plugin info
    if P.plugin_name:

        # Load the plugins list
        try:
            manager = PriscillaPluginManager()
            manager.find_plugins(plugins_folder)
        except Exception, e:
            Logger.log("[!] Error loading plugins list: %s" % e.message)
            exit(1)

        # Show the plugin information
        Logger.configure(level=Logger.VERBOSE)
        try:
            m_plugin_info = manager.get_plugin_by_name(P.plugin_name)
            m_plugin_obj  = manager.load_plugin_by_name(P.plugin_name)
            if m_plugin_info and m_plugin_obj:
                message = m_plugin_obj.display_help()
                message = textwrap.dedent(message)
                Logger.log("Information for plugin: %s" % m_plugin_info.display_name)
                Logger.log("----------------------")
                Logger.log("Location: %s" % m_plugin_info.descriptor_file)
                Logger.log("Source code: %s" % m_plugin_info.plugin_module)
                if m_plugin_info.plugin_class:
                    Logger.log("Class name: %s" % m_plugin_info.plugin_class)
                if m_plugin_info.description != m_plugin_info.display_name:
                    Logger.log("")
                    Logger.log(m_plugin_info.description)
                if message != m_plugin_info.description:
                    Logger.log("")
                    Logger.log(message)
            else:
                Logger.log("[!] Plugin name not found")
                exit(1)
            exit(0)
        except KeyError:
            Logger.log("[!] Plugin name not found")
            exit(1)
        except ValueError:
            Logger.log("[!] Plugin name not found")
            exit(1)
        except Exception, e:
            Logger.log("[!] Error recovering plugin info: %s" % e.message)
            exit(1)


    #------------------------------------------------------------
    # Launch GoLismero
    Logger.log("GoLismero started at %s" % datetime.datetime.now())
    try:
        launcher(cmdParams)
    except KeyboardInterrupt:
        Logger.log("GoLismero cancelled by the user at %s" % datetime.datetime.now())
        exit(1)
    except SystemExit:
        Logger.log("GoLismero stopped at %s" % datetime.datetime.now())
        raise


if __name__ == '__main__':
    main()
