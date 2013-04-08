#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn@cr0hn.com
  Mario Vilas | mvilas@gmail.com

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


from django.shortcuts import render_to_response
from django.template import RequestContext

def home(request):
    ctx = {"option": "home", "suboption": "home"}

    return render_to_response('home/home.html', ctx, context_instance=RequestContext(request))


#----------------------------------------------------------------------
def many_links(request):
    """"""
    ctx = {"option": "home", "suboption": "many_link"}

    return render_to_response('home/many_links.html', ctx, context_instance=RequestContext(request))

#----------------------------------------------------------------------
def dir_listing(request):
    """"""
    ctx = {"option": "home", "suboption": "dir_listing"}

    return render_to_response('home/dir_listing.html', ctx, context_instance=RequestContext(request))
