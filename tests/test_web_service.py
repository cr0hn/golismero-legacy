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

# Test the GoLismero daemon.

import argparse
import json
import time
import traceback
import urllib2
import urlparse


# Test targets
TARGET = {
    'quick'      : "http://terra.es",
    'long'      : "http://www.terra.es/portada/"
}

AUDIT_DATA = {
    'short'    : '{"audit_name":"asdfasdf", "targets":["%s"], "enable_plugins": [{ "plugin_name" : "testing/recon/spider"}]}',
    # Run OpenVAS
    'long'   : '{"audit_name":"asdfasdf", "targets":["%s"], "enable_plugins": [{ "plugin_name" : "testing/scan/openvas", "params" : [{"param_name" : "host", "param_value" : "192.168.2.104"}] }]}',
}

RESULT_FORMATS = [
    "txt",
    "html",
    "xml",
    "csv",
    "json",
    "rst",
    "odt",
    "tex",
]

#----------------------------------------------------------------------
def main(args):

    # Get the parameters.
    target      = TARGET.get("long") if args.TYPE else TARGET.get("quick")
    data        = (AUDIT_DATA.get("long") if args.TYPE else AUDIT_DATA.get("short")) % target
    daemon_addr = args.ADDRESS
    daemon_port = args.PORT
    address     = "http://%s:%s" % (daemon_addr, daemon_port)

    # Prepare urllib2.
    opener  = urllib2.build_opener()
    headers = {'Content-Type': 'application/json'}

    # Create the audit.
    query = urlparse.urljoin(address, "/api/audits/create/")
    print "[*] Creating audit"
    audit_id = json.load(opener.open(urllib2.Request(query, data=data, headers=headers)))["audit_id"]
    print "    | Got audit id: %s" % str(audit_id)
    assert bool(audit_id)

    # Start the audit.
    query = urlparse.urljoin(address, "/api/audits/start/%s" % str(audit_id))
    print "[*] Starting audit %s" % str(audit_id)
    print "      %s" % opener.open(urllib2.Request(query, headers=headers)).read()

    # Wait until the audit is finished.
    while True:

        # Get the state, to know if it's running.
        query = urlparse.urljoin(address, "/api/audits/state/%s" % str(audit_id))
        print "[*] Making request: state..."
        resp = opener.open(urllib2.Request(query, headers=headers)).read()
        print "      %s" % resp

        # Break if it's not running anymore.
        if json.loads(resp)["state"] != "running":
            break

        # Get the progress.
        query = urlparse.urljoin(address, "/api/audits/progress/%s" % str(audit_id))
        print "[*] Making request: progress..."
        resp = opener.open(urllib2.Request(query, headers=headers)).read()
        print "      %s" % resp

        # Get the summary.
        query = urlparse.urljoin(address, "/api/audits/results/summary/%s" % str(audit_id))
        print "[*] Making request: summary..."
        resp = opener.open(urllib2.Request(query, headers=headers)).read()
        print "      %s" % resp

        # Wait before polling again.
        time.sleep(1)

    # Get the results in each format.
    for l_format in RESULT_FORMATS:
        print "[*] Getting results for audit %s in format %s" % (str(audit_id), l_format)
        try:
            query = urlparse.urljoin(address, "/api/audits/results/%s/%s" % (str(audit_id), l_format))
            print "%s\n      %s" % ("=" * 70, opener.open(urllib2.Request(query, headers=headers)).read())
        except Exception:
            traceback.print_exc()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='GoLismero web service tester')
    parser.add_argument('-d', dest="ADDRESS", help="daemon address", default="127.0.0.1")
    parser.add_argument('-p', dest="PORT", help="daemon port", type=int, default=8000)
    parser.add_argument('--long', dest="TYPE", action="store_false", help="long test type", default=False)

    args = parser.parse_args()

    main(args)
