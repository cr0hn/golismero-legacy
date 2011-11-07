import sys
from io import *
import csv
import urllib2
import md5
import mmap
from Admin.ChangesGenerator import *

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

URL = "http://golismero.googlecode.com/git/"
_l_file = "Admin/changes.dat"


#
# Actualiza la aplicacion
#
def update():

	
	# Comprueba si ya existe un fichero de cambios
	l_changes = None
	try:
		tmp = open(_l_file,"r") # lectura
		text = str(tmp.readlines())
		l_changes = mmap.mmap(-1,len(text))
		l_changes.write(text)
		l_changes.flush()
		l_changes.seek(0)
		tmp.close()
	except IOError:
		# Creamos el fichero
		generate()
		tmp = open(_l_file,"r") # lectura
		text = str(tmp.readlines())
		l_changes = mmap.mmap(-1,len(text))
		l_changes.write(text)
		l_changes.flush()
		l_changes.seek(0)
		tmp.close()
	
	news_changes = open(_l_file,"w") # sobrescribira los cambios
	
	# Recuperamos el fichero de cambios remoto
	r_changes = None
	try:
		tmp = urllib2.urlopen(URL + "Admin/changes.dat").read()
		
		#r_changes = csv.reader(tmp)
		
		r_changes = mmap.mmap(-1,len(tmp))
		r_changes.write(tmp)
		r_changes.flush()
		r_changes.seek(0)
		
	except IOError,e:
		print "[!] Error while geting changes file from remote site: " + str(e)
		print ""
		sys.exit(1)
		
	# Comprobamos versiones
	already_procesed = []
	m_md5 = md5.new()
	try:
		while True:
			r_f = r_changes.readline()
			
			if r_f == "":
				break
						
			# Formato del CSV:
			#
			# (Filename, md5sum)
			#			
			t = r_f.split(",")
			
			r_filename = t[0]
			r_md5 = t[1]
			
			# Buscamos el fichero que conincida con el remoto
			encontrado = False
			for l_f in l_changes:

				l_filename = t[0]
				l_md5 = t[1]
				
				# Comprobamos si ya ha sido procesado
				if not l_filename in already_procesed:
					
					# Si los nombres coinciden
					if l_filename == r_filename:
						# Lo agregamos como procesado
						already_procesed.append(l_filename)

						# Marcamos como encontrado
						encontrado = True
						
						# Comprobamos firmas, si son diferentes hay que actualizar
						if r_md5 != l_md5:
							# Actualizamos firmas
							news_changes.write(unicode(r_filename + "," + r_md5))
							
							# Descargamos el nuevo fichero
							f = urllib2.urlopen(URL + r_filename)
							# Copiamos el contenido al directorio local
							local_file = open(os.curdir + "/" + r_filename, "w")
							local_file.write(f.read())
							local_file.close()
							
						else:
							# Conservamos las firmas
							news_changes.write(unicode(l_filename + "," + l_md5))
			
			# Si el fichero no esta en los fichero locales es que es nuevo y hay que crearlo
			if encontrado == False:
				# Lo agregamos como procesado
				already_procesed.append(r_filename)
				
				# Actualizamos el fichero de cambios
				news_changes.write(unicode(r_filename + "," + r_md5))
				
				# Descargamos el nuevo fichero
				f = urllib2.urlopen(URL + r_filename)
				# Copiamos el contenido al directorio local
				local_file = open(os.curdir + "/" + r_filename, "w")
				local_file.write(f.read())
				local_file.close()
		
		news_changes.flush()
		news_changes.close()
			
			
	except IOError,e:
		print "Error was caught while update: " + str(e)
		print ""  
		sys.exit(1)

	