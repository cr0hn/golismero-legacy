#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__ = """
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

from golismero.api.config import Config
from golismero.api.data.db import Database
from golismero.api.data.resource.domain import Domain
from golismero.api.data.resource.url import BaseUrl, Url
from golismero.api.data.vulnerability.ssl import SSLVulnerability
from golismero.api.data.vulnerability.ssl.insecure_algorithm import InsecureAlgorithm
from golismero.api.data.vulnerability.ssl.invalid_cert import InvalidCert
from golismero.api.data.vulnerability.ssl.obsolete_protocol import ObsoleteProtocol
from golismero.api.data.vulnerability.ssl.outdated_cert import OutdatedCert
from golismero.api.data.vulnerability.ssl.weak_key import WeakKey
from golismero.api.data.vulnerability.ssl.invalid_common_name import InvalidCommonName
from golismero.api.external import run_external_tool, \
     find_cygwin_binary_in_path, tempfile, find_binary_in_path
from golismero.api.logger import Logger
from golismero.api.net import ConnectionSlot
from golismero.api.plugin import ImportPlugin, TestingPlugin

from os.path import join, sep
from traceback import format_exc
from time import time

try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from collections import namedtuple
from datetime import datetime
from traceback import format_exc

import re


Ciphers = namedtuple("Ciphers", ["version", "bits", "cipher"])


#------------------------------------------------------------------------------
class SSLScanImportPlugin(ImportPlugin):


    #--------------------------------------------------------------------------
    def is_supported(self, input_file):
        if input_file and input_file.lower().endswith(".xml"):
            with open(input_file, "rU") as fd:
                return "SSLScan Results" in fd.read(1024)
        return False


    #--------------------------------------------------------------------------
    def import_results(self, input_file):
        results = SSLScanPlugin.parse_sslscan_results(None, input_file)
        if results:
            Database.async_add_many(results)
            Logger.log("Loaded %d elements from file: %s" %
                       (len(results), input_file))
        else:
            Logger.log_verbose("No data found in file: %s" % input_file)


#------------------------------------------------------------------------------
class SSLScanPlugin(TestingPlugin):


    #--------------------------------------------------------------------------
    def check_params(self):
        if not find_binary_in_path("sslscan"):
            if sep == "\\":
                url = "https://code.google.com/p/sslscan-win/"
            else:
                url = "http://sourceforge.net/projects/sslscan/"
            raise RuntimeError(
                "SSLScan not found! You can download it from: %s" % url)


    #--------------------------------------------------------------------------
    def get_accepted_info(self):
        return [Domain]


    #--------------------------------------------------------------------------
    def recv_info(self, info):

        m_host = info.hostname

        # Create a temporary output file.
        with tempfile(suffix = ".xml") as output:

            # Build the command line arguments.
            args = [
                "--no-failed",
                "--xml=%s" % output,
                m_host
            ]

            # Run SSLscan and capture the text output.
            Logger.log("Launching SSLscan against: %s" % m_host)
            Logger.log_more_verbose("SSLscan arguments: %s" % " ".join(args))
            with ConnectionSlot(m_host):
                t1 = time()
                code = run_external_tool("sslscan", args, callback=Logger.log_verbose)
                t2 = time()
            if code:
                Logger.log_error(
                    "SSLscan execution failed, status code: %d" % code)
            else:
                Logger.log("SSLscan scan finished in %s seconds for target: %s"
                           % (t2 - t1, m_host))

            # Parse and return the results.
            r = self.parse_sslscan_results(info, output)
            if r and len(r) > 1:
                Logger.log("Found %s SSL vulns." % len(r) - 1)
            else:
                Logger.log("No SSL vulns found.")
            return r


    #--------------------------------------------------------------------------
    @staticmethod
    def parse_sslscan_results(info, output_filename):
        """
        Convert the output of a SSLscan scan to the GoLismero data model.

        :param info: Data object to link all results to (optional).
        :type info: Domain | None

        :param output_filename: Path to the output filename.
            The format should always be XML.
        :type output_filename:

        :returns: Results from the SSLscan scan.
        :rtype: list(Vulnerability)
        """
        results = []
        try:

            # Read the XML file contents.
            with open(output_filename, "rU") as f:
                m_info = f.read()

            # Force conversion to UTF-8, or Latin-1 on failure.
            # This prevents XML parsing errors.
            try:
                m_text = m_info.encode("utf-8")
            except UnicodeDecodeError:
                m_text = m_info.decode("latin-1").encode("utf-8")

            # Parse the XML file.
            try:
                t = ET.fromstring(m_text)
            except ET.ParseError, e:
                Logger.log_error("Error parsing XML file: %s" % str(e))
                return results

            # Get the target hostname if not provided.
            if info is None:
                try:
                    info = Domain( t.find(".//ssltest").get("host") )
                except Exception, e:
                    tb = format_exc()
                    Logger.log_error("Error parsing XML file: %s" % str(e))
                    Logger.log_error_more_verbose(tb)
                    return results
                results.append(info)

            # Get the ciphers.
            try:
                m_ciphers = [
                    Ciphers(version = c.get("sslversion"),
                            bits    = c.get("bits"),
                            cipher  = c.get("cipher"))
                    for c in t.findall(".//cipher")
                ]
            except Exception, e:
                tb = format_exc()
                Logger.log_error("Error parsing XML file: %s" % str(e))
                Logger.log_error_more_verbose(tb)
                return results

            try:

                # Get CERT dates.
                m_valid_before      = re.search("([a-zA-Z:0-9\s]+)( GMT)", t.find(".//not-valid-before").text).group(1)
                m_valid_after       = re.search("([a-zA-Z:0-9\s]+)( GMT)", t.find(".//not-valid-after").text).group(1)
                m_valid_before_date = datetime.strptime(m_valid_before, "%b %d %H:%M:%S %Y")
                m_valid_after_date  = datetime.strptime(m_valid_after, "%b %d %H:%M:%S %Y")

                # Get subject.
                m_cn                = re.search("(CN=)([0-9a-zA-Z\.\*]+)", t.find(".//subject").text).group(2)

                # Is self signed?
                m_self_signed       = t.find(".//pk").get("error")

            except Exception, e:
                tb = format_exc()
                Logger.log_error("Error parsing XML file: %s" % str(e))
                Logger.log_error_more_verbose(tb)
                return results

            # Insecure algorithm?
            c = [y.cipher for y in m_ciphers if "CBC" in y.cipher]
            if len(c):
                results.append( InsecureAlgorithm(info, c) )

            # Self-signed?
            if m_self_signed:
                results.append( InvalidCert(info) )

            # Valid CN?
            if m_cn != info.hostname:
                results.append( InvalidCommonName(info, m_cn) )

            # Weak keys?
            k = [int(y.bits) for i in m_ciphers if int(y.bits) <= 56]
            if len(k):
                results.append( WeakKey(info, k) )

            # Obsolete protocol?
            c = [y.version for y in m_ciphers if "SSLv1" in y.version]
            if len(c):
                results.append( ObsoleteProtocol(info, "SSLv1") )

            # Outdated?
            if m_valid_after_date < m_valid_before_date:
                results.append( OutdatedCert(info) )

        # On error, log the exception.
        except Exception, e:
            tb = format_exc()
            Logger.log_error_verbose(str(e))
            Logger.log_error_more_verbose(tb)

        # Return the results.
        return results
