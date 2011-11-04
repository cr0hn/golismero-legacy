#!/usr/bin/python

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

import argparse
from spider import *
from io_functions import *
from Data import *
from checks import *
from sys import exit
from net_io import *
from updater import *

__version__ = "0.2"
__prog__ = "GoLISMERO"

# Parameters
PARAMETERS=cParams()

def Credits():

	print ""
	print "%s- The Web Knife." % (__prog__)
	print ""
	print "Daniel Garcia Garcia - dani@iniqua.com | dani@estotengoqueprobarlo.es"
	print ""


#
# Comienzo del programa
#
if __name__ == '__main__':
	
	Credits()
	
	#En caso de que se haya introducido una pagina, navegamos a esta URL e iniciamos el proceso de investigacion
	parser = argparse.ArgumentParser()
	parser.add_argument('-R', action='store', dest='recursivity', help='recursivity level of spider.', default = 0)
	parser.add_argument('-t', action='store', dest='target', help='target web site.')
	parser.add_argument('-o', action='store', dest='output', help='output file.', default = None)
	parser.add_argument('-F', action='store', dest='format', help='output format. "scripting" is perfect to combine with awk,cut,grep...', choices = ['text','html','csv','xml','scripting','wfuzz'], default = 'text')
	parser.add_argument('-A', action='store', dest='scan', help='Scan only forms, only links or both.', choices = ['all','forms','links'], default = 'all')
	parser.add_argument('-V', action='store_true', help='Show version.')
	parser.add_argument('-c', action='store_true', help='colorize output')
	parser.add_argument('-m','--compat-mode', action='store_true', help='show results as compact format.')
	parser.add_argument('-na','--no-all', action='store_true', help='implies no-css, no-script, no-images and no-mail.')
	parser.add_argument('-nc','--no-css', action='store_true', help='don\'t get css links.')
	parser.add_argument('-ns','--no-script', action='store_true', help='don\'t get script links.')
	parser.add_argument('-ni','--no-images', action='store_true', help='don\'t get script links.')
	parser.add_argument('-nm','--no-mail', action='store_true', help='don\'t get mails (mailto: tags).')
	parser.add_argument('-nl','--no-unparam-links', action='store_true', help='don\'t get links that have not parameters.')
	parser.add_argument('-l','--long-summary', action='store_true',  help='detailed summary of process.')
	parser.add_argument('-us','--http-auth-user', action='store', dest='http_auth_user', help='set http authenticacion user.', default =  None)
	parser.add_argument('-ps','--http-auth-pass', action='store', dest='http_auth_pass', help='set http authenticacion pass.', default =  None)
	parser.add_argument('-C','--cookie', action='store', dest='cookie', help='set custom cookie.', default =  None)
	parser.add_argument('-P','--proxy', action='store', dest='proxy', help='set proxy, as format: IP:PORT.', default =  None)
	parser.add_argument('-U','--update', action='store_true', help='update Golismero.')
	parser.add_argument('-f','--finger', action='store', dest='finger', help='fingerprint web aplication (not implemented yet).', default =  None)
	
	P = parser.parse_args()
	
			
	if P.update is True:
		print "[i] Updating..."
		update()
		print ""
		exit(0)
	
			
	if P.target is None:
		print ""
		print "[!] You must specify a target: -t option."
		print ""
		exit(1)
	
	
	# Asociamos variable globales
	PARAMETERS.RECURSIVITY = P.recursivity
	PARAMETERS.OUTPUT_FILE = P.output
	PARAMETERS.TARGET = PrepareURL(P.target)
	PARAMETERS.DOMAIN = getDomain(PARAMETERS.TARGET)
	PARAMETERS.PROTOCOL = getProtocol(PARAMETERS.TARGET)
	PARAMETERS.SHOW_TYPE = P.scan
	PARAMETERS.SUMMARY= P.long_summary
	PARAMETERS.COLOR = P.c
	PARAMETERS.OUTPUT_FILE = P.output
	PARAMETERS.OUTPUT_FORMAT = P.format
	PARAMETERS.IS_NCSS = P.no_css
	PARAMETERS.IS_NJS = P.no_script
	PARAMETERS.IS_NIMG = P.no_images
	PARAMETERS.IS_NMAIL = P.no_mail
	PARAMETERS.PROXY = P.proxy
	PARAMETERS.COOKIE = P.cookie
	PARAMETERS.AUTH_USER = P.http_auth_user
	PARAMETERS.AUTH_PASS = P.http_auth_pass
	PARAMETERS.IS_N_PARAMS_LINKS = P.no_unparam_links
	PARAMETERS.COMPACT = P.compat_mode
	
	
	# Mostrar version
	if P.V is True:
		print "%s version is '%s'" % (__prog__, __version__)
		print ""
		exit(0)

	
	# Comprobamos opciones de autenticacion
	if (PARAMETERS.AUTH_USER is not None and PARAMETERS.AUTH_PASS is None) or (PARAMETERS.AUTH_USER is None and PARAMETERS.AUTH_PASS is not None):
		print ""
		print "[!] If you want authentication you need to expecify authentication type."
		print ""
		exit(1)
	elif PARAMETERS.AUTH_USER is not None and PARAMETERS.AUTH_PASS is not None:
		# Comprobamos que la autenticacion con el usuario y password funciona
		if checkAuthCredentials(PARAMETERS.TARGET, PARAMETERS.PROXY, PARAMETERS.AUTH_USER, PARAMETERS.AUTH_PASS) is False:
			print ""
			print "[!] User or password are not correct and can't connect to target."
			print ""
			exit(1)
	
	# Check proxy
	if PARAMETERS.PROXY is not None:
		if isCheckProxy(P.proxy) is False:
			print ""
			print "[!] Proxy format are not correct."
			print ""
			exit(1)
		
	# Marcamos todos los "no"
	if P.no_all is True:
		PARAMETERS.IS_NCSS = True
		PARAMETERS.IS_NJS = True
		PARAMETERS.IS_NIMG = True
		PARAMETERS.IS_NMAIL = True
	
	# Crear fichero de salida, si procede
	MakeFileResults(PARAMETERS)
	
	# Ejecucion principal
	spider(PARAMETERS)

	# Ordenar los resultados
	for i in PARAMETERS.RESULTS:
		i.Order()
		
	# Mostrar resultados
	ShowScreenResults(PARAMETERS)
	
	# Write results to file
	if PARAMETERS.OUTPUT_FILE is not None:
		writeToFile(PARAMETERS)
	
	try:
		pass

	except:
		print "Introduzca una pagina Web correcta"