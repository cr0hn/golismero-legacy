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
#
# Note: this is mostly because of argparse, if you install it
#       separately you can try removing this check and seeing
#       what happens (we haven't tested it!).

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

from os import getenv

from core.main.console import Console
from core.main.commonstructures import GlobalParams
from core.main.orchestrator import Orchestrator
from core.managers.priscillapluginmanager import PriscillaPluginManager

#----------------------------------------------------------------------
# Exported function to launch GoLismero

def launcher(options):

    if not isinstance(options, GlobalParams):
        raise TypeError("Expected GlobalParams, got %s instead" % type(options))

    m_orchestrator = None

    if options.run_mode == GlobalParams.RUN_MODE.standalone:

        # Run Orchestrator
        m_orchestrator = Orchestrator(options)

        # Start UI
        m_orchestrator.start_ui()

        # New audit with command line options
        m_orchestrator.add_audit(options)

        # Message loop
        m_orchestrator.msg_loop()

    elif options.run_mode == GlobalParams.RUN_MODE.master:
        #
        # TODO
        #
        raise NotImplementedError("Master mode not yet implemented!")

    elif options.run_mode == GlobalParams.RUN_MODE.slave:
        #
        # TODO
        #
        raise NotImplementedError("Slave mode not yet implemented!")

    else:
        raise ValueError("Invalid run mode: %r" % options.run_mode)


#----------------------------------------------------------------------
# Custom argparse actions

# --enable-plugin
class EnablePluginAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        assert self.dest == "enabled_plugins"
        values = values.strip()
        if values.lower() == "all":
            namespace.enabled_plugins  = ["all"]
            namespace.disabled_plugins = []
        else:
            enabled_plugins = getattr(namespace, "enabled_plugins", [])
            if "all" not in enabled_plugins:
                enabled_plugins.append(values)
            disabled_plugins = getattr(namespace, "disabled_plugins", [])
            if values in disabled_plugins:
                disabled_plugins.remove(values)

# --disable-plugin
class DisablePluginAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        assert self.dest == "disabled_plugins"
        values = values.strip()
        if values.lower() == "all":
            namespace.enabled_plugins  = []
            namespace.disabled_plugins = ["all"]
        else:
            disabled_plugins = getattr(namespace, "disabled_plugins", [])
            if "all" not in disabled_plugins:
                disabled_plugins.append(values)
            enabled_plugins = getattr(namespace, "enabled_plugins", [])
            if values in enabled_plugins:
                enabled_plugins.remove(values)

# --cookie-file
class ReadValueFromFileAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            with open(values, "rU") as f:
                data = f.read()
        except IOError, e:
            parser.error("Can't read file %r. Error: %s" % (values, e.message))
        setattr(namespace, self.dest, data)


#----------------------------------------------------------------------
# Start of program

def main():

    # Show the program banner
    show_banner()

    # Configure command line parser
    parser = argparse.ArgumentParser(fromfile_prefix_chars="@")
    parser.add_argument("targets", metavar="TARGET", nargs="+", help="one or more target web sites")

    gr_main = parser.add_argument_group("main options")
    gr_main.add_argument("-M", "--run-mode", metavar="MODE", help="run mode [default: standalone]", default="standalone", choices=GlobalParams.RUN_MODE._values.keys())
    gr_main.add_argument("-I", "--user-interface", metavar="MODE", help="user interface mode [default: console]", default="console", choices=GlobalParams.USER_INTERFACE._values.keys())
    gr_main.add_argument("-v", "--verbose", action="count", default=1, help="increase output verbosity")
    gr_main.add_argument("-q", "--quiet", action="store_const", dest="verbose", const=0, help="suppress text output")
    gr_main.add_argument("--max-process", metavar="N", type=int, help="maximum number of plugins to run concurrently [default: 2]", default=2)
    gr_main.add_argument("--color", action="store_true", dest="colorize", help="use colors in console output [default]", default=True)
    gr_main.add_argument("--no-color", action="store_false", dest="colorize", help="suppress colors in console output")

    gr_report = parser.add_argument_group("report options")
    gr_report.add_argument("-o", "--output-file", metavar="BASENAME", help="output file, without extension")
    gr_report.add_argument("-of", "--output-format", metavar="FORMAT", action="append", dest="output_formats", help="add an output format", default=["screen"], choices=GlobalParams.REPORT_FORMAT._values.keys())

    gr_net = parser.add_argument_group("network options")
    gr_net.add_argument("--max-connections", help="maximum number of concurrent connections per host [default: 4]", default=50)
    gr_net.add_argument("--allow-subdomains", action="store_true", dest="include_subdomains", help="include subdomains in the target scope [default]", default=True)
    gr_net.add_argument("--forbid-subdomains", action="store_false", dest="include_subdomains", help="do not include subdomains in the target scope")
    gr_net.add_argument("--subdomain-regex", metavar="REGEX", help="filter subdomains using a regular expression", default="")
    gr_net.add_argument("-r", "--depth", type=int, help="depth level of spider [default: 0]", default=0)
    gr_net.add_argument("-f","--follow-redirects", action="store_true", dest="follow_redirects", help="follow redirects", default=False)
    gr_net.add_argument("-nf","--no-follow-redirects", action="store_false", dest="follow_redirects", help="do not follow redirects [default]")
    gr_net.add_argument("-ff","--follow-first", action="store_true", dest="follow_first_redirect", help="always follow a redirection on the target URL itself [default]", default=True)
    gr_net.add_argument("-nff","--no-follow-first", action="store_false", dest="follow_first_redirect", help="don't treat a redirection on a target URL as a special case")
    gr_net.add_argument("-pu","--proxy-user", metavar="USER", help="HTTP proxy username")
    gr_net.add_argument("-pp","--proxy-pass", metavar="PASS", help="HTTP proxy password")
    gr_net.add_argument("-pa","--proxy-addr", metavar="ADDRESS:PORT", help="HTTP proxy address in format: address:port")
    gr_net.add_argument("--cookie", metavar="COOKIE", help="set cookie for requests")
    gr_net.add_argument("--cookie-file", metavar="FILE", action=ReadValueFromFileAction, dest="cookie", help="load a cookie from file")
    gr_net.add_argument("--persistent-cache", action="store_true", dest="use_cache_db", help="use a persistent network cache [default in distributed modes]")
    gr_net.add_argument("--volatile-cache", action="store_false", dest="use_cache_db", help="use a volatile network cache [default in standalone mode]")

    gr_audit = parser.add_argument_group("audit options")
    gr_audit.add_argument("--audit-name", metavar="NAME", help="customize the audit name")
    gr_audit.add_argument("--audit-database", metavar="DATABASE", dest="audit_db", default="memory://", help="specify a database connection string")

    gr_plugins = parser.add_argument_group("plugin options")
    gr_plugins.add_argument("-P", "--enable-plugin", metavar="NAME", action=EnablePluginAction, dest="enabled_plugins", help="customize which plugins to load", default=["all"])
    gr_plugins.add_argument("-NP", "--disable-plugin", metavar="NAME", action=DisablePluginAction, dest="disabled_plugins", help="customize which plugins not to load", default=[])
    gr_plugins.add_argument("--plugins-folder", metavar="PATH", help="customize the location of the plugins" )
    gr_plugins.add_argument("--plugin-list", action="store_true", help="list available plugins and quit")
    gr_plugins.add_argument("--plugin-info", metavar="NAME", dest="plugin_name", help="show plugin info and quit")


    # Parse command line options
    try:
        args = sys.argv[1:]
        envcfg = getenv("GOLISMERO_SETTINGS")
        if envcfg:
            args = parser.convert_arg_line_to_args(envcfg) + args
        P = parser.parse_args(args)
        cmdParams = GlobalParams()
        cmdParams.from_cmdline( P )
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
    # List plugins and quit

    if P.plugin_list:

        # Load the plugins list
        try:
            manager = PriscillaPluginManager()
            manager.find_plugins(plugins_folder)
        except Exception, e:
            Console.display("[!] Error loading plugins list: %s" % e.message)
            exit(1)

        # Show the list of plugins
        Console.display("-------------")
        Console.display(" Plugin list")
        Console.display("-------------\n")
        # Testing plugins
        Console.display("-= Testing plugins =-")
        for name, info in manager.get_plugins("testing").iteritems():
            Console.display("+ %s: %s" % (name, info.description))
        # Report plugins
        Console.display("\n-= UI plugins =-")
        for name, info in manager.get_plugins("ui").iteritems():
            Console.display("+ %s: %s" % (name, info.description))
        # UI plugins
        Console.display("\n-= Report plugins =-")
        for name, info in manager.get_plugins("report").iteritems():
            Console.display("+ %s: %s" % (name, info.description))

        Console.display(" ")
        exit(0)


    #------------------------------------------------------------
    # Display plugin info and quit

    if P.plugin_name:

        # Load the plugins list
        try:
            manager = PriscillaPluginManager()
            manager.find_plugins(plugins_folder)
        except Exception, e:
            Console.display("[!] Error loading plugins list: %s" % e.message)
            exit(1)

        # Show the plugin information
        Logger.configure(level=Logger.VERBOSE)
        try:
            m_plugin_info = manager.get_plugin_by_name(P.plugin_name)
            m_plugin_obj  = manager.load_plugin_by_name(P.plugin_name)
            if m_plugin_info and m_plugin_obj:
                message = m_plugin_obj.display_help()
                message = textwrap.dedent(message)
                Console.display("Information for plugin: %s" % m_plugin_info.display_name)
                Console.display("----------------------")
                Console.display("Location: %s" % m_plugin_info.descriptor_file)
                Console.display("Source code: %s" % m_plugin_info.plugin_module)
                if m_plugin_info.plugin_class:
                    Console.display("Class name: %s" % m_plugin_info.plugin_class)
                if m_plugin_info.description != m_plugin_info.display_name:
                    Console.display("")
                    Console.display(m_plugin_info.description)
                if message != m_plugin_info.description:
                    Console.display("")
                    Console.display(message)
            else:
                Console.display("[!] Plugin name not found")
                exit(1)
            exit(0)
        except KeyError:
            Console.display("[!] Plugin name not found")
            exit(1)
        except ValueError:
            Console.display("[!] Plugin name not found")
            exit(1)
        except Exception, e:
            Console.display("[!] Error recovering plugin info: %s" % e.message)
            exit(1)


    #------------------------------------------------------------
    # Use the --output and --output-formats defaults if needed.

    if cmdParams.output_file and (
        not cmdParams.output_formats or
        cmdParams.output_formats == [GlobalParams.REPORT_FORMAT.screen]
    ):
        filename, ext = path.splitext(cmdParams.output_file)
        ext = ext.lower()
        if ext == ".txt":
            cmdParams.output_formats = [GlobalParams.REPORT_FORMAT.text]
        elif ext == ".grepable":
            cmdParams.output_formats = [GlobalParams.REPORT_FORMAT.grepable]
        elif ext in (".html", ".htm"):
            cmdParams.output_formats = [GlobalParams.REPORT_FORMAT.html]
        else:
            parser.error("Can't guess the output format from that filename! Use '--output-format'.")
        cmdParams.output_file = filename


    #------------------------------------------------------------
    # Check if all options are correct

    try:
        cmdParams.check_params()
    except Exception, e:
        parser.error(e.message)


    #------------------------------------------------------------
    # Launch GoLismero

    Console.display("GoLismero started at %s" % datetime.datetime.now())
    try:
        from core.api.net.web_utils import detect_auth_method, check_auth

        # Detect auth in URLs
        if 1 == 2:
            for t in cmdParams.targets:
                auth, realm = detect_auth_method(t)
                if auth:
                    Console.display("[!] '%s' authentication is needed for '%s'. Specify using syntax: http://user:pass@target.com." % (auth, t))
                    exit(1)

        # Detect auth in proxy, if specified
        if cmdParams.proxy_addr:
            if cmdParams.proxy_user:
                check_auth(cmdParams.proxy_addr, cmdParams.proxy_user, cmdParams.proxy_pass)
            else:
                auth, realm = detect_auth_method(cmdParams.proxy_addr)
                if auth:
                    Console.display("[!] Authentication is needed for '%s' proxy. Use '--proxy-user' and '--proxy-pass' to specify them." % cmdParams.proxy_addr)
                    exit(1)

        launcher(cmdParams)

    except KeyboardInterrupt:
        Console.display("GoLismero cancelled by the user at %s" % datetime.datetime.now())
        exit(1)
    except SystemExit:
        Console.display("GoLismero stopped at %s" % datetime.datetime.now())
        raise


if __name__ == '__main__':
    main()
