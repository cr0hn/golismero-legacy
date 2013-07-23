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


from golismero.api.config import Config
from golismero.api.data import discard_data
from golismero.api.data.resource.domain import Domain
from golismero.api.data.resource.email import Email
from golismero.api.logger import Logger
from golismero.api.plugin import TestingPlugin

import imp
import functools
import os, os.path
import socket
import StringIO
import sys
import traceback
import warnings

# Import theHarvester as a library.
cwd = os.path.abspath(os.path.split(__file__)[0])
cwd = os.path.join(cwd, "theharvester")
sys.path.insert(0, cwd)
try:
    import lib
    import discovery
    from discovery import *
finally:
    sys.path.remove(cwd)
del cwd


#------------------------------------------------------------------------------
class HarvesterPlugin(TestingPlugin):
    """
    Integration with `theHarvester <https://code.google.com/p/theharvester/>`_.
    """


    # Supported theHarvester modules.
    SUPPORTED = (
        "google", "bing", "pgp", "exalead", # "yandex",
    )


    #--------------------------------------------------------------------------
    def get_accepted_info(self):
        return [Domain]


    #--------------------------------------------------------------------------
    def recv_info(self, info):

        # Get the search parameters.
        word  = info.name
        limit = 100
        try:
            limit = int(Config.plugin_config.get("limit", str(limit)), 0)
        except ValueError:
            pass

        # Search every supported engine.
        all_emails, all_hosts = set(), set()
        for engine in self.SUPPORTED:
            try:
                emails, hosts = self.search(engine, word, limit)
            except Exception, e:
                t = traceback.format_exc()
                m = "theHarvester raised an exception: %s\n%s"
                warnings.warn(m % (e, t))
                continue
            all_emails.update(address.lower() for address in emails if address)
            all_hosts.update(name.lower() for name in hosts if name)

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
            else:
                Logger.log_more_verbose("Email address out of scope: %s" % address)
                discard_data(data)

        # Hostnames.
        for name in all_hosts:
            if name not in Config.audit_scope:
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
                    if name not in Config.audit_scope:
                        Logger.log_more_verbose("Hostname out of scope: %s" % name)
                        continue
                    data = Domain(name, *addresslist)
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

        Logger.log_more_verbose("Searching on: %s" % engine)

        # Get the search class.
        if engine == "pgp":
            def search_fn(word, limit, start):
                return discovery.pgpsearch.search_pgp(word)
        else:
            search_mod = getattr(discovery,  "%ssearch"  % engine)
            search_fn  = getattr(search_mod, "search_%s" % engine)

        # Run the search, hiding all the prints.
        fd = StringIO.StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = fd, fd
            search = search_fn(word, limit, 0)
            if engine == "bing":
                search.process("no")
            else:
                search.process()
        finally:
            sys.stdout, sys.stderr = old_out, old_err

        # Extract the results.
        emails, hosts = [], []
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

        Logger.log_more_verbose(
            "Found %d emails and %d hostnames on %s for domain %s" %
            (len(emails), len(hosts), engine, word)
        )

        # Return the results.
        return emails, hosts
