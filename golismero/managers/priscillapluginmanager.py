#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

__all__ = ["PriscillaPluginManager", "PluginInfo"]

from ..api.plugin import TestingPlugin, ReportPlugin, UIPlugin, GlobalPlugin
from ..common import Singleton

from os import path, walk
from keyword import iskeyword
from collections import defaultdict
from ConfigParser import RawConfigParser

import re
import imp
import warnings


#----------------------------------------------------------------------
class PluginInfo (object):
    """
    Plugin descriptor object.
    """

    @property
    def plugin_name(self):
        "Plugin name."
        return self.__plugin_name

    @property
    def descriptor_file(self):
        "Plugin descriptor file name."
        return self.__descriptor_file

    @property
    def category(self):
        "Plugin category."
        return self.__plugin_name.split("/")[0].lower()

    @property
    def stage(self):
        "Plugin stage."
        return self.__stage

    @property
    def dependencies(self):
        "Plugin dependencies."
        return self.__dependencies

    @property
    def plugin_module(self):
        "Plugin module file name."
        return self.__plugin_module

    @property
    def plugin_class(self):
        "Plugin class name."
        return self.__plugin_class

    @property
    def plugin_config(self):
        "Plugin configuration."
        return self.__plugin_config

    @property
    def plugin_extra_config(self):
        "Plugin extra configuration."
        return self.__plugin_extra_config

    @property
    def display_name(self):
        "Display name to be shown to the user."
        return self.__display_name

    @property
    def description(self):
        "Description of this plugin's functionality."
        return self.__description

    @property
    def version(self):
        "Version of this plugin."
        return self.__version

    @property
    def author(self):
        "Author of this plugin."
        return self.__author

    @property
    def copyright(self):
        "Copyright of this plugin."
        return self.__copyright

    @property
    def license(self):
        "License for this plugin."
        return self.__license

    @property
    def website(self):
        "Web site where you can download the latest version of this plugin."
        return self.__website


    #----------------------------------------------------------------------
    def __init__(self, plugin_name, descriptor_file):
        """
        Load a plugin descriptor file.

        :param plugin_name: Plugin name.
        :type plugin_name: str

        :param descriptor_file: Descriptor file (with ".golismero" extension).
        :type descriptor_file: str
        """

        # Store the plugin name.
        self.__plugin_name = plugin_name

        # Make sure the descriptor filename is an absolute path.
        descriptor_file = path.abspath(descriptor_file)

        # Store the descriptor filename.
        self.__descriptor_file = descriptor_file

        # Parse the descriptor file.
        parser = RawConfigParser()
        parser.read(descriptor_file)

        # Read the "[Core]" section.
        self.__display_name = parser.get("Core", "Name")
        try:
            plugin_module   = parser.get("Core", "Module")
        except Exception:
            plugin_module   = path.splitext(path.basename(descriptor_file))[0]
        try:
            plugin_class    = parser.get("Core", "Class")
        except Exception:
            plugin_class    = None
        try:
            stage           = parser.get("Core", "Stage")
        except Exception:
            stage           = None
        try:
            dependencies    = parser.get("Core", "Dependencies")
        except Exception:
            dependencies    = None

        # Parse the stage name to get the number.
        if not stage:
            try:
                subcategory  = plugin_name.split("/")[1].lower()
                self.__stage = PriscillaPluginManager.STAGES[subcategory]
            except Exception:
                self.__stage = 1
        else:
            try:
                self.__stage = PriscillaPluginManager.STAGES[stage.lower()]
            except KeyError:
                try:
                    self.__stage = int(stage)
                    if self.__stage not in PriscillaPluginManager.STAGES.values():
                        raise ValueError()
                except Exception:
                    msg = "Error parsing %r: invalid execution stage: %s"
                    raise ValueError(msg % (descriptor_file, stage))

        # Sanitize the plugin module pathname.
        if not plugin_module.endswith(".py"):
            plugin_module += ".py"
        if path.sep != "/":
            plugin_module = plugin_module.replace("/", path.sep)
        if path.isabs(plugin_module):
            msg = "Error parsing %r: plugin module path is absolute"
            raise ValueError(msg % descriptor_file)
        plugin_folder = path.split(descriptor_file)[0]
        plugin_module = path.abspath(path.join(plugin_folder, plugin_module))
        if not plugin_module.startswith(plugin_folder):
            msg = "Error parsing %r: plugin module is located outside its plugin folder"
            raise ValueError(msg % descriptor_file)

        # Sanitize the plugin classname.
        if plugin_class is not None:
            plugin_class = re.sub(r"\W|^(?=\d)", "_", plugin_class.strip())
            if iskeyword(plugin_class):
                msg = "Error parsing %r: plugin class (%s) is a Python reserved keyword"
                raise ValueError(msg % (plugin_class, descriptor_file))

        # Store the plugin module and class.
        self.__plugin_module = plugin_module
        self.__plugin_class  = plugin_class

        # Parse the list of dependencies.
        if not dependencies:
            self.__dependencies = ()
        else:
            self.__dependencies = tuple(sorted( {x.strip() for x in dependencies.split(",")} ))

        # Read the "[Description]" section.
        try:
            self.__description = parser.get("Documentation", "Description")
        except Exception:
            self.__description = self.__display_name
        try:
            self.__version     = parser.get("Documentation", "Version")
        except Exception:
            self.__version     = "?.?"
        try:
            self.__author      = parser.get("Documentation", "Author")
        except Exception:
            self.__author      = "Anonymous"
        try:
            self.__copyright   = parser.get("Documentation", "Copyright")
        except Exception:
            self.__copyright   = "No copyright information"
        try:
            self.__license   = parser.get("Documentation", "License")
        except Exception:
            self.__license   = "No license information"
        try:
            self.__website     = parser.get("Documentation", "Website")
        except Exception:
            self.__website     = "https://github.com/cr0hn/golismero/"

        # Load the plugin configuration as a Python dictionary.
        # This section is optional.
        try:
            self.__plugin_config = dict( parser.items("Configuration") )
        except Exception:
            self.__plugin_config = dict()

        # Load the plugin extra configuration sections as a dict of dicts.
        # All sections not parsed above will be included here.
        self.__plugin_extra_config = dict()
        for section in parser.sections():
            if section not in ("Core", "Documentation", "Configuration"):
                options = dict( (k.lower(), v) for (k, v) in parser.items(section) )
                self.__plugin_extra_config[section] = options


    #----------------------------------------------------------------------
    # Protected method to update the class name if found during plugin load
    # (Assumes it's always valid, so no sanitization is performed).
    def _fix_classname(self, plugin_class):
        self.__plugin_class = plugin_class


#----------------------------------------------------------------------
class PriscillaPluginManager (Singleton):
    """Priscilla Plugin Manager."""


    # Plugin categories and their base classes.
    CATEGORIES = {
        "testing" : TestingPlugin,
        "report"  : ReportPlugin,
        "ui"      : UIPlugin,
        "global"  : GlobalPlugin,
    }


    # Testing plugin execution stages by name.
    STAGES = {
        "recon"   : 1,    # Reconaissance stage.
        "scan"    : 2,    # Scanning (non-intrusive) stage.
        "exploit" : 3,    # Exploitation (intrusive) stage.
        "post"    : 4,    # Post-exploitation stage.
        "cleanup" : 5,    # Cleanup stage.
    }

    # Minimum and maximum stage numbers.
    min_stage = min(*STAGES.values())
    max_stage = max(*STAGES.values())
##    assert sorted(STAGES.itervalues()) == range(min_stage, max_stage + 1)


    #----------------------------------------------------------------------
    def __init__(self):

        # Dictionary to collect the info for each plugin found
        self.__plugins = {}    # plugin name -> plugin info

        # Dictionary to cache the plugin instances
        self.__cache = {}

        # Batches and stages of plugins
        self.__batches = []
        self.__stages = {}


    #----------------------------------------------------------------------
    def find_plugins(self, plugins_folder):
        """
        Find plugins in the given folder.

        The folder must contain one subfolder for each plugin category,
        inside which are the plugins.

        Each plugin is defined in a file with the ".golismero" extension.
        The code for each plugin must be in a Python script within the same
        folder as the ".golismero" file, or within any subdirectory of it.

        :param plugins_folder: Folder where to look for plugins.
        :type plugins_folder: str

        :returns: tuple(list, list) -- A list of plugins loaded, and a list of plugins that failed to load.
        """

        # Make sure the plugins folder is an absolute path.
        plugins_folder = path.abspath(plugins_folder)

        # Raise an exception if the plugins folder doesn't exist or isn't a folder.
        if not path.isdir(plugins_folder):
            raise ValueError("Invalid plugin folder: %s" % plugins_folder)

        # List to collect the plugins that loaded successfully.
        success = list()

        # List to collect the plugins that failed to load.
        failure = list()

        # The first directory level is the category.
        for category, _ in self.CATEGORIES.iteritems():
            category_folder = path.join(plugins_folder, category)

            # Skip missing folders.
            if not path.isdir(category_folder):
                warnings.warn("Missing plugin category folder: %s" % category_folder)
                continue

            # The following levels belong to the plugins.
            for (dirpath, _, filenames) in walk(category_folder):

                # Look for plugin descriptor files.
                for fname in filenames:
                    if not fname.endswith(".golismero"):
                        continue

                    # Convert the plugin descriptor filename to an absolute path.
                    fname = path.abspath(path.join(dirpath, fname))

                    # The plugin name is the relative path + filename without extension,
                    # where the path separator is always "/" regardless of the current OS.
                    plugin_name = path.splitext(fname)[0][len(plugins_folder):]
                    if plugin_name[0] == path.sep:
                        plugin_name = plugin_name[1:]
                    if path.sep != "/":
                        plugin_name = plugin_name.replace(path.sep, "/")

                    # If the plugin name already exists, skip it.
                    if plugin_name in self.__plugins:
                        failure.append(plugin_name)
                        continue

                    # Parse the plugin descriptor file.
                    try:
                        plugin_info = PluginInfo(plugin_name, fname)

                        # Collect the plugin info.
                        self.__plugins[plugin_name] = plugin_info

                        # Add the plugin name to the success list.
                        success.append(plugin_name)

                    # On error add the plugin name to the list of failures.
                    except Exception:
                        failure.append(plugin_name)

        return success, failure


    #----------------------------------------------------------------------
    def get_plugins(self, category = "all"):
        """
        Get info on the available plugins, optionally filtering by category.

        :param category: Category. Use "all" to get plugins from all categories.
        :type category: str

        :returns: dict -- Mapping of plugin names to instances of PluginInfo.
        :raises: KeyError -- The requested category doesn't exist.
        """

        # Make sure the category is lowercase.
        category = category.lower()

        # If not filtering for category, just return the whole dictionary.
        if category == "all":
            return self.__plugins

        # Make sure the category exists, otherwise raise an exception.
        if category not in self.CATEGORIES:
            raise KeyError("Unknown plugin category: %r" % category)

        # Get only the plugins that match the category.
        category = category + "/"
        return { plugin: self.__plugins[plugin] for plugin in self.__plugins if plugin.startswith(category) }


    #----------------------------------------------------------------------
    def get_plugin_names(self, category = "all"):
        """
        Get the names of the available plugins, optionally filtering by category.

        :param category: Category. Use "all" to get plugins from all categories.
        :type category: str

        :returns: set -- Plugin names.
        :raises: KeyError -- The requested category doesn't exist.
        """
        return set(self.get_plugins(category).keys())


    #----------------------------------------------------------------------
    def get_plugin_by_name(self, plugin_name):
        """
        Get info on the requested plugin.

        :param plugin_name: Plugin name.
        :type plugin_name: str

        :returns: PluginInfo
        :raises: KeyError -- The requested plugin doesn't exist.
        """
        try:
            return self.get_plugins()[plugin_name]
        except KeyError:
            raise KeyError("Plugin not found: %r" % plugin_name)


    #----------------------------------------------------------------------
    def load_plugins(self, enabled_plugins = ("all",), disabled_plugins = (), category = "all"):
        """
        Get info on the available plugins, optionally filtering by category.

        :param enabled_plugins: List of enabled plugins, by name. Use "all" to enable all plugins (save those in disabled_plugins).
        :type enabled_plugins: list

        :param disabled_plugins: List of disabled plugins, by name. Use "all" to disable all plugins (save those in enabled_plugins).
        :type disabled_plugins: list

        :param category: Category. Use "all" to load plugins from all categories.
        :type category: str

        :returns: dict -- Mapping of plugin names to Plugin instances.
        :raises: KeyError -- The requested plugin or category doesn't exist.
        :raises: Exception -- Plugins may throw exceptions if they fail to load.
        """

        # Sanitize the category.
        category = category.strip().lower()

        # Make sure the category exists, otherwise raise an exception.
        if category != "all" and category not in self.CATEGORIES:
            raise KeyError("Unknown plugin category: %r" % category)

        # Get the list of all plugins for the requested category.
        plugins = self.get_plugin_names(category)

        # Remove duplicates in black and white lists.
        if "all" in enabled_plugins:
            enabled_plugins  = {"all"}
        if "all" in disabled_plugins:
            disabled_plugins = {"all"}
        enabled_plugins  = set(enabled_plugins)
        disabled_plugins = set(disabled_plugins)

        # Convert categories to plugin names.
        for cat in self.CATEGORIES:
            if cat in disabled_plugins:
                if cat in enabled_plugins:
                    raise ValueError("Conflicting black and white lists!")
                if cat == category:   # if the requested category is disabled,
                    return {}         # just return an empty set now.
                disabled_plugins.remove(cat)
                if category == "all":
                    disabled_plugins.update(self.get_plugin_names(cat))
            elif cat in enabled_plugins:
                if cat in disabled_plugins:
                    raise ValueError("Conflicting black and white lists!")
                enabled_plugins.remove(cat)
                if category == "all" or cat == category:
                    enabled_plugins.update(self.get_plugin_names(cat))

        # Check for consistency in black and white lists.
        if enabled_plugins.intersection(disabled_plugins):
            raise ValueError("Conflicting black and white lists!")
        if "all" not in enabled_plugins and "all" not in disabled_plugins:
            disabled_plugins = set()

        # Make sure all the plugins in the whitelist exist.
        all_plugins = self.get_plugin_names()
        missing_plugins = enabled_plugins.difference(all_plugins)
        if "all" in missing_plugins:
            missing_plugins.remove("all")
        if missing_plugins:
            if len(missing_plugins) > 1:
                raise KeyError("Missing plugins: %s" % ", ".join(sorted(missing_plugins)))
            raise KeyError("Missing plugin: %s" % missing_plugins.pop())

        # Make sure all the plugins in the blacklist exist.
        missing_plugins = disabled_plugins.difference(all_plugins)
        if "all" in missing_plugins:
            missing_plugins.remove("all")
        if missing_plugins:
            if len(missing_plugins) > 1:
                raise KeyError("Unknown plugins: %s" % ", ".join(sorted(missing_plugins)))
            raise KeyError("Unknown plugin: %s" % missing_plugins.pop())

        # Blacklist approach.
        if "all" in enabled_plugins:
            plugins.difference_update(disabled_plugins)

        # Whitelist approach.
        else:
            plugins.intersection_update(enabled_plugins)

        # Load each requested plugin.
        return { name : self.load_plugin_by_name(name) for name in plugins }


    #----------------------------------------------------------------------
    def load_plugin_by_name(self, name):
        """
        Load the requested plugin by name.

        Plugins are only loaded once.
        Subsequent calls to this method yield always the same Plugin instance.

        :param name: Name of the plugin to load.
        :type name: str

        :returns: Plugin instance
        :raises: Exception -- Plugins may throw exceptions if they fail to load.
        """

        # If the plugin was already loaded, return the instance from the cache.
        instance = self.__cache.get(name, None)
        if instance is not None:
            return instance

        # Get the plugin info.
        try:
            info = self.__plugins[name]
        except KeyError:
            raise KeyError("Plugin not found: %r" % name)

        # Get the plugin module file.
        source = info.plugin_module

        # Import the plugin module.
        module_fake_name = "plugin_" + re.sub(r"\W|^(?=\d)", "_", name)
        module = imp.load_source(module_fake_name, source)

        # Get the plugin classname.
        classname = info.plugin_class

        # If we know the plugin classname, get the class.
        if classname:
            try:
                clazz = getattr(module, classname)
            except Exception:
                raise ImportError("Plugin class %s not found in file: %s" % (classname, source))

        # If we don't know the plugin classname, we need to find it.
        else:

            # Get the plugin base class for its category.
            base_class = self.CATEGORIES[ name[ : name.find("/") ] ]

            # Get all public symbols from the module.
            public_symbols = [getattr(module, symbol) for symbol in getattr(module, "__all__", [])]
            if not public_symbols:
                public_symbols = [value for (symbol, value) in module.__dict__.iteritems()
                                        if not symbol.startswith("_")]
                if not public_symbols:
                    raise ImportError("Plugin class not found in file: %s" % source)

            # Find all public classes that derive from the base class.
            # NOTE: it'd be faster to stop on the first match,
            #       but then we can't check for ambiguities (see below)
            candidates = []
            bases = self.CATEGORIES.values()
            for value in public_symbols:
                try:
                    if issubclass(value, base_class) and value not in bases:
                        candidates.append(value)
                except TypeError:
                    pass

            # There should be only one candidate, if not raise an exception.
            if not candidates:
                raise ImportError("Plugin class not found in file: %s" % source)
            if len(candidates) > 1:
                msg = "Error loading %r: can't decide which plugin class to load: %s"
                msg = msg % (source, ", ".join(c.__name__ for c in candidates))
                raise ImportError(msg)

            # Get the plugin class.
            clazz = candidates.pop()

            # Add the classname to the plugin info.
            info._fix_classname(clazz.__name__)

        # Instance the plugin class.
        instance = clazz()

        # Add it to the cache.
        self.__cache[name] = instance

        # Return the instance.
        return instance


    #----------------------------------------------------------------------
    def get_plugin_info_from_instance(self, instance):
        """
        Get a plugin's name and information from its already loaded instance.

        :param instance: Plugin instance.
        :type instance: Plugin

        :returns: tuple(str, PluginInfo) -- Plugin name and information.
        """
        for (name, value) in self.__cache.iteritems():
            if value is instance:
                return (name, self.__plugins[name])


    #----------------------------------------------------------------------
    def calculate_dependencies(self):
        """
        Generate a dependency graph for all plugins found, and calculate
        the batches of plugins that can be run concurrently.

        :raises ValueError: The dependencies are broken.
        """

        # Get all the plugins that support dependencies.
        plugins = self.get_plugins("testing")
        all_names = set(plugins.iterkeys())

        # Build the dependency graph, and group plugins by stage.
        # Raise an exception for missing dependencies.
        graph = defaultdict(set)
        stages = defaultdict(set)
        for name, info in plugins.iteritems():
            stage = info.stage
            if not stage or stage < 0:
                stage = 0
            stages[stage].add(name)
            deps = set(info.dependencies)
            if not deps.issubset(all_names):
                msg = "Plugin %s depends on missing plugin(s): %s"
                msg %= (name, ", ".join(sorted(deps.difference(all_names))))
                raise ValueError(msg)
            graph[name] = deps

        # Add the implicit dependencies defined by the stages into the graph.
        # (We're creating dummy bridge nodes to reduce the number of edges.)
        stage_numbers = sorted(self.STAGES.itervalues())
        for n in stage_numbers:
            this_stage = "* stage %d" % n
            next_stage = "* stage %d" % (n + 1)
            graph[next_stage].add(this_stage)
        for n in stage_numbers:
            bridge = "* stage %d" % n
            graph[bridge].update(stages[n])
            for node in stages[n + 1]:
                graph[node].add(bridge)

        # Calculate the plugin batches.
        # Raise an exception for circular dependencies.
        batches = []
        while graph:
            ready = {name for name, deps in graph.iteritems() if not deps}
            if not ready:
                # TODO: find each circle in the graph and show it,
                #       instead of dumping the remaining graph
                msg = "Circular dependencies found in plugins: "
                keys = [ k for k in graph.iterkeys() if not k.startswith("*") ]
                keys.sort()
                raise ValueError(msg + ", ".join(keys))
            for name in ready:
                del graph[name]
            for deps in graph.itervalues():
                deps.difference_update(ready)
            ready = {k for k in ready if not k.startswith("*")}
            if ready:
                batches.append(ready)

        # Store the plugin batches and stages.
        self.__batches = batches
        self.__stages = stages


    #----------------------------------------------------------------------
    def next_concurrent_plugins(self, candidate_plugins):
        """
        Based on the previously executed plugins, get the next plugins
        to execute.

        :param candidate_plugins: Plugins we may want to execute.
        :type candidate_plugins: set(str)

        :returns: set(str) -- Next plugins to execute.
        """
        if candidate_plugins:
            for batch in self.__batches:
                batch = batch.intersection(candidate_plugins)
                if batch:
                    return batch
        return set()


    #----------------------------------------------------------------------
    @property
    def batches(self):
        return self.__batches

    @property
    def stages(self):
        return self.__stages
