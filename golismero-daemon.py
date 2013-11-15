#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run GoLismero as a Unix daemon.
"""

__license__="""
GoLismero 2.0 - The web knife.

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


#------------------------------------------------------------------------------
# Fix the module load path.

import sys
from os import path

script = __file__
if path.islink(script):
    script = path.realpath(script)
here = path.split(path.abspath(script))[0]
assert here
thirdparty_libs = path.join(here, "thirdparty_libs")
assert path.exists(thirdparty_libs)
has_here = here in sys.path
has_thirdparty_libs = thirdparty_libs in sys.path
if not (has_here and has_thirdparty_libs):
    if has_here:
        sys.path.remove(here)
    if has_thirdparty_libs:
        sys.path.remove(thirdparty_libs)
    sys.path.insert(0, thirdparty_libs)
    sys.path.insert(0, here)


#------------------------------------------------------------------------------
# Python version check.
# We must do it now before trying to import any more modules.

from golismero import show_banner
from sys import version_info, exit
if __name__ == "__main__":
    if version_info < (2, 7) or version_info >= (3, 0):
        show_banner()
        print "[!] You must use Python version 2.7"
        exit(1)
    import platform
    if (
        platform.system() == "Darwin" and
        (version_info < (2,7,6) or version_info >= (3,0))
    ):
        show_banner()
        print (
            "[!] In OS X you must use Python version greater than 2.7.6:"
            " http://www.python.org/download/releases/2.7.6/"
        )
        exit(1)


#------------------------------------------------------------------------------
# Check we're not running on Windows.

if path.sep == "\\":
    print "[!] This script does not run on Windows."
    exit(1)


#------------------------------------------------------------------------------
# Imported modules.

import daemon


#------------------------------------------------------------------------------
# GoLismero modules.

from golismero.api.logger import Logger
from golismero.common import OrchestratorConfig, get_profile, \
    get_default_config_file
from golismero.main import launcher
import netaddr
import argparse


#----------------------------------------------------------------------
#
# Aux functions
#
#----------------------------------------------------------------------
def check_port(port):
    """
    Checks a port number.

    :param port: Port number.
    :type port: int

    :raises: ValueError, TypeError
    """
    if not isinstance(port, int):
        raise TypeError("Expected int, got '%s' instead" % type(port))

    if port < 1 or port > 65535:
        raise ValueError("Port range must be between 1-65535")


#----------------------------------------------------------------------
def check_ip(ip):
    """
    Checks an IP address.

    :param ip: IP address.
    :type ip: str

    :raises: ValueError, TypeError
    """
    if not isinstance(ip, basestring):
        raise TypeError("Expected basestring, got '%s' instead" % type(ipo))

    try:
        netaddr.IPAddress(ip)
    except:
        try:
            m_listen = None
            if ip.startswith("[") and ip.endswith("]"):
                m_listen = ip[1:-1]
            else:
                m_listen =  ip
            netaddr.IPAddress(m_listen, version=6)
        except:
            raise ValueError("'%s' IP is not a valid IPv4 or IPv6 address" % str(ip))


#------------------------------------------------------------------------------
# Command line parser.

def cmdline_parser():

    # Usage help.
    usage = """Daemon for GoLismero 2.0

Listen in all network interfaces at port 9000:
%(prog)s -l 0.0.0.0 -p 9000

Listen in loopback IPv6 at port 8000:
%(prog)s -l ::1
"""

    # Parse the command line arguments.
    parser = argparse.ArgumentParser(usage=usage, description='run GoLismero web UI')
    parser.add_argument('-l', dest="IP_LISTEN", help="IP address where to listen to (default: 127.0.0.1).", default="127.0.0.1")
    parser.add_argument('-p', dest="PORT", type=int, help="port where to listen to (default 9000).", default=9000)
    parser.add_argument('-v', '--verbose', dest="VERBOSE", action="store_true", help="display debug info into console instead of file.", default=False)
    parser.add_argument('-r', '--auto-restart', dest="AUTO_RESTART", action="store_true", help="automatically restart the service when stopped.", default=False)
    args = parser.parse_args()

    # Check the port number.
    if args.PORT:
        try:
            check_port(args.PORT)
        except Exception, e:
            parser.error(str(e))

    # Check the listening IP address.
    if args.IP_LISTEN:
        try:
            check_ip(args.IP_LISTEN)
        except Exception, e:
            parser.error(str(e))

    # Return the parsed command line options.
    return args


#------------------------------------------------------------------------------
# Start of program.

def daemon_main(listen_address, listen_port):

    # Get the config file name.
    config_file = get_default_config_file()
    if not config_file:
        raise RuntimeError("Could not find config file, aborting!")

    # Load the Orchestrator options.
    orchestrator_config = OrchestratorConfig()
    orchestrator_config.verbose     = Logger.MORE_VERBOSE
    orchestrator_config.config_file = config_file

    # Config service bind
    orchestrator_config.listen_address = listen_address
    orchestrator_config.listen_port    = listen_port

    orchestrator_config.from_config_file(orchestrator_config.config_file,
                                         allow_profile = True)
    if orchestrator_config.profile:
        orchestrator_config.profile_file = get_profile(
                                            orchestrator_config.profile)
        if orchestrator_config.profile_file:
            orchestrator_config.from_config_file(
                                            orchestrator_config.profile_file)
        else:
            raise RuntimeError("Could not find profile, aborting!")

    # Get the plugins folder from the parameters.
    # If no plugins folder is given, use the default.
    plugins_folder = orchestrator_config.plugins_folder
    if not plugins_folder:
        print __file__
        plugins_folder = path.abspath(__file__)
        print plugins_folder
        plugins_folder = path.dirname(plugins_folder)
        print plugins_folder
        plugins_folder = path.join(plugins_folder, "plugins")
        print plugins_folder
        if not path.isdir(plugins_folder):
            from golismero import common
            plugins_folder = path.abspath(common.__file__)
            plugins_folder = path.dirname(plugins_folder)
            plugins_folder = path.join(plugins_folder, "plugins")
            if not path.isdir(plugins_folder):
                raise RuntimeError(
                    "Default plugins folder not found, aborting!")
        orchestrator_config.plugins_folder = plugins_folder

    # Force the Web UI.
    orchestrator_config.ui_mode = "web"

    # Force disable colored output.
    orchestrator_config.color = False

    # Launch GoLismero.
    launcher.run(orchestrator_config)


#------------------------------------------------------------------------------
# Run as daemon.

if __name__ == '__main__':

    # Parse the command line options.
    args = cmdline_parser()

    # Get the working directory.
    working_directory = path.dirname( path.abspath(__file__) )

    ## Save logs to file, unless we're in verbose mode.
    #fout = None
    #fin  = None
    #if not args.VERBOSE:
        #fout = open(path.join(working_directory, "golismero-out.log"), "a")
        #fin  = open(path.join(working_directory, "golismero-err.log"), "a")
        ###fout = open("/var/log/golismero-out.log", "a")
        ###fin  = open("/var/log/golismero-err.log", "a")
    #else:
        #fout = sys.stdout
        #fin  = sys.stderr

    with daemon.DaemonContext(
        working_directory = working_directory,
        detach_process = False,
        stdout = fout,
        stderr = fin
    ):
        if args.AUTO_RESTART:
            while True:
                try:
                    daemon_main(args.IP_LISTEN, args.PORT)
                except:
                    pass
        else:
            daemon_main(args.IP_LISTEN, args.PORT)
