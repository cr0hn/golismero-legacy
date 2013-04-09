#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com
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

from random import choice, randint
from string import ascii_letters, digits

#----------------------------------------------------------------------
def generate_random_url(base, number=10, with_payload = True):
	"""
	Generate a random URLs from a base site. For example:
	base   = /home/links/
	number = 2

	This function will generate 2 links :
    - /home/links/link2_name.asp
    - /home/links/link1.php?a=b&c
    - /home/links/link1.php

	:param base: base text of URL generated.
	:type base: str

	:param number: number of URL generated.
	:type number: int

	:return: tuple as format (index, URL)
	"""
	if not base or number < 1:
		raise ValueError("Expected a non-empty string and a number > 0")

	# Url extensions
	m_extenstion = ["", ".asp", ".aspx", ".php", ".php3", ".jsp", ".do"]

	m_return = []
	m_return_append = m_return.append

	# Generate
	for i in xrange(number):
		# Generate the payload?
		l_payload = []
		l_payload_append = l_payload.append
		if randint(0,1) == 1 and with_payload:
			# Number of payloads
			for i in xrange(randint(1,10)):
				# Generate value?
				if randint(0,1) == 1:
					l_payload_append("%s=%s" %
					                 (
					                     ''.join(choice(ascii_letters) for _ in xrange(randint(1,10))),
					                     ''.join(choice(ascii_letters + digits) for _ in xrange(randint(1,10)))
					                 )
					)
				else:
					l_payload_append("%s" % ''.join(choice(ascii_letters + digits) for _ in xrange(randint(1,10))))

		# Make the url
		m_name_file = ''.join(choice(ascii_letters + digits) for i in xrange(randint(0,15)))
		m_return_append(
		    (
		        i,
		        "%s%s%s%s" %
		        (
		            base,
		            m_name_file,
		            choice(m_extenstion) if m_name_file else '',
		            '?%s' % '&'.join(l_payload) if l_payload else ''
		        )
		    )
		)

	return m_return