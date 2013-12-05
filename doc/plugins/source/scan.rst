Scan
****

Scan plugins perform active, non-invasive information gathering tests on the targets.

Bruteforce directories discovery (*brute_directories*)
======================================================

Tries to discover hidden folders by brute force:

www.site.com/folder/ -> www.site.com/folder2 www.site.com/folder3 ...

DNS Bruteforcer (*brute_dns*)
=============================

Tries to find hidden subdomains by brute force.

================= =================
**Argument name** **Default value**
----------------- -----------------
wordlist          dns/dnsrecon.txt
================= =================

Bruteforce file extensions discovery (*brute_extensions*)
=========================================================

Tries to discover hidden files by brute force:

www.site.com/index.php -> www.site.com/index.php.old

Bruteforce permutations discovery (*brute_permutations*)
========================================================

Tries to discover hidden files by bruteforcing the extension:

www.site.com/index.php -> www.site.com/index.php2

Bruteforce predictables discovery (*brute_predictables*)
========================================================

Tries to discover hidden files at predictable locations.

For example: (Apache) www.site.com/error_log

Bruteforce prefixes discovery (*brute_prefixes*)
================================================

Tries to discover hidden files by bruteforcing prefixes:

www.site.com/index.php -> www.site.com/~index.php

Bruteforce suffixes discovery (*brute_suffixes*)
================================================

Tries to discover hidden files by bruteforcing suffixes:

www.site.com/index.php -> www.site.com/index2.php

Nikto (*nikto*)
===============

Integration with Nikto: https://www.cirt.net/nikto2

================= ====================================================================================================================================================================================================================================================================================================================================
**Argument name** **Default value**
----------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
pause             0
tuning            x6
exec
timeout           10
plugins           nikto_apacheusers,nikto_apache_expect_xss,nikto_auth,nikto_cgi, nikto_clientaccesspolicy,nikto_content_search,nikto_cookies,nikto_core, nikto_embedded,nikto_favicon,nikto_fileops,nikto_headers,nikto_httpoptions, nikto_msgs,nikto_multiple_index,nikto_outdated,nikto_parked,nikto_report_csv, nikto_siebel,nikto_ssl,nikto_tests
config
================= ====================================================================================================================================================================================================================================================================================================================================

Nmap (*nmap*)
=============

Integration with Nmap: http://nmap.org/

================= =================
**Argument name** **Default value**
----------------- -----------------
args              -vv -A -P0
================= =================

OpenVAS (*openvas*)
===================

Integration with OpenVAS: http://www.openvas.org/

================= ================================
**Argument name** **Default value**
----------------- --------------------------------
profile           Full and fast
host
user              admin
timeout           30
password          \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
port              9390
================= ================================

SSLScan (*sslscan*)
===================

Integration with SSLScan: http://sourceforge.net/projects/sslscan/

DNS Zone Transfer (*zone_transfer*)
===================================

Detects and exploits DNS zone transfer vulnerabilities.

