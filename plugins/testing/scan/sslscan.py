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

from os.path import join, split, sep
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
        results, count = SSLScanPlugin.parse_sslscan_results(input_file)
        if results:
            Database.async_add_many(results)
            Logger.log("Loaded %d hosts and %d vulnerabilities from file: %s" %
                       (len(results) - count, count, input_file))
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

        # Detect sslscan-win bug #2:
        # https://code.google.com/p/sslscan-win/issues/detail?id=2
        if sep == "\\":
            from ctypes import windll, c_char_p, c_uint32, c_void_p, byref, create_string_buffer, Structure, sizeof, POINTER
            class VS_FIXEDFILEINFO (Structure):
                _fields_ = [
                    ("dwSignature",         c_uint32),     # 0xFEEF04BD
                    ("dwStrucVersion",      c_uint32),
                    ("dwFileVersionMS",     c_uint32),
                    ("dwFileVersionLS",     c_uint32),
                    ("dwProductVersionMS",  c_uint32),
                    ("dwProductVersionLS",  c_uint32),
                    ("dwFileFlagsMask",     c_uint32),
                    ("dwFileFlags",         c_uint32),
                    ("dwFileOS",            c_uint32),
                    ("dwFileType",          c_uint32),
                    ("dwFileSubtype",       c_uint32),
                    ("dwFileDateMS",        c_uint32),
                    ("dwFileDateLS",        c_uint32),
                ]
            def GetFileVersionInfo(lptstrFilename):
                _GetFileVersionInfoA = windll.version.GetFileVersionInfoA
                _GetFileVersionInfoA.argtypes = [c_char_p, c_uint32, c_uint32, c_void_p]
                _GetFileVersionInfoA.restype  = bool
                _GetFileVersionInfoSizeA = windll.version.GetFileVersionInfoSizeA
                _GetFileVersionInfoSizeA.argtypes = [c_char_p, c_void_p]
                _GetFileVersionInfoSizeA.restype  = c_uint32
                _VerQueryValueA = windll.version.VerQueryValueA
                _VerQueryValueA.argtypes = [c_void_p, c_char_p, c_void_p, POINTER(c_uint32)]
                _VerQueryValueA.restype  = bool
                dwLen = _GetFileVersionInfoSizeA(lptstrFilename, None)
                if dwLen:
                    lpData = create_string_buffer(dwLen)
                    if _GetFileVersionInfoA(lptstrFilename, 0, dwLen, byref(lpData)):
                        lpFileInfo = POINTER(VS_FIXEDFILEINFO)()
                        uLen = c_uint32(sizeof(lpFileInfo))
                        if _VerQueryValueA(lpData, "\\", byref(lpFileInfo), byref(uLen)):
                            sFileInfo = lpFileInfo.contents
                            if sFileInfo.dwSignature == 0xFEEF04BD:
                                return sFileInfo
            def LOWORD(x):
                return x & 0xFFFF
            def HIWORD(x):
                return (x >> 16) & 0xFFFF
            filename = find_binary_in_path("sslscan")[0]
            filename = split(filename)[0]
            filename = join(filename, "libeay32.dll")
            vinfo = GetFileVersionInfo(filename)
            if not vinfo:
                return # skip check if no file version info present
            ms = vinfo.dwFileVersionMS
            ls = vinfo.dwFileVersionLS
            a = HIWORD(ms)
            b = LOWORD(ms)
            c = HIWORD(ls)
            d = LOWORD(ls)
            if not (
                a > 0 or
                b > 9 or
                c > 8 or
                d >= 20
            ):
                raise RuntimeError(
                    "This version of OpenSSL (%s.%s.%s.%s) has a bug on"
                    " Windows that causes a crash when run from GoLismero,"
                    " please replace it with a newer version from: "
                    "https://slproweb.com/products/Win32OpenSSL.html"
                    % (a, b, c, d)
                )


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

            # Run SSLScan and capture the text output.
            Logger.log("Launching SSLScan against: %s" % m_host)
            Logger.log_more_verbose("SSLScan arguments: %s" % " ".join(args))
            with ConnectionSlot(m_host):
                t1 = time()
                code = run_external_tool("sslscan", args, callback=Logger.log_verbose)
                t2 = time()
            if code:
                Logger.log_error(
                    "SSLScan execution failed, status code: %d" % code)
            else:
                Logger.log("SSLScan scan finished in %s seconds for target: %s"
                           % (t2 - t1, m_host))

            # Parse and return the results.
            r, v = self.parse_sslscan_results(output)
            if v:
                Logger.log("Found %s SSL vulnerabilities." % v)
            else:
                Logger.log("No SSL vulnerabilities found.")
            return r


    #--------------------------------------------------------------------------
    @staticmethod
    def parse_sslscan_results(output_filename):
        """
        Convert the output of a SSLScan run to the GoLismero data model.

        :param output_filename: Path to the output filename.
            The format should always be XML.
        :type output_filename:

        :returns: Results from the SSLScan scan, and the vulnerability count.
        :rtype: list(Domain|Vulnerability), int
        """
        results = []
        count   = 0
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
                tree = ET.fromstring(m_text)
            except ET.ParseError, e:
                Logger.log_error("Error parsing XML file: %s" % str(e))
                return results, count

            # For each scan result...
            try:
                tags = tree.findall(".//ssltest")
            except Exception, e:
                tb = format_exc()
                Logger.log_error("Error parsing XML file: %s" % str(e))
                Logger.log_error_more_verbose(tb)
                return results, count
            for t in tags:
                try:

                    # Get the target hostname.
                    info = Domain( t.get("host") )
                    results.append(info)

                    # Get the ciphers.
                    m_ciphers = [
                        Ciphers(version = c.get("sslversion"),
                                bits    = c.get("bits"),
                                cipher  = c.get("cipher"))
                        for c in t.findall(".//cipher")
                        if c.get("status") == "accepted"
                    ]

                    # Get CERT dates.
                    m_valid_before      = re.search("([a-zA-Z:0-9\s]+)( GMT)", t.find(".//not-valid-before").text).group(1)
                    m_valid_after       = re.search("([a-zA-Z:0-9\s]+)( GMT)", t.find(".//not-valid-after").text).group(1)
                    m_valid_before_date = datetime.strptime(m_valid_before, "%b %d %H:%M:%S %Y")
                    m_valid_after_date  = datetime.strptime(m_valid_after, "%b %d %H:%M:%S %Y")

                    # Get subject.
                    m_cn                = re.search("(CN=)([0-9a-zA-Z\.\*]+)", t.find(".//subject").text).group(2)

                    # Is self signed?
                    m_self_signed       = t.find(".//pk").get("error")

                    # Insecure algorithm?
                    c = [y.cipher for y in m_ciphers if "CBC" in y.cipher]
                    if c:
                        results.append( InsecureAlgorithm(info, c) )
                        count += 1

                    # Self-signed?
                    if m_self_signed:
                        results.append( InvalidCert(info) )
                        count += 1

                    # Valid CN?
                    if m_cn != info.hostname:
                        results.append( InvalidCommonName(info, m_cn) )
                        count += 1

                    # Weak keys?
                    k = [int(y.bits) for i in m_ciphers if int(y.bits) <= 56]
                    if k:
                        results.append( WeakKey(info, k) )
                        count += 1

                    # Obsolete protocol?
                    c = [y.version for y in m_ciphers if "SSLv1" in y.version]
                    if c:
                        results.append( ObsoleteProtocol(info, "SSLv1") )
                        count += 1

                    # Outdated?
                    if m_valid_after_date < m_valid_before_date:
                        results.append( OutdatedCert(info) )
                        count += 1

                # On error, log the exception and continue.
                except Exception, e:
                    tb = format_exc()
                    Logger.log_error_verbose(str(e))
                    Logger.log_error_more_verbose(tb)

        # On error, log the exception.
        except Exception, e:
            tb = format_exc()
            Logger.log_error_verbose(str(e))
            Logger.log_error_more_verbose(tb)

        # Return the results and the vulnerability count.
        return results, count
