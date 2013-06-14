#!/usr/bin/env python
# -*- coding: utf-8 -*-


__license__="""
GoLismero 2.0 - The web knife.

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

__all__ = ["launcher", "show_banner"]


#----------------------------------------------------------------------
# Metadata

__author__ = "Daniel Garcia Garcia a.k.a cr0hn (@ggdaniel) - cr0hn<@>cr0hn.com"
__copyright__ = "Copyright 2011-2013 - GoLismero Project"
__credits__ = ["Daniel Garcia Garcia a.k.a cr0hn (@ggdaniel)", "Mario Vilas (@Mario_Vilas)"]
__maintainer__ = "cr0hn"
__email__ = "golismero.project<@>gmail.com"
__version__ = "2.0.0a1"


#----------------------------------------------------------------------
# Show program banner
def show_banner():
    print
    print "|--------------------------------------------------|"
    print "| GoLismero - The Web Knife                        |"
    print "| Contact: golismero.project<@>gmail.com           |"
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
    if version_info < (2, 7) or version_info >= (3, 0):
        show_banner()
        print "[!] You must use Python version 2.7"
        exit(1)


#----------------------------------------------------------------------
# Fix the module load path when running as a portable script and during installation.

import os
from os import path
try:
    _FIXED_PATH_
except NameError:
    here = path.split(path.abspath(__file__))[0]
    if not here:  # if it fails use cwd instead
        here = path.abspath(os.getcwd())
    thirdparty_libs = path.join(here, "thirdparty_libs")
    if path.exists(thirdparty_libs):
        has_here = here in sys.path
        has_thirdparty_libs = thirdparty_libs in sys.path
        if not (has_here and has_thirdparty_libs):
            if has_here:
                sys.path.remove(here)
            if has_thirdparty_libs:
                sys.path.remove(thirdparty_libs)
            if __name__ == "__main__":
                # As a portable script: use our versions always
                sys.path.insert(0, thirdparty_libs)
                sys.path.insert(0, here)
            else:
                # When installing: prefer system version to ours
                sys.path.insert(0, here)
                sys.path.append(thirdparty_libs)
    _FIXED_PATH_ = True


#----------------------------------------------------------------------
# Imported modules

import argparse
import datetime
import textwrap
import traceback

from os import getenv, getpid


#----------------------------------------------------------------------
# GoLismero modules

from golismero.api.config import Config
from golismero.common import launcher, OrchestratorConfig, AuditConfig
from golismero.main.orchestrator import Orchestrator
from golismero.managers.pluginmanager import PluginManager
from golismero.managers.processmanager import PluginContext


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

# --no-output
class ResetListAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, [])

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
# Command line parser using argparse

def cmdline_parser():
    parser = argparse.ArgumentParser(fromfile_prefix_chars="@")
    parser.add_argument("targets", metavar="TARGET", nargs="*", help="one or more target web sites")

    gr_main = parser.add_argument_group("main options")
    gr_main.add_argument("--ui-mode", metavar="MODE", help="UI mode [default: console]", default="console")
    gr_main.add_argument("-v", "--verbose", action="count", default=1, help="increase output verbosity")
    gr_main.add_argument("-q", "--quiet", action="store_const", dest="verbose", const=0, help="suppress text output")
    gr_main.add_argument("--color", action="store_true", dest="colorize", help="use colors in console output [default]", default=True)
    gr_main.add_argument("--no-color", action="store_false", dest="colorize", help="suppress colors in console output")

    gr_audit = parser.add_argument_group("audit options")
    gr_audit.add_argument("--audit-name", metavar="NAME", help="customize the audit name")
    gr_audit.add_argument("--audit-db", metavar="DATABASE", dest="audit_db", default="memory://", help="specify a database connection string")

    gr_report = parser.add_argument_group("report options")
    gr_report.add_argument("-o", "--output", dest="reports", metavar="FILENAME", action="append", default=[None], help="write the results of the audit to this file [default: stdout]")
    gr_report.add_argument("-no", "--no-output", dest="reports", action=ResetListAction, help="do not output the results")
    gr_report.add_argument("--only-vulns", action="store_true", dest="only_vulns", help="display only vulnerable resources", default=False)

    gr_net = parser.add_argument_group("network options")
    gr_net.add_argument("--max-connections", help="maximum number of concurrent connections per host [default: 50]", default=50)
    gr_net.add_argument("--allow-subdomains", action="store_true", dest="include_subdomains", help="include subdomains in the target scope [default]", default=True)
    gr_net.add_argument("--forbid-subdomains", action="store_false", dest="include_subdomains", help="do not include subdomains in the target scope")
    gr_net.add_argument("--subdomain-regex", metavar="REGEX", help="filter subdomains using a regular expression", default="")
    gr_net.add_argument("-r", "--depth", type=int, help="depth level of spider [default: 0]", default=0)
    gr_net.add_argument("-l", "--max-links", type=int, help="maximum number of links to analyze [default: 0 => infinite]", default=0)
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

    gr_plugins = parser.add_argument_group("plugin options")
    gr_plugins.add_argument("-P", "--enable-plugin", metavar="NAME", action=EnablePluginAction, dest="enabled_plugins", help="customize which plugins to load", default=["all"])
    gr_plugins.add_argument("-NP", "--disable-plugin", metavar="NAME", action=DisablePluginAction, dest="disabled_plugins", help="customize which plugins not to load", default=[])
    gr_plugins.add_argument("--max-process", metavar="N", type=int, help="maximum number of plugins to run concurrently [default: 8]", default=8)
    gr_plugins.add_argument("--plugins-folder", metavar="PATH", help="customize the location of the plugins" )
    gr_plugins.add_argument("--plugin-list", action="store_true", help="list available plugins and quit")
    gr_plugins.add_argument("--plugin-info", metavar="NAME", dest="plugin_name", help="show plugin info and quit")

    return parser


#----------------------------------------------------------------------
# Start of program

def main(args):

    # Show the program banner.
    show_banner()

    # Get the command line parser.
    parser = cmdline_parser()

    # Parse command line options.
    try:
        envcfg = getenv("GOLISMERO_SETTINGS")
        if envcfg:
            args = parser.convert_arg_line_to_args(envcfg) + args
        P = parser.parse_args(args)
        cmdParams = OrchestratorConfig()
        cmdParams.from_object(P)
        auditParams = AuditConfig()
        auditParams.from_object(P)
    except Exception, e:
        ##raise    # XXX DEBUG
        parser.error(str(e))

    # Get the plugins folder from the parameters.
    # If no plugins folder is given, use the default.
    # TODO: allow more than one plugin location!
    plugins_folder = cmdParams.plugins_folder
    if not plugins_folder:
        plugins_folder = path.abspath(__file__)
        plugins_folder = path.dirname(plugins_folder)
        plugins_folder = path.join(plugins_folder, "plugins")
        if not path.isdir(plugins_folder):
            from golismero import common
            plugins_folder = path.abspath(common.__file__)
            plugins_folder = path.dirname(plugins_folder)
            plugins_folder = path.join(plugins_folder, "plugins")
            if not path.isdir(plugins_folder):
                parser.error("Default plugins folder not found, aborting!")
        cmdParams.plugins_folder = plugins_folder


    #------------------------------------------------------------
    # List plugins and quit

    if P.plugin_list:

        # Load the plugins list
        try:
            manager = PluginManager()
            manager.find_plugins(plugins_folder)
        except Exception, e:
            print "[!] Error loading plugins list: %s" % e.message
            exit(1)

        # Show the list of plugins.
        print "-------------"
        print " Plugin list"
        print "-------------\n"

        # Testing plugins...
        testing_plugins = manager.get_plugins("testing")
        if testing_plugins:
            print "-= Testing plugins =-"
            for name in sorted(testing_plugins.keys()):
                info = testing_plugins[name]
                print "+ %s: %s" % (name, info.description)

        # UI plugins...
        ui_plugins = manager.get_plugins("ui")
        if ui_plugins:
            print "\n-= UI plugins =-"
            for name in sorted(ui_plugins.keys()):
                info = ui_plugins[name]
                print "+ %s: %s" % (name, info.description)

        # Report plugins...
        report_plugins = manager.get_plugins("report")
        if ui_plugins:
            print "\n-= Report plugins =-"
            for name in sorted(report_plugins.keys()):
                info = report_plugins[name]
                print "+ %s: %s" % (name, info.description)

        if os.sep != "\\":
            print
        exit(0)


    #------------------------------------------------------------
    # Display plugin info and quit

    if P.plugin_name:

        # Load the plugins list.
        try:
            manager = PluginManager()
            manager.find_plugins(plugins_folder)
        except Exception, e:
            print "[!] Error loading plugins list: %s" % e.message
            exit(1)

        # Show the plugin information.
        try:
            try:
                m_plugin_info = manager.get_plugin_by_name(P.plugin_name)
            except KeyError:
                try:
                    m_found = manager.search_plugins_by_name(P.plugin_name)
                    if len(m_found) > 1:
                        print "[!] Error: which plugin did you mean?"
                        for plugin_name in m_found.iterkeys():
                            print "\t%s" % plugin_name
                        exit(1)
                    m_plugin_info = m_found.pop(m_found.keys()[0])
                except Exception:
                    raise KeyError(P.plugin_name)
            Config._context = PluginContext( orchestrator_pid = getpid(),
                                                  plugin_info = m_plugin_info,
                                                    msg_queue = None )
            m_plugin_obj = manager.load_plugin_by_name(m_plugin_info.plugin_name)
            message = m_plugin_obj.display_help()
            message = textwrap.dedent(message)
            print "Information for plugin: %s" % m_plugin_info.display_name
            print "----------------------"
            print "Location: %s" % m_plugin_info.descriptor_file
            print "Source code: %s" % m_plugin_info.plugin_module
            if m_plugin_info.plugin_class:
                print "Class name: %s" % m_plugin_info.plugin_class
            if m_plugin_info.description != m_plugin_info.display_name:
                print
                print m_plugin_info.description
            if message.strip().lower() != m_plugin_info.description.strip().lower():
                print
                print message
            exit(0)
        except KeyError:
            print "[!] Plugin name not found"
            exit(1)
        except ValueError:
            print "[!] Plugin name not found"
            exit(1)
        except Exception, e:
            print "[!] Error recovering plugin info: %s" % e.message
            exit(1)


    #------------------------------------------------------------
    # Check if all options are correct

    try:
        cmdParams.check_params()
        auditParams.check_params()
    except Exception, e:
        parser.error(e.message)


    #------------------------------------------------------------
    # Launch GoLismero

    from golismero.main.console import Console

    Console.level = cmdParams.verbose
    Console.display("GoLismero started at %s" % datetime.datetime.now())
    try:
        from golismero.api.net.web_utils import detect_auth_method, check_auth

        # Detect auth in URLs.
        if 1 == 2:
            for t in auditParams.targets:
                auth, realm = detect_auth_method(t)
                if auth:
                    Console.display_error("[!] '%s' authentication is needed for '%s'. Specify using syntax: http://user:pass@target.com." % (auth, t))
                    exit(1)

        # Detect auth in proxy, if specified.
        if auditParams.proxy_addr:
            if auditParams.proxy_user:
                check_auth(auditParams.proxy_addr, auditParams.proxy_user, auditParams.proxy_pass)
            else:
                auth, realm = detect_auth_method(auditParams.proxy_addr)
                if auth:
                    Console.display_error("[!] Authentication is needed for '%s' proxy. Use '--proxy-user' and '--proxy-pass' to specify them." % cmdParams.proxy_addr)
                    exit(1)

        # Launch GoLismero.
        try:
            launcher(cmdParams, auditParams)
        except Exception, e:
            Console.display_error("[!] Fatal error: %s" % e.message)
            Console.display_error_more_verbose(traceback.format_exc())
            exit(1)

    except KeyboardInterrupt:
        Console.display("GoLismero cancelled by the user at %s" % datetime.datetime.now())
        exit(1)
    except SystemExit:
        Console.display("GoLismero stopped at %s" % datetime.datetime.now())
        raise


if __name__ == '__main__':
    main(sys.argv[1:])
