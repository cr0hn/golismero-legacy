#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Author: Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com

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


# Testing file

from golismero.api.data.information.html import HTML, HTMLElement
from golismero.api.net.network_api import *
from golismero.api.data.information.http import *
from golismero.main.commonstructures import GlobalParams
from golismero.managers.priscillapluginmanager import PriscillaPluginManager
from golismero.api.data.information.url import Url
from thirdparty_libs.urllib3 import *

import sys

if __name__=='__main__':

    #a = PoolManager(10)
    #b=a.request("GET", "localhost", fields=None, encode_multipart=False)
    #sys.exit(1)


    #print str(Url("terra.es", method="post", url_params={"url1":"url1_param"}, post_params={"post1":"post1_data", "post2":"data_post2"}))

    # Config
    p = GlobalParams()
    p.target = ["terra.es"]

    c = NetworkAPI.get_connection()

    # Make request
    #req = HTTP_Request("www.terra.es/portada/")
    #req.add_file_from_file("archivo", "TODO.txt")

    r = c.get("www.terra.es/portada/")
    r = c.get_custom(req)

    r.information.find_all(name="h4", attrs={'class':'ttl-single'})


    sys.exit(0)


    # Plugins
    m_plugins = PriscillaPluginManager().get_plugins(["spider"])

    # Processed URL
    m_processed = []
    m_pendant = [Url("http://www.terra.es/portada/")]

    for a in m_plugins:
        while m_pendant:
            l_url = m_pendant.pop()
            ri = a.recv_info(l_url) # Set for delete duplicates

            if ri:
                m_pendant.extend([x for x in ri if x.url not in m_processed])

            m_processed.append(l_url.url)




    print "a"

