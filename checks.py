'''
GoLISMERO - Simple web analisis
Copyright (C) 2011  Daniel Garcia | dani@estotengoqueprobarlo.es

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
'''

from urlparse import urlparse

#
# Comprueba si la URL tiene el formato correcto y la corrige
#
def PrepareURL(url):
	"""Comprueba y correo el formato de una URL"""	
	if url.lower().find("http") < 0 and url.lower().find("https") < 0:
		return "http://" + url
	else:
		return url

#
# Extra el dominio de una url
#
def getDomain(url):
	if url is not None:
		return urlparse(url)[1].lower()
	
#
# Extra el dominio de una url
#
def getProtocol(url):
	if url is not None:
		return urlparse(url)[0].lower()
	
#
# Comprobar configuracion de proxy
#
def isCheckProxy(proxy):
	if proxy is not None:
		p = proxy.split(":")

		if len(p) <> 2:
			return False
		else:
			if p[1].isdigit() is False or int(p[1]) < 0 or int(p[1]) > 65535: # comprobar puertos
				return False
			else:
				return True