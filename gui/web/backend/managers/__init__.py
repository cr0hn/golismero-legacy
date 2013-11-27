#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: http://golismero-project.com
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


from collections import defaultdict
from backend.models import *
from os.path import join, abspath, exists, split
from os import listdir
import yaml


#----------------------------------------------------------------------
#
# Data variables
#
#----------------------------------------------------------------------


REPORT_FORMATS           = []
REPORT_PLUGINS           = []
CONTENT_TYPES_BY_FORMAT  = {}
EXTENSIONS_BY_FORMAT     = {}

#
# Get plugin info from files
#
g_folder = (split(__file__)[0])

for f in listdir(g_folder):
    if f.endswith("yaml"):
        l_file = join(g_folder, f)
        if exists(l_file):
            info = yaml.load(file(l_file))
            REPORT_FORMATS.extend(info.get("formats", None))
            REPORT_PLUGINS.extend(info.get("plugins", None))
            CONTENT_TYPES_BY_FORMAT.update(info.get("content_types", None))
            EXTENSIONS_BY_FORMAT.update(info.get("extension_by_format", None))

# Info can't be loaded
if not REPORT_FORMATS:
    REPORT_FORMATS = ["html", "txt", "rst"]
if not REPORT_PLUGINS:
    REPORT_PLUGINS = ["html", "text", "rstext"]
if not CONTENT_TYPES_BY_FORMAT:
    CONTENT_TYPES_BY_FORMAT = {
        'xml'    : 'application/xml',
        'html'   : 'text/html',
        'rstext' : 'text/html',
        'text'   : 'text/plain'
    }
if not EXTENSIONS_BY_FORMAT:
    EXTENSIONS_BY_FORMAT = {
        'xml'    : 'xml',
        'html'   : 'html',
        'rst'    : 'rst',
        'rstext' : 'rst',
        'text'   : 'txt',
        'txt'    : 'txt',
        'json'   : 'json'
    }

#----------------------------------------------------------------------
#
# Data structures
#
#----------------------------------------------------------------------
class _AbstractInfo(object):
    """Abstract class for GoLismero managers data structures"""

    #----------------------------------------------------------------------
    def __init__(self, json_info):
        self.__json_info             = json_info

    #----------------------------------------------------------------------
    @property
    def to_json(self):
        """
        :return:
        :rtype:
        """
        return self.__json_info





    #----------------------------------------------------------------------
    def __getitem__(self, value):
        return self.__json_info[value]



class GoLismeroAuditInfo(_AbstractInfo):
    """
    Get the audit info for errors or warnings. This class acts as java POJO, having these attributes:

    - text      :: str
    - level     :: int
    """

    PROPERTIES     = ["text", "level"]


    #----------------------------------------------------------------------
    def __init__(self, data):
        """
        Load data from JSON, in format:

        {
          text      :: str
          level     :: int
        }

        :param data: dict with info.
        :type data: dict

        :raises: ValueError
        """
        if not isinstance(data, dict):
            raise TypeError("Expected dict, got '%s' instead" % type(data))

        for p in GoLismeroAuditInfo.PROPERTIES:
            try:
                setattr(self, p, data[p])
            except KeyError:
                raise ValueError("Invalid JSON format. Property '%s' unknown" % p)

        # Store original json
        super(GoLismeroAuditInfo, self).__init__(data)


class GoLismeroAuditLog(GoLismeroAuditInfo):
    """
    Get the audit info for log. This class acts as java POJO, having these attributes:

    - is_error  :: bool
    - text      :: str
    - level     :: int
    """

    PROPERTIES     = GoLismeroAuditInfo.PROPERTIES
    PROPERTIES.extend(["is_error", "verbosity", "timestamp"])


    #----------------------------------------------------------------------
    def __init__(self, data):
        """
        Load data from JSON, in format:

        {
          is_error  :: bool
          text      :: str
          level     :: int
        }

        :param data: dict with info.
        :type data: dict

        :raises: ValueError
        """
        super(GoLismeroAuditLog, self).__init__(data)

        try:
            setattr(self, "is_error", data["is_error"])
        except KeyError:
            raise ValueError("Invalid JSON format. Property '%s' unknown" % p)






class GoLismeroAuditSummary(_AbstractInfo):
    """
    Get the audit summary. This class acts as java POJO, having these attributes:

    'vulns_number'            = int
    'discovered_hosts'        = int # Host discovered into de scan process
    'total_hosts'             = int
    'vulns_by_level'          = {
       'info'     : int,
       'low'      : int,
       'medium'   : int,
       'high'     : int,
       'critical' : int,
     }
    """

    PROPERTIES     = ["vulns_number", "discovered_hosts", "total_hosts"]
    LEVEL_VULNS    = ["info", "low", "medium", "high", "critical"]


    #----------------------------------------------------------------------
    def __init__(self, data):
        """
        Load data from JSON, in format:

        {
        'vulns_number'            = int
        'discovered_hosts'        = int # Host discovered into de scan process
        'total_hosts'             = int
        'vulns_by_level'          = {
           'info'     : int,
           'low'      : int,
           'medium'   : int,
           'high'     : int,
           'critical' : int,
         }

        :param data: dict with info.
        :type data: dict

        :raises: ValueError
        """
        if not isinstance(data, dict):
            raise TypeError("Expected dict, got '%s' instead" % type(data))

        # Commom properties
        for p in GoLismeroAuditSummary.PROPERTIES:
            try:
                setattr(self, p, data[p])
            except KeyError:
                raise ValueError("Invalid JSON format. Property '%s' unknown" % p)

        # Vulns by level
        m_vulns_by_level = data.get("vulns_by_level", None)
        if not m_vulns_by_level:
            raise ValueError("Invalid JSON format. Property 'vulns_by_level' unknown")

        for p in GoLismeroAuditSummary.LEVEL_VULNS:
            try:
                setattr(self, p, m_vulns_by_level[p])
            except KeyError:
                raise ValueError("Invalid JSON format. Property '%s' unknown" % p)


        # Store original json
        super(GoLismeroAuditSummary, self).__init__(data)


class GoLismeroAuditProgress(_AbstractInfo):
    """
    Get the audit progress. This class acts as java POJO, having these attributes:

    - current_stage :: str
    - steps         :: int
    - tests_remain  :: int
    - tests_done     :: int

    """

    PROPERTIES     = ["current_stage", "steps", "tests_remain", "tests_done"]


    #----------------------------------------------------------------------
    def __init__(self, data):
        """
        Load data from JSON, in format:

        {
          'current_stage' : str,
          'steps'         : int,
          'tests_remain'  : int,
          'tests_done'    : int
        }

        :param data: dict with info.
        :type data: dict

        :raises: ValueError
        """
        if not isinstance(data, dict):
            raise TypeError("Expected dict, got '%s' instead" % type(data))

        for p in GoLismeroAuditProgress.PROPERTIES:
            try:
                setattr(self, p, data[p])
            except KeyError:
                raise ValueError("Invalid JSON format. Property '%s' unknown" % p)

        # Store original json
        super(GoLismeroAuditProgress, self).__init__(data)

class GoLismeroAuditData(object): # TODO: Rewrite and clean this class
    """Audit info"""

    PROPERTIES = [
        "id",
        "audit_name",
        "only_vulns",
        "include_subdomains",
        "subdomain_regex",
        "depth",
        "max_links",
        "follow_redirects",
        "follow_first_redirect",
        "proxy_addr",
        "proxy_port",
        "proxy_user",
        "proxy_pass",
        "cookie",
        "user_agent",
        "start_date",
        "end_date",
        "audit_state",
        "user",
        "disable_plugins"
    ]

    COMPLEX_PROPERTIES = ["enable_plugins", "user", "targets"]


    #----------------------------------------------------------------------
    def __init__(self):
        for v in GoLismeroAuditData.PROPERTIES:
            setattr(self, v, None)

        # Set list properties
        self.targets         = []
        self.enable_plugins  = []

        # store path
        self.store_path      = None


    #----------------------------------------------------------------------
    @classmethod
    def from_json(cls, data):
        """
        Load from json model.

        :param data: json object as a dict
        :type data: dict

        :retrun: GoLismeroAuditData instance
        :rtype: GoLismeroAuditData

        :raises: TypeError
        """
        if not isinstance(data, dict):
            raise TypeError("Expected basestring, got '%s' instead" % type(data))

        # Set PK
        c = cls()
        for k, v in data.iteritems():
            setattr(c, k, v)

        return c


    #----------------------------------------------------------------------
    @classmethod
    def from_django(cls, data):
        """
        Loads object form Audits django object.

        :param data: Audits instance
        :type data: Audits

        :raises: TypeError
        """
        if not isinstance(data, Audit):
            raise TypeError("Expected Audits, got '%s' instead" % type(data))

        c = cls()

        for d in GoLismeroAuditData.PROPERTIES:
            setattr(c, d, str(getattr(data, d)))

        #
        # Set relations
        #
        # Targets
        ts = data.targets.all()
        if ts:
            c.targets = []
            for d in ts:
                c.targets.append(d.target_name)

        # Plugins
        ps = data.enable_plugins.all()
        if ps:
            c.enable_plugins = []
            for d in ps:
                l_plugin = {}
                l_plugin['plugin_name'] = str(d.plugin_name)
                l_plugin['params'] = []

                for p in d.pluginparameters_set.filter(audit__id=data.id).all():
                    l_param = {}
                    l_param['param_name']  = str(p.param_name)
                    l_param['param_value'] = str(p.param_value)
                    l_plugin['params'].append(l_param)

                c.enable_plugins.append(l_plugin)

        # Users
        c.user = str(data.user.username)

        return c


    #----------------------------------------------------------------------
    @property
    def to_json(self):
        """
        Returns a JSON with all info in format:

        {
          "audit_name": "asdfasdf",
          "targets": [ "127.0.0.1", "mysite.com" ],
          "enabled_plugins": [
            {
              "plugin_name": "openvas",
              "params": [
                {
                  "param_name": "profile",
                  "param_value": "Full and fast"
                },
                {
                  "param_name": "user",
                  "param_value": "admin"
                },
                {
                  "param_name": "password",
                  "param_value": "admin"
                }
              ]
            }
          ],
          "disabled_plugins": ["spider","nikto"]

        :returns: JSON with info.
        """
        return { k : v for k, v in self.__dict__.iteritems() }


    #----------------------------------------------------------------------
    @property
    def to_json_brief(self):
        """
        Returns only a json in format:

        {
           'id'    : int,
           'name'  : str,
           'user'  : str,
           'state' : str
        }

        :returns: dict
        :rtype: dict
        """
        return {
            'id'     : self.id,
            'name'   : self.audit_name,
            'user'   : self.user,
            'state'  : self.audit_state
        }


    #----------------------------------------------------------------------
    @property
    def to_json_console(self):
        """
        :returns: return a JSON formated for GoLismero console:
        {
          "audit_name": "asdfasdf_1",
          "targets": ["127.0.0.1", "mysite.com" ],
          "enabled_plugins": ["openvas"]
          "disabled_plugins": ["spider","nikto"]

        }
        :rtype: dict
        """
        # Add simple config
        m_config                    = { k : str(v) for k, v in self.__dict__.iteritems() if k not in GoLismeroAuditData.COMPLEX_PROPERTIES and not isinstance(v, list) and not isinstance(v, dict)}

        # Fix audit name
        m_config['audit_name']      = "%s_%s" % (self.audit_name, str(self.id))

        # Add targets
        try:
            #m_config['targets']         = self.__dict__["targets"]

            tmp_targets = []

            for target in self.__dict__["targets"]:
                if not "://" in target:
                    tmp_targets.append("http://" + target)

                tmp_targets.append(target)

            m_config['targets'] = tmp_targets

        except KeyError:
            pass # No targets -> imports audits

        #
        # FIXME in next version:
        #
        # For this version, golismero will generate reports in all possible formats.
        # After, core will choice what to serve.
        #
        m_config['reports'] = ','.join([join(self.store_path, "report.%s" % x) for x in REPORT_FORMATS])

        #
        # Plugins
        #
        # Add plugins enabled
        m_config['disable_plugins']        = None
        m_config['enable_plugins']         = []

        if len(self.enable_plugins) == 0 or \
           len(self.enable_plugins) == 1 and self.enable_plugins[0]['plugin_name'] == "all" : # No plugins selected -> enable all
            m_config['disable_plugins']        = []
            m_config['plugin_load_overrides']  = []
            m_config['enable_plugins']         = ["all"]
        else: # Plugins selected -> enable one by one

            #----------------------------------------------------------------------
            #m_config['disable_plugins']        = ["all"]
            #m_config['enable_plugins']         = []
            #m_config['plugin_load_overrides']  = []
            #m_tmp_plugin_args                  = {}

            ## Add plugins config
            #for p in self.enable_plugins:
                #l_plugin_name = p["plugin_name"]
                #m_config['plugin_load_overrides'].append((True, l_plugin_name))

                ## Plugins params
                #for pp in p.get("params", []):
                    #l_plugin_param_name  = pp["param_name"]
                    #l_plugin_param_value = pp["param_value"]
                    #if not l_plugin_name in m_tmp_plugin_args:
                        #m_tmp_plugin_args[l_plugin_name] = {}
                    #m_tmp_plugin_args[l_plugin_name][l_plugin_param_name] = l_plugin_param_value

            #m_config['plugin_args'] = m_tmp_plugin_args

            ## Configure to golismero format
            #if m_config['plugin_load_overrides']:
                #m_config['enable_plugins'] =  ','.join(x[1] for x in m_config['plugin_load_overrides'])
                #m_config['enable_plugins'] += ','
                #m_config['enable_plugins'] = ','.join(REPORT_PLUGINS) # Report plugins



            #----------------------------------------------------------------------
            m_config['enable_plugins']         = ["all"]
            m_config['disable_plugins']        = []
            m_config['plugin_load_overrides']  = []
            m_tmp_plugin_args                  = {}

            # Add plugins config
            for p in self.enable_plugins:
                l_plugin_name = p["plugin_name"]

                # If plugin is a report plugin, It must not be included in the overrides
                check = [True for y in REPORT_PLUGINS if y in l_plugin_name]
                if not check:
                    m_config['plugin_load_overrides'].append((True, l_plugin_name))

                # Plugins params
                for pp in p.get("params", []):
                    l_plugin_param_name  = pp["param_name"]
                    l_plugin_param_value = pp["param_value"]
                    if l_plugin_name not in m_tmp_plugin_args:
                        m_tmp_plugin_args[l_plugin_name] = {}
                    m_tmp_plugin_args[l_plugin_name][l_plugin_param_name] = l_plugin_param_value

            m_config['plugin_args'] = m_tmp_plugin_args

            # Configure to golismero format
            #if m_config['plugin_load_overrides']:
                #m_config['enable_plugins'] =  ','.join(x[1] for x in m_config['plugin_load_overrides'])
                #m_config['enable_plugins'] += ','
                #m_config['enable_plugins'] = ','.join(REPORT_PLUGINS) # Report plugins

        return m_config
