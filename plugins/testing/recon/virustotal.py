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
from golismero.api.data.information.binary import Binary
from golismero.api.data.resource.url import URL, BaseURL
from golismero.api.data.vulnerability.suspicious.url import SuspiciousURL
from golismero.api.logger import Logger
from golismero.api.plugin import TestingPlugin
from golismero.api.text.text_utils import to_utf8

from hashlib import md5
from requests import request

import traceback


#------------------------------------------------------------------------------
class VirusTotalPlugin(TestingPlugin):
    """
    Integration with VirusTotal.
    """


    #--------------------------------------------------------------------------
    def check_params(self):

        # Make sure we have an API key.
        self.get_api_key()

        # Make sure we have to process at least one data type.
        assert self.get_accepted_types(), "No actions requested"


    #--------------------------------------------------------------------------
    def get_accepted_types(self):

        # We'll decide what data types we want based on the configuration.
        accepted_types = []

        # If we must send URLs, request the corresponding type.
        send_urls = Config.plugin_args.get("urls", "suspicious")
        send_urls = send_urls.strip().lower()
        if send_urls == "all":
            accepted_types.append(URL)
        elif send_urls == "base":
            accepted_types.append(BaseURL)
        elif send_urls == "suspicious":
            accepted_types.append(SuspiciousURL)
        elif send_urls != "none":
            raise ValueError("Invalid value for 'urls': %r" % send_urls)

        # If we must send hashes, request the Binary type.
        send_hashes = Config.audit_config.boolean(
            Config.plugin_args.get("hashes", "yes"))
        if send_hashes:
            accepted_types.append(Binary)

        # Tell GoLismero what data types we want to receive.
        return accepted_types


    #--------------------------------------------------------------------------
    def run(self, info):

        # This is where we'll collect the data we'll return.
        results = []

        # If it's a file...
        if isinstance(info, Binary):

            # Send a hash of the file.
            h = md5()
            h.update(info[1].raw_data)
            params = {
                "resource": h.hexdigest(),
                "allinfo": "1",
            }
            r = self.get("file/report", params)

            # If we found a report, process it.
            if int(r.response_code) == 1:
                results.extend( self.parse_response(r) )

        # If it's an URL...
        else:

            # Send the URL.
            params = {
                "url": info.url,
                "scan": "0",
            }
            r = self.get("url/report", params)

            # If we found a report, process it.
            if int(r.response_code) == 1:
                results.extend( self.parse_response(r) )

        # Return the results.
        return results


    #--------------------------------------------------------------------------
    def get(self, path, params = None, files = None):
        return self.request("get", path, params, files)


    #--------------------------------------------------------------------------
    def post(self, path, params = None, files = None):
        return self.request("post", path, params, files)


    #--------------------------------------------------------------------------
    def request(self, method, path, params = None, files = None):

        # Sanitize the parameters.
        if not params:
            params = {}

        # Add the API key to the parameters.
        params["apikey"] = self.get_api_key()

        # If the key is not for the private API, slow down.
        private = Config.audit_config.boolean(
            Config.plugin_args.get("private", "yes"))
        if not private:
            self.slow_down()

        # Make the request. On HTTP errors raise an exception.
        # If we get a request rate limit error, slow down and retry.
        while True:
            resp = request(
                method = "get",
                url = "https://www.virustotal.com/vtapi/v2/" + path,
                params = params,
                files = files,
            )
            if resp.status_code != 200:
                if resp.status_code == 403:
                    raise RuntimeError(
                        "Your VirusTotal API key was revoked, or doesn't have"
                        " enough privileges for this operation.")
                if resp.status_code == 204:
                    Logger.log_error_more_verbose(
                        "Too many requests, slowing down...")
                    self.slow_down()
                    continue
                raise RuntimeError(
                    "Failed to call the VirusTotal API, make sure your"
                    " Internet connection is working properly.")

            # Return the decoded JSON response data.
            return resp.json()


    #--------------------------------------------------------------------------
    def get_api_key(self):
        key = Config.plugin_args.get("apikey", None)
        if not key:
            key = Config.plugin_config.get("apikey", None)
        if not key:
            raise ValueError(
                "Missing API key! Get one at:"
                " https://www.virustotal.com/en/documentation/public-api/")
        return key


    #--------------------------------------------------------------------------
    def parse_results(self, json):

        # This is where we'll collect the data we'll return.
        results = []









        # Return the results.
        return results
