#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

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

from golismero.api.config import Config
from golismero.api.data.resource.domain import Domain
from golismero.api.data.resource.url import Url
from golismero.api.data.vulnerability.injection.sql_injection import SQLInjection
from golismero.api.data.vulnerability.injection.xss import XSS
from golismero.api.logger import Logger
from golismero.api.plugin import TestingPlugin
from golismero.api.text.text_utils import to_utf8
from golismero.api.net.web_utils import parse_url

import requests
import traceback
import warnings


#------------------------------------------------------------------------------
class PunkSPIDER(TestingPlugin):
    """
    This plugin tries to perform passive reconnaissance on a target using
    the PunkSPIDER vulnerability lookup engine.
    """


    #--------------------------------------------------------------------------
    def get_accepted_info(self):
        return [Domain]


    #--------------------------------------------------------------------------
    def recv_info(self, info):

        # Get the hostname to search for.
        target = info.hostname

        # Make the first query.
        page = 1
        r = self.query_punkspider_search(target, page)

        # Stop if we have no results.
        if not r:
            return

        # Get the summary.
        r = r["data"]

        # Get the total number of pages.
        total_pages = r["numberOfPages"]
        Logger.log("Found %d pages of search results." % total_pages)

        # Tell GoLismero how many pages we have to process.
        self.progress.set_total(total_pages)
        self.progress.min_delta = 1

        # This is where we'll collect the data we'll return.
        results = []

        # For each page in the response...
        while r:

            # For each result in the page...
            for x in r.get("domainSummaryDTOs", []):
                try:

                    # Skip if the result domain is in scope.
                    url = to_utf8(x["url"])
                    if url not in Config.audit_scope:
                        continue

                    # Skip if not exploitable.
                    if not x["exploitabilityLevel"]:
                        Logger.log_verbose(
                            "No known vulnerabilities found for: %s" % url)
                        continue

                    # Log how many vulnerabilities were found.
                    m = "Known vulnerabilities found for %r: " % url
                    if x["xss"]:
                        m += "%d XSS, " % x["xss"]
                    if x["sqli"]:
                        m += "%d SQL injections, " % x["sqli"]
                    if x["bsqli"]:
                        m += "%d blind SQL injections, " % x["bsqli"]
                    if m.endswith(", "):
                        m = m[:-2] + "."
                    Logger.log(m)

                    # Get the details.
                    host_id = to_utf8(x["id"])
                    host_id = parse_url(host_id).hostname
                    host_id = ".".join(reversed(host_id.split(".")))
                    d = self.query_punkspider_details(host_id)

                    # For each vulnerability...
                    for v in d["data"]:
                        try:

                            # Skip if the protocol isn't "http".
                            # We don't know how to handle those (yet).
                            if v["protocol"] != "http":
                                Logger.log_more_verbose(
                                    "Skipped non-HTTP vulnerability: %s"
                                    % to_utf8(v["id"]))
                                continue

                            # Get the vulnerable URL and parameter.
                            url = to_utf8(v["vulnerabilityUrl"])
                            param = to_utf8(v["parameter"])

                            # Parse the URL.
                            parsed = parse_url(url)

                            # Get the payload.
                            payload = parsed.query_params[param]

                            # Get the level.
                            level = to_utf8(v["level"])

                            # Create the Url object.
                            url_o = Url(url)
                            results.append(url_o)

                            # Get the vulnerability class.
                            if v["bugType"] == "xss":
                                clazz = XSS
                            else:
                                clazz = SQLInjection

                            # Create the Vulnerability object.
                            vuln = clazz(
                                url = url_o,
                                vulnerable_params = { param: payload },
                                injection_point = clazz.INJECTION_POINT_URL,
                                injection_type = to_utf8(v["bugType"]), # FIXME
                                level = level,
                                tool_id = to_utf8(v["id"]),
                            )
                            results.append(vuln)

                        # Log errors.
                        except Exception, e:
                            tb = traceback.format_exc()
                            Logger.log_error_verbose(str(e))
                            Logger.log_error_more_verbose(tb)

                # Log errors.
                except Exception, e:
                    tb = traceback.format_exc()
                    Logger.log_error_verbose(str(e))
                    Logger.log_error_more_verbose(tb)

            # Tell GoLismero we finished a result page.
            self.progress.add_completed(1)

            # Get the next page.
            page += 1
            if page >= total_pages:
                break
            r = self.query_punkspider_search(target, page)

        # If we couldn't get all the pages, something went wrong.
        if page < total_pages:
            Logger.log_error("Only got %d pages (from a total of %d),"
                             " some results may have been lost!"
                             % (page, total_pages))

        # Log how many vulnerabilities we found.
        count = int(len(results) / 2)
        if count == 0:
            Logger.log("No vulnerabilities found.")
        elif count == 1:
            Logger.log("Found one vulnerability.")
        else:
            Logger.log("Found %d vulnerabilities." % count)

        # Return the results.
        return results


    #--------------------------------------------------------------------------
    # The PunkSPIDER API.

    SUMMARY_URL = (
        "http://punkspider.hyperiongray.com/service/search/domain/?"
        "searchkey=url&"
        "searchvalue=.%s/&"
        "pagesize=10&"
        "pagenumber=%d&"
        "filtertype=AND"
    )
    DETAILS_URL = (
        "http://punkspider.hyperiongray.com/service/search/detail/%s"
    )
    HEADERS = {
        "Accept": "*/*",
        "Referer": "http://punkspider.hyperiongray.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64)"
                      " AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/31.0.1650.63 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    def __query_punkspider(self, url):
        try:
            r = requests.get(url,
                             headers = self.HEADERS)
            assert r.headers["Content-Type"].startswith("application/json"),\
                "Response from server is not a JSON encoded object"
            return r.json()
        except requests.RequestException, e:
            Logger.log_error(
                "Query to PunkSPIDER failed, reason: %s" % str(e))

    def query_punkspider_search(self, hostname, page = 1):
        return self.__query_punkspider(self.SUMMARY_URL % (hostname, page))

    def query_punkspider_details(self, host_id):
        return self.__query_punkspider(self.DETAILS_URL % host_id)
