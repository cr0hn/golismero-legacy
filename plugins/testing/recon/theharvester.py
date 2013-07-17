#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integration with `theHarvester <https://code.google.com/p/theharvester/>`_.
"""

__license__ = """
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


from golismero.api.data import discard_data
from golismero.api.data.information.auth import Username
from golismero.api.data.resource.email import Email
from golismero.api.data.resource.domain import Domain
from golismero.api.config import Config
from golismero.api.logger import Logger
from golismero.api.net.web_utils import is_in_scope
from golismero.api.plugin import TestingPlugin

import imp
import functools
import os, os.path
import socket
import traceback
import warnings

# Delayed imports.
lib = None
discovery = None


#------------------------------------------------------------------------------
class HarvesterPlugin(TestingPlugin):
    """
    Integration with `theHarvester <https://code.google.com/p/theharvester/>`_.
    """


    #--------------------------------------------------------------------------
    def get_accepted_info(self):
        return [Domain]


    #--------------------------------------------------------------------------
    def recv_info(self, info):

        # Import theHarvester as a library the first time this plugin is run.
        global lib
        global discovery
        if None in (lib, discovery):
            cwd = os.path.abspath(os.path.split(__file__))
            lib = imp.load_module(
                name = "%s.lib" % __name__,
                pathname = os.path.join(cwd, "lib")
            )
            discovery = imp.load_module(
                name = "%s.discovery" % __name__,
                pathname = os.path.join(cwd, "discovery")
            )

        # Get the search parameters.
        word  = info.name
        limit = 100
        try:
            limit = int(Config.plugin_config.get("limit", str(limit)), 0)
        except ValueError:
            pass

        # Search every supported engine.
        all_emails, all_hosts, all_people = set(), set(), set()
        for engine in discovery.__all__:
            try:
                emails, hosts, people = self.search(engine, word, limit)
            except Exception, e:
                t = traceback.format_exc()
                m = "theHarvester raised an exception: %s\n%s"
                warnings.warn(m % (e, t))
            all_emails.update(address.lower() for address in emails if address)
            all_hosts.update(name.lower() for name in hosts if name)
            all_people.update(username for username in people if username)

        # Adapt the data into our model.
        results = []

        # Email addresses.
        for address in all_emails:
            try:
                data = Email(address)
            except Exception, e:
                warnings.warn("Cannot parse email address: %r" % address)
                continue
            if data.is_in_scope():
                data.add_resource(info)
                results.append(data)
                all_hosts.add(data.hostname)
                all_people.add(data.username)
            else:
                Logger.log_more_verbose("Email address out of scope: %s" % address)
                discard_data(data)

        # Hostnames.
        for name in all_hosts:
            if not is_in_scope("http://" + name):
                Logger.log_more_verbose("Hostname out of scope: %s" % name)
                continue
            try:
                real_name, aliaslist, addresslist = socket.gethostbyname_ex(name)
            except socket.error:
                continue
            all_names = set()
            all_names.add(name)
            all_names.add(real_name)
            all_names.update(aliaslist)
            for name in all_names:
                if name:
                    if not is_in_scope("http://" + name):
                        Logger.log_more_verbose("Hostname out of scope: %s" % name)
                        continue
                    data = Domain(name, *addresslist)
                    data.add_resource(info)
                    results.append(data)

        # Usernames.
        for username in all_people:
            data = Username(username)
            data.add_resource(info)
            results.append(data)

        # Return the data.
        return results


    #--------------------------------------------------------------------------
    @staticmethod
    def search(engine, word, limit = 100):
        """
        Run a theHarvester search on the given engine.

        :param engine: Search engine.
        :type engine: str

        :param word: Word to search for.
        :type word: str

        :param limit: Maximum number of results.
            Its exact meaning may depend on the search engine.
        :type limit: int

        :returns: All email addresses, hostnames and usernames collected.
        :rtype: tuple(list(str), list(str), list(str))
        """

        # This code tries to adapt to theHarvester's inconsistent API
        # the best it can. Most of the functions and modules somewhat
        # follow a pattern but some don't. Hopefully we won't have to
        # update this code too often as new versions come out. :(

        # TODO: add support for Google profiles

        # Get the search function.
        if engine.endswith("search"):
            engine = engine[:-6]
        if engine == "yandex":
            return [], []   # not working :P
        if engine == "bing":
            search_fn = functools.partial(discovery.bingsearch.search_bing, "no")
        if engine == "people123":
            search_fn = discovery.people123.search_123people
        else:
            search_mod = getattr(discovery,  "%ssearch"  % engine)
            search_fn  = getattr(search_mod, "search_%s" % engine)

        # Run the search.
        search = search_fn(word, limit, 0)

        # Extract the results.
        emails, hosts, people = [], [], []
        if hasattr(search, "get_emails"):
            try:
                emails = search.get_emails()
            except Exception, e:
                t = traceback.format_exc()
                m = "theHarvester (%s, get_emails) raised an exception: %s\n%s"
                warnings.warn(m % (engine, e, t))
        if hasattr(search, "get_hostnames"):
            try:
                hosts = search.get_hostnames()
            except Exception, e:
                t = traceback.format_exc()
                m = "theHarvester (%s, get_hostnames) raised an exception: %s\n%s"
                warnings.warn(m % (engine, e, t))
        if hasattr(search, "get_people"):
            try:
                people = search.get_people()
            except Exception, e:
                t = traceback.format_exc()
                m = "theHarvester (%s, get_people) raised an exception: %s\n%s"
                warnings.warn(m % (engine, e, t))

        # Return the results.
        return emails, hosts, people
