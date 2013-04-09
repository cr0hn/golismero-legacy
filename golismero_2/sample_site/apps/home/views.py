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


from backend.url_generator import generate_random_url
from backend.text import TextRandom, example_texs
from random import randint, random
#from datetime.datetime import fromtimestamp
import datetime

def home(request):
    ctx = {"option": "home", "suboption": "home"}

    return render_to_response('home/home.html', ctx, context_instance=RequestContext(request))


#----------------------------------------------------------------------
def many_links(request):
    """"""
    ctx = {"option": "home", "suboption": "many_link"}

    ctx['urls'] = generate_random_url("/home/links/", randint(10,500))

    return render_to_response('home/many_links.html', ctx, context_instance=RequestContext(request))

#----------------------------------------------------------------------
def phantom_links(request):
    """"""
    # Generator for random texts
    m_random_text = TextRandom(example_texs)

    # Generate random strings
    m_texts = []
    m_texts_append = m_texts.append
    for i in xrange(randint(1,4)):
        m_texts_append(m_random_text.generate(randint(10,50)))

    # Generate columns
    m_cols = []
    m_cols_append = m_cols.append
    for i in xrange(randint(1,6)):
        m_cols_append(m_random_text.generate(randint(2,10)))

    ctx = {"option": "home", "suboption": "many_link", 'random_texts' : m_texts, 'cols': m_cols, 'spans': 12/len(m_cols)}

    return render_to_response('home/phantom_links.html', ctx, context_instance=RequestContext(request))

#----------------------------------------------------------------------
def dir_listing(request):
    """"""
    # Generate random links and files
    m_types = [
        ('  ' , 'unknown.gif'),
        ('TXT', 'text.gif'),
        ('DIR', 'folder.gif'),
        ('IMG', 'image2.gif'),
    ]

    m_urls = []
    m_urls_append = m_urls.append
    for x in xrange(randint(2,50)):
        l_type = randint(0,len(m_types) - 1)
        # [IMG, ALT, URL, DATE, SIZE]
        m_urls_append(
            [
                m_types[l_type][1],
                m_types[l_type][0],
                generate_random_url("/home/links/", 1 , False)[0][1],
                datetime.datetime.fromtimestamp(randint(0,135) + 100000000).strftime("%Y-%m-%d %H:%M"),
                '{:.2f}'.format(random() * 10)
            ]
        )

    ctx = {'urls':m_urls}

    return render_to_response('home/dir_listing.html', ctx, context_instance=RequestContext(request))
