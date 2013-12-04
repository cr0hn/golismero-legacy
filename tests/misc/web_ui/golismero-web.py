#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: http://golismero-project.com
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

import os
import sys
import argparse
import netaddr

cwd = os.path.split(os.path.abspath(__file__))[0]
cwd = os.path.join(cwd, "gui", "web")
sys.path.insert(0, cwd)


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


if __name__ == "__main__":

    usage = """
Run web server UI for GoLismero 2.0.

** Make sure you're running golismero-daemon.py

Listen in all network interfaces at port 9000:
%(prog)s -l 0.0.0.0 -p 9000

Listen in loopback IPv6 at port 8000:
%(prog)s -l ::1
"""

    parser = argparse.ArgumentParser(usage=usage, description='run GoLismero web UI')
    parser.add_argument('-l', dest="IP_LISTEN", help="IP address where to listen to (default: 127.0.0.1)", default="127.0.0.1")
    parser.add_argument('-p', dest="PORT", type=int, help="port where to listen to (default 8000)", default=8000)
    parser.add_argument('--debug', dest="DEBUG_MODE", action="store_true", help="runs debug web server instead a gunicorn (default)", default=False)
    parser.add_argument('--push', dest="PUSH_MODE", action="store_true", help="set PUSH mode for get stats", default=False)

    gr1 = parser.add_argument_group("GoLismero server settings")
    gr1.add_argument('-sa', dest="SERVER_ADDR", help="GoLismero server address [default 127.0.0.1]", default="127.0.0.1")
    gr1.add_argument('-sp', dest="SERVER_PORT", type=int, help="GoLismero server port [default 9000]", default=9000)



    args = parser.parse_args()

    #
    # Listen params
    #

    # Check port
    if args.PORT:
        try:
            check_port(args.PORT)
        except ValueError,e:
            print "\n[!] %s\n" % str(e)
            sys.exit(1)
        except TypeError, e:
            print "\n[!] %s\n" % str(e)
            sys.exit(1)

    # Check for IP
    if args.IP_LISTEN:
        try:
            check_ip(args.IP_LISTEN)
        except ValueError,e:
            print "\n[!] %s\n" % str(e)
            sys.exit(1)
        except TypeError, e:
            print "\n[!] %s\n" % str(e)
            sys.exit(1)

    #
    # GoLismero server params
    #

    # Check port
    if args.SERVER_PORT:
        try:
            check_port(args.SERVER_PORT)
        except ValueError,e:
            print "\n[!] %s\n" % str(e)
            sys.exit(1)
        except TypeError, e:
            print "\n[!] %s\n" % str(e)
            sys.exit(1)

    # Check for IP
    if args.SERVER_ADDR:
        try:
            check_ip(args.SERVER_ADDR)
        except ValueError,e:
            print "\n[!] %s\n" % str(e)
            sys.exit(1)
        except TypeError, e:
            print "\n[!] %s\n" % str(e)
            sys.exit(1)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

    from django.core.management import execute_from_command_line, call_command
    from django.conf import settings

    # Configure RPC
    settings.GOLISMERO_CORE_PORT = args.SERVER_PORT
    settings.GOLISMERO_CORE_HOST = args.SERVER_ADDR

    # Push setted?
    settings.GOLISMERO_PUSH_MODE = args.PUSH_MODE

    # Prepare IPv6 address
    m_ip = args.IP_LISTEN
    if m_ip.find(":") != -1:
        if not m_ip.startswith("["):
            m_ip = "[%s]" % m_ip

    # Run django
    listen_addr = "%s:%s" % (m_ip, args.PORT)

    # Create database if not exits
    if not os.path.exists(os.path.abspath((settings.DATABASES['default']['NAME']))):
        call_command("syncdb", interactive=False)

    if args.DEBUG_MODE:
        # Set debug mode
        settings.DEBUG    = True

        call_command("runserver", listen_addr)
    else:


        # Unset debug mode
        settings.DEBUG    = True

        sys.argv = [listen_addr, "--timeout", "6000"]
        call_command("run_gunicorn", listen_addr, timeout=6000)
