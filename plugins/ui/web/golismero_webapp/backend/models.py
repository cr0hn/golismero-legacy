from django.db import models
from django.contrib.auth.models import User

import datetime
from string import ascii_letters, digits, printable
from random import choice


#------------------------------------------------------------------------------
def generate_random_string(length = 30):
    m_available_chars = ascii_letters + digits

    return "".join(choice(m_available_chars) for _ in xrange(length))


__all__ = ["Audits", "Target", "Plugins", "PluginParameters"]

#------------------------------------------------------------------------------
class Target(models.Model):
    """
    Audit targets
    """
    target_name = models.CharField(max_length=255)

#------------------------------------------------------------------------------
class Plugins(models.Model):
    """
    Available plugins
    """
    plugin_name   = models.CharField(max_length=255, primary_key=True)

#------------------------------------------------------------------------------
class PluginParameters(models.Model):
    """
    Plugins parameters. Each parameter only belongs to one plugin.
    """
    param_name        = models.CharField(max_length=200)
    param_value       = models.CharField(max_length=200)
    param_type        = models.CharField(max_length=50, default="string")
    param_default     = models.CharField(max_length=50, default="")
    param_restriction = models.CharField(max_length=255, default="")

    # Relations
    plugin_params = models.ForeignKey(Plugins)


#------------------------------------------------------------------------------
class Audits(models.Model):
    """
    Audit configuration
    """
    audit_name              = models.CharField(max_length=200, default=generate_random_string)
    only_vulns              = models.BooleanField(blank=True)
    #imports                 = serializers.ChoiceField()
    include_subdomains      = models.BooleanField(blank=True)
    subdomain_regex         = models.CharField(max_length=200, default="*")
    depth                   = models.IntegerField(max_length=3, default=0)
    max_links               = models.IntegerField(max_length=6, default=0)
    follow_redirects        = models.BooleanField(blank=True)
    follow_first_redirect   = models.BooleanField(blank=True)
    proxy_addr              = models.CharField(max_length=200, blank=True)
    proxy_user              = models.CharField(max_length=200, blank=True)
    proxy_pass              = models.CharField(max_length=200, blank=True)
    cookie                  = models.CharField(max_length=200, blank=True)
    user_agent              = models.CharField(max_length=200, blank=True)
    start_date              = models.DateField(auto_now_add=True, auto_now=True, default=datetime.datetime.now)
    end_date                = models.DateField(null=True, blank=True)
    # Comma separated disabled plugins
    disable_plugins         = models.CharField(max_length=1000, blank=True)

    audit_state             = models.CharField(max_length=50, default="new")

    # String with type of results: csv, html, xml...
    results_type            = models.CharField(max_length=50, default="html")
    results_location        = models.CharField(max_length=255, blank=True)

    # Relations
    targets                 = models.ManyToManyField(Target)
    enabled_plugins         = models.ManyToManyField(Plugins)
    user                    = models.OneToOneField(User)

    #----------------------------------------------------------------------
    #def clean_disabled_plugins(self):
        #"""Checks if disabled plugins ir a comma separated list."""
        #p = self.cleaned_data.get("disabled_plugins", None)

        #if p:




    #----------------------------------------------------------------------
    #def to_json(self):
        #"""
        #returns a JSON object as format:

        #{
          #'id'                      : str,
          #'follow_redirects'        : str,
          #'plugins'                 : str,
          #'audit_name'              : str,
          #'user_id'                 : str,
          #'proxy_pass'              : str,
          #'audit_state'             : str,
          #'proxy_addr'              : str,
          #'only_vulns'              : str,
          #'start_date'              : str,
          #'subdomain_regex'         : str,
          #'results_type'            : str,
          #'end_date'                : str,
          #'cookie'                  : str,
          #'user'                    : str,
          #'proxy_user'              : str,
          #'include_subdomains'      : str,
          #'max_links'               : str,
          #'depth'                   : str,
          #'user_agent'              : str,
          #'results_location'        : str,
          #'follow_first_redirect'   : str,
          #'users'                   : str,
          #'plugins'                 : [
             #{
                #'plugin_id'   : str,
                #'plugin_name' : str
             #},
             #{
                #'plugin_id'   : str,
                #'plugin_name' : str
             #}
           #]
          #'targets'                 :[
             #{
                #'target_id'   : str,
                #'target_name' : str
             #},
             #{
                #'target_id'   : str,
                #'target_name' : str
             #}
           #]
        #}

        #"""

        #EXCLUDED = ["targets", "enabled_plugins", "user"]

        ## Set common info
        #m_info = { k : str(v) for k, v in self.__dict__.iteritems() if k not in EXCLUDED and not k.startswith("_") }

        ## Set relations
        #m_info['user']    = getattr(self.user, "username", "")
        #m_info['plugins'] = [ { 'plugins_id' : p.id, 'plugin_name' : p.plugin_name } for p in self.enabled_plugins.all()]
        #m_info['targets'] = [ { 'target_id' : t.id, 'target_name' : t.target} for t in audit.targets.all()]

        #return m_info