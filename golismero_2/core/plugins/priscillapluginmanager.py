#!/usr/bin/python

# -*- coding: utf-8 -*-
"""
GoLismero 2.0 - The web knife.

Copyright (C) 2011-2013 - Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com

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



from thirdparty_libs.yapsy.PluginManager import PluginManager
from os import path, getcwd
from core.api.plugins.plugin import TestingPlugin,GlobalPLugin,UIPlugin,ResultsPlugin

class PriscillaPluginManager(object):
    """"""


    #----------------------------------------------------------------------
    #
    # Private methods
    #
    #----------------------------------------------------------------------
    __instance = None
    def __new__(cls, *args, **kargs):
        """Structure for Singleton pattern"""
        if cls.__instance is not None:
            return cls.__instance
        else:
            cls.__instance = super(PriscillaPluginManager, cls).__new__(cls, *args, **kargs)
            return cls.__instance


    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        # Load plugins
        self.__load_plugins()


    #----------------------------------------------------------------------
    def __load_plugins(self):
        # start manager
        self.__pluginManager = PluginManager()
        # Set directories where plugins are
        self.__pluginManager.setPluginPlaces(self.__prepare_plugins_dirs())
        # Configure categories
        self.__pluginManager.setCategoriesFilter(
            {
                "global" : GlobalPLugin,
                "testing" : TestingPlugin,
                "ui" : UIPlugin,
                "result" : ResultsPlugin
            }
        )
        # Load plugins
        self.__pluginManager.locatePlugins()
        self.__pluginManager.loadPlugins()


    #----------------------------------------------------------------------
    def __prepare_plugins_dirs(self):
        """
        Collect al path with plugins and return an array with them.

        :returns: list -- dict as format (plugin_type, path)
        """

        # Path to this file

        m_relative_path = path.join(getcwd(), "plugins")
        m_paths = list()

        # Absolute paths to plugins
        m_paths.append(path.join(m_relative_path, "ui"))
        m_paths.append(path.join(m_relative_path, "global"))
        m_paths.append(path.join(m_relative_path, "results"))
        m_paths.append(path.join(m_relative_path, "testing"))

        return m_paths

    #----------------------------------------------------------------------
    #
    # Public methods
    #
    #----------------------------------------------------------------------
    def get_plugins(self, plugin_list):
        """
        Get a plugin list from a list of names.

        :param plugin_list: List with names of plugins you want.
        :type plugin_list: list

        :returns: list -- list of plugin instances
        """

        # Check for keyword "all"
        if "all" in plugin_list or "All" in plugin_list:
            return self.get_all_plugins().values()

        return_plugin = list()
        if plugin_list:
            for name, plugin_obj in self.get_all_plugins():
                for p in plugin_list:
                    if name is p:
                        return_plugin.append(plugin_obj)

        return return_plugin

    #----------------------------------------------------------------------
    def get_all_plugins(self):
        """
        Get all available plugins

        :returns: dict -- List with all plugins as format (name, plugin_instance)
        """
        for i in self.__pluginManager.getAllPlugins():
            m_plugins[i.name] = i.plugin_object

        return m_plugins


    #----------------------------------------------------------------------
    def get_all_plugins_descriptions(self):
        """Get all descriptions available plugins

        :returns: dict -- List with all plugins as (name, description)
        """

        for i in self.__pluginManager.getAllPlugins():
            m_plugins[i.name] = i.description

        return m_plugins

    #----------------------------------------------------------------------
    def get_plugin_by_name(self, pluginName):
        """
        Return an instance os IPlugin

        :param pluginName: plugin name
        :type pluginName: str
        :returns: IPlugin
        :raises: ValueError
        """
        plugin_name = list()
        plugin_name.append(self.__pluginManager.getPluginByName(pluginName, "global"))
        plugin_name.append(self.__pluginManager.getPluginByName(pluginName, "testing"))
        plugin_name.append(self.__pluginManager.getPluginByName(pluginName, "ui"))
        plugin_name.append(self.__pluginManager.getPluginByName(pluginName, "results"))
        return plugin_name.pop()

    #----------------------------------------------------------------------
    #
    # Testing methods
    #
    #----------------------------------------------------------------------
    def test_all_plugins(self):
        """Function for testing purposes. Run all plugins"""
        pass

    #----------------------------------------------------------------------
    def rest_run_testPlugin(self):
        """Run test plugin. For testing purposes"""
        for i in self.__pluginManager.getAllPlugins():
            i.plugin_object.run()
