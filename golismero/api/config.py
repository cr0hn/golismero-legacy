#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------
# Plugin configuration API
#-----------------------------------------------------------------------

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

__doc__ = """
Global variable to access the current plugin and audit configuration.

Whenever a plugin accesses this object it will receive its own
configuration, including the current audit's name and settings.

Example:

    >>> from golismero.api.config import Config
    >>> Config.plugin_name
    'my_plugin_name'
"""

__all__ = ["Config"]

from ..common import Singleton

class _Config (Singleton):
    """
    Current plugin and audit configuration.

    Whenever a plugin accesses this object it will receive its own
    configuration, including the current audit's name and settings.
    """

    # The constructor tries to prevent the user
    # from instancing this class directly.
    def __init__(self):
        try:
            Config
            raise NotImplementedError("Use Config instead!")
        except NameError:
            pass

    @property
    def audit_name(self):
        """
        :returns: Name of the audit.
        :rtype: str
        """
        return self.__context.audit_name

    @property
    def audit_config(self):
        """
        :returns: Parameters of the audit.
        :rtype: AuditConfig
        """
        return self.__context.audit_config

    @property
    def plugin_info(self):
        """
        :returns: Plugin information.
        :rtype: PluginInfo
        """
        return self.__context.plugin_info

    @property
    def plugin_name(self):
        """
        :returns: Plugin name.
        :rtype: str
        """
        return self.plugin_info.plugin_name

    @property
    def plugin_module(self):
        """
        :returns: Module where the plugin was loaded from.
        :rtype: str
        """
        return self.plugin_info.plugin_module

    @property
    def plugin_class(self):
        """
        :returns: Class name of the plugin.
        :rtype: str
        """
        return self.plugin_info.plugin_class

    @property
    def plugin_config(self):
        """
        Plugin configuration.

        Here you will find all settings under the [Configuration]
        section in the plugin configuration file.

        :returns:
        :rtype: dict(str -> str)
        """
        return self.plugin_info.plugin_config

    @property
    def plugin_extra_config(self):
        """
        Plugin extra configuration.

        Here you will find all information in the plugin
        configuration file outside the following sections:

        * [Core]
        * [Documentation]

        >>> from golismero.api.config import Config
        >>> print open("suspicious_url.golismero").read()
        [Core]
        Name = Suspicious URL
        Module = suspicious_url.py
        Stage = Recon
        [Documentation]
        Description = Find suspicious words in URLs
        Author = Daniel Garcia Garcia (cr0hn)
        Version = 0.1
        Website = https://github.com/cr0hn/golismero/
        Copyright = Copyright (C) 2011-2013 GoLismero Project
        License = GNU Public License
        [Wordlist_middle]
        wordlist = golismero/warning_url.txt
        [Wordlist_extensions]
        wordlist = fuzzdb/Discovery/FilenameBruteforce/Extensions.Backup.fuzz.txt
        >>> Config.plugin_extra_config['Wordlist_middle']['wordlist']
        'golismero/warning_url.txt'
        >>> Config.plugin_extra_config['Wordlist_extensions']['wordlist']
        'fuzzdb/Discovery/FilenameBruteforce/Extensions.Backup.fuzz.txt'

        :returns: Map of configuration file sections to their settings and values.
        :rtype: dict(str -> dict(str -> str))
        """
        return self.plugin_info.plugin_extra_config

    # The following properties may only be used internally.

    @property
    def _context(self):
        """:returns: PluginContext"""
        return self.__context

    @_context.setter
    def _context(self, context):
        """:type context: PluginContext"""
        # TODO: check the call stack to make sure it's called only
        #       from pre-approved places.
        self.__context = context

# Instance the singleton.
Config = _Config()
