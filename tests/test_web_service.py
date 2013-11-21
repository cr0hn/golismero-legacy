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

"""

This test file makes tests for GoLismero when it works as daemon

"""

from time import sleep
import urllib2
import urlparse
import json
import argparse

# Test targets
TARGET = {
    'quick'      : "http://navajanegra.com",
    #'long'      : "http://www.terra.es/portada/"
}

STATES = {
    'progress'    : "/api/audits/progress/%s",
    'status'      : "/api/audits/state/%s",
    'summary'     : "/api/audits/results/summary/%s"
}

AUDIT_DATA = {
    'short'    : '{"audit_name":"asdfasdf", "targets":["%s"], "enable_plugins": [{ "plugin_name" : "testing/recon/spider"} , { "plugin_name" : "testing/recon/theharvester"}]}',
    # Run OpenVAS
    'long'   : '{"audit_name":"asdfasdf", "targets":["%s"], "enable_plugins": [{ "plugin_name" : "testing/scan/openvas", "params" : [{"param_name" : "host", "param_value" : "192.168.2.104"}] }]}',
}

RESULTS_FORMATS = [
    'txt',
    "html",
    "xml",
    "csv",
    "json"
]

#----------------------------------------------------------------------
def main(args):
    """Main func"""

    target      = TARGET.get("long") if args.TYPE else TARGET.get("quick")
    data        = (AUDIT_DATA.get("long") if args.TYPE else AUDIT_DATA.get("short")) % target
    daemon_addr = args.ADDRESS
    daemon_port = args.PORT
    address     = "http://%s:%s" % (daemon_addr, daemon_port)
    print data
    # Prepare urllib2
    opener  = urllib2.build_opener()
    headers = {'Content-Type': 'application/json'}

    # First, make the create
    query      = urlparse.urljoin(address, "/api/audits/create/")
    audit_id   = None
    try:
        print "[*] Creating audit"
        audit_id   = json.load(opener.open(urllib2.Request(query, data=data, headers=headers)))["audit_id"]
        print "    | Got audit id: %s" % str(audit_id)
    except urllib2.HTTPError, e:
        print "[!] Error creating the audit"
        print e

    if not audit_id:
        print "[!] Audit not created correctly"
        return

    # First, make the start
    query      = urlparse.urljoin(address, "/api/audits/start/%s" % str(audit_id))
    try:
        print "[*] Starting audit %s" % str(audit_id)
        print "      %s" % opener.open(urllib2.Request(query, headers=headers)).read()
    except urllib2.HTTPError, e:
        print "[!] Error creating the audit"
        print e

    # Check states
    try:
        while True:
            for t, r in STATES.iteritems():
                print "[*] Making request: %s..." % t
                query  = urlparse.urljoin(address, r % audit_id)
                print "      %s" % opener.open(urllib2.Request(query, headers=headers)).read()
                sleep(1)
    except urllib2.HTTPError, e:
        print "    | Error in method: %s (Probably the audit is finished)" % t
        print e

    # Wait while generate the results
    print "[*] Waiting for report generation"
    sleep(5)


    # Gettirng results for each format
    for l_format in RESULTS_FORMATS:
        # Try to get 3 times the results
        print "[*] Getting results for audit %s in format %s" % (str(audit_id), l_format)
        for l_times in xrange(3):
            try:
                # Get results
                query      = urlparse.urljoin(address, "/api/audits/results/%s/%s" % (str(audit_id), l_format))
                print "%s\n      %s" % ("=" * 70, opener.open(urllib2.Request(query, headers=headers)).read())

                # Out of first loop
                break
            except urllib2.HTTPError, e:
                print "    | - i - Error getting results. Waiting 1 second..."
                sleep(1)
        else:
            print "[!] Can't generate the results in format: %s" % l_format



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='GoLismero web service tester')
    parser.add_argument('-d', dest="ADDRESS", help="daemon address", default="127.0.0.1")
    parser.add_argument('-p', dest="PORT", help="daemon port", type=int, default=8000)
    parser.add_argument('--long', dest="TYPE", action="store_false", help="long test type", default=False)

    args = parser.parse_args()

    main(args)