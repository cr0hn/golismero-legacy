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


#
# Genera el fichero de cambios de todos los ficheros del directorio donde se ejecuta
#
import os
import sys
import csv
import md5


def generate():
	fileList = []
	rootdir = os.curdir
	
	# Obtencion de todos los ficheros .py y .csv
	for root, subFolders, files in os.walk(rootdir):
		#folderCount += len(subFolders)
		for file in files:
			spt = file.split(".")
			ext = spt[len(spt) - 1 ] # obtenemos la extension del fichero
			if ext == "py" or ext == "csv": # filtramos por extension
				f = os.path.join(root,file)
				fileList.append(f.replace("./",""))
				
	# creacion del fichero de cambios
	f_changes = csv.writer(open("Admin/changes.dat","w"))
	
	# para cada fichero creamos una fila
	m_md5 = md5.new()
	for f in fileList:
		# Nombre del fichero
		filename = f
		
		# firma
		m_md5.update(filename)
		firma = m_md5.hexdigest()
		
		f_changes.writerow([filename,firma])
		

	
	
if __name__ == '__main__':
	
	
	print ""
	print "ChangesGenerator- File changes maker"
	print ""
	print "Daniel Garcia Garcia - dani@estotengoqueprobarlo.es"
	print "http://www.estotengoqueprobarlo.es"
	print ""
	
	print ""
	print "[i] Obtieniendo listado de directorios"
		
	generate()
	
	print "[i] Fichero creado correctamente"
	print ""