#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

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

import sys
import os
from os import path

def test_pylint():

    # Fix the module load path for the test.
    here = path.split(path.abspath(__file__))[0]
    if not here:  # if it fails use cwd instead
        here = path.abspath(os.getcwd())
    golismero = path.join(here, "..")
    golismero = path.abspath(golismero)
    thirdparty_libs = path.join(golismero, "thirdparty_libs")
    pythonpath = list(sys.path)
    pythonpath.insert(0, thirdparty_libs)
    pythonpath.insert(0, golismero)
    os.environ['PYTHONPATH'] = path.pathsep.join(pythonpath)

    try:

        # Run PyLint against the sources and save the log.
        print "Running PyLint..."
        with open("_tmp_pylint.log", "w") as log:
            from pylint import epylint as lint
            lint.py_run('golismero', False, log, log)

        # Clean up the log, filter out the false positives, and write the log to disk.
        print "Cleaning up the PyLint log..."
        if not golismero.endswith(path.sep):
            golismero += path.sep
        with open("_tmp_pylint.log", "r") as log:
            with open("pylint.log", "w") as output:
                for line in log:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith(golismero):
                        line = line[ len(golismero) : ]
                    try:
                        p = line.find(":")
                        q = line.find(":", p + 1)
                        f = line[ : p ]
                        d = line[ q : ]
                        n = int( line[ p + 1 : q ] )
                        if os.sep != "/":
                            f = f.replace(os.sep, "/")
                        found = False
                        for false in FALSE_POSITIVES:
                            if not false:
                                continue
                            fp = false.find(":")
                            fq = false.find(":", fp + 1)
                            ff = false[ : fp ]
                            fd = false[ fq : ]
                            fn = int( false[ fp + 1 : fq ] )
                            if f == ff and d == fd and (fn - 10) <= n <= (fn + 10):
                                found = True
                                break
                        if found:
                            continue
                    except Exception:
                        pass
                    output.write(line)
                    output.write("\n")
                    output.flush()

    finally:

        # Delete the temporary file.
        try:
            os.unlink("_tmp_pylint.log")
        except:
            pass
        print "Done!"


# False positives to filter out.
FALSE_POSITIVES = """
golismero/common.py:100: Warning (W): TODO: on Windows, use the roaming data folder instead.
golismero/common.py:771: Warning (W): TODO: maybe this should be done by the UI plugins instead?
golismero/common.py:103: Warning (W, get_user_settings_folder): Using the global statement
golismero/common.py:126: Warning (W, get_user_settings_folder): Catching too general exception Exception
golismero/common.py:158: Warning (W, get_wordlists_folder): Using the global statement
golismero/common.py:177: Warning (W, get_profiles_folder): Using the global statement
golismero/common.py:398: Warning (W, Configuration.__init__): Used * or ** magic
golismero/common.py:488: Warning (W, Configuration.from_json): Redefining name 'json_decode' from outer scope (line 57)
golismero/common.py:484: Warning (W, Configuration.from_json): Using global for 'json_decode' but no assignment is done
golismero/common.py:488: [F, Configuration.from_json] Unable to import 'cjson.decode'
golismero/common.py:492: [F, Configuration.from_json] Unable to import 'simplejson.loads'
golismero/common.py:495: [F, Configuration.from_json] Unable to import 'json.loads'
golismero/common.py:588: Error (E, OrchestratorConfig.check_params): Instance of 'OrchestratorConfig' has no 'max_connections' member
golismero/common.py:589: Error (E, OrchestratorConfig.check_params): Instance of 'OrchestratorConfig' has no 'max_connections' member
golismero/common.py:592: Error (E, OrchestratorConfig.check_params): Instance of 'OrchestratorConfig' has no 'max_process' member
golismero/common.py:593: Error (E, OrchestratorConfig.check_params): Instance of 'OrchestratorConfig' has no 'max_process' member
golismero/common.py:596: Error (E, OrchestratorConfig.check_params): Instance of 'OrchestratorConfig' has no 'enabled_plugins' member
golismero/common.py:598: Error (E, OrchestratorConfig.check_params): Instance of 'OrchestratorConfig' has no 'enabled_plugins' member
golismero/common.py:598: Error (E, OrchestratorConfig.check_params): Instance of 'OrchestratorConfig' has no 'disabled_plugins' member
golismero/common.py:776: Error (E, AuditConfig.check_params): Instance of 'AuditConfig' has no 'enabled_plugins' member
golismero/common.py:778: Error (E, AuditConfig.check_params): Instance of 'AuditConfig' has no 'enabled_plugins' member
golismero/common.py:778: Error (E, AuditConfig.check_params): Instance of 'AuditConfig' has no 'disabled_plugins' member
golismero/common.py:782: Error (E, AuditConfig.check_params): Instance of 'AuditConfig' has no 'subdomain_regex' member
golismero/common.py:786: Error (E, AuditConfig.check_params): Instance of 'AuditConfig' has no 'subdomain_regex' member
golismero/common.py:791: Error (E, AuditConfig.check_params): Instance of 'AuditConfig' has no 'depth' member
golismero/common.py:791: Error (E, AuditConfig.check_params): Instance of 'AuditConfig' has no 'depth' member
golismero/common.py:792: Error (E, AuditConfig.check_params): Instance of 'AuditConfig' has no 'depth' member
golismero/common.py:720: Warning (W, AuditConfig.reports): Attribute '_reports' defined outside __init__
golismero/common.py:738: Warning (W, AuditConfig.audit_db): Attribute '_audit_db' defined outside __init__
golismero/common.py:764: Warning (W, AuditConfig.cookie): Attribute '_cookie' defined outside __init__
golismero/common.py:703: Warning (W, AuditConfig.targets): Attribute '_targets' defined outside __init__
golismero/scope.py:92: Warning (W): FIXME: this should be smarter and use port scanning!
golismero/scope.py:108: Warning (W): FIXME: this should be smarter and use port scanning!
golismero/scope.py:127: Warning (W): FIXME: this should be smarter and use port scanning!
golismero/scope.py:100: Warning (W, AuditScope.__init__): Catching too general exception Exception
golismero/scope.py:115: Warning (W, AuditScope.__init__): Catching too general exception Exception
golismero/scope.py:135: Warning (W, AuditScope.__init__): Catching too general exception Exception
golismero/scope.py:147: Warning (W, AuditScope.__init__): Catching too general exception Exception
golismero/scope.py:244: Warning (W, AuditScope.__contains__): Catching too general exception Exception
golismero/scope.py:270: Warning (W, AuditScope.__contains__): Catching too general exception Exception
golismero/testing.py:98: Warning (W, PluginTester.__init__): Access to a protected member _Audit__audit_scope of a client class
golismero/testing.py:101: Warning (W, PluginTester.__init__): Access to a protected member _Audit__database of a client class
golismero/testing.py:104: Warning (W, PluginTester.__init__): Access to a protected member _AuditManager__audits of a client class
golismero/testing.py:104: Error (E, PluginTester.__init__): Instance of 'AuditManager' has no '_AuditManager__audits' member
golismero/testing.py:107: Warning (W, PluginTester.__init__): Access to a protected member _context of a client class
golismero/testing.py:109: Warning (W, PluginTester.__init__): Access to a protected member _Orchestrator__queue of a client class
golismero/testing.py:109: Error (E, PluginTester.__init__): Instance of 'Orchestrator' has no '_Orchestrator__queue' member
golismero/testing.py:116: Warning (W, PluginTester.__init__): Access to a protected member _initialize of a client class
golismero/testing.py:117: Warning (W, PluginTester.__init__): Access to a protected member _clear_local_cache of a client class
golismero/testing.py:118: Warning (W, PluginTester.__init__): Access to a protected member _update_plugin_path of a client class
golismero/testing.py:119: Warning (W, PluginTester.__init__): Access to a protected member _enabled of a client class
golismero/testing.py:129: Warning (W, PluginTester.__exit__): Redefining built-in 'type'
golismero/testing.py:160: Warning (W, PluginTester.run_plugin): Access to a protected member _PluginContext__plugin_info of a client class
golismero/testing.py:160: Warning (W, PluginTester.run_plugin): Access to a protected member _context of a client class
golismero/testing.py:165: Warning (W, PluginTester.run_plugin): Access to a protected member _initialize of a client class
golismero/testing.py:166: Warning (W, PluginTester.run_plugin): Access to a protected member _clear_local_cache of a client class
golismero/testing.py:167: Warning (W, PluginTester.run_plugin): Access to a protected member _update_plugin_path of a client class
golismero/testing.py:208: Warning (W, PluginTester.run_plugin): Access to a protected member _PluginContext__plugin_info of a client class
golismero/testing.py:208: Warning (W, PluginTester.run_plugin): Access to a protected member _context of a client class
golismero/testing.py:220: Warning (W, PluginTester.cleanup): Access to a protected member _update_plugin_path of a client class
golismero/testing.py:221: Warning (W, PluginTester.cleanup): Access to a protected member _clear_local_cache of a client class
golismero/testing.py:223: Warning (W, PluginTester.cleanup): Access to a protected member _finalize of a client class
golismero/api/config.py:201: Warning (W): TODO: check the call stack to make sure it's called only
golismero/api/config.py:57: Warning (W, _Config.__init__): Statement seems to have no effect
golismero/api/config.py:213: Warning (W, _Config._has_context): Statement seems to have no effect
golismero/api/config.py:203: Warning (W, _Config._context): Attribute '__context' defined outside __init__
golismero/api/external.py:37: Warning (W): TODO: Use pexpect to run tools interactively.
golismero/api/logger.py:82: Warning (W, Logger._log): Access to a protected member _context of a client class
golismero/api/parallel.py:334: Warning (W): TODO: Return exceptions to the caller.
golismero/api/parallel.py:123: Warning (W, setInterval.outer_wrap.wrap.inner_wrap): Used * or ** magic
golismero/api/parallel.py:207: Warning (W, pmap): Used builtin function 'map'
golismero/api/parallel.py:213: Warning (W, pmap): Used builtin function 'map'
golismero/api/parallel.py:223: Warning (W, pmap): Used * or ** magic
golismero/api/parallel.py:332: Warning (W, Task.run): No exception type(s) specified
golismero/api/parallel.py:617: Warning (W, WorkerPool.__init__): Access to a protected member _callback of a client class
golismero/api/parallel.py:750: Warning (W, WorkerPool.stop): Used builtin function 'map'
golismero/api/parallel.py:777: Warning (W, WorkerPool.terminate): No exception type(s) specified
golismero/api/plugin.py:78: Warning (W, _PluginState.get): Access to a protected member _context of a client class
golismero/api/plugin.py:98: Warning (W, _PluginState.check): Access to a protected member _context of a client class
golismero/api/plugin.py:114: Warning (W, _PluginState.set): Access to a protected member _context of a client class
golismero/api/plugin.py:129: Warning (W, _PluginState.remove): Access to a protected member _context of a client class
golismero/api/plugin.py:142: Warning (W, _PluginState.get_names): Access to a protected member _context of a client class
golismero/api/plugin.py:232: Warning (W, Plugin._set_observer): Unused argument 'observer'
golismero/api/plugin.py:256: Warning (W, Plugin.update_status): Access to a protected member _context of a client class
golismero/api/plugin.py:400: Warning (W, UIPlugin._set_observer): Attribute '__observer_ref' defined outside __init__
golismero/api/plugin.py:446: Warning (W, TestingPlugin): Method 'get_accepted_info' is abstract in class 'InformationPlugin' but is not overridden
golismero/api/plugin.py:446: Warning (W, TestingPlugin): Method 'recv_info' is abstract in class 'InformationPlugin' but is not overridden
golismero/api/data/db.py:59: Warning (W, Database.add): Access to a protected member _context of a client class
golismero/api/data/db.py:72: Warning (W, Database.async_add): Access to a protected member _context of a client class
golismero/api/data/db.py:94: Warning (W, Database.remove): Access to a protected member _context of a client class
golismero/api/data/db.py:116: Warning (W, Database.async_remove): Access to a protected member _context of a client class
golismero/api/data/db.py:136: Warning (W, Database.has_key): Access to a protected member _context of a client class
golismero/api/data/db.py:158: Warning (W, Database.get): Access to a protected member _context of a client class
golismero/api/data/db.py:177: Warning (W, Database.get_many): Access to a protected member _context of a client class
golismero/api/data/db.py:201: Warning (W, Database.keys): Access to a protected member _context of a client class
golismero/api/data/db.py:225: Warning (W, Database.count): Access to a protected member _context of a client class
golismero/api/data/db.py:261: Warning (W, Database.get_plugin_history): Access to a protected member _context of a client class
golismero/api/data/__init__.py:75: Warning (W): TODO: benchmark!!!
golismero/api/data/__init__.py:108: Warning (W): TODO: benchmark!!!
golismero/api/data/__init__.py:139: Warning (W): TODO: benchmark!!!
golismero/api/data/__init__.py:252: Warning (W): TODO: Add user-defined tags to Data objects.
golismero/api/data/__init__.py:253: Warning (W): TODO: Add user-defined properties to Data objects.
golismero/api/data/__init__.py:918: Warning (W): TODO: maybe we should compare all properties, not just identity.
golismero/api/data/__init__.py:1008: Warning (W): FIXME review, some data may be lost... (merge instead?)
golismero/api/data/__init__.py:81: Warning (W, identity.is_identity_property): Statement seems to have no effect
golismero/api/data/__init__.py:82: Warning (W, identity.is_identity_property): Statement seems to have no effect
golismero/api/data/__init__.py:112: Warning (W, merge.is_mergeable_property): Statement seems to have no effect
golismero/api/data/__init__.py:113: Warning (W, merge.is_mergeable_property): Statement seems to have no effect
golismero/api/data/__init__.py:143: Warning (W, overwrite.is_overwriteable_property): Statement seems to have no effect
golismero/api/data/__init__.py:144: Warning (W, overwrite.is_overwriteable_property): Statement seems to have no effect
golismero/api/data/__init__.py:543: Warning (W, Data._merge_links): Access to a protected member __linked of a client class
golismero/api/data/__init__.py:544: Warning (W, Data._merge_links): Access to a protected member __linked of a client class
golismero/api/data/__init__.py:547: Warning (W, Data._merge_links): Access to a protected member __linked of a client class
golismero/api/data/__init__.py:549: Warning (W, Data._merge_links): Access to a protected member __linked of a client class
golismero/api/data/__init__.py:550: Warning (W, Data._merge_links): Access to a protected member __linked of a client class
golismero/api/data/__init__.py:633: Warning (W, Data._convert_links_to_data): Access to a protected member _enabled of a client class
golismero/api/data/__init__.py:658: Warning (W, Data.add_link): Access to a protected member _can_link of a client class
golismero/api/data/__init__.py:659: Warning (W, Data.add_link): Access to a protected member _add_link of a client class
golismero/api/data/__init__.py:944: Warning (W, _LocalDataCache.__cleanup): Access to a protected member _context of a client class
golismero/api/data/__init__.py:1263: Warning (W, _LocalDataCache.on_finish): Redefining name 'identity' from outer scope (line 47)
golismero/api/data/__init__.py:1155: Warning (W, _LocalDataCache.on_finish): Catching too general exception Exception
golismero/api/data/__init__.py:1207: Warning (W, _LocalDataCache.on_finish): Catching too general exception Exception
golismero/api/data/__init__.py:1204: Warning (W, _LocalDataCache.on_finish): Catching too general exception Exception
golismero/api/data/__init__.py:1229: Warning (W, _LocalDataCache.on_finish): Catching too general exception Exception
golismero/api/data/__init__.py:1289: Warning (W, _LocalDataCache.on_finish): Catching too general exception Exception
golismero/api/data/__init__.py:955: Warning (W, _LocalDataCache.__cleanup): Attribute '__discarded' defined outside __init__
golismero/api/data/__init__.py:996: Warning (W, _LocalDataCache.update): Attribute '__fresh' defined outside __init__
golismero/api/data/__init__.py:946: Warning (W, _LocalDataCache.__cleanup): Attribute '_enabled' defined outside __init__
golismero/api/data/__init__.py:949: Warning (W, _LocalDataCache.__cleanup): Attribute '__new_data' defined outside __init__
golismero/api/data/__init__.py:958: Warning (W, _LocalDataCache.__cleanup): Attribute '__autogen' defined outside __init__
golismero/api/data/information/dns.py:920: Warning (W): XXX TODO: add a discovered host fingerprint here
golismero/api/data/information/dns.py:929: Warning (W): TODO: discover the gateway address
golismero/api/data/information/dns.py:1063: Warning (W): TODO: discover a geolocation information type here
golismero/api/data/information/dns.py:2081: Warning (W): TODO discover the port
golismero/api/data/information/dns.py:333: Warning (W, DnsRegister.name2id): Redefining built-in 'id'
golismero/api/data/information/dns.py:1421: Warning (W, DnsRegisterNSEC.__init__): Redefining built-in 'next'
golismero/api/data/information/http.py:402: Warning (W): TODO:
golismero/api/data/information/http.py:480: Warning (W): FIXME: better collation!
golismero/api/data/information/http.py:810: Warning (W): TODO: use the headers, Luke!
golismero/api/data/information/http.py:817: Warning (W): TODO: maybe the times should be collected and/or averaged instead?
golismero/api/data/information/http.py:1027: Warning (W): FIXME: not sure how Requests handles content encoding,
golismero/api/data/information/http.py:471: Warning (W, HTTP_Request.__init__): Catching too general exception Exception
golismero/api/data/information/http.py:484: Error (E, HTTP_Request.__init__): Instance of 'str' has no 'items' member (but some types could not be inferred)
golismero/api/data/information/http.py:655: Warning (W, HTTP_Request.content_length): Catching too general exception Exception
golismero/api/data/information/http.py:758: Warning (W, HTTP_Response.__init__): Catching too general exception Exception
golismero/api/data/information/http.py:818: Error (E, HTTP_Response.elapsed): An attribute affected in golismero.api.data.information.http line 792 hide this method
golismero/api/data/information/http.py:913: Warning (W, HTTP_Response.content_length): Catching too general exception Exception
golismero/api/data/information/http.py:985: Warning (W, HTTP_Response.__parse_raw_response): Catching too general exception Exception
golismero/api/data/information/http.py:989: Warning (W, HTTP_Response.__parse_raw_response): Catching too general exception Exception
golismero/api/data/information/webserver_fingerprint.py:48: Warning (W): TODO: we may want to add a list of default servers and descriptions.
golismero/api/data/resource/url.py:113: Warning (W): TODO: if relative, make it absolute using the referer when available.
golismero/api/data/vulnerability/__init__.py:108: Warning (W): TODO: more type checking and sanitization in setters
golismero/api/data/vulnerability/__init__.py:162: Warning (W, Vulnerability.cwe): Attribute '__cwe' defined outside __init__
golismero/api/data/vulnerability/__init__.py:200: Warning (W, Vulnerability.risk): Attribute '__risk' defined outside __init__
golismero/api/data/vulnerability/__init__.py:146: Warning (W, Vulnerability.cve): Attribute '__cve' defined outside __init__
golismero/api/data/vulnerability/__init__.py:127: Warning (W, Vulnerability.impact): Attribute '__impact' defined outside __init__
golismero/api/data/vulnerability/__init__.py:181: Warning (W, Vulnerability.severity): Attribute '__severity' defined outside __init__
golismero/api/data/vulnerability/__init__.py:219: Warning (W, Vulnerability.references): Attribute '__references' defined outside __init__
golismero/api/data/vulnerability/__init__.py:267: Warning (W, UrlVulnerability.__init__): Catching too general exception Exception
golismero/api/net/cache.py:92: Warning (W, _NetworkCache.get): Access to a protected member _context of a client class
golismero/api/net/cache.py:128: Warning (W, _NetworkCache.set): Access to a protected member _context of a client class
golismero/api/net/cache.py:151: Warning (W, _NetworkCache.remove): Access to a protected member _context of a client class
golismero/api/net/cache.py:172: Warning (W, _NetworkCache.exists): Access to a protected member _context of a client class
golismero/api/net/cache.py:69: Warning (W, _NetworkCache._clear_local_cache): Attribute '__cache' defined outside __init__
golismero/api/net/dns.py:35: Warning (W): Wildcard import data.information.dns
golismero/api/net/dns.py:44: Warning (W): Wildcard import dns.zone
golismero/api/net/dns.py:92: Warning (W, _DNS.check_tcp_dns): Catching too general exception Exception
golismero/api/net/dns.py:101: Warning (W, _DNS.resolve): Redefining built-in 'type'
golismero/api/net/dns.py:143: Error (E, _DNS.get_a): Undefined variable 'DnsRegisterA'
golismero/api/net/dns.py:182: Error (E, _DNS.get_aaaa): Undefined variable 'DnsRegisterAAAA'
golismero/api/net/dns.py:416: Warning (W, _DNS.zone_transfer): Used builtin function 'map'
golismero/api/net/dns.py:572: Warning (W, _DNS.zone_transfer): No exception type(s) specified
golismero/api/net/dns.py:646: Error (E, _DNS.get_ips): Undefined variable 'DnsRegister'
golismero/api/net/dns.py:685: Warning (W, _DNS._dnslib2register): Redefining built-in 'type'
golismero/api/net/dns.py:710: Error (E, _DNS._dnslib2register): Undefined variable 'DnsRegister'
golismero/api/net/dns.py:720: Error (E, _DNS._dnslib2register): Undefined variable 'DnsRegister'
golismero/api/net/dns.py:743: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterA'
golismero/api/net/dns.py:746: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterAAAA'
golismero/api/net/dns.py:749: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterAFSDB'
golismero/api/net/dns.py:752: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterCERT'
golismero/api/net/dns.py:758: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterCNAME'
golismero/api/net/dns.py:761: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterDNSKEY'
golismero/api/net/dns.py:763: Warning (W, _DNS.__dnsregister2golismeroregister): Access to a protected member _hexify of a client class
golismero/api/net/dns.py:767: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterDS'
golismero/api/net/dns.py:768: Warning (W, _DNS.__dnsregister2golismeroregister): Access to a protected member _hexify of a client class
golismero/api/net/dns.py:773: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterHINFO'
golismero/api/net/dns.py:777: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterIPSECKEY'
golismero/api/net/dns.py:784: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterISDN'
golismero/api/net/dns.py:788: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterLOC'
golismero/api/net/dns.py:794: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterMX'
golismero/api/net/dns.py:798: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterNAPTR'
golismero/api/net/dns.py:805: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterNS'
golismero/api/net/dns.py:808: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterNSAP'
golismero/api/net/dns.py:811: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'm_return_append'
golismero/api/net/dns.py:811: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterNSEC'
golismero/api/net/dns.py:814: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterNSEC3'
golismero/api/net/dns.py:817: Warning (W, _DNS.__dnsregister2golismeroregister): Access to a protected member _hexify of a client class
golismero/api/net/dns.py:820: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterNSEC3PARAM'
golismero/api/net/dns.py:823: Warning (W, _DNS.__dnsregister2golismeroregister): Access to a protected member _hexify of a client class
golismero/api/net/dns.py:826: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterPTR'
golismero/api/net/dns.py:829: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterRP'
golismero/api/net/dns.py:833: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterRRSIG'
golismero/api/net/dns.py:843: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterSIG'
golismero/api/net/dns.py:853: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterSOA'
golismero/api/net/dns.py:859: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterSPF'
golismero/api/net/dns.py:862: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterSRV'
golismero/api/net/dns.py:868: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterTXT'
golismero/api/net/dns.py:871: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterWKS'
golismero/api/net/dns.py:876: Error (E, _DNS.__dnsregister2golismeroregister): Undefined variable 'DnsRegisterX25'
golismero/api/net/dns.py:930: Warning (W, _DNS._make_request): Catching too general exception Exception
golismero/api/net/dns.py:44: Warning (W): Unused import from_xfr from wildcard import
golismero/api/net/dns.py:44: Warning (W): Unused import sys from wildcard import
golismero/api/net/dns.py:44: Warning (W): Unused import NoNS from wildcard import
golismero/api/net/dns.py:44: Warning (W): Unused import NoSOA from wildcard import
golismero/api/net/dns.py:44: Warning (W): Unused import UnknownOrigin from wildcard import
golismero/api/net/dns.py:44: Warning (W): Unused import from_file from wildcard import
golismero/api/net/dns.py:44: Warning (W): Unused import re from wildcard import
golismero/api/net/dns.py:44: Warning (W): Unused import generators from wildcard import
golismero/api/net/dns.py:44: Warning (W): Unused import BadZone from wildcard import
golismero/api/net/dns.py:44: Warning (W): Unused import from_text from wildcard import
golismero/api/net/http.py:278: Warning (W): FIXME: the depth level is broken!!!
golismero/api/net/http.py:317: Warning (W): FIXME the cache timestamps are broken!!!
golismero/api/net/http.py:418: Warning (W): FIXME: this fails for IPv6!
golismero/api/net/http.py:464: Warning (W): XXX TODO
golismero/api/net/http.py:263: Warning (W, _HTTP.make_request): Catching too general exception Exception
golismero/api/net/http.py:483: Warning (W, _HTTP.make_raw_request): Catching too general exception Exception
golismero/api/net/http.py:488: Warning (W, _HTTP.make_raw_request): Catching too general exception Exception
golismero/api/net/scraper.py:44: Warning (W): TODO:
golismero/api/net/scraper.py:135: Warning (W): FIXME
golismero/api/net/scraper.py:103: Warning (W, is_link): Catching too general exception Exception
golismero/api/net/web_utils.py:196: Warning (W): TODO: add support for FTP
golismero/api/net/web_utils.py:224: Warning (W): TODO: parse the Content-Disposition header.
golismero/api/net/web_utils.py:585: Warning (W): TODO: for the time being we're using the buggy quote and unquote
golismero/api/net/web_utils.py:855: Warning (W): TODO: maybe use **kwargs so we can support 'case_sensitive' (common mistake),
golismero/api/net/web_utils.py:1108: Warning (W): TODO: according to this: https://en.wikipedia.org/wiki/URL_normalization
golismero/api/net/web_utils.py:1135: Warning (W): XXX DEBUG
golismero/api/net/web_utils.py:1286: Warning (W): TODO: roll back changes if it fails
golismero/api/net/web_utils.py:390: Error (E, check_auth): Instance of 'LookupDict' has no 'ok' member
golismero/api/net/web_utils.py:1134: Warning (W, ParsedURL.query): Catching too general exception Exception
golismero/api/net/web_utils.py:1128: Warning (W, ParsedURL.query): Used builtin function 'map'
golismero/api/net/web_utils.py:1151: Warning (W, ParsedURL.query_params): Attribute '__query_params' defined outside __init__
golismero/api/net/web_utils.py:1152: Warning (W, ParsedURL.query_params): Attribute '__query' defined outside __init__
golismero/api/net/web_utils.py:1051: Warning (W, ParsedURL.host): Attribute '__host' defined outside __init__
golismero/api/net/web_utils.py:1080: Warning (W, ParsedURL.path): Attribute '__path' defined outside __init__
golismero/api/net/web_utils.py:1066: Warning (W, ParsedURL.port): Attribute '__port' defined outside __init__
golismero/api/net/web_utils.py:1316: Warning (W, ParsedURL.auth): Attribute '__password' defined outside __init__
golismero/api/net/web_utils.py:1092: Warning (W, ParsedURL.fragment): Attribute '__fragment' defined outside __init__
golismero/api/net/web_utils.py:1315: Warning (W, ParsedURL.auth): Attribute '__username' defined outside __init__
golismero/api/net/web_utils.py:1651: Error (E, HTMLParser.title): Instance of 'ResultSet' has no 'name' member (but some types could not be inferred)
golismero/api/net/__init__.py:93: Warning (W): FIXME
golismero/api/net/__init__.py:89: Warning (W, ConnectionSlot.__enter__): Access to a protected member _context of a client class
golismero/api/net/__init__.py:97: Warning (W, ConnectionSlot.__exit__): Redefining built-in 'type'
golismero/api/net/__init__.py:98: Warning (W, ConnectionSlot.__exit__): Access to a protected member _context of a client class
golismero/api/net/__init__.py:89: Warning (W, ConnectionSlot.__enter__): Attribute '__token' defined outside __init__
golismero/api/text/text_utils.py:41: Warning (W): Uses of a deprecated module 'string'
golismero/api/text/wordlist_api.py:410: Warning (W, AdvancedListWordlist.clone): Access to a protected member __wordlist of a client class
golismero/api/text/wordlist_api.py:678: Warning (W, AdvancedDicWordlist.clone): Access to a protected member __wordlist of a client class
golismero/database/auditdb.py:936: Warning (W): TODO: optimize by checking multiple identities in the same query,
golismero/database/auditdb.py:1003: Warning (W): TODO: optimize by checking multiple identities in the same query,
golismero/database/auditdb.py:401: Warning (W, AuditMemoryDB): Method '_atom' is abstract in class 'BaseDB' but is not overridden
golismero/database/auditdb.py:401: Warning (W, AuditMemoryDB): Method 'dump' is abstract in class 'BaseDB' but is not overridden
golismero/database/auditdb.py:401: Warning (W, AuditMemoryDB): Method '_transaction' is abstract in class 'BaseDB' but is not overridden
golismero/database/auditdb.py:638: Warning (W, AuditSQLiteDB.__init__): Redefining name 'sqlite3' from outer scope (line 50)
golismero/database/auditdb.py:636: Warning (W, AuditSQLiteDB.__init__): Using global for 'sqlite3' but no assignment is done
golismero/database/auditdb.py:665: Warning (W, AuditSQLiteDB._atom): Used * or ** magic
golismero/database/auditdb.py:683: Warning (W, AuditSQLiteDB._transaction): Used * or ** magic
golismero/database/auditdb.py:1295: Warning (W, AuditSQLiteDB.close): Catching too general exception Exception
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'add_state_variable' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'get_data' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'get_pending_data' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'mark_stage_finished' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'add_data' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'has_data_key' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'remove_data' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'get_data_count' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'get_past_plugins' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'get_data_types' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'has_state_variable' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'get_state_variable' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'get_state_variable_names' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'get_data_keys' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'remove_state_variable' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'mark_plugin_finished' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'get_many_data' is abstract in class 'BaseAuditDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method '_atom' is abstract in class 'BaseDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'dump' is abstract in class 'BaseDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method 'close' is abstract in class 'BaseDB' but is not overridden
golismero/database/auditdb.py:1300: Warning (W, AuditDB): Method '_transaction' is abstract in class 'BaseDB' but is not overridden
golismero/database/cachedb.py:163: Warning (W, VolatileNetworkCache): Method '_atom' is abstract in class 'BaseDB' but is not overridden
golismero/database/cachedb.py:163: Warning (W, VolatileNetworkCache): Method '_transaction' is abstract in class 'BaseDB' but is not overridden
golismero/database/cachedb.py:231: Warning (W, PersistentNetworkCache.__init__): Redefining name 'sqlite3' from outer scope (line 46)
golismero/database/cachedb.py:229: Warning (W, PersistentNetworkCache.__init__): Using global for 'sqlite3' but no assignment is done
golismero/database/cachedb.py:246: Warning (W, PersistentNetworkCache._atom): Used * or ** magic
golismero/database/cachedb.py:261: Warning (W, PersistentNetworkCache._transaction): Used * or ** magic
golismero/database/cachedb.py:390: Warning (W, PersistentNetworkCache.close): Catching too general exception Exception
golismero/database/common.py:46: Warning (W, transactional): Access to a protected member _transaction of a client class
golismero/database/common.py:55: Warning (W, atomic): Access to a protected member _atom of a client class
golismero/database/common.py:67: Warning (W, BaseDB.__exit__): Redefining built-in 'type'
golismero/main/console.py:97: Warning (W): XXX TODO:
golismero/main/console.py:204: Warning (W, _get_terminal_size_windows): No exception type(s) specified
golismero/main/console.py:208: Warning (W, _get_terminal_size_windows): Unused variable 'curx'
golismero/main/console.py:208: Warning (W, _get_terminal_size_windows): Unused variable 'cury'
golismero/main/console.py:209: Warning (W, _get_terminal_size_windows): Unused variable 'maxy'
golismero/main/console.py:208: Warning (W, _get_terminal_size_windows): Unused variable 'bufy'
golismero/main/console.py:208: Warning (W, _get_terminal_size_windows): Unused variable 'bufx'
golismero/main/console.py:209: Warning (W, _get_terminal_size_windows): Unused variable 'maxx'
golismero/main/console.py:208: Warning (W, _get_terminal_size_windows): Unused variable 'wattr'
golismero/main/console.py:228: Warning (W, _get_terminal_size_tput): No exception type(s) specified
golismero/main/console.py:236: Warning (W, _get_terminal_size_linux.ioctl_GWINSZ): No exception type(s) specified
golismero/main/console.py:234: [F, _get_terminal_size_linux.ioctl_GWINSZ] Unable to import 'fcntl'
golismero/main/console.py:234: [F, _get_terminal_size_linux.ioctl_GWINSZ] Unable to import 'termios'
golismero/main/console.py:246: Warning (W, _get_terminal_size_linux): No exception type(s) specified
golismero/main/console.py:243: Error (E, _get_terminal_size_linux): Module 'os' has no 'ctermid' member
golismero/main/console.py:253: Warning (W, _get_terminal_size_linux): No exception type(s) specified
golismero/main/console.py:293: Warning (W, Console._display): Catching too general exception Exception
golismero/main/console.py:349: Warning (W, Console._display_error): Catching too general exception Exception
golismero/main/orchestrator.py:444: Warning (W): TODO: maybe this should be done by the UI plugins instead?
golismero/main/orchestrator.py:473: Warning (W): FIXME
golismero/main/orchestrator.py:497: Warning (W): TODO: dump any pending messages and store the current state.
golismero/main/orchestrator.py:85: Error (E, Orchestrator.__init__): Instance of 'SyncManager' has no 'Queue' member
golismero/main/orchestrator.py:91: Warning (W, Orchestrator.__init__): Access to a protected member _context of a client class
golismero/main/orchestrator.py:117: Warning (W, Orchestrator.__init__): Access to a protected member _orchestrator of a client class
golismero/main/orchestrator.py:167: Warning (W, Orchestrator.__exit__): Redefining built-in 'type'
golismero/main/orchestrator.py:249: Warning (W, Orchestrator.__control_c_handler): Catching too general exception Exception
golismero/main/orchestrator.py:232: Warning (W, Orchestrator.__control_c_handler): Unused argument 'frame'
golismero/main/orchestrator.py:232: Warning (W, Orchestrator.__control_c_handler): Unused argument 'signum'
golismero/main/orchestrator.py:268: Warning (W, Orchestrator.__panic_control_c_handler): Catching too general exception Exception
golismero/main/orchestrator.py:259: Warning (W, Orchestrator.__panic_control_c_handler): Unused argument 'frame'
golismero/main/orchestrator.py:259: Warning (W, Orchestrator.__panic_control_c_handler): Unused argument 'signum'
golismero/main/orchestrator.py:462: Warning (W, Orchestrator.run): Catching too general exception Exception
golismero/main/orchestrator.py:481: Warning (W, Orchestrator.run): Catching too general exception Exception
golismero/main/orchestrator.py:494: Warning (W, Orchestrator.close): No exception type(s) specified
golismero/main/orchestrator.py:503: Warning (W, Orchestrator.close): No exception type(s) specified
golismero/main/orchestrator.py:509: Warning (W, Orchestrator.close): No exception type(s) specified
golismero/main/orchestrator.py:513: Warning (W, Orchestrator.close): No exception type(s) specified
golismero/main/orchestrator.py:520: Warning (W, Orchestrator.close): Access to a protected member _context of a client class
golismero/managers/auditmanager.py:219: Warning (W): TODO: pause and resume audits, start new audits
golismero/managers/auditmanager.py:473: Warning (W): FIXME performance
golismero/managers/auditmanager.py:474: Warning (W): FIXME what about links?
golismero/managers/auditmanager.py:607: Warning (W): FIXME possible performance problem here!
golismero/managers/auditmanager.py:60: Warning (W, AuditManager.__init__): Unused argument 'config'
golismero/managers/auditmanager.py:117: Warning (W, AuditManager.new_audit): Catching too general exception Exception
golismero/managers/auditmanager.py:232: Warning (W, AuditManager.close): No exception type(s) specified
golismero/managers/auditmanager.py:396: Warning (W, Audit.run): Access to a protected member _context of a client class
golismero/managers/auditmanager.py:401: Warning (W, Audit.run): Access to a protected member _context of a client class
golismero/managers/auditmanager.py:410: Warning (W, Audit.run): Access to a protected member _context of a client class
golismero/managers/auditmanager.py:492: Warning (W, Audit.run): Access to a protected member _context of a client class
golismero/managers/auditmanager.py:651: Warning (W, Audit.dispatch_msg): Access to a protected member _context of a client class
golismero/managers/auditmanager.py:656: Warning (W, Audit.dispatch_msg): Access to a protected member _context of a client class
golismero/managers/auditmanager.py:667: Warning (W, Audit.dispatch_msg): Access to a protected member _context of a client class
golismero/managers/auditmanager.py:761: Warning (W, Audit.__dispatch_msg): Access to a protected member _update_data of a client class
golismero/managers/auditmanager.py:407: Warning (W, Audit.run): Attribute '__audit_scope' defined outside __init__
golismero/managers/importmanager.py:141: Warning (W, ImportManager.import_results): Catching too general exception Exception
golismero/managers/importmanager.py:135: Warning (W, ImportManager.import_results): Access to a protected member _context of a client class
golismero/managers/importmanager.py:137: Warning (W, ImportManager.import_results): Access to a protected member _context of a client class
golismero/managers/importmanager.py:140: Warning (W, ImportManager.import_results): Access to a protected member _context of a client class
golismero/managers/networkmanager.py:133: Warning (W, NetworkManager.release_slot): Catching too general exception Exception
golismero/managers/pluginmanager.py:925: Warning (W): TODO: find each circle in the graph and show it,
golismero/managers/pluginmanager.py:221: Warning (W, PluginInfo.__init__): Catching too general exception Exception
golismero/managers/pluginmanager.py:225: Warning (W, PluginInfo.__init__): Catching too general exception Exception
golismero/managers/pluginmanager.py:229: Warning (W, PluginInfo.__init__): Catching too general exception Exception
golismero/managers/pluginmanager.py:233: Warning (W, PluginInfo.__init__): Catching too general exception Exception
golismero/managers/pluginmanager.py:237: Warning (W, PluginInfo.__init__): Catching too general exception Exception
golismero/managers/pluginmanager.py:245: Warning (W, PluginInfo.__init__): Catching too general exception Exception
golismero/managers/pluginmanager.py:300: Warning (W, PluginInfo.__init__): Catching too general exception Exception
golismero/managers/pluginmanager.py:304: Warning (W, PluginInfo.__init__): Catching too general exception Exception
golismero/managers/pluginmanager.py:308: Warning (W, PluginInfo.__init__): Catching too general exception Exception
golismero/managers/pluginmanager.py:312: Warning (W, PluginInfo.__init__): Catching too general exception Exception
golismero/managers/pluginmanager.py:316: Warning (W, PluginInfo.__init__): Catching too general exception Exception
golismero/managers/pluginmanager.py:320: Warning (W, PluginInfo.__init__): Catching too general exception Exception
golismero/managers/pluginmanager.py:327: Warning (W, PluginInfo.__init__): Catching too general exception Exception
golismero/managers/pluginmanager.py:331: Warning (W, PluginInfo.__init__): Access to a protected member _has_context of a client class
golismero/managers/pluginmanager.py:400: Warning (W, PluginManager): Used * or ** magic
golismero/managers/pluginmanager.py:401: Warning (W, PluginManager): Used * or ** magic
golismero/managers/pluginmanager.py:523: Warning (W, PluginManager.find_plugins): Catching too general exception Exception
golismero/managers/pluginmanager.py:850: Warning (W, PluginManager.load_plugin_by_name): Access to a protected member _fix_classname of a client class
golismero/managers/pluginmanager.py:420: Warning (W, PluginManager.reset): Attribute '__cache' defined outside __init__
golismero/managers/pluginmanager.py:684: Warning (W, PluginManager.apply_black_and_white_lists): Attribute '__plugins' defined outside __init__
golismero/managers/pluginmanager.py:941: Warning (W, PluginManager.calculate_dependencies): Attribute '__stages' defined outside __init__
golismero/managers/pluginmanager.py:940: Warning (W, PluginManager.calculate_dependencies): Attribute '__batches' defined outside __init__
golismero/managers/processmanager.py:175: Warning (W): TODO: hook stdout and stderr to catch print statements
golismero/managers/processmanager.py:73: Warning (W, Process.daemon): Arguments number differs from overridden method
golismero/managers/processmanager.py:77: Warning (W, Process.daemon): Arguments number differs from overridden method
golismero/managers/processmanager.py:82: Warning (W, Pool): Method '__reduce__' is abstract in class 'Pool' but is not overridden
golismero/managers/processmanager.py:98: Warning (W, do_nothing): Unused argument 'argd'
golismero/managers/processmanager.py:98: Warning (W, do_nothing): Unused argument 'argv'
golismero/managers/processmanager.py:122: Warning (W, _launcher): No exception type(s) specified
golismero/managers/processmanager.py:133: Warning (W, _launcher): Used * or ** magic
golismero/managers/processmanager.py:140: Warning (W, _launcher): No exception type(s) specified
golismero/managers/processmanager.py:265: Warning (W, _bootstrap): No exception type(s) specified
golismero/managers/processmanager.py:254: Warning (W, _bootstrap): Catching too general exception Exception
golismero/managers/processmanager.py:160: Warning (W, _bootstrap): Access to a protected member _context of a client class
golismero/managers/processmanager.py:178: Warning (W, _bootstrap): Access to a protected member _initialize of a client class
golismero/managers/processmanager.py:181: Warning (W, _bootstrap): Access to a protected member _clear_local_cache of a client class
golismero/managers/processmanager.py:187: Warning (W, _bootstrap): Access to a protected member _update_plugin_path of a client class
golismero/managers/processmanager.py:214: Warning (W, _bootstrap): Used * or ** magic
golismero/managers/processmanager.py:233: Warning (W, _bootstrap): Catching too general exception Exception
golismero/managers/processmanager.py:247: Warning (W, _bootstrap): Catching too general exception Exception
golismero/managers/processmanager.py:277: Warning (W, _bootstrap): No exception type(s) specified
golismero/managers/processmanager.py:493: Warning (W, PluginContext.send_msg): Used * or ** magic
golismero/managers/processmanager.py:546: Error (E, PluginContext.remote_call): Instance of 'SyncManager' has no 'Queue' member
golismero/managers/processmanager.py:559: Warning (W, PluginContext.remote_call): No exception type(s) specified
golismero/managers/processmanager.py:569: Warning (W, PluginContext.remote_call): Catching too general exception Exception
golismero/testing.py:208: Warning (W, PluginTester.run_plugin): Attribute '_PluginContext__plugin_info' defined outside __init__
golismero/managers/processmanager.py:682: Warning (W, PluginPoolManager.run_plugin): Access to a protected member _context of a client class
golismero/managers/processmanager.py:686: Warning (W, PluginPoolManager.run_plugin): Access to a protected member _context of a client class
golismero/managers/processmanager.py:761: Error (E, PluginLauncher.__init__): Instance of 'SyncManager' has no 'Queue' member
golismero/managers/processmanager.py:832: Warning (W, PluginLauncher.stop): Catching too general exception Exception
golismero/managers/processmanager.py:890: Warning (W, ProcessManager.run_plugin): Access to a protected member _context of a client class
golismero/managers/processmanager.py:894: Warning (W, ProcessManager.run_plugin): Access to a protected member _context of a client class
golismero/managers/processmanager.py:943: Warning (W, _suicide): Unused argument 'frame'
golismero/managers/processmanager.py:943: Warning (W, _suicide): Unused argument 'signum'
golismero/managers/reportmanager.py:133: Warning (W, ReportManager.generate_reports): Catching too general exception Exception
golismero/managers/rpcmanager.py:69: Warning (W): TODO: use introspection to validate the function signature
golismero/managers/rpcmanager.py:65: Warning (W, _add_implementor): Catching too general exception Exception
golismero/managers/rpcmanager.py:91: Warning (W, rpc_bulk): Used builtin function 'map'
golismero/managers/rpcmanager.py:166: Warning (W, RPCManager.execute_rpc): Catching too general exception Exception
golismero/managers/rpcmanager.py:163: Warning (W, RPCManager.execute_rpc): Used * or ** magic
golismero/managers/rpcmanager.py:196: Warning (W, RPCManager.__prepare_exception): Catching too general exception Exception
golismero/managers/rpcmanager.py:200: Warning (W, RPCManager.__prepare_exception): Catching too general exception Exception
golismero/managers/uimanager.py:69: Warning (W, UIManager.__init__): Access to a protected member _set_observer of a client class
golismero/messaging/message.py:39: Warning (W): Wildcard import codes
golismero/messaging/message.py:39: Warning (W): Unused import MSG_CODES from wildcard import
golismero/messaging/notifier.py:230: Warning (W): XXX DEBUG
golismero/messaging/notifier.py:380: Warning (W): FIXME this is very inefficient!
golismero/messaging/notifier.py:549: Warning (W): XXXXXXXXXXXXXXXXXXXXXXX NOTE XXXXXXXXXXXXXXXXXXXXXXX
golismero/messaging/notifier.py:685: Warning (W): FIXME: maybe we want to raise an exception here instead.
golismero/messaging/notifier.py:708: Warning (W): XXX this allows UI plugins to have state, do we really want this?
golismero/messaging/notifier.py:701: Warning (W, UINotifier.__run_plugin): Access to a protected member _context of a client class
golismero/messaging/notifier.py:705: Warning (W, UINotifier.__run_plugin): Access to a protected member _context of a client class
golismero/messaging/notifier.py:710: Warning (W, UINotifier.__run_plugin): Access to a protected member _context of a client class
golismero/messaging/notifier.py:712: Warning (W, UINotifier.__run_plugin): Access to a protected member _context of a client class
golismero/messaging/notifier.py:715: Warning (W, UINotifier.__run_plugin): Access to a protected member _context of a client class
""".split("\n")[1:]



# Run the test from the command line.
if __name__ == "__main__":
    test_pylint()
