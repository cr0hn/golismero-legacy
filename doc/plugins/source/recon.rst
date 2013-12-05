Reconnaisance
*************

Reconnaisance plugins perform passive, non-invasive information gathering tests on the targets.

Default Error Page Finder (*default_error_page*)
================================================

Identifies default error pages for most commonly used web servers.

DNS Resolver (*dns*)
====================

DNS resolver plugin.

Without it, GoLismero can't resolve domain names to IP addresses.

Malware DNS detection (*dns_malware*)
=====================================

Detect if a domain has been potentially spoofed, hijacked.

================= ========================================
**Argument name** **Default value**
----------------- ----------------------------------------
wordlist          malware/joxean/paranoid_only_domains.txt
================= ========================================

Web Server Fingerprinter (*fingerprint_web*)
============================================

Fingerprinter of web servers.

IP Geolocator (*geoip*)
=======================

Geolocates IP addresses using online services.

This plugin requires a working Internet connection to work.

Robots.txt Analyzer (*robots*)
==============================

Analyzes robots.txt files and extracts their links.

Web Spider (*spider*)
=====================

Web spider plugin.

Without it, GoLismero can't crawl web sites.

Suspicious URL Finder (*suspicious_url*)
========================================

Flags suspicious words in URLs.

theHarvester (*theharvester*)
=============================

Integration with theHarvester: https://code.google.com/p/theharvester/

