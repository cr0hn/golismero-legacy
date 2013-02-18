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

__all__ = ["PriscillaPluginManager"]

from thirdparty_libs.yapsy.PluginManager import PluginManager
from os import path, getcwd
from core.main.commonstructures import Singleton
from core.api.plugins.plugin import *

#
# TODO plugins shouldn't be loaded ONLY on startup!
#

class PriscillaPluginManager (Singleton):
    """Priscilla Plugin Manager"""


    #----------------------------------------------------------------------
    #
    # Private methods
    #
    #----------------------------------------------------------------------


    #----------------------------------------------------------------------
    def __init__(self):

        # Load plugins
        self.__load_plugins()


    #----------------------------------------------------------------------
    def __load_plugins(self):

        # Start the plugin manager
        self.__pluginManager = PluginManager()

        # Set directories where the plugins are
        self.__pluginManager.setPluginPlaces(self.__prepare_plugin_dirs())

        # Configure the categories
        self.__pluginManager.setCategoriesFilter(
            {
                "global"  : GlobalPlugin,
                "testing" : TestingPlugin,
                "ui"      : UIPlugin,
                "report"  : ReportPlugin,
            }
        )

        # Locate and load the plugins
        self.__pluginManager.locatePlugins()
        self.__pluginManager.loadPlugins()


    #----------------------------------------------------------------------
    def __prepare_plugin_dirs(self):
        """
        Collect all paths with plugins.

        :returns: list -- List of tuples (plugin_type, path)
        """

        # Path to this file
        m_base_path = path.abspath(__file__)                         # core/managers/priscillapluginmanager.py
        m_base_path = path.split(m_base_path)[0]                     # core/managers
        m_base_path = path.join(m_base_path, "..", "..", "plugins")  # core/managers/../../plugins
        m_base_path = path.abspath(m_base_path)

        # Absolute paths to plugins
        m_paths = [ path.join(m_base_path, m_category) for m_category in self.categories ]

        # Return paths
        return m_paths


    #----------------------------------------------------------------------
    #
    # Public methods
    #
    #----------------------------------------------------------------------


    #----------------------------------------------------------------------
    @property
    def categories(self):
        "Plugin categories."
        return (
            "testing",
            "report",
            "ui",
            "global",
        )


    #----------------------------------------------------------------------
    def get_plugins_by_category(self, plugin_list, category = "all"):
        """
        Get a plugin list from a list of names.

        :param plugin_list: List with names of plugins you want. Special value "all" gets all the plugins.
        :type plugin_list: list

        :param category: get plugin list from category specified. Valid values: all, ui, global, report, testing.
        :type category: str

        :returns: list -- List of plugin instances
        """

        # Get all plugins for the requested category
        all_plugins = self.get_all_plugins(category.lower())

        # Check for keyword "all"
        if "all" in map(str.lower, plugin_list):
            return all_plugins.values()

        # Collect the requested plugins
        return_plugin = list()
        for p in plugin_list:
            if p in all_plugins:
                return_plugin.append(all_plugins[p])
            else:
                raise KeyError()

        return return_plugin


    #----------------------------------------------------------------------
    def get_all_plugins(self, category = "all"):
        """
        Get all available plugins.

        :param category: the category of plugin to return. Valid values: all, ui, global, results, testing.
        :type category: str

        :returns: dict -- Mapping of plugin names to instances
        """
        m_plugins = dict()
        if category.lower() == "all":
            for i in self.__pluginManager.getAllPlugins():
                m_plugins[i.name] = i.plugin_object
        else:
            for i in self.__pluginManager.getPluginsOfCategory(category.lower()):
                m_plugins[i.name] = i.plugin_object

        return m_plugins


    #----------------------------------------------------------------------
    def get_all_plugin_descriptions(self):
        """
        Get the descriptions of all available plugins.

        :returns: dict -- Mapping of plugin names to descriptions
        """
        m_plugins = dict()
        for i in self.__pluginManager.getAllPlugins():
            m_plugins[i.name] = i.description
        return m_plugins


    #----------------------------------------------------------------------
    def get_plugin_by_name(self, pluginName):
        """
        Return a plugin instance.

        :param pluginName: plugin name
        :type pluginName: str
        :returns: Plugin
        """
        l_pluginName = pluginName.lower()
        if category.lower() == "all":
            for i in self.__pluginManager.getAllPlugins():
                if i.name.lower() == l_pluginName:
                    return i.plugin_object
        else:
            for i in self.__pluginManager.getPluginsOfCategory(category.lower()):
                if i.name.lower() == l_pluginName:
                    return i.plugin_object
        raise KeyError("Plugin not found: %s" % pluginName)
