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

<<<<<<< HEAD
from time import sleep
import requests
=======
import argparse
import json
import time
import traceback
import urllib2
>>>>>>> af84b98cb1da5dcef26514e58b5adb112c85c50e
import urlparse


# Test targets
TARGET = {
    'quick'      : "http://navajanegra.com",
    'long'      : "http://www.terra.es/portada/"
}

<<<<<<< HEAD
STATUS =  "/api/audits/state/%s"

STATES = {
    'progress'    : "/api/audits/progress/%s",
    'summary'     : "/api/audits/results/summary/%s",
    'log'         : "/api/audits/log/%s"
}

=======
>>>>>>> af84b98cb1da5dcef26514e58b5adb112c85c50e
AUDIT_DATA = {
    'short'    : '{"audit_name":"asdfasdf", "targets":["%s"], "enable_plugins": [{ "plugin_name" : "testing/recon/spideraaa"}, { "plugin_name" : "testing/recon/theharvester"}]}',
    # Run OpenVAS
    'long'   : '{"audit_name":"asdfasdf", "targets":["%s"], "enable_plugins": [{ "plugin_name" : "testing/scan/openvas", "params" : [{"param_name" : "host", "param_value" : "192.168.2.104"}] }]}',
}

<<<<<<< HEAD
IMPORT = "/api/audits/import/"

RESULTS_FORMATS = [
    'txt',
=======
RESULT_FORMATS = [
    "txt",
>>>>>>> af84b98cb1da5dcef26514e58b5adb112c85c50e
    "html",
    "xml",
    "csv",
    "json",
    "rst",
    "odt",
    "tex",
]


#----------------------------------------------------------------------
<<<<<<< HEAD
def import_options(args):
    """"""
    daemon_addr = args.ADDRESS
    daemon_port = args.PORT
    files       = args.IMPORT_FILES

    if not files:
        raise ValueError("files can't be None")

    address     = "http://%s:%s" % (daemon_addr, daemon_port)
    query       = urlparse.urljoin(address, IMPORT)
    headers     = {'Content-Type': 'application/json'}


    data        = '{"audit_name":"asdfasdf", "imports": [%s], "enable_plugins": [{ "plugin_name" : "report/bugblast_1.6", "params" : [{"param_name" : "proyecto_d", "param_value" : "GRUPOOO"}] }]}' % ','.join("\"%s\"" % y.strip() for y in files.split(","))
    print data

    print "[*] Importing files"
    r          = requests.post(query, data=data, headers=headers)
    if r.status_code != 200:
        print "[!] Error importing the files"
        print r.text
        return
    r_json     = json.loads(r.text)
    audit_id   = r_json["audit_id"]
    print "    | Got audit id: %s" % str(audit_id)

    if not audit_id:
        print "[!] Import can't be done."
        return

#----------------------------------------------------------------------
def scan_audit(args):
    """Test the complete audit scan"""
=======
def main(args):
>>>>>>> af84b98cb1da5dcef26514e58b5adb112c85c50e

    # Get the parameters.
    target      = TARGET.get("long") if args.TYPE else TARGET.get("quick")
    data        = (AUDIT_DATA.get("long") if args.TYPE else AUDIT_DATA.get("short")) % target
    daemon_addr = args.ADDRESS
    daemon_port = args.PORT
    address     = "http://%s:%s" % (daemon_addr, daemon_port)
<<<<<<< HEAD
    headers     = {'Content-Type': 'application/json'}

    # First, make the create
    query      = urlparse.urljoin(address, "/api/audits/create/")
    audit_id   = None

    #
    # Create audit
    #
    print "[*] Creating audit"
    r          = requests.post(query, data=data, headers=headers)
    if r.status_code != 200:
        print "[!] Error creating the audit"
        print r.text
        return
    r_json     = json.loads(r.text)
    audit_id   = r_json["audit_id"]
    print "    | Got audit id: %s" % str(audit_id)

    if not audit_id:
        print "[!] Audit not created correctly"
        return

    #
    # Start the audit
    #
    print "[*] Starting audit %s" % str(audit_id)
    query   = urlparse.urljoin(address, "/api/audits/start/%s" % str(audit_id))
    r       = requests.get(query, headers=headers)
    if r.status_code != 200:
        print "[!] Error creating the audit"
        print r.text
        return
    print "      %s" % r.text


    # Check states
    cont = True
    while cont:

        # Check state for finish
        query  = urlparse.urljoin(address, STATUS % audit_id)
        r      = json.loads(requests.get(query, headers = headers).text)
        print "[*] Audit state: %s" % r["state"]
        if r["state"] != "running":
            print "Audit finished with state: %s" % r["state"]
            break

        for t, r in STATES.iteritems():

            # Check progress + summary
            print "[*] Making request: %s..." % t
            query  = urlparse.urljoin(address, r % audit_id)
            r      = requests.get(query, headers = headers)
            r_json = json.loads(r.text)

            # To console...
            print r.text

            # Check for errors
            if r_json.get("error_code", True):
                if r_json.get("error_code") == -1:
                    return

            if r.status_code != 200:
                print "    | Error in method: %s (Probably the audit is finished):" % t
                print "    | %s" % r.text
                cont = False
                break


            sleep(1)

    # Wait while generate the results
    print "[*] Waiting for report generation"
    sleep(5)

    # Gettirng results for each format
    for l_format in RESULTS_FORMATS:
        # Try to get 3 times the results
        print "[*] Getting results for audit %s in format %s..." % (str(audit_id), l_format),
        for l_times in xrange(3):

            # Get results
            query      = urlparse.urljoin(address, "/api/audits/results/%s/%s" % (str(audit_id), l_format))
            r          = requests.get(query)

            if r.status_code == "200":
                print "OK!"
                # Out of first loop
                break
        else:
            print "[!] Can't generate the results in format: %s" % l_format

=======

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
>>>>>>> af84b98cb1da5dcef26514e58b5adb112c85c50e


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='GoLismero web service tester')
    parser.add_argument('-d', dest="ADDRESS", help="daemon address", default="127.0.0.1")
    parser.add_argument('-p', dest="PORT", help="daemon port", type=int, default=8000)
    parser.add_argument('--long', dest="TYPE", action="store_false", help="long test type", default=False)

    gr1 = parser.add_argument_group("Import options")
    gr1.add_argument('-i', dest="IMPORT", action="store_true", help="test the import options only", default=False)
    gr1.add_argument('--files', dest="IMPORT_FILES", help="comma separeted files to import.", default=False)

    args = parser.parse_args()

<<<<<<< HEAD
    if args.IMPORT:
        import_options(args)
    else:
        scan_audit(args)
=======
    main(args)
>>>>>>> af84b98cb1da5dcef26514e58b5adb112c85c50e
