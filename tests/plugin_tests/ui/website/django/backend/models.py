from django.db import models

__all__ = ["Audits"]

#------------------------------------------------------------------------------
class Targets(models.Model):
    """
    Audit targets
    """
    target = models.CharField(max_length=255)

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

    only_vulns              = models.BooleanField(blank=True)
    audit_name              = models.CharField(max_length=200)
    #imports                 = serializers.ChoiceField()
    include_subdomains      = models.BooleanField(blank=True)
    subdomain_regex         = models.CharField(max_length=200)
    depth                   = models.IntegerField(max_length=3, default=0)
    max_links               = models.IntegerField(max_length=6, default=0)
    follow_redirects        = models.BooleanField(blank=True)
    follow_first_redirect   = models.BooleanField(blank=True)
    proxy_addr              = models.CharField(max_length=200)
    proxy_user              = models.CharField(max_length=200)
    proxy_pass              = models.CharField(max_length=200)
    cookie                  = models.CharField(max_length=200)
    user_agent              = models.CharField(max_length=200)
    #start_date
    #end_date


    # Relations
    targets                 = models.ManyToManyField(Targets)
    enabled_plugins         = models.ManyToManyField(Plugins)
