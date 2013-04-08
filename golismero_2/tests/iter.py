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




if __name__=='__main__':
	pass

#------------------------------------------------------------------------------
class itero(object):
	""""""

	#----------------------------------------------------------------------
	def __init__(self):
		"""Constructor"""
		self.a = list(xrange(10))
		self.index = -1

	#----------------------------------------------------------------------
	def __iter__(self):
		""""""
		return self

	#----------------------------------------------------------------------
	def next(self):
		""""""
		self.index+=1
		if self.index < len(self.a):
			return self.a[self.index]
		else:
			raise StopIteration


	#----------------------------------------------------------------------
	def hola_get(self):
		""""""
		if not hasattr(self, '_%s__associated_url' % self.__class__.__name__):
			return None
		else:
			return self.__associated_url


	#----------------------------------------------------------------------
	def hola_set(self, value):
		""""""
		self.__associated_url = value

	hola = property(hola_get, hola_set)


from urllib import url