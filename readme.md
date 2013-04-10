= What is GoLISMERO? =
GoLISMERO is a *web spider* is able to *detect vulnerabilities* and *format results* a very useful when starting a web audit.

= It's for? =
GoLISMERO is intended to be a first step when starting a web security audit.

Every time we face a *new URL*, would not it be great to have *easily* and *quick* all the *links*, *forms* with *parameters*, to detect possible URL *vulnerable* and in addition to being presented so that gives us an idea of ​​all points of entry where we could launch attacks? *GoLISMERO lets us do all this.*

= Learning with examples =

=== *Remember: For execute GoLismero you need python 2.7.X or abobe.* ===

Below are several examples and case studies, which are the best way to learn to use a security tool.

  # Getting all links and forms from a web, with all its parameters, extended format:

{{{GoLISMERO.py –t google.com}}}

<img src="http://www.iniqua.com/wp-content/uploads/2011/11/x110911_1801_GoLISMEROSi12.png.pagespeed.ic.Xewovcm3yz.png" />

  # Getting all links, on compact mode, and colorize output:

{{{GoLISMERO.py –c –m –t google.com}}}

<img src="http://www.iniqua.com/wp-content/uploads/2011/11/x110911_1801_GoLISMEROSi22.png.pagespeed.ic.S5Cs2lcYJa.png" />

  # Getting only links. Removing css, javascript, images and mails:

{{{GoLISMERO.py --no-css--no-script --no-images --no-mail –c –A links –m –t google.com}}}

Or, reduced format: 

{{{GoLISMERO.py –na –c –A links –m –t google.com}}}

<img src="http://www.iniqua.com/wp-content/uploads/2011/11/golismero_google_3-1024x882.png.pagespeed.ce.Hoki-xr7Dd.png" />

  # Getting only links with params and follow redirects (HTTP 302) and export results in HTML:

{{{GoLISMERO.py –c –A links --follow –F html –o results.html –m –t google.com}}}

<img src="http://www.iniqua.com/wp-content/uploads/2011/11/x110911_1801_GoLISMEROSi43.png.pagespeed.ic.2lJh2Hy8jH.png" />

And HTML generated code:

<img src="http://www.iniqua.com/wp-content/uploads/2011/11/x110911_1801_GoLISMEROSi53.png.pagespeed.ic.wYdeAb8WuU.png" />

  # Getting all links, looking for potentially vulnerable URL and using an intermediate proxy to analyze responses. The URLs or vulnerable parameters are highlighted in red.

{{{GoLISMERO.py –c –A links --follow -na –x –m –t terra.com}}}

<img src="http://www.iniqua.com/wp-content/uploads/2011/11/golismer_terra_1-1024x702.png" />

Check as ZAP Proxy capture request:

<img src="http://www.iniqua.com/wp-content/uploads/2011/11/x110911_1801_GoLISMEROSi71.png.pagespeed.ic.blW7vCO2YW.png" />
