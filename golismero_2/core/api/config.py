#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Author: Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com

Golismero project site: http://code.google.com/p/golismero/
Golismero project mail: golismero.project@gmail.com

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

__all__ = ["Config"]

from ..main.commonstructures import Singleton

class Config (Singleton):

    @property
    def audit_name(self):
        "str -- Audit name."
        return self.__audit_name

    @property
    def audit_config(self):
        "GlobalConfig -- Audit config."
        return self.__audit_config

    @property
    def plugin_info(self):
        "PluginInfo -- Plugin information."
        return self.__plugin_info

    @property
    def plugin_config(self):
        "dict -- Plugin configuration."
        return self.__plugin_info.plugin_config

    def _set_config(self, audit_name, audit_config, plugin_info):
        self.__audit_name   = audit_name
        self.__audit_config = audit_config
        self.__plugin_info  = plugin_info
