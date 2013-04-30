#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

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


from django.template import RequestContext

from backend.http import render_to_response_random_server
from backend.url_generator import generate_random_url
from backend.text import TextRandom, example_texs
from random import Random, randint, random
import datetime

def home(request):
    ctx = {"option": "home", "suboption": "home",'sessionid_name': 'jsessionid', 'sessionid_value': randint(100000000,999999999999)}



    return render_to_response_random_server('home/home.html', ctx, context_instance=RequestContext(request))


#----------------------------------------------------------------------
def many_links(request):
    """Generate view for 'many links' option menu."""
    ctx = {"option": "home", "suboption": "many_link"}

    ctx['urls'] = generate_random_url("/home/links/", randint(10,500))

    return render_to_response_random_server('home/many_links.html', ctx, context_instance=RequestContext(request))

#----------------------------------------------------------------------
def phantom_links(request):
    """Receive the on-fly created links"""
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
    m_cols_num = randint(0,8)
    for i in xrange(m_cols_num):
        m_cols_append(m_random_text.generate(randint(2,60/m_cols_num)))
    m_cols_num = m_cols_num if m_cols_num > 0 else 1

    # Generate image columns
    m_imgs = []
    m_imgs_append = m_imgs.append
    m_imgs_num = randint(0,8)
    for i in xrange(m_imgs_num):
        m_imgs_append(randint(1,9))
    m_imgs_num = m_imgs_num if m_imgs_num > 0 else 1
    m_image_borders = ["rounded", "circle", "polaroid"]

    ctx = {"option": "home", "suboption": "many_link", 'random_texts' : m_texts, 'cols': m_cols, 'spans': 12/m_cols_num, 'imgs': m_imgs, 'imgspans' : 12/m_imgs_num, 'img_borders': m_image_borders}

    return render_to_response_random_server('home/phantom_links.html', ctx, context_instance=RequestContext(request))

#----------------------------------------------------------------------
def dir_listing(request):
    """Generate view for 'dir listing' option menu."""
    # Generate random links and files
    m_types = [
        ('  ' , 'unknown.gif'),
        ('TXT', 'text.gif'),
        ('DIR', 'folder.gif'),
        ('IMG', 'image2.gif'),
    ]

    m_urls = []
    m_urls_append = m_urls.append
    m_rand = Random()
    for x in xrange(m_rand.randint(2,50)):
        l_type = m_rand.randint(0,len(m_types) - 1)
        # [IMG, ALT, URL, DATE, SIZE]
        l_date = datetime.datetime.fromtimestamp(m_rand.randint(10000000,1350000000)).strftime("%Y-%m-%d %H:%M")
        l_url = generate_random_url("/home/links/", 1 , False)[0]

        m_urls_append(
            [
                m_types[l_type][1],
                m_types[l_type][0],
                l_url,
                l_date,
                '{:.2f}'.format(m_rand.random() * 10)
            ]
        )

    ctx = {'urls':m_urls}

    return render_to_response_random_server('home/dir_listing.html', ctx, context_instance=RequestContext(request))
