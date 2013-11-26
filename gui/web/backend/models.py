from django.db import models
from django.contrib.auth.models import User

import datetime
from string import ascii_letters, digits, printable
from random import choice


#------------------------------------------------------------------------------
def generate_random_string(length = 30):
    m_available_chars = ascii_letters + digits

    return "".join(choice(m_available_chars) for _ in xrange(length))

#----------------------------------------------------------------------
def generate_random_string_long():
    """Generate token with 100 chars of length"""
    return generate_random_string(100)



__all__ = ["Audit", "Target", "Plugins", "PluginParameters",
           "RTAuditProgress", "RTAuditSummary", "RTAuditLog", "RTPluginErrors",
           "RTPluginWarning", "RTAuditStage"]




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
class Audit(models.Model):
    """
    Audit configuration
    """
    audit_name              = models.CharField(max_length=200, default=generate_random_string)
    # Audit type: scan or import.
    audit_type              = models.CharField(max_length=20, default="scan")
    only_vulns              = models.BooleanField(blank=True)
    #imports                 = serializers.ChoiceField()
    include_subdomains      = models.BooleanField(blank=True)
    subdomain_regex         = models.CharField(max_length=200, blank=True)
    depth                   = models.IntegerField(max_length=3, default=0)
    max_links               = models.IntegerField(max_length=6, default=0)
    follow_redirects        = models.BooleanField(blank=True)
    follow_first_redirect   = models.BooleanField(blank=True)
    proxy_addr              = models.CharField(max_length=200, blank=True)
    proxy_port              = models.IntegerField(max_length=6, default=0)
    proxy_user              = models.CharField(max_length=200, blank=True)
    proxy_pass              = models.CharField(max_length=200, blank=True)
    cookie                  = models.CharField(max_length=200, blank=True)
    user_agent              = models.CharField(max_length=200, blank=True)
    start_date              = models.DateField(auto_now_add=True, auto_now=True, default=datetime.datetime.now)
    end_date                = models.DateField(auto_now_add=True, auto_now=True, default=datetime.datetime.now)

    # Running stage
    current_stage           = models.CharField(max_length=30, default="start")

    # Comma separated disabled plugins
    disable_plugins         = models.CharField(max_length=1000, blank=True)
    audit_state             = models.CharField(max_length=50, default="new")

    # Relations
    targets                 = models.ManyToManyField(Target, blank=True)
    enable_plugins          = models.ManyToManyField(Plugins, blank=True)
    user                    = models.ForeignKey(User)

    # Pushing info
    token                   = models.CharField(max_length=100, default=generate_random_string_long)


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
    plugin     = models.ForeignKey(Plugins)
    audit      = models.ForeignKey(Audit)


#------------------------------------------------------------------------------
#
# Real time options
#
#------------------------------------------------------------------------------
class RTAuditProgress(models.Model):
    """
    Summarized audit progress.
    """
    current_stage      = models.CharField(max_length=20)
    steps              = models.IntegerField(default=0)
    # Number of test not finished
    tests_remain       = models.IntegerField(default=0)
    # Number of tests done
    tests_done         = models.IntegerField(default=0)
    # Last check
    last_update        = models.DateField(auto_now_add=True, auto_now=True, default=datetime.datetime.now)

    # Relations
    audit              = models.OneToOneField(Audit, primary_key=True)



#------------------------------------------------------------------------------
class RTAuditSummary(models.Model):
    """
    Summarized results info.
    """
    vulns_number                 = models.IntegerField(default=0)
    discovered_hosts             = models.IntegerField(default=0)
    total_hosts                  = models.IntegerField(default=0)
    vuln_level_info_number       = models.IntegerField(default=0)
    vuln_level_low_number        = models.IntegerField(default=0)
    vuln_level_medium_number     = models.IntegerField(default=0)
    vuln_level_high_number       = models.IntegerField(default=0)
    vuln_level_critical_number   = models.IntegerField(default=0)

    # Last check
    last_update                  = models.DateField(auto_now_add=True, auto_now=True, default=datetime.datetime.now)

    # Relations
    audit                        = models.OneToOneField(Audit, primary_key=True)


#------------------------------------------------------------------------------
class RTAuditLog(models.Model):
    """
    Audit logs
    """
    text                 = models.TextField()
    level                = models.IntegerField(default=0)
    verbosity            = models.IntegerField(default=0)
    timestamp            = models.DateField()
    is_error             = models.BooleanField(default=False)
    insert_date          = models.DateField(auto_now_add=True, auto_now=True, default=datetime.datetime.now)

    # Relations
    audit                = models.ForeignKey(Audit)

#------------------------------------------------------------------------------
class RTPluginErrors(models.Model):
    """
    Plugin errors
    """
    text                 = models.TextField()
    level                = models.IntegerField(default=0)
    insert_date          = models.DateField(auto_now_add=True, auto_now=True, default=datetime.datetime.now)

    # Relations
    plugin               = models.ForeignKey(Plugins)
    audit                = models.ForeignKey(Audit)

#------------------------------------------------------------------------------
class RTPluginWarning(models.Model):
    """
    Plugin warnings
    """
    text                 = models.TextField()
    level                = models.IntegerField(default=0)
    insert_date          = models.DateField(auto_now_add=True, auto_now=True, default=datetime.datetime.now)

    # Relations
    plugin               = models.ForeignKey(Plugins)
    audit                = models.ForeignKey(Audit)

#------------------------------------------------------------------------------
class RTAuditStage(models.Model):
    """
    Audit logs
    """
    stage                = models.CharField(max_length=30)
    insert_date          = models.DateField(auto_now_add=True, auto_now=True, default=datetime.datetime.now)

    # Relations
    audit                = models.ForeignKey(Audit)
