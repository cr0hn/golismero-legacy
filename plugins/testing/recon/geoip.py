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

# Acknowledgements:
# Thank you Danito for pointing out the Freegeoip.net service!
# https://twitter.com/dan1t0

from golismero.api.data.information.geolocation import Geolocation
from golismero.api.data.information.traceroute import Traceroute
from golismero.api.data.resource.domain import Domain
from golismero.api.data.resource.ip import IP
from golismero.api.logger import Logger
from golismero.api.plugin import TestingPlugin
from golismero.api.net.web_utils import json_decode

import netaddr
import requests
import traceback

from geopy import geocoders


#------------------------------------------------------------------------------
class GeoIP(TestingPlugin):
    """
    This plugin tries to geolocate all IP addresses and domain names.
    """

    # TODO: this could be useful as a fallback if freegeoip.net fails:
    # http://linux.die.net/man/1/geoiplookup
    # https://github.com/ioerror/blockfinder


    #--------------------------------------------------------------------------
    def get_accepted_info(self):
        return [Domain, IP, Traceroute, Geolocation]


    #--------------------------------------------------------------------------
    def recv_info(self, info):

        # This is where we'll collect the data we'll return.
        results = []

        # Augment geolocation data obtained through other means.
        # (For example: image metadata)
        if info.is_instance(Geolocation):
            if not info.street_addr:
                street_addr = self.query_google(info.latitude, info.longitude)
                if street_addr:
                    info.street_addr = street_addr
                    #
                    # TODO: parse the street address
                    #
                    Logger.log("(%s, %s) is in %s" % \
                               (info.latitude, info.longitude, street_addr))
            return

        # Extract IPs and domains from traceroute results and geolocate them.
        if info.is_instance(Traceroute):
            hops = []
            for hop in info.hops:
                if hop is not None:
                    if hop.address:
                        hops.append( IP(hop.address) )
                    elif hop.hostname:
                        hops.append( Domain(hop.hostname) )
            results.extend(hops)
            for res in hops:
                r = self.recv_info(res)
                if r:
                    results.extend(r)
            return results

        # Get the IP address or domain name.
        # Skip unsupported targets.
        if info.is_instance(IP):
            if info.version != 4:
                return
            target = info.address
            parsed = netaddr.IPAddress(target)
            if parsed.is_loopback() or \
               parsed.is_private()  or \
               parsed.is_link_local():
                return
        elif info.is_instance(Domain):
            target = info.hostname
            if "." not in target:
                return
        else:
            assert False, type(info)

        # Query the freegeoip.net service.
        kwargs = self.query_freegeoip(target)
        if not kwargs:
            return

        # Remove the IP address from the response.
        address = kwargs.pop("ip")

        # Query the Google Geocoder.
        street_addr = self.query_google(
            kwargs["latitude"], kwargs["longitude"])
        if street_addr:
            kwargs["street_addr"] = street_addr

        # Create a Geolocation object.
        geoip = Geolocation(**kwargs)
        geoip.add_resource(info)
        results.append(geoip)

        # Log the location.
        try:
            Logger.log_verbose("%s is in %s" % (target, geoip))
        except Exception, e:
            fmt = traceback.format_exc()
            Logger.log_error("Error: %s" % str(e))
            Logger.log_error_more_verbose(fmt)

        # If we received a Domain object, create an IP object too.
        if info.resource_type == Domain.resource_type:
            ip = IP(address)
            ip.add_resource(info)
            ip.add_information(geoip)
            results.append(ip)

        # Return the results.
        return results


    #--------------------------------------------------------------------------
    @staticmethod
    def query_freegeoip(target):
        Logger.log_more_verbose("Querying freegeoip.net for: " + target)
        try:
            resp = requests.get("http://freegeoip.net/json/" + target)
            if resp.status_code == 200:
                return json_decode(resp.content)
            Logger.log_more_verbose(
                "Response from freegeoip.net for %s: %s" %
                    (target, resp.content))
        except Exception:
            raise RuntimeError(
                "Freegeoip.net webservice is not available,"
                " possible network error?"
            )


    #--------------------------------------------------------------------------
    @staticmethod
    def query_google(latitude, longitude):
        coordinates = "%s, %s" % (latitude, longitude)
        Logger.log_more_verbose(
            "Querying Google Geocoder for: %s" % coordinates)
        try:
            g = geocoders.GoogleV3()
            r = g.reverse(coordinates)
            if r:
                return r[0][0].encode("UTF-8")
        except Exception, e:
            fmt = traceback.format_exc()
            Logger.log_error_verbose("Error: %s" % str(e))
            Logger.log_error_more_verbose(fmt)
