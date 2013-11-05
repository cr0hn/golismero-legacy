from django.db import models
from django.contrib.auth.models import User

import datetime
from string import ascii_letters, digits, printable
from random import choice


#------------------------------------------------------------------------------
def generate_random_string(length = 30):
    m_available_chars = ascii_letters + digits

    return "".join(choice(m_available_chars) for _ in xrange(length))


__all__ = ["Audit", "Target", "Plugins", "PluginParameters"]

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
    plugin_params     = models.OneToOneField(Plugins)


#------------------------------------------------------------------------------
class Audit(models.Model):
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
    end_date                = models.DateField(auto_now_add=True, auto_now=True, default=datetime.datetime.now)
    # Comma separated disabled plugins
    disable_plugins         = models.CharField(max_length=1000, blank=True)

    audit_state             = models.CharField(max_length=50, default="new")

    # String with type of results: csv, html, xml...
    results_type            = models.CharField(max_length=50, default="html")
    results_location        = models.CharField(max_length=255, blank=True)

    # Relations
    targets                 = models.ManyToManyField(Target)
    enable_plugins          = models.ManyToManyField(Plugins)
    user                    = models.ForeignKey(User)
